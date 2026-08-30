# -*- coding: utf-8 -*-
"""
THE BERRY — 微型静态站点生成器（纯 Python 标准库，无依赖）
- i18n: en/zh 双版本静态页 + 根路径客户端语言检测重定向（默认 en）
- 暗色模式: CSS 变量 + data-theme + 手动切换（localStorage）
- 博客: Markdown 预渲染为 HTML（content/posts/*.md）
- 复用设计稿 Apple 风格样式（src/styles/global.css）

用法: python build_site.py  （输出到 dist/）
"""
import hashlib
import html as html_mod
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
ASSETS_SRC = SRC / "assets"
POSTS_SRC = SRC / "content" / "posts"

# 资源版本号（内容哈希）—— CSS/JS 变更后 URL 自动变化，强制浏览器拉新，避免缓存旧版
CSS_V = ""
JS_V = ""

# 用户主页仓库模式：https://berryuiki.github.io/（根路径，无 base 前缀）
BASE = ""
SITE_URL = "https://berryuiki.github.io"

# ============================================================
# 翻译数据（与设计稿文案一致）
# ============================================================
T = {
  "en": {
    "meta": {"title": "Berry Wahlberg — Product Designer & Developer",
             "description": "Portfolio of Berry Wahlberg (花雨琦): product designer and developer crafting simple, human software."},
    "nav": {"about": "About", "skills": "Skills", "experience": "Experience", "work": "Work", "blog": "Blog", "contact": "Contact"},
    "hero": {"eyebrow": "PRODUCT DESIGNER & DEVELOPER", "badge": "THE BERRY · Aries",
             "title": "Hi, I'm Berry Wahlberg.",
             "subtitle": "I design and build thoughtful digital products — simple, fast, and human by default.",
             "cta1": "View My Work", "cta2": "Contact Me", "scroll": "Scroll — photo shrinks"},
    "about": {"title": "About Me", "subtitle": "Designer, developer, and lifelong learner based in Shanghai.",
              "p1": "I like turning ambiguous ideas into products people can understand and use. I work across the whole stack — from wireframes and design systems to frontend and backend code — because great products are built at the intersection of craft and engineering.",
              "p2": "My goal is simple: make technology feel human. I care deeply about accessibility, internationalization, and the small details that turn an interface into an experience.",
              "stats": [("8+", "Years Experience"), ("40+", "Projects Shipped"), ("12", "Countries Served")],
              "statsNote": "Placeholder metrics — pending verification",
              "chips": ["Aries", "ENFP · Happy Pup", "Gentle Bottom"]},
    "skills": {"title": "Skills & Tools", "subtitle": "The tools and crafts I reach for every day.",
               "cols": [("Design", ["Product Design", "Design Systems", "Prototyping", "Usability Testing"]),
                        ("Frontend", ["React", "TypeScript", "Tailwind CSS", "Web Animations"]),
                        ("Backend", ["Node.js", "Python", "GraphQL", "PostgreSQL"]),
                        ("Platform", ["CI/CD", "Internationalization", "Performance", "Accessibility"])]},
    "experience": {"title": "Experience", "subtitle": "Placeholder career history — pending verification.",
                   "items": [("2021 — Present", "Senior Product Designer", "Acme Studio · Shanghai", "Leading the design system and core product flows for a B2B analytics platform used by 2,000+ teams."),
                             ("2018 — 2021", "Product Designer", "Nova Labs · Remote", "Designed end-to-end experiences for a consumer fintech app, growing activation by 34%."),
                             ("2016 — 2018", "Frontend Developer", "Pixel Works · Guangzhou", "Built responsive marketing sites and internal tools with React, cutting page load times by 60%.")]},
    "work": {"title": "Selected Work", "subtitle": "Public projects, documented as real case studies."},
    "testi": {"title": "What People Say", "subtitle": "Placeholder testimonials — pending verification.",
              "items": [("Berry has an eye for detail that most designers only dream of. Every handoff is pixel-perfect and every decision is backed by reasoning.", "Sarah Kim — VP Product, Acme Studio"),
                        ("Working with Berry felt like adding a co-founder, not a contractor. She pushed our product to a level we didn't think we could reach.", "Daniel Chen — Founder, Nova Labs"),
                        ("Fast, thoughtful, and endlessly curious. Berry rebuilt our design system and the whole team felt the difference within a week.", "Mia Zhou — Engineering Lead, Pixel Works")]},
    "contact": {"title": "Let's work together.", "subtitle": "Have a project in mind? I'd love to hear about it.",
                "email": "berrywahlberg@gmail.com"},
    "footer": {"tagline": "Designer & developer crafting simple, human software.",
               "navTitle": "Navigation", "socialTitle": "Social", "contactTitle": "Contact",
               "social": ["GitHub", "X"],
               "contact": ["berrywahlberg@gmail.com", "Shanghai, CN"],
               "copyright": "Copyright 2026 Berry Wahlberg. All rights reserved."},
    "blog": {"title": "Blog", "sub": "Field notes on local-first products, design, and code.", "back": "Back to blog", "empty": "No posts yet.", "latest": "Latest notes", "all": "View all posts"},
  },
  "zh": {
    "meta": {"title": "花雨琦 — 产品设计师 & 开发者",
             "description": "花雨琦（Berry Wahlberg）的个人网站：设计与开发简洁、快速、以人为本的数字产品。"},
    "nav": {"about": "关于", "skills": "技能", "experience": "经历", "work": "作品", "blog": "博客", "contact": "联系"},
    "hero": {"eyebrow": "产品设计师 & 开发者", "badge": "THE BERRY · 白羊座",
             "title": "你好，我是花雨琦。",
             "subtitle": "我设计并打造以人为本的数字产品——简洁、快速、自然。",
             "cta1": "查看我的作品", "cta2": "联系我", "scroll": "下滑 — 照片缩小"},
    "about": {"title": "关于我", "subtitle": "现居上海的设计师与开发者，终身学习者。",
              "p1": "我喜欢把模糊的想法变成让人容易理解、愿意使用的产品。我的工作横跨全栈——从线框稿与设计系统，到前后端代码——因为好的产品诞生于设计手艺与工程实现的交汇处。",
              "p2": "我的目标很简单：让技术有人情味。我关注无障碍、国际化，以及那些把界面变成体验的微小细节。",
              "stats": [("8+", "年经验"), ("40+", "交付项目"), ("12", "服务国家/地区")],
              "statsNote": "占位数据 · 等待核实",
              "chips": ["白羊座", "ENFP · 快乐小狗", "温柔受"]},
    "skills": {"title": "技能与工具", "subtitle": "我每天都会用到的工具与手艺。",
               "cols": [("设计", ["产品设计", "设计系统", "原型制作", "可用性测试"]),
                        ("前端", ["React", "TypeScript", "Tailwind CSS", "Web 动效"]),
                        ("后端", ["Node.js", "Python", "GraphQL", "PostgreSQL"]),
                        ("平台", ["CI/CD", "国际化", "性能优化", "无障碍"])]},
    "experience": {"title": "工作经历", "subtitle": "占位经历 · 等待核实后更新。",
                   "items": [("2021 — 至今", "资深产品设计师", "Acme Studio · 上海", "负责 B2B 分析平台的设计系统与核心产品流程，服务 2,000+ 团队。"),
                             ("2018 — 2021", "产品设计师", "Nova Labs · 远程", "为消费级金融应用设计端到端体验，激活率提升 34%。"),
                             ("2016 — 2018", "前端开发者", "Pixel Works · 广州", "使用 React 构建响应式营销网站与内部工具，页面加载时间降低 60%。")]},
    "work": {"title": "精选作品", "subtitle": "来自公开项目的真实案例。"},
    "testi": {"title": "他们怎么说", "subtitle": "占位评价 · 等待核实后更新。",
              "items": [("花雨琦（Berry）对细节的洞察是大多数设计师梦寐以求的。每次交付都像素级完美，每个决策都有理有据。", "Sarah Kim — Acme Studio 产品副总裁"),
                        ("与花雨琦合作就像多了一位联合创始人，而不是外包。她把我们的产品推到了我们以为到不了的高度。", "Daniel Chen — Nova Labs 创始人"),
                        ("高效、深思熟虑、永远充满好奇。花雨琦重建了我们的设计系统，整个团队在一周内就感受到了差别。", "Mia Zhou — Pixel Works 技术负责人")]},
    "contact": {"title": "一起合作吧。", "subtitle": "有项目想法？很乐意与你聊聊。",
                "email": "berrywahlberg@gmail.com"},
    "footer": {"tagline": "用设计与代码，打造简洁而有温度的产品。",
               "navTitle": "导航", "socialTitle": "社交", "contactTitle": "联系",
               "social": ["GitHub", "X"],
               "contact": ["berrywahlberg@gmail.com", "中国 · 上海"],
               "copyright": "2026 花雨琦 · 版权所有"},
    "blog": {"title": "博客", "sub": "关于本地优先产品、设计与代码的实践笔记。", "back": "返回博客", "empty": "暂无文章。", "latest": "最新文章", "all": "查看全部文章"},
  },
}

CASES = [
  {
    "slug": "lexora",
    "name": "Lexora",
    "repo": "https://github.com/BerryUIKI/Lexora",
    "live": "https://berryuiki.github.io/Lexora/",
    "mark": "LXR",
    "tone": "violet",
    "stack": "Tauri 2 · Rust · SolidJS · Milkdown",
    "en": {
      "summary": "A local-first Markdown workspace with in-place WYSIWYG editing, built for speed, privacy, and focused writing.",
      "status": "Open source · v0.1.3",
      "challenge": "Markdown tools often force a choice between source control and a calm writing surface. Lexora explores how both can live in one lightweight desktop workspace.",
      "approach": "The app separates reading, writing, and code modes while keeping files local. Tauri and Rust provide the desktop shell; SolidJS and Milkdown power the editing experience.",
      "facts": ["Fully offline with zero telemetry", "Nine interface languages", "Workspace tabs, search, diagrams, math, and HTML export", "README reports startup under 400 ms and an app size around 3.6 MB"],
    },
    "zh": {
      "summary": "一款本地优先的 Markdown 工作台，用原位 WYSIWYG 编辑兼顾速度、隐私与专注写作。",
      "status": "开源项目 · v0.1.3",
      "challenge": "Markdown 工具常让用户在源码掌控和安静的写作界面之间二选一。Lexora 尝试把两者放进一个轻量桌面工作台。",
      "approach": "产品区分阅读、写作与代码模式，并让文件始终留在本地。Tauri 与 Rust 负责桌面外壳，SolidJS 与 Milkdown 承载编辑体验。",
      "facts": ["完全离线，零遥测", "支持九种界面语言", "包含工作区标签、搜索、图表、数学公式与 HTML 导出", "README 标注启动低于 400 ms、应用体积约 3.6 MB"],
    },
  },
  {
    "slug": "berry-aigc-toolbox",
    "name": "Berry AIGC Toolbox",
    "repo": "https://github.com/BerryUIKI/Berry-AIGC-Toolbox",
    "live": "",
    "mark": "BAT",
    "tone": "blue",
    "stack": "Tauri 2 · Rust · Vue 3 · SQLite",
    "en": {
      "summary": "An open-source metadata indexer and visual library for organizing AI-generated images and video.",
      "status": "Open source · Active development (M1)",
      "challenge": "Generated media arrives with fragmented prompts and metadata across different tools. The project creates one searchable, local catalog without moving the original files.",
      "approach": "A Rust scanning pipeline extracts multiple metadata formats into SQLite, while the Vue interface adds search, filters, albums, tags, favorites, ratings, and visual browsing.",
      "facts": ["Indexes images and video without moving originals", "Parses metadata from multiple generation tools", "Albums, tags, favorites, ratings, and visual search", "Seven interface languages; current rewrite is at milestone M1"],
    },
    "zh": {
      "summary": "面向 AI 生成图片与视频的开源元数据索引器和可视化素材库。",
      "status": "开源项目 · 活跃开发中（M1）",
      "challenge": "生成式媒体的提示词与元数据分散在不同工具和文件格式里。这个项目希望在不移动原文件的前提下，建立统一、可搜索的本地目录。",
      "approach": "Rust 扫描管线提取多种元数据并写入 SQLite，Vue 界面提供搜索、筛选、相册、标签、收藏、评分与可视化浏览。",
      "facts": ["索引图片和视频，不移动原文件", "解析多种生成工具的元数据", "支持相册、标签、收藏、评分与视觉搜索", "支持七种界面语言；当前重写版本处于 M1 里程碑"],
    },
  },
  {
    "slug": "axiara",
    "name": "Axiara",
    "repo": "https://github.com/BerryUIKI/Axiara",
    "live": "",
    "mark": "AXR",
    "tone": "rose",
    "stack": "Python 3.12 · FastAPI · LangGraph",
    "en": {
      "summary": "An agent workspace for valuation research with explicit capability modes and permission boundaries.",
      "status": "Open source · Research workspace",
      "challenge": "Valuation agents need access to evidence, calculations, and review tools without silently crossing data or permission boundaries.",
      "approach": "Axiara organizes the workflow into archive, query, batch quote, and review modes, backed by three data layers with deliberately separated permissions.",
      "facts": ["Four explicit capability modes", "Three storage layers with strict permission boundaries", "FastAPI service and LangGraph orchestration", "Repository test suite documents 234 tests"],
    },
    "zh": {
      "summary": "一个用于估值研究的 Agent 工作台，以明确的能力模式和权限边界组织工作流。",
      "status": "开源项目 · 研究型工作台",
      "challenge": "估值 Agent 需要访问证据、计算与审核工具，同时不能悄悄越过数据或权限边界。",
      "approach": "Axiara 将流程拆分为归档、查询、批量报价与审核四种模式，并用三层数据结构刻意隔离权限。",
      "facts": ["四种明确的能力模式", "三层存储结构与严格权限边界", "FastAPI 服务与 LangGraph 编排", "仓库测试说明记录了 234 项测试"],
    },
  },
]

LANGS = ["en", "zh"]
DEFAULT_LANG = "en"

ANCHORS = ["about", "skills", "experience", "work", "contact"]


def esc(s: str) -> str:
    return html_mod.escape(str(s), quote=True)


def esc_attr(s: str) -> str:
    return html_mod.escape(str(s), quote=True)


# ============================================================
# 组件渲染
# ============================================================
def render_nav(locale: str, t: dict, locale_path: str = "/") -> str:
    section_links = "".join(
        f'<li><a href="{BASE}/{locale}/#{a}">{esc(t["nav"][a])}</a></li>' for a in ANCHORS
    )
    links = section_links + f'<li><a href="{BASE}/{locale}/blog/">{esc(t["nav"]["blog"])}</a></li>'
    mobile_links = "".join(
        f'<a href="{BASE}/{locale}/#{a}">{esc(t["nav"][a])}</a>' for a in ANCHORS
    ) + f'<a href="{BASE}/{locale}/blog/">{esc(t["nav"]["blog"])}</a>'
    lang_switch_parts = []
    for l in LANGS:
        current = ' aria-current="true"' if l == locale else ""
        label = "EN" if l == "en" else "中文"
        lang_switch_parts.append(f'<a href="{BASE}/{l}{locale_path}" lang="{l}"{current}>{label}</a>')
    lang_switch = "".join(lang_switch_parts)
    menu_label = "打开导航菜单" if locale == "zh" else "Open navigation menu"
    menu_close_label = "关闭导航菜单" if locale == "zh" else "Close navigation menu"
    theme_label = "切换明暗主题" if locale == "zh" else "Toggle color theme"
    nav_label = "主导航" if locale == "zh" else "Primary navigation"
    return f"""
<nav class="global-nav" aria-label="{nav_label}">
  <div class="scroll-progress" aria-hidden="true"><span></span></div>
  <a class="global-nav__logo" href="{BASE}/{locale}/">THE BERRY</a>
  <ul class="global-nav__links">{links}</ul>
  <div class="global-nav__actions">
    <div class="lang-switch" role="group" aria-label="{'语言' if locale == 'zh' else 'Language'}">{lang_switch}</div>
    <button class="theme-toggle" id="theme-toggle" type="button" aria-label="{theme_label}" aria-pressed="false">
      <svg id="theme-icon-sun" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <circle cx="12" cy="12" r="5"/><path d="M12 1v3M12 20v3M1 12h3M20 12h3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/>
      </svg>
      <svg id="theme-icon-moon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="display:none">
        <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/>
      </svg>
    </button>
    <button class="nav-menu-toggle" id="nav-menu-toggle" type="button" aria-label="{menu_label}" data-open-label="{menu_label}" data-close-label="{menu_close_label}" aria-controls="mobile-nav" aria-expanded="false">
      <span></span><span></span>
    </button>
  </div>
  <div class="global-nav__mobile" id="mobile-nav">{mobile_links}</div>
</nav>"""


def render_hero(locale: str, t: dict) -> str:
    frame_left = "作品集 / 2026" if locale == "zh" else "PORTFOLIO / 2026"
    frame_right = "上海 — 北纬 31.2304°" if locale == "zh" else "SHANGHAI — 31.2304° N"
    return f"""
<section class="hero" id="top">
  <picture>
    <source media="(max-width: 640px)" srcset="{BASE}/assets/hero-mobile.webp" />
    <img class="hero__img" src="{BASE}/assets/hero.webp" alt="" width="1672" height="941" />
  </picture>
  <div class="hero__scrim" aria-hidden="true"></div>
  <div class="hero__frame" aria-hidden="true">
    <span>{frame_left}</span>
    <span>{frame_right}</span>
  </div>
  <div class="hero__content">
    <p class="hero__eyebrow">{esc(t["hero"]["eyebrow"])}</p>
    <p class="hero__badge">{esc(t["hero"]["badge"])}</p>
    <h1 class="hero__title">{esc(t["hero"]["title"])}</h1>
    <p class="hero__subtitle">{esc(t["hero"]["subtitle"])}</p>
    <div class="hero__ctas">
      <a class="btn btn-primary" href="{BASE}/{locale}/#work">{esc(t["hero"]["cta1"])}</a>
      <a class="btn btn-ghost-on-dark" href="{BASE}/{locale}/#contact">{esc(t["hero"]["cta2"])}</a>
    </div>
  </div>
  <a class="hero__scroll-hint" href="#about" aria-label="Scroll to content">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M6 9l6 6 6-6"/>
    </svg>
  </a>
</section>"""


def render_about(t: dict) -> str:
    section_label = "人物" if t is T["zh"] else "PROFILE"
    portrait_label = "另一面 / 02" if t is T["zh"] else "ALTER EGO / 02"
    stats = "".join(
        f'<div><div class="about-stats__num">{esc(v)}</div><div class="about-stats__label">{esc(l)}</div></div>'
        for v, l in t["about"]["stats"]
    )
    chips = "".join(f'<span class="chip">{esc(c)}</span>' for c in t["about"]["chips"])
    return f"""
<section class="section section--parchment section--indexed" id="about" data-index="01" data-label="{section_label}">
  <div class="container">
    <div class="section-head">
      <h2 class="section-title">{esc(t["about"]["title"])}</h2>
      <p class="section-sub">{esc(t["about"]["subtitle"])}</p>
    </div>
    <div class="about-grid">
      <div class="about-text">
        <p>{esc(t["about"]["p1"])}</p>
        <p>{esc(t["about"]["p2"])}</p>
        <div class="about-stats">{stats}</div>
        <p class="content-status">{esc(t["about"]["statsNote"])}</p>
        <div class="about-chips">{chips}</div>
      </div>
      <div class="about-portrait">
        <img src="{BASE}/assets/portrait.webp" alt="{esc(t["about"]["title"])}" width="1080" height="1080" loading="lazy" />
        <span class="about-portrait__label" aria-hidden="true">{portrait_label}</span>
      </div>
    </div>
  </div>
</section>"""


def render_skills(t: dict) -> str:
    section_label = "能力" if t is T["zh"] else "CAPABILITIES"
    cols = "".join(
        f'<div class="skills-card" data-spotlight><span class="skills-card__index">0{i + 1}</span><h3>{esc(name)}</h3><ul>'
        + "".join(f"<li>{esc(i)}</li>" for i in items)
        + "</ul></div>"
        for i, (name, items) in enumerate(t["skills"]["cols"])
    )
    return f"""
<section class="section section--dark section--indexed" id="skills" data-index="02" data-label="{section_label}">
  <div class="container">
    <div class="section-head">
      <h2 class="section-title">{esc(t["skills"]["title"])}</h2>
      <p class="section-sub">{esc(t["skills"]["subtitle"])}</p>
    </div>
    <div class="skills-grid">{cols}</div>
  </div>
</section>"""


def render_experience(t: dict) -> str:
    section_label = "旅程" if t is T["zh"] else "JOURNEY"
    items = "".join(
        f'<div class="timeline__item"><span class="timeline__index">0{i + 1}</span><div class="timeline__period">{esc(period)}</div>'
        f'<div><div class="timeline__role">{esc(role)}</div>'
        f'<div class="timeline__company">{esc(company)}</div>'
        f'<p class="timeline__desc">{esc(desc)}</p></div></div>'
        for i, (period, role, company, desc) in enumerate(t["experience"]["items"])
    )
    return f"""
<section class="section section--indexed" id="experience" data-index="03" data-label="{section_label}">
  <div class="container">
    <div class="section-head">
      <h2 class="section-title">{esc(t["experience"]["title"])}</h2>
      <p class="section-sub">{esc(t["experience"]["subtitle"])}</p>
    </div>
    <div class="timeline">{items}</div>
  </div>
</section>"""


def render_work(locale: str, t: dict) -> str:
    section_label = "精选作品" if t is T["zh"] else "SELECTED WORK"
    cards = ""
    for i, case in enumerate(CASES):
        copy = case[locale]
        href = f'{BASE}/{locale}/work/{case["slug"]}/'
        more = "查看案例" if locale == "zh" else "Read case study"
        cards += (
            f'<a class="work-card" data-tilt href="{href}" aria-label="{esc_attr(case["name"] + ": " + copy["summary"])}">'
            f'<span class="work-card__index">0{i + 1}</span>'
            f'<div class="work-card__cover work-card__cover--{esc_attr(case["tone"])}" aria-hidden="true">'
            f'<span>{esc(case["mark"])}</span><small>{esc(case["name"])}</small></div>'
            f'<h3>{esc(case["name"])}</h3><p>{esc(copy["summary"])}</p>'
            f'<div class="work-card__tags">{esc(case["stack"])}</div>'
            f'<span class="work-card__more">{more} →</span></a>'
        )
    return f"""
<section class="section section--parchment section--indexed" id="work" data-index="04" data-label="{section_label}">
  <div class="container">
    <div class="section-head">
      <h2 class="section-title">{esc(t["work"]["title"])}</h2>
      <p class="section-sub">{esc(t["work"]["subtitle"])}</p>
    </div>
    <div class="work-grid">{cards}</div>
  </div>
</section>"""


def render_testimonials(t: dict) -> str:
    section_label = "回声" if t is T["zh"] else "VOICES"
    cards = "".join(
        f'<figure class="testi-card"><span class="testi-card__quote" aria-hidden="true">“</span><blockquote>{esc(q)}</blockquote><figcaption><span>0{i + 1}</span>{esc(a)}</figcaption></figure>'
        for i, (q, a) in enumerate(t["testi"]["items"])
    )
    return f"""
<section class="section section--dark section--indexed" id="testimonials" data-index="06" data-label="{section_label}">
  <div class="container">
    <div class="section-head">
      <h2 class="section-title">{esc(t["testi"]["title"])}</h2>
      <p class="section-sub">{esc(t["testi"]["subtitle"])}</p>
    </div>
    <div class="testi-grid">{cards}</div>
  </div>
</section>"""


def render_contact(t: dict) -> str:
    email = t["contact"]["email"]
    section_label = "联系" if t is T["zh"] else "CONTACT"
    marquee = "一起创造难忘的作品 — 一起创造难忘的作品 —" if t is T["zh"] else "LET'S MAKE SOMETHING UNFORGETTABLE — LET'S MAKE SOMETHING UNFORGETTABLE —"
    socials = (
        f'<a href="https://github.com/BerryUIKI">GitHub @BerryUIKI</a>'
        f'<a href="https://x.com/BerryUIKI">X @BerryUIKI</a>'
        f'<a href="mailto:{esc_attr(email)}">Email</a>'
    )
    return f"""
<section class="contact section--indexed" id="contact" data-index="07" data-label="{section_label}">
  <div class="contact__marquee" aria-hidden="true"><span>{marquee}</span></div>
  <div class="container">
    <h2>{esc(t["contact"]["title"])}</h2>
    <p>{esc(t["contact"]["subtitle"])}</p>
    <a class="btn btn-primary" href="mailto:{esc_attr(email)}">{esc(email)}</a>
    <div class="contact__socials">{socials}</div>
  </div>
</section>"""


def render_footer(locale: str, t: dict) -> str:
    nav_links = "".join(
        f'<a href="{BASE}/{locale}/#{anchor}">{esc(t["nav"][anchor])}</a>' for anchor in ANCHORS
    )
    nav_links += f'<a href="{BASE}/{locale}/blog/">{esc(t["nav"]["blog"])}</a>'
    social = "".join(
        f'<a href="{url}">{esc(label)}</a>'
        for label, url in zip(t["footer"]["social"], ["https://github.com/BerryUIKI", "https://x.com/BerryUIKI"])
    )
    contact_col = "".join(
        f'<a href="mailto:{esc_attr(t["contact"]["email"])}">{esc(label)}</a>' if i == 0 else f'<span>{esc(label)}</span>'
        for i, label in enumerate(t["footer"]["contact"])
    )
    return f"""
<footer class="footer">
  <div class="container">
    <div class="footer__top">
      <div class="footer__brand"><div class="logo">THE BERRY</div><p>{esc(t["footer"]["tagline"])}</p></div>
      <div class="footer__cols">
        <div class="footer__col"><h4>{esc(t["footer"]["navTitle"])}</h4>{nav_links}</div>
        <div class="footer__col"><h4>{esc(t["footer"]["socialTitle"])}</h4>{social}</div>
        <div class="footer__col"><h4>{esc(t["footer"]["contactTitle"])}</h4>{contact_col}</div>
      </div>
    </div>
    <div class="footer__bottom"><span>{esc(t["footer"]["copyright"])}</span><span>EN | 中文</span></div>
  </div>
</footer>"""


# ============================================================
# 页面壳 + 交互脚本
# ============================================================
SCRIPT_JS = """// THE BERRY — 交互脚本
// 主题初始化（localStorage 优先，跟随系统，默认 light）
(function () {
  try {
    var saved = localStorage.getItem('berry-theme');
    var theme = saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
  } catch (e) { document.documentElement.setAttribute('data-theme', 'light'); }
})();

// 主题切换按钮
document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('theme-toggle');
  var root = document.documentElement;
  var nav = document.querySelector('.global-nav');
  var progress = document.querySelector('.scroll-progress span');
  var menuToggle = document.getElementById('nav-menu-toggle');
  var mobileNav = document.getElementById('mobile-nav');

  function closeMenu() {
    if (!nav || !menuToggle) return;
    nav.classList.remove('is-menu-open');
    menuToggle.setAttribute('aria-expanded', 'false');
    menuToggle.setAttribute('aria-label', menuToggle.getAttribute('data-open-label'));
  }
  if (menuToggle && nav) {
    menuToggle.addEventListener('click', function () {
      var open = !nav.classList.contains('is-menu-open');
      nav.classList.toggle('is-menu-open', open);
      menuToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      menuToggle.setAttribute('aria-label', menuToggle.getAttribute(open ? 'data-close-label' : 'data-open-label'));
      if (open && mobileNav) {
        var firstLink = mobileNav.querySelector('a');
        if (firstLink) firstLink.focus();
      }
    });
  }
  if (mobileNav) {
    mobileNav.addEventListener('click', function (event) {
      if (event.target.closest('a')) closeMenu();
    });
  }
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      closeMenu();
      if (menuToggle) menuToggle.focus();
    }
  });
  function syncIcon() {
    var dark = root.getAttribute('data-theme') === 'dark';
    var sun = document.getElementById('theme-icon-sun');
    var moon = document.getElementById('theme-icon-moon');
    if (sun) sun.style.display = dark ? 'none' : '';
    if (moon) moon.style.display = dark ? '' : 'none';
    if (toggle) toggle.setAttribute('aria-pressed', dark ? 'true' : 'false');
  }
  syncIcon();
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      var applyTheme = function () {
        root.setAttribute('data-theme', next);
        try { localStorage.setItem('berry-theme', next); } catch (e) {}
        syncIcon();
      };
      var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (document.startViewTransition && !reduce) {
        var rect = toggle.getBoundingClientRect();
        root.style.setProperty('--theme-x', (rect.left + rect.width / 2) + 'px');
        root.style.setProperty('--theme-y', (rect.top + rect.height / 2) + 'px');
        document.startViewTransition(applyTheme);
      } else {
        applyTheme();
      }
    });
  }

  // 语言切换持久化：点击语言链接时记住选择，下次访问直接用
  var langLinks = document.querySelectorAll('.lang-switch a');
  for (var li = 0; li < langLinks.length; li++) {
    langLinks[li].addEventListener('click', function () {
      try { localStorage.setItem('berry-lang', this.getAttribute('lang')); } catch (e) {}
    });
  }

  // Hero 滚动缩小（Apple 产品页式 scroll-shrink，加强版）
  var hero = document.querySelector('.hero');
  var img = hero ? hero.querySelector('.hero__img') : null;
  var scrim = hero ? hero.querySelector('.hero__scrim') : null;
  var heroContent = hero ? hero.querySelector('.hero__content') : null;
  var heroFrame = hero ? hero.querySelector('.hero__frame') : null;
  function updateHero() {
    if (!hero || !img) return;
    var y = window.scrollY;
    var max = Math.max(hero.offsetHeight, 1);
    var p = Math.min(y / max, 1);
    hero.style.setProperty('--hero-progress', String(p));
    img.style.transform = 'scale(' + (1 - 0.45 * p) + ') translateY(' + (120 * p) + 'px)';
    img.style.opacity = String(1 - 0.6 * p);
    // 下滑时底部两角渐变圆角（全屏直角 → 卡片圆角）
    var br = Math.round(28 * p);
    img.style.borderRadius = '0 0 ' + br + 'px ' + br + 'px';
    // scrim 随滚动淡出，露出纯色主题背景（亮色=白 / 暗色=黑）
    if (scrim) scrim.style.opacity = String(1 - 0.92 * p);
    if (heroContent) heroContent.style.opacity = String(Math.max(0, 1 - 2.1 * p));
    if (heroFrame) heroFrame.style.opacity = String(Math.max(0, 1 - 1.35 * p));
    if (nav) nav.classList.toggle('is-scrolled', y > 24);
    if (progress) {
      var doc = document.documentElement;
      var total = Math.max(doc.scrollHeight - window.innerHeight, 1);
      progress.style.transform = 'scaleX(' + Math.min(y / total, 1) + ')';
    }
  }
  var ticking = false;
  function onScroll() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(function () {
        updateHero();
        ticking = false;
      });
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  updateHero();

  // Section reveals + active navigation
  var sections = document.querySelectorAll('main > section');
  if ('IntersectionObserver' in window) {
    document.body.classList.add('reveal-ready');
    var revealObserver = new IntersectionObserver(function (entries) {
      for (var r = 0; r < entries.length; r++) {
        if (entries[r].isIntersecting) entries[r].target.classList.add('is-visible');
      }
    }, { threshold: 0.14 });
    for (var s = 0; s < sections.length; s++) revealObserver.observe(sections[s]);

    var navLinks = document.querySelectorAll('.global-nav__links a');
    var activeObserver = new IntersectionObserver(function (entries) {
      for (var a = 0; a < entries.length; a++) {
        if (!entries[a].isIntersecting || !entries[a].target.id) continue;
        for (var n = 0; n < navLinks.length; n++) {
          var active = navLinks[n].getAttribute('href').indexOf('#' + entries[a].target.id) !== -1;
          if (active) navLinks[n].setAttribute('aria-current', 'location');
          else navLinks[n].removeAttribute('aria-current');
        }
      }
    }, { rootMargin: '-42% 0px -52% 0px' });
    for (var o = 0; o < sections.length; o++) activeObserver.observe(sections[o]);
  }

  // Pointer spotlight and restrained 3D tilt
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (finePointer) {
    var spotlights = document.querySelectorAll('[data-spotlight]');
    for (var sp = 0; sp < spotlights.length; sp++) {
      spotlights[sp].addEventListener('pointermove', function (event) {
        var rect = this.getBoundingClientRect();
        this.style.setProperty('--spot-x', (event.clientX - rect.left) + 'px');
        this.style.setProperty('--spot-y', (event.clientY - rect.top) + 'px');
      });
    }
  }
  if (finePointer && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var tilts = document.querySelectorAll('[data-tilt]');
    for (var ti = 0; ti < tilts.length; ti++) {
      tilts[ti].addEventListener('pointermove', function (event) {
        var rect = this.getBoundingClientRect();
        var x = (event.clientX - rect.left) / Math.max(rect.width, 1) - 0.5;
        var y = (event.clientY - rect.top) / Math.max(rect.height, 1) - 0.5;
        this.style.setProperty('--tilt-x', (-y * 5).toFixed(2) + 'deg');
        this.style.setProperty('--tilt-y', (x * 7).toFixed(2) + 'deg');
        this.style.setProperty('--image-x', (x * 12).toFixed(2) + 'px');
        this.style.setProperty('--image-y', (y * 12).toFixed(2) + 'px');
      });
      tilts[ti].addEventListener('pointerleave', function () {
        this.style.setProperty('--tilt-x', '0deg');
        this.style.setProperty('--tilt-y', '0deg');
        this.style.setProperty('--image-x', '0px');
        this.style.setProperty('--image-y', '0px');
      });
    }
  }
});
"""

INDEX_REDIRECT = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>THE BERRY — Berry Wahlberg / 花雨琦</title>
<script>
(function () {{
  // 统一响应式页面 → 语言检测重定向（默认英语优先）
  var SUPPORTED = ['en', 'zh'];
  var DEFAULT = 'en';
  var lang = DEFAULT;
  try {{
    var saved = localStorage.getItem('berry-lang');
    if (saved && SUPPORTED.indexOf(saved) !== -1) {{
      lang = saved;
    }} else {{
      var list = (navigator.languages && navigator.languages.length)
        ? navigator.languages
        : [navigator.language || DEFAULT];
      var hasZh = false;
      for (var i = 0; i < list.length; i++) {{
        var code = String(list[i]).toLowerCase().split('-')[0];
        if (code === 'en') {{ lang = 'en'; break; }}
        if (code === 'zh') {{ hasZh = true; }}
      }}
      if (lang === DEFAULT && hasZh) {{ lang = 'zh'; }}
    }}
  }} catch (e) {{ lang = DEFAULT; }}
  location.replace('{BASE}/' + lang + '/');
}})();
</script>
</head>
<body style="font-family:system-ui;padding:24px;color:#666">
<p>Redirecting to your language… / 正在为你切换语言…</p>
</body>
</html>"""


def page_shell(locale: str, t: dict, title: str, desc: str, body: str, canonical_path: str,
               has_alternates: bool = True, schema=None,
               og_type: str = "website", og_image: str = "/og.png",
               robots: str = "index,follow,max-image-preview:large") -> str:
    meta = t["meta"]
    full_title = f"{title} — {meta['title']}" if title else meta["title"]
    canonical_url = f"{SITE_URL}{canonical_path}"
    alternate_links = ""
    if has_alternates:
        locale_prefix = f"/{locale}"
        suffix = canonical_path[len(locale_prefix):] if canonical_path.startswith(locale_prefix) else "/"
        alternate_links = (
            f'<link rel="alternate" hreflang="en" href="{SITE_URL}/en{suffix}" />\n'
            f'<link rel="alternate" hreflang="zh-Hans" href="{SITE_URL}/zh{suffix}" />\n'
            f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/en{suffix}" />'
        )
    person_schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Berry Wahlberg",
        "alternateName": "花雨琦",
        "url": SITE_URL,
        "email": "mailto:berrywahlberg@gmail.com",
        "sameAs": ["https://github.com/BerryUIKI", "https://x.com/BerryUIKI"],
        "jobTitle": "Product Designer & Developer",
    }
    structured_data = json.dumps(schema or person_schema, ensure_ascii=False, separators=(",", ":"))
    skip_label = "跳到主要内容" if locale == "zh" else "Skip to main content"
    return f"""<!doctype html>
<html lang="{locale}" data-theme="light">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc or meta['description'])}" />
<meta name="author" content="Berry Wahlberg / 花雨琦" />
<meta name="robots" content="{esc_attr(robots)}" />
<meta property="og:title" content="{esc(full_title)}" />
<meta property="og:description" content="{esc(desc or meta['description'])}" />
<meta property="og:type" content="{esc_attr(og_type)}" />
<meta property="og:site_name" content="THE BERRY" />
<meta property="og:locale" content="{'zh_CN' if locale == 'zh' else 'en_US'}" />
<meta property="og:url" content="{canonical_url}" />
<meta property="og:image" content="{SITE_URL}{og_image}" />
<meta property="og:image:alt" content="THE BERRY — Berry Wahlberg / 花雨琦" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(full_title)}" />
<meta name="twitter:description" content="{esc(desc or meta['description'])}" />
<meta name="twitter:image" content="{SITE_URL}{og_image}" />
<meta name="twitter:creator" content="@BerryUIKI" />
<meta name="theme-color" content="#08080a" />
<link rel="canonical" href="{canonical_url}" />
{alternate_links}
  <link rel="icon" type="image/svg+xml" href="{BASE}/favicon.svg" />
  <link rel="manifest" href="{BASE}/site.webmanifest" />
  <link rel="stylesheet" href="{BASE}/styles.css?v={CSS_V}" />
  <script type="application/ld+json">{structured_data}</script>
</head>
<body>
<a class="skip-link" href="#main-content">{skip_label}</a>
{body}
<script src="{BASE}/script.js?v={JS_V}"></script>
</body>
</html>"""


def format_post_date(locale: str, value: date) -> str:
    if locale == "zh":
        return f"{value.year}年{value.month}月{value.day}日"
    return value.strftime("%B %d, %Y")


def render_blog_teaser(locale: str, t: dict) -> str:
    posts = [p for p in load_posts() if p["lang"] == locale][:3]
    cards = ""
    for post in posts:
        cards += (
            f'<article class="blog-teaser__card"><time datetime="{post["date"].isoformat()}">{esc(format_post_date(locale, post["date"]))}</time>'
            f'<h3><a href="{BASE}/{locale}/blog/{post["slug"]}/">{esc(post["title"])}</a></h3>'
            f'<p>{esc(post["description"])}</p><a class="blog-teaser__read" href="{BASE}/{locale}/blog/{post["slug"]}/">'
            f'{"阅读文章" if locale == "zh" else "Read note"} →</a></article>'
        )
    return f"""
<section class="section section--indexed blog-teaser" id="notes" data-index="05" data-label="{'最新文章' if locale == 'zh' else 'LATEST NOTES'}">
  <div class="container">
    <div class="section-head"><h2 class="section-title">{esc(t["blog"]["latest"])}</h2><p class="section-sub">{esc(t["blog"]["sub"])}</p></div>
    <div class="blog-teaser__grid">{cards}</div>
    <a class="blog-teaser__all" href="{BASE}/{locale}/blog/">{esc(t["blog"]["all"])} →</a>
  </div>
</section>"""


def render_home(locale: str) -> str:
    t = T[locale]
    body = (
        render_nav(locale, t)
        + '<main id="main-content">'
        + render_hero(locale, t)
        + render_about(t)
        + render_skills(t)
        + render_experience(t)
        + render_work(locale, t)
        + render_blog_teaser(locale, t)
        + render_testimonials(t)
        + render_contact(t)
        + '</main>'
        + render_footer(locale, t)
    )
    return page_shell(locale, t, "", "", body, f"/{locale}/")


def render_case_page(locale: str, case: dict) -> str:
    t = T[locale]
    copy = case[locale]
    labels = {
        "en": {"work": "Selected work", "challenge": "The challenge", "approach": "The approach", "evidence": "What exists today", "repo": "View on GitHub", "live": "Open live site", "more": "More public projects"},
        "zh": {"work": "精选作品", "challenge": "问题与目标", "approach": "实现方式", "evidence": "当前成果", "repo": "在 GitHub 查看", "live": "打开项目网站", "more": "更多公开项目"},
    }[locale]
    facts = "".join(f'<li>{esc(fact)}</li>' for fact in copy["facts"])
    live = f'<a class="btn btn-ghost" href="{case["live"]}">{labels["live"]} ↗</a>' if case["live"] else ""
    more = "".join(
        f'<a href="{BASE}/{locale}/work/{other["slug"]}/"><span>{esc(other["name"])}</span><small>{esc(other[locale]["summary"])}</small></a>'
        for other in CASES if other["slug"] != case["slug"]
    )
    body = (
        render_nav(locale, t, f'/work/{case["slug"]}/')
        + f'''<main id="main-content" class="case-page">
<article>
  <header class="case-hero case-hero--{esc_attr(case["tone"])}">
    <div class="container">
      <a class="case-back" href="{BASE}/{locale}/#work">← {labels["work"]}</a>
      <div class="case-hero__mark" aria-hidden="true">{esc(case["mark"])}</div>
      <p class="case-kicker">{esc(copy["status"])}</p>
      <h1>{esc(case["name"])}</h1>
      <p class="case-summary">{esc(copy["summary"])}</p>
      <p class="case-stack">{esc(case["stack"])}</p>
      <div class="case-actions"><a class="btn btn-primary" href="{case["repo"]}">{labels["repo"]} ↗</a>{live}</div>
    </div>
  </header>
  <div class="case-body container">
    <section><p class="case-section__label">01</p><h2>{labels["challenge"]}</h2><p>{esc(copy["challenge"])}</p></section>
    <section><p class="case-section__label">02</p><h2>{labels["approach"]}</h2><p>{esc(copy["approach"])}</p></section>
    <section class="case-evidence"><p class="case-section__label">03</p><h2>{labels["evidence"]}</h2><ul>{facts}</ul></section>
    <aside class="case-more"><h2>{labels["more"]}</h2><div>{more}</div></aside>
  </div>
</article>
</main>'''
        + render_footer(locale, t)
    )
    schema = {
        "@context": "https://schema.org", "@type": "SoftwareApplication",
        "name": case["name"], "description": copy["summary"],
        "url": f'{SITE_URL}/{locale}/work/{case["slug"]}/',
        "codeRepository": case["repo"], "applicationCategory": "DeveloperApplication",
        "author": {"@type": "Person", "name": "Berry Wahlberg", "url": SITE_URL},
    }
    return page_shell(locale, t, case["name"], copy["summary"], body,
                      f'/{locale}/work/{case["slug"]}/', schema=schema)


# ============================================================
# 博客：frontmatter + 最小 Markdown 渲染
# ============================================================
def parse_md(text: str) -> dict:
    """解析 frontmatter (---\nkey: value\n---) + 正文，返回 {meta, body_html}"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    meta = {}
    body = text
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")
        body = m.group(2)
    return {"meta": meta, "body": md_to_html(body)}


def md_to_html(md: str) -> str:
    """最小 Markdown：h2、p、ul/li、strong、em、code、pre、链接、blockquote"""
    lines = md.splitlines()
    out = []
    i = 0
    in_list = False
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            out.append("<pre><code>" + esc("\n".join(code)) + "</code></pre>")
        elif line.startswith("## "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(line[2:])}</li>")
        elif line.startswith("> "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<blockquote>{inline(line[2:])}</blockquote>")
        elif line.strip() == "":
            if in_list:
                out.append("</ul>")
                in_list = False
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p>{inline(line)}</p>")
        i += 1
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def inline(s: str) -> str:
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\[(.+?)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    return s


def load_posts() -> list:
    posts = []
    if POSTS_SRC.exists():
        for f in POSTS_SRC.glob("*.md"):
            parsed = parse_md(f.read_text(encoding="utf-8"))
            meta = parsed["meta"]
            lang = meta.get("lang", "en")
            title = meta.get("title", f.stem)
            date_str = meta.get("date", "")
            try:
                d = date.fromisoformat(date_str)
            except ValueError:
                d = date.today()
            posts.append({
                "slug": f.stem,
                "lang": lang,
                "title": title,
                "date": d,
                "description": meta.get("description", ""),
                "body": parsed["body"],
            })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def render_blog_index(locale: str) -> str:
    t = T[locale]
    posts = [p for p in load_posts() if p["lang"] == locale]
    items = ""
    for p in posts:
        fmt = format_post_date(locale, p["date"])
        items += (
            f'<article class="blog-list__item"><h2><a href="{BASE}/{locale}/blog/{p["slug"]}/">{esc(p["title"])}</a></h2>'
            f'<time datetime="{p["date"].isoformat()}">{esc(fmt)}</time><p>{esc(p["description"])}</p>'
            f'<a class="blog-list__read" href="{BASE}/{locale}/blog/{p["slug"]}/">{"阅读文章" if locale == "zh" else "Read note"} →</a></article>'
        )
    if not items:
        items = f'<p style="color:var(--ink-muted-48)">{esc(t["blog"]["empty"])}</p>'
    body = (
        render_nav(locale, t, "/blog/")
        + '<main id="main-content"><section class="section page-intro"><div class="container"><div class="section-head">'
        + f'<h2 class="section-title">{esc(t["blog"]["title"])}</h2>'
        + f'<p class="section-sub">{esc(t["blog"]["sub"])}</p></div>'
        + f'<div class="blog-list">{items}</div></div></section></main>'
        + render_footer(locale, t)
    )
    schema = {"@context": "https://schema.org", "@type": "Blog", "name": t["blog"]["title"],
              "description": t["blog"]["sub"], "url": f"{SITE_URL}/{locale}/blog/"}
    return page_shell(locale, t, t["blog"]["title"], t["blog"]["sub"], body, f"/{locale}/blog/", schema=schema)


def render_blog_post(locale: str, post: dict) -> str:
    t = T[locale]
    fmt = format_post_date(locale, post["date"])
    body = (
        render_nav(locale, t, "/blog/")
        + '<main id="main-content"><section class="section page-intro"><div class="container">'
        + f'<div style="margin-bottom:16px"><a href="{BASE}/{locale}/blog/" style="font-size:14px">← {esc(t["blog"]["back"])}</a></div>'
        + '<article class="blog-post">'
        + f'<h1>{esc(post["title"])}</h1>'
        + f'<time datetime="{post["date"].isoformat()}">{esc(fmt)}</time>'
        + f'<div class="blog-post__body">{post["body"]}</div></article>'
        + "</div></section></main>"
        + render_footer(locale, t)
    )
    schema = {
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": post["title"],
        "description": post.get("description", ""), "datePublished": post["date"].isoformat(),
        "inLanguage": locale, "url": f"{SITE_URL}/{locale}/blog/{post['slug']}/",
        "author": {"@type": "Person", "name": "Berry Wahlberg", "url": SITE_URL},
    }
    return page_shell(locale, t, post["title"], post.get("description", ""), body,
                      f"/{locale}/blog/{post['slug']}/", has_alternates=False,
                      schema=schema, og_type="article")


def minify_css(css: str) -> str:
    """简单 CSS 压缩：去注释 + 折叠空白 + 精简标点周边空格"""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>])\s*", r"\1", css)
    return css.strip()


def minify_js(js: str) -> str:
    """简单 JS 压缩：去行注释（均在行首）+ 折叠空白"""
    lines = [ln for ln in js.splitlines() if not ln.strip().startswith("//")]
    js = "\n".join(lines)
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    js = re.sub(r"\s+", " ", js)
    return js.strip()


def build_sitemap(posts: list) -> str:
    urls = []
    for locale in LANGS:
        urls.extend([f"/{locale}/", f"/{locale}/blog/"])
        urls.extend(f'/{locale}/work/{case["slug"]}/' for case in CASES)
        urls.extend(f'/{locale}/blog/{post["slug"]}/' for post in posts if post["lang"] == locale)
    entries = "".join(f"  <url><loc>{SITE_URL}{path}</loc></url>\n" for path in urls)
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + '</urlset>\n'


def render_not_found() -> str:
    t = T["en"]
    body = (
        render_nav("en", t)
        + '<main id="main-content"><section class="section page-intro"><div class="container not-found">'
        + '<p class="case-kicker">404 / NOT FOUND</p><h1>That page wandered off.</h1>'
        + '<p>Return to the portfolio, or switch to the Chinese version.</p>'
        + f'<div class="case-actions"><a class="btn btn-primary" href="{BASE}/en/">Back home</a>'
        + f'<a class="btn btn-ghost" href="{BASE}/zh/">中文主页</a></div></div></section></main>'
        + render_footer("en", t)
    )
    return page_shell("en", t, "Page not found", "The requested page could not be found.", body,
                      "/404.html", has_alternates=False, robots="noindex,follow")


# ============================================================
# 构建入口
# ============================================================
def main():
    # 沙箱环境禁用文件删除（回收站不可用），采用覆盖写入方式构建
    global CSS_V, JS_V
    DIST.mkdir(parents=True, exist_ok=True)

    # 静态资源（CSS/JS 压缩，图片仅发布 WebP）
    for public_file in (ROOT / "public").iterdir():
        if public_file.is_file():
            shutil.copy(public_file, DIST / public_file.name)
    css = minify_css((SRC / "styles" / "global.css").read_text(encoding="utf-8"))
    js = minify_js(SCRIPT_JS)
    (DIST / "styles.css").write_text(css, encoding="utf-8")
    (DIST / "script.js").write_text(js, encoding="utf-8")
    CSS_V = hashlib.md5(css.encode("utf-8")).hexdigest()[:8]
    JS_V = hashlib.md5(js.encode("utf-8")).hexdigest()[:8]
    assets = DIST / "assets"
    assets.mkdir(exist_ok=True)
    for f in ASSETS_SRC.iterdir():
        if f.suffix == ".webp":
            shutil.copy(f, assets / f.name)

    # 根路径：语言检测重定向
    (DIST / "index.html").write_text(INDEX_REDIRECT, encoding="utf-8")

    # 旧 /m/ 路径保留兼容重定向；生产站统一使用同一套响应式模板。
    for obsolete in (DIST / "mobile.css", DIST / "mobile.js"):
        if obsolete.exists():
            obsolete.unlink()
    mdir = DIST / "m"
    mdir.mkdir(exist_ok=True)
    (mdir / "index.html").write_text(INDEX_REDIRECT, encoding="utf-8")

    # 双语言主页
    for locale in LANGS:
        d = DIST / locale
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(render_home(locale), encoding="utf-8")

        for case in CASES:
            case_dir = d / "work" / case["slug"]
            case_dir.mkdir(parents=True, exist_ok=True)
            (case_dir / "index.html").write_text(render_case_page(locale, case), encoding="utf-8")

    # 博客
    posts = load_posts()
    for locale in LANGS:
        blog_dir = DIST / locale / "blog"
        blog_dir.mkdir(parents=True, exist_ok=True)
        (blog_dir / "index.html").write_text(render_blog_index(locale), encoding="utf-8")
        for post in [p for p in posts if p["lang"] == locale]:
            pdir = blog_dir / post["slug"]
            pdir.mkdir(exist_ok=True)
            (pdir / "index.html").write_text(render_blog_post(locale, post), encoding="utf-8")

    (DIST / "sitemap.xml").write_text(build_sitemap(posts), encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    (DIST / "404.html").write_text(render_not_found(), encoding="utf-8")

    # 统计
    html_count = sum(1 for _ in DIST.rglob("*.html"))
    print(f"✓ 构建完成：{html_count} 个 HTML 页面 → {DIST}")


if __name__ == "__main__":
    main()
