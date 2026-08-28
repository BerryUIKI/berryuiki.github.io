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
    "nav": {"about": "About", "skills": "Skills", "experience": "Experience", "work": "Work", "contact": "Contact"},
    "hero": {"eyebrow": "PRODUCT DESIGNER & DEVELOPER", "badge": "THE BERRY · Aries",
             "title": "Hi, I'm Berry Wahlberg.",
             "subtitle": "I design and build thoughtful digital products — simple, fast, and human by default.",
             "cta1": "View My Work", "cta2": "Contact Me", "scroll": "Scroll — photo shrinks"},
    "about": {"title": "About Me", "subtitle": "Designer, developer, and lifelong learner based in Shanghai.",
              "p1": "For the past eight years, I've helped startups and product teams turn ambiguous ideas into shipped products. I work across the whole stack — from wireframes and design systems to React and Node.js — because great products are built at the intersection of craft and code.",
              "p2": "My goal is simple: make technology feel human. I care deeply about accessibility, internationalization, and the small details that turn an interface into an experience.",
              "stats": [("8+", "Years Experience"), ("40+", "Projects Shipped"), ("12", "Countries Served")],
              "chips": ["Aries", "ENFP · Happy Pup", "Tender Soul"]},
    "skills": {"title": "Skills & Tools", "subtitle": "The tools and crafts I reach for every day.",
               "cols": [("Design", ["Product Design", "Design Systems", "Prototyping", "Usability Testing"]),
                        ("Frontend", ["React", "TypeScript", "Tailwind CSS", "Web Animations"]),
                        ("Backend", ["Node.js", "Python", "GraphQL", "PostgreSQL"]),
                        ("Platform", ["CI/CD", "Internationalization", "Performance", "Accessibility"])]},
    "experience": {"title": "Experience", "subtitle": "Where I've been and what I've shipped.",
                   "items": [("2021 — Present", "Senior Product Designer", "Acme Studio · Shanghai", "Leading the design system and core product flows for a B2B analytics platform used by 2,000+ teams."),
                             ("2018 — 2021", "Product Designer", "Nova Labs · Remote", "Designed end-to-end experiences for a consumer fintech app, growing activation by 34%."),
                             ("2016 — 2018", "Frontend Developer", "Pixel Works · Guangzhou", "Built responsive marketing sites and internal tools with React, cutting page load times by 60%.")]},
    "work": {"title": "Selected Work", "subtitle": "A few projects I'm proud of.",
             "items": [("Aurora Dashboard", "Real-time analytics for SaaS teams.", "React · D3 · Design System", "work-aurora.webp"),
                       ("Wander", "A travel planner that feels like a journal.", "Mobile · iOS · Figma", "work-wander.webp"),
                       ("Echo Notes", "AI note-taking that summarizes as you type.", "AI · TypeScript · GraphQL", "work-echo.webp")]},
    "testi": {"title": "What People Say", "subtitle": "Colleagues and clients on working together.",
              "items": [("Berry has an eye for detail that most designers only dream of. Every handoff is pixel-perfect and every decision is backed by reasoning.", "Sarah Kim — VP Product, Acme Studio"),
                        ("Working with Berry felt like adding a co-founder, not a contractor. She pushed our product to a level we didn't think we could reach.", "Daniel Chen — Founder, Nova Labs"),
                        ("Fast, thoughtful, and endlessly curious. Berry rebuilt our design system and the whole team felt the difference within a week.", "Mia Zhou — Engineering Lead, Pixel Works")]},
    "contact": {"title": "Let's work together.", "subtitle": "Have a project in mind? I'd love to hear about it.",
                "email": "berrywahlberg@gmail.com"},
    "footer": {"tagline": "Designer & developer crafting simple, human software.",
               "navTitle": "Navigation", "socialTitle": "Social", "contactTitle": "Contact",
               "social": ["GitHub", "LinkedIn", "X / Twitter"],
               "contact": ["berrywahlberg@gmail.com", "Shanghai, CN"],
               "copyright": "Copyright 2026 Berry Wahlberg. All rights reserved."},
    "blog": {"title": "Blog", "sub": "Notes on design, code & life.", "back": "Back to blog", "empty": "No posts yet."},
  },
  "zh": {
    "meta": {"title": "花雨琦 — 产品设计师 & 开发者",
             "description": "花雨琦（Berry Wahlberg）的个人网站：设计与开发简洁、快速、以人为本的数字产品。"},
    "nav": {"about": "关于", "skills": "技能", "experience": "经历", "work": "作品", "contact": "联系"},
    "hero": {"eyebrow": "产品设计师 & 开发者", "badge": "THE BERRY · 白羊座",
             "title": "你好，我是花雨琦。",
             "subtitle": "我设计并打造以人为本的数字产品——简洁、快速、自然。",
             "cta1": "查看我的作品", "cta2": "联系我", "scroll": "下滑 — 照片缩小"},
    "about": {"title": "关于我", "subtitle": "现居上海的设计师与开发者，终身学习者。",
              "p1": "八年来，我帮助初创公司与产品团队把模糊的想法变成落地的产品。我的工作横跨全栈——从线框稿与设计系统，到 React 与 Node.js——因为伟大的产品诞生于设计与代码的交汇处。",
              "p2": "我的目标很简单：让技术有人情味。我关注无障碍、国际化，以及那些把界面变成体验的微小细节。",
              "stats": [("8+", "年经验"), ("40+", "交付项目"), ("12", "服务国家/地区")],
              "chips": ["白羊座", "ENFP · 快乐小狗", "温柔受"]},
    "skills": {"title": "技能与工具", "subtitle": "我每天都会用到的工具与手艺。",
               "cols": [("设计", ["产品设计", "设计系统", "原型制作", "可用性测试"]),
                        ("前端", ["React", "TypeScript", "Tailwind CSS", "Web 动效"]),
                        ("后端", ["Node.js", "Python", "GraphQL", "PostgreSQL"]),
                        ("平台", ["CI/CD", "国际化", "性能优化", "无障碍"])]},
    "experience": {"title": "工作经历", "subtitle": "走过的路，交付过的产品。",
                   "items": [("2021 — 至今", "资深产品设计师", "Acme Studio · 上海", "负责 B2B 分析平台的设计系统与核心产品流程，服务 2,000+ 团队。"),
                             ("2018 — 2021", "产品设计师", "Nova Labs · 远程", "为消费级金融应用设计端到端体验，激活率提升 34%。"),
                             ("2016 — 2018", "前端开发者", "Pixel Works · 广州", "使用 React 构建响应式营销网站与内部工具，页面加载时间降低 60%。")]},
    "work": {"title": "精选作品", "subtitle": "我引以为豪的几个项目。",
             "items": [("Aurora Dashboard", "为 SaaS 团队打造的实时数据分析工具。", "React · D3 · 设计系统", "work-aurora.webp"),
                       ("Wander", "像日记一样自然的旅行规划应用。", "移动端 · iOS · Figma", "work-wander.webp"),
                       ("Echo Notes", "边输入边总结的 AI 笔记工具。", "AI · TypeScript · GraphQL", "work-echo.webp")]},
    "testi": {"title": "他们怎么说", "subtitle": "同事与客户眼中的合作体验。",
              "items": [("花雨琦（Berry）对细节的洞察是大多数设计师梦寐以求的。每次交付都像素级完美，每个决策都有理有据。", "Sarah Kim — Acme Studio 产品副总裁"),
                        ("与花雨琦合作就像多了一位联合创始人，而不是外包。她把我们的产品推到了我们以为到不了的高度。", "Daniel Chen — Nova Labs 创始人"),
                        ("高效、深思熟虑、永远充满好奇。花雨琦重建了我们的设计系统，整个团队在一周内就感受到了差别。", "Mia Zhou — Pixel Works 技术负责人")]},
    "contact": {"title": "一起合作吧。", "subtitle": "有项目想法？很乐意与你聊聊。",
                "email": "berrywahlberg@gmail.com"},
    "footer": {"tagline": "用设计与代码，打造简洁而有温度的产品。",
               "navTitle": "导航", "socialTitle": "社交", "contactTitle": "联系",
               "social": ["GitHub", "LinkedIn", "X / Twitter"],
               "contact": ["berrywahlberg@gmail.com", "中国 · 上海"],
               "copyright": "2026 花雨琦 · 版权所有"},
    "blog": {"title": "博客", "sub": "随笔、设计与代码。", "back": "返回博客", "empty": "暂无文章。"},
  },
}

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
def render_nav(locale: str, t: dict) -> str:
    links = "".join(
        f'<li><a href="{BASE}/{locale}/#{a}">{esc(t["nav"][a])}</a></li>' for a in ANCHORS
    )
    lang_switch_parts = []
    for l in LANGS:
        current = ' aria-current="true"' if l == locale else ""
        label = "EN" if l == "en" else "中文"
        lang_switch_parts.append(f'<a href="{BASE}/{l}/" lang="{l}"{current}>{label}</a>')
    lang_switch = "".join(lang_switch_parts)
    return f"""
<nav class="global-nav">
  <div class="scroll-progress" aria-hidden="true"><span></span></div>
  <a class="global-nav__logo" href="{BASE}/{locale}/">THE BERRY</a>
  <ul class="global-nav__links">{links}</ul>
  <div class="global-nav__actions">
    <div class="lang-switch" role="group" aria-label="Language">{lang_switch}</div>
    <button class="theme-toggle" id="theme-toggle" type="button" aria-label="Toggle theme" aria-pressed="false">
      <svg id="theme-icon-sun" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <circle cx="12" cy="12" r="5"/><path d="M12 1v3M12 20v3M1 12h3M20 12h3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/>
      </svg>
      <svg id="theme-icon-moon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="display:none">
        <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/>
      </svg>
    </button>
  </div>
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


def render_work(t: dict) -> str:
    section_label = "精选作品" if t is T["zh"] else "SELECTED WORK"
    cards = "".join(
        f'<article class="work-card" data-tilt><span class="work-card__index">0{i + 1}</span><div class="work-card__img"><img src="{BASE}/assets/{img}" alt="{esc(name)}" width="672" height="380" loading="lazy" /></div>'
        f'<h3>{esc(name)}</h3><p>{esc(desc)}</p><div class="work-card__tags">{esc(tags)}</div></article>'
        for i, (name, desc, tags, img) in enumerate(t["work"]["items"])
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
<section class="section section--dark section--indexed" id="testimonials" data-index="05" data-label="{section_label}">
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
        f'<a href="https://www.linkedin.com/">LinkedIn</a>'
        f'<a href="mailto:{esc_attr(email)}">Email</a>'
    )
    return f"""
<section class="contact section--indexed" id="contact" data-index="06" data-label="{section_label}">
  <div class="contact__marquee" aria-hidden="true"><span>{marquee}</span></div>
  <div class="container">
    <h2>{esc(t["contact"]["title"])}</h2>
    <p>{esc(t["contact"]["subtitle"])}</p>
    <a class="btn btn-primary" href="mailto:{esc_attr(email)}">{esc(email)}</a>
    <div class="contact__socials">{socials}</div>
  </div>
</section>"""


def render_footer(locale: str, t: dict) -> str:
    footer_anchors = ["about", "skills", "work", "contact"]
    nav_links = "".join(
        f'<a href="{BASE}/{locale}/#{a}">{esc(label)}</a>'
        for a, label in zip(footer_anchors, [t["nav"]["about"], t["nav"]["skills"], t["nav"]["work"], t["nav"]["contact"]])
    )
    social = "".join(
        f'<a href="{url}">{esc(label)}</a>'
        for label, url in zip(t["footer"]["social"], ["https://github.com/BerryUIKI", "https://www.linkedin.com/"])
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
  var spotlights = document.querySelectorAll('[data-spotlight]');
  for (var sp = 0; sp < spotlights.length; sp++) {
    spotlights[sp].addEventListener('pointermove', function (event) {
      var rect = this.getBoundingClientRect();
      this.style.setProperty('--spot-x', (event.clientX - rect.left) + 'px');
      this.style.setProperty('--spot-y', (event.clientY - rect.top) + 'px');
    });
  }
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
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
  // 移动端 → /m/ 独立页面
  if (window.innerWidth < 900) {{
    location.replace('{BASE}/m/');
    return;
  }}
  // 桌面端 → 语言检测重定向（默认英语优先）
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


def page_shell(locale: str, t: dict, title: str, desc: str, body: str, canonical_path: str, has_alternates: bool = True) -> str:
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
    return f"""<!doctype html>
<html lang="{locale}" data-theme="light">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc or meta['description'])}" />
<meta property="og:title" content="{esc(full_title)}" />
<meta property="og:description" content="{esc(desc or meta['description'])}" />
<meta property="og:type" content="website" />
<meta property="og:url" content="{canonical_url}" />
<meta property="og:image" content="{SITE_URL}/og.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(full_title)}" />
<meta name="twitter:description" content="{esc(desc or meta['description'])}" />
<meta name="twitter:image" content="{SITE_URL}/og.png" />
<meta name="theme-color" content="#08080a" />
<link rel="canonical" href="{canonical_url}" />
{alternate_links}
  <link rel="icon" type="image/svg+xml" href="{BASE}/favicon.svg" />
  <link rel="stylesheet" href="{BASE}/styles.css?v={CSS_V}" />
</head>
<body>
{body}
<script>
// 移动端访问 PC 页 → 跳转 /m/ 独立页（博客页与 ?full=1 除外）
if (window.innerWidth < 900 && location.pathname.indexOf('/blog') === -1 && !location.search.includes('full')) {{
  location.replace('{BASE}/m/');
}}
</script>
<script src="{BASE}/script.js?v={JS_V}"></script>
</body>
</html>"""


def render_home(locale: str) -> str:
    t = T[locale]
    body = (
        render_nav(locale, t)
        + render_hero(locale, t)
        + render_about(t)
        + render_skills(t)
        + render_experience(t)
        + render_work(t)
        + render_testimonials(t)
        + render_contact(t)
        + render_footer(locale, t)
    )
    return page_shell(locale, t, "", "", body, f"/{locale}/")


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
        fmt = p["date"].strftime("%B %d, %Y")
        items += (
            f'<article class="blog-list__item"><h2><a href="{BASE}/{locale}/blog/{p["slug"]}/">{esc(p["title"])}</a></h2>'
            f'<time datetime="{p["date"].isoformat()}">{esc(fmt)}</time></article>'
        )
    if not items:
        items = f'<p style="color:var(--ink-muted-48)">{esc(t["blog"]["empty"])}</p>'
    body = (
        render_nav(locale, t)
        + '<section class="section"><div class="container"><div class="section-head">'
        + f'<h2 class="section-title">{esc(t["blog"]["title"])}</h2>'
        + f'<p class="section-sub">{esc(t["blog"]["sub"])}</p></div>'
        + f'<div class="blog-list">{items}</div></div></section>'
        + render_footer(locale, t)
    )
    return page_shell(locale, t, t["blog"]["title"], t["blog"]["sub"], body, f"/{locale}/blog/")


def render_blog_post(locale: str, post: dict) -> str:
    t = T[locale]
    fmt = post["date"].strftime("%B %d, %Y")
    body = (
        render_nav(locale, t)
        + '<section class="section"><div class="container">'
        + f'<div style="margin-bottom:16px"><a href="{BASE}/{locale}/blog/" style="font-size:14px">← {esc(t["blog"]["back"])}</a></div>'
        + '<article class="blog-post">'
        + f'<h1>{esc(post["title"])}</h1>'
        + f'<time datetime="{post["date"].isoformat()}">{esc(fmt)}</time>'
        + f'<div class="blog-post__body">{post["body"]}</div></article>'
        + "</div></section>"
        + render_footer(locale, t)
    )
    return page_shell(locale, t, post["title"], post.get("description", ""), body, f"/{locale}/blog/{post['slug']}/", has_alternates=False)


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


SCRIPT_MOBILE_JS = """// THE BERRY — 移动端独立页脚本（/m/）
(function () {
  try {
    var saved = localStorage.getItem('berry-theme');
    var theme = saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
  } catch (e) { document.documentElement.setAttribute('data-theme', 'light'); }
})();

document.addEventListener('DOMContentLoaded', function () {
  var SUPPORTED = ['en', 'zh'];
  var DEFAULT = 'en';
  var lang = DEFAULT;
  try {
    var savedLang = localStorage.getItem('berry-lang');
    if (savedLang && SUPPORTED.indexOf(savedLang) !== -1) {
      lang = savedLang;
    } else {
      var list = (navigator.languages && navigator.languages.length) ? navigator.languages : [navigator.language || DEFAULT];
      var hasZh = false;
      for (var i = 0; i < list.length; i++) {
        var code = String(list[i]).toLowerCase().split('-')[0];
        if (code === 'en') { lang = 'en'; break; }
        if (code === 'zh') { hasZh = true; }
      }
      if (lang === DEFAULT && hasZh) { lang = 'zh'; }
    }
  } catch (e) { lang = DEFAULT; }

  function applyLang(l) {
    document.documentElement.setAttribute('lang', l);
    document.title = l === 'zh' ? '花雨琦 — 产品设计师 & 开发者' : 'Berry Wahlberg — Product Designer & Developer';
    var metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) metaDescription.setAttribute('content', l === 'zh'
      ? '花雨琦（Berry Wahlberg）的个人网站：设计与开发简洁、快速、以人为本的数字产品。'
      : 'Portfolio of Berry Wahlberg (花雨琦): product designer and developer crafting simple, human software.');
    var els = document.querySelectorAll('[data-en]');
    for (var i = 0; i < els.length; i++) {
      var val = l === 'zh' ? els[i].getAttribute('data-zh') : els[i].getAttribute('data-en');
      if (val !== null) els[i].textContent = val;
    }
    var links = document.querySelectorAll('[data-href-en]');
    for (var j = 0; j < links.length; j++) {
      var href = l === 'zh' ? links[j].getAttribute('data-href-zh') : links[j].getAttribute('data-href-en');
      if (href !== null) links[j].setAttribute('href', href);
    }
    var indexed = document.querySelectorAll('[data-label-en]');
    for (var q = 0; q < indexed.length; q++) {
      var label = l === 'zh' ? indexed[q].getAttribute('data-label-zh') : indexed[q].getAttribute('data-label-en');
      if (label !== null) indexed[q].setAttribute('data-label', label);
    }
    var btns = document.querySelectorAll('.m-lang button');
    for (var k = 0; k < btns.length; k++) {
      var active = btns[k].getAttribute('data-lang') === l;
      btns[k].setAttribute('data-active', active ? 'true' : 'false');
      btns[k].setAttribute('aria-pressed', active ? 'true' : 'false');
    }
  }
  applyLang(lang);

  var langBtns = document.querySelectorAll('.m-lang button');
  for (var b = 0; b < langBtns.length; b++) {
    langBtns[b].addEventListener('click', function () {
      lang = this.getAttribute('data-lang');
      applyLang(lang);
      try { localStorage.setItem('berry-lang', lang); } catch (e) {}
    });
  }

  var themeBtn = document.getElementById('m-theme-toggle');
  var root = document.documentElement;
  function syncThemeIcon() {
    var dark = root.getAttribute('data-theme') === 'dark';
    var sun = document.getElementById('m-icon-sun');
    var moon = document.getElementById('m-icon-moon');
    if (sun) sun.style.display = dark ? 'none' : '';
    if (moon) moon.style.display = dark ? '' : 'none';
    if (themeBtn) themeBtn.setAttribute('aria-pressed', dark ? 'true' : 'false');
  }
  syncThemeIcon();
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      var applyTheme = function () {
        root.setAttribute('data-theme', next);
        try { localStorage.setItem('berry-theme', next); } catch (e) {}
        syncThemeIcon();
      };
      if (document.startViewTransition && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        var rect = themeBtn.getBoundingClientRect();
        root.style.setProperty('--theme-x', (rect.left + rect.width / 2) + 'px');
        root.style.setProperty('--theme-y', (rect.top + rect.height / 2) + 'px');
        document.startViewTransition(applyTheme);
      } else {
        applyTheme();
      }
    });
  }

  // Hero 滚动缩小（移动版）
  var hero = document.querySelector('.m-hero');
  var img = hero ? hero.querySelector('.m-hero__img') : null;
  var heroContent = hero ? hero.querySelector('.m-hero__content') : null;
  var heroCtas = hero ? hero.querySelector('.m-hero__ctas') : null;
  var nav = document.querySelector('.m-nav');
  var progress = document.querySelector('.m-scroll-progress span');
  function updateHero() {
    if (!hero || !img) return;
    var y = window.scrollY;
    var max = Math.max(hero.offsetHeight, 1);
    var p = Math.min(y / max, 1);
    hero.style.setProperty('--hero-progress', String(p));
    img.style.transform = 'scale(' + (1 - 0.3 * p) + ') translateY(' + (60 * p) + 'px)';
    img.style.opacity = String(1 - 0.5 * p);
    var br = Math.round(24 * p);
    img.style.borderRadius = '0 0 ' + br + 'px ' + br + 'px';
    if (heroContent) heroContent.style.opacity = String(Math.max(0, 1 - 2 * p));
    if (heroCtas) heroCtas.style.opacity = String(Math.max(0, 1 - 1.65 * p));
    if (nav) nav.classList.toggle('is-scrolled', y > 18);
    if (progress) {
      var total = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1);
      progress.style.transform = 'scaleX(' + Math.min(y / total, 1) + ')';
    }
  }
  var ticking = false;
  function onScroll() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(function () { updateHero(); ticking = false; });
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  updateHero();

  var sections = document.querySelectorAll('main > section');
  if ('IntersectionObserver' in window) {
    document.body.classList.add('m-reveal-ready');
    var observer = new IntersectionObserver(function (entries) {
      for (var e = 0; e < entries.length; e++) {
        if (entries[e].isIntersecting) entries[e].target.classList.add('is-visible');
      }
    }, { threshold: 0.12 });
    for (var s = 0; s < sections.length; s++) observer.observe(sections[s]);
  }
});
"""


def render_mobile(css_v: str, js_v: str) -> str:
    """移动端独立页 /m/（双语内嵌，data-en/data-zh 属性，JS 即时切换）"""
    en, zh = T["en"], T["zh"]

    def d(txt_en: str, txt_zh: str) -> str:
        return f'data-en="{esc(txt_en)}" data-zh="{esc(txt_zh)}"'

    def dref(href_en: str, href_zh: str) -> str:
        return f'data-href-en="{esc(href_en)}" data-href-zh="{esc(href_zh)}"'

    b = BASE
    m = "/m"

    # --- Hero ---
    hero_html = f"""
<section class="m-hero" id="top">
  <img class="m-hero__img" src="{b}/assets/hero-mobile.webp" alt="" width="941" height="1672" />
  <div class="m-hero__content">
    <p class="m-hero__eyebrow" {d(en['hero']['eyebrow'], zh['hero']['eyebrow'])}>{esc(en['hero']['eyebrow'])}</p>
    <p class="m-hero__badge" {d(en['hero']['badge'], zh['hero']['badge'])}>{esc(en['hero']['badge'])}</p>
    <h1 class="m-hero__title" {d(en['hero']['title'], zh['hero']['title'])}>{esc(en['hero']['title'])}</h1>
    <p class="m-hero__subtitle" {d(en['hero']['subtitle'], zh['hero']['subtitle'])}>{esc(en['hero']['subtitle'])}</p>
  </div>
  <div class="m-hero__ctas">
    <a class="m-btn m-btn--primary" href="{m}/#work" {d(en['hero']['cta1'], zh['hero']['cta1'])}>{esc(en['hero']['cta1'])}</a>
    <a class="m-btn m-btn--ghost" href="{m}/#contact" {d(en['hero']['cta2'], zh['hero']['cta2'])}>{esc(en['hero']['cta2'])}</a>
  </div>
  <a class="m-hero__scroll" href="{m}/#about" aria-label="Scroll to content">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>
  </a>
</section>"""

    # --- About ---
    about_stats = ""
    for i, (v, _lbl) in enumerate(en['about']['stats']):
        about_stats += (
            f'<div><div class="m-stats__num">{esc(v)}</div>'
            f'<div class="m-stats__label" {d(en["about"]["stats"][i][1], zh["about"]["stats"][i][1])}>{esc(en["about"]["stats"][i][1])}</div></div>'
        )
    chips = ""
    for i, c in enumerate(en['about']['chips']):
        chips += f'<span class="m-chip" {d(c, zh["about"]["chips"][i])}>{esc(c)}</span>'
    about_html = f"""
<section class="section section--parchment m-section--indexed" id="about" data-index="01" data-label="PROFILE" data-label-en="PROFILE" data-label-zh="人物">
  <h2 class="section-title" {d(en['about']['title'], zh['about']['title'])}>{esc(en['about']['title'])}</h2>
  <p class="section-sub" {d(en['about']['subtitle'], zh['about']['subtitle'])}>{esc(en['about']['subtitle'])}</p>
  <div class="m-about-text" style="margin-top:18px">
    <p {d(en['about']['p1'], zh['about']['p1'])}>{esc(en['about']['p1'])}</p>
    <p {d(en['about']['p2'], zh['about']['p2'])}>{esc(en['about']['p2'])}</p>
  </div>
  <div class="m-stats">{about_stats}</div>
  <div class="m-chips">{chips}</div>
  <div class="m-portrait"><img src="{b}/assets/portrait.webp" alt="{esc(en['about']['title'])}" width="1080" height="1080" loading="lazy" /></div>
</section>"""

    # --- Skills ---
    skills_cards = ""
    for i, (name, items) in enumerate(en['skills']['cols']):
        zh_name, zh_items = zh['skills']['cols'][i]
        lis = "".join(
            f"<li>{esc(item)}</li>" if i2 < len(items) else ""
            for i2, item in enumerate(items)
        )
        zh_lis = "".join(
            f'<li class="zh-only" data-en="{esc(items[i2]) if i2 < len(items) else ""}" data-zh="{esc(zh_items[i2]) if i2 < len(zh_items) else ""}">{esc(zh_items[i2]) if i2 < len(zh_items) else ""}</li>'
            for i2 in range(max(len(items), len(zh_items)))
        )
        lis = "".join(
            f'<li data-en="{esc(items[i2]) if i2 < len(items) else ""}" data-zh="{esc(zh_items[i2]) if i2 < len(zh_items) else ""}">{esc(items[i2]) if i2 < len(items) else ""}</li>'
            for i2 in range(max(len(items), len(zh_items)))
        )
        skills_cards += (
            f'<div class="m-skills-card"><span class="m-card-index">0{i + 1}</span><h3 data-en="{esc(name)}" data-zh="{esc(zh_name)}">{esc(name)}</h3><ul>{lis}</ul></div>'
        )
    skills_html = f"""
<section class="section section--dark m-section--indexed" id="skills" data-index="02" data-label="CAPABILITIES" data-label-en="CAPABILITIES" data-label-zh="能力">
  <h2 class="section-title" {d(en['skills']['title'], zh['skills']['title'])}>{esc(en['skills']['title'])}</h2>
  <p class="section-sub" {d(en['skills']['subtitle'], zh['skills']['subtitle'])}>{esc(en['skills']['subtitle'])}</p>
  <div class="m-skills" style="margin-top:20px">{skills_cards}</div>
</section>"""

    # --- Experience ---
    exp_items = ""
    for i, (period, role, company, desc) in enumerate(en['experience']['items']):
        z = zh['experience']['items'][i]
        exp_items += f"""
<div class="m-timeline__item"><span class="m-card-index">0{i + 1}</span>
  <div class="m-timeline__period">{esc(period)}</div>
  <div class="m-timeline__role" {d(role, z[1])}>{esc(role)}</div>
  <div class="m-timeline__company" {d(company, z[2])}>{esc(company)}</div>
  <p class="m-timeline__desc" {d(desc, z[3])}>{esc(desc)}</p>
</div>"""
    exp_html = f"""
<section class="section m-section--indexed" id="experience" data-index="03" data-label="JOURNEY" data-label-en="JOURNEY" data-label-zh="旅程">
  <h2 class="section-title" {d(en['experience']['title'], zh['experience']['title'])}>{esc(en['experience']['title'])}</h2>
  <p class="section-sub" {d(en['experience']['subtitle'], zh['experience']['subtitle'])}>{esc(en['experience']['subtitle'])}</p>
  <div class="m-timeline" style="margin-top:20px">{exp_items}</div>
</section>"""

    # --- Work ---
    work_cards = ""
    for i, (name, desc, tags, img) in enumerate(en['work']['items']):
        z = zh['work']['items'][i]
        work_cards += f"""
<div class="m-work-card"><span class="m-card-index m-work-card__index">0{i + 1}</span>
  <img src="{b}/assets/{img}" alt="{esc(name)}" width="672" height="380" loading="lazy" />
  <h3>{esc(name)}</h3>
  <p {d(desc, z[1])}>{esc(desc)}</p>
  <div class="tags" {d(tags, z[2])}>{esc(tags)}</div>
</div>"""
    work_html = f"""
<section class="section section--parchment m-section--indexed" id="work" data-index="04" data-label="SELECTED WORK" data-label-en="SELECTED WORK" data-label-zh="精选作品">
  <h2 class="section-title" {d(en['work']['title'], zh['work']['title'])}>{esc(en['work']['title'])}</h2>
  <p class="section-sub" {d(en['work']['subtitle'], zh['work']['subtitle'])}>{esc(en['work']['subtitle'])}</p>
  <div class="m-work" style="margin-top:20px">{work_cards}</div>
  <a class="m-blog-link" {d("Blog / 博客", "博客 / Blog")} {dref(f"{b}/en/blog/", f"{b}/zh/blog/")} href="{b}/en/blog/">Blog</a>
</section>"""

    # --- Testimonials ---
    testi_cards = ""
    for i, (quote, author) in enumerate(en['testi']['items']):
        z = zh['testi']['items'][i]
        testi_cards += f"""
<figure class="m-testi-card"><span class="m-testi-card__quote" aria-hidden="true">“</span>
  <blockquote {d(quote, z[0])}>{esc(quote)}</blockquote>
  <figcaption {d(author, z[1])}>{esc(author)}</figcaption>
</figure>"""
    testi_html = f"""
<section class="section section--dark m-section--indexed" id="testimonials" data-index="05" data-label="VOICES" data-label-en="VOICES" data-label-zh="回声">
  <h2 class="section-title" {d(en['testi']['title'], zh['testi']['title'])}>{esc(en['testi']['title'])}</h2>
  <p class="section-sub" {d(en['testi']['subtitle'], zh['testi']['subtitle'])}>{esc(en['testi']['subtitle'])}</p>
  <div class="m-testi" style="margin-top:20px">{testi_cards}</div>
</section>"""

    # --- Contact ---
    email = en['contact']['email']
    contact_html = f"""
<section class="m-contact m-section--indexed" id="contact" data-index="06" data-label="CONTACT" data-label-en="CONTACT" data-label-zh="联系">
  <div class="m-contact__word" aria-hidden="true" {d("CREATE", "创造")}>CREATE</div>
  <h2 {d(en['contact']['title'], zh['contact']['title'])}>{esc(en['contact']['title'])}</h2>
  <p {d(en['contact']['subtitle'], zh['contact']['subtitle'])}>{esc(en['contact']['subtitle'])}</p>
  <a class="m-btn m-btn--primary" href="mailto:{esc(email)}">{esc(email)}</a>
  <div class="m-socials">
    <a href="https://github.com/BerryUIKI">GitHub @BerryUIKI</a>
    <a href="https://www.linkedin.com/">LinkedIn</a>
    <a href="mailto:{esc(email)}">Email</a>
  </div>
</section>"""

    # --- Footer ---
    footer_links = ""
    nav_keys = ["about", "skills", "work", "contact"]
    for i, key in enumerate(nav_keys):
        label = en["nav"][key]
        zh_label = zh["nav"][key]
        footer_links += f'<a href="{m}/#{key}" {d(label, zh_label)}>{esc(label)}</a>'
    footer_html = f"""
<footer class="m-footer">
  <div class="m-footer__brand">
    <div class="logo">THE BERRY</div>
    <p {d(en['footer']['tagline'], zh['footer']['tagline'])}>{esc(en['footer']['tagline'])}</p>
  </div>
  <div class="m-footer__cols">
    <div class="m-footer__col">
      <h4 {d(en['footer']['navTitle'], zh['footer']['navTitle'])}>{esc(en['footer']['navTitle'])}</h4>{footer_links}
    </div>
    <div class="m-footer__col">
      <h4 {d(en['footer']['socialTitle'], zh['footer']['socialTitle'])}>{esc(en['footer']['socialTitle'])}</h4>
      <a href="https://github.com/BerryUIKI">GitHub</a>
      <a href="https://www.linkedin.com/">LinkedIn</a>
    </div>
    <div class="m-footer__col">
      <h4 {d(en['footer']['contactTitle'], zh['footer']['contactTitle'])}>{esc(en['footer']['contactTitle'])}</h4>
      <a href="mailto:{esc(email)}">{esc(email)}</a>
      <span {d(en['footer']['contact'][1], zh['footer']['contact'][1])}>{esc(en['footer']['contact'][1])}</span>
    </div>
  </div>
  <a class="m-footer__desktop-link" {d("View desktop site", "访问完整版")} {dref(f"{b}/en/?full=1", f"{b}/zh/?full=1")} href="{b}/en/?full=1">View desktop site</a>
  <div class="m-footer__bottom">
    <span {d(en['footer']['copyright'], zh['footer']['copyright'])}>{esc(en['footer']['copyright'])}</span>
    <span>EN | 中文</span>
  </div>
</footer>"""

    nav = f"""
<nav class="m-nav">
  <div class="m-scroll-progress" aria-hidden="true"><span></span></div>
  <a class="m-nav__logo" href="{m}/">THE BERRY</a>
  <div class="m-nav__actions">
    <div class="m-lang" role="group" aria-label="Language">
      <button type="button" data-lang="en" data-active="true">EN</button>
      <button type="button" data-lang="zh" data-active="false">中文</button>
    </div>
    <button class="m-theme" id="m-theme-toggle" type="button" aria-label="Toggle theme">
      <svg id="m-icon-sun" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v3M12 20v3M1 12h3M20 12h3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/></svg>
      <svg id="m-icon-moon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="display:none"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/></svg>
    </button>
  </div>
</nav>"""

    return f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>THE BERRY — Berry Wahlberg / 花雨琦</title>
<meta name="description" content="Berry Wahlberg (花雨琦) — Product designer & developer." />
<meta property="og:title" content="THE BERRY — Berry Wahlberg / 花雨琦" />
<meta property="og:description" content="Berry Wahlberg (花雨琦) — Product designer & developer." />
<meta property="og:type" content="website" />
<meta property="og:url" content="{SITE_URL}/m/" />
<meta property="og:image" content="{SITE_URL}/og.png" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="{SITE_URL}/og.png" />
<meta name="theme-color" content="#08080a" />
<link rel="canonical" href="{SITE_URL}/m/" />
<link rel="icon" type="image/svg+xml" href="{b}/favicon.svg" />
<link rel="stylesheet" href="{b}/mobile.css?v={css_v}" />
</head>
<body>
{nav}
<main>
{hero_html}
{about_html}
{skills_html}
{exp_html}
{work_html}
{testi_html}
{contact_html}
</main>
{footer_html}
<script src="{b}/mobile.js?v={js_v}"></script>
</body>
</html>"""


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

    # 移动端独立页 /m/
    mobile_css = minify_css((SRC / "styles" / "mobile.css").read_text(encoding="utf-8"))
    mobile_js = minify_js(SCRIPT_MOBILE_JS)
    (DIST / "mobile.css").write_text(mobile_css, encoding="utf-8")
    (DIST / "mobile.js").write_text(mobile_js, encoding="utf-8")
    m_css_v = hashlib.md5(mobile_css.encode("utf-8")).hexdigest()[:8]
    m_js_v = hashlib.md5(mobile_js.encode("utf-8")).hexdigest()[:8]
    mdir = DIST / "m"
    mdir.mkdir(exist_ok=True)
    (mdir / "index.html").write_text(render_mobile(m_css_v, m_js_v), encoding="utf-8")

    # 双语言主页
    for locale in LANGS:
        d = DIST / locale
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(render_home(locale), encoding="utf-8")

    # 博客
    for locale in LANGS:
        blog_dir = DIST / locale / "blog"
        blog_dir.mkdir(parents=True, exist_ok=True)
        (blog_dir / "index.html").write_text(render_blog_index(locale), encoding="utf-8")
        for post in [p for p in load_posts() if p["lang"] == locale]:
            pdir = blog_dir / post["slug"]
            pdir.mkdir(exist_ok=True)
            (pdir / "index.html").write_text(render_blog_post(locale, post), encoding="utf-8")

    # 统计
    html_count = sum(1 for _ in DIST.rglob("*.html"))
    print(f"✓ 构建完成：{html_count} 个 HTML 页面 → {DIST}")


if __name__ == "__main__":
    main()
