# -*- coding: utf-8 -*-
"""
THE BERRY — 微型静态站点生成器（纯 Python 标准库，无依赖）
- i18n: en/zh 双版本静态页 + 根路径客户端语言检测重定向（默认 en）
- 暗色模式: CSS 变量 + data-theme + 手动切换（localStorage）
- 博客: Markdown 预渲染为 HTML（content/posts/*.md）
- 复用设计稿 Apple 风格样式（src/styles/global.css）

用法: python build_site.py  （输出到 dist/）
"""
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

# 用户主页仓库模式：https://berryuiki.github.io/（根路径，无 base 前缀）
BASE = ""

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
             "items": [("Aurora Dashboard", "Real-time analytics for SaaS teams.", "React · D3 · Design System", "work-aurora.png"),
                       ("Wander", "A travel planner that feels like a journal.", "Mobile · iOS · Figma", "work-wander.png"),
                       ("Echo Notes", "AI note-taking that summarizes as you type.", "AI · TypeScript · GraphQL", "work-echo.png")]},
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
             "items": [("Aurora Dashboard", "为 SaaS 团队打造的实时数据分析工具。", "React · D3 · 设计系统", "work-aurora.png"),
                       ("Wander", "像日记一样自然的旅行规划应用。", "移动端 · iOS · Figma", "work-wander.png"),
                       ("Echo Notes", "边输入边总结的 AI 笔记工具。", "AI · TypeScript · GraphQL", "work-echo.png")]},
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
    lang_switch = "".join(
        f'<a href="{BASE}/{l}/" lang="{l}" {"aria-current=\"true\"" if l == locale else ""}>'
        f'{"EN" if l == "en" else "中文"}</a>'
        for l in LANGS
    )
    return f"""
<nav class="global-nav">
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
    return f"""
<section class="hero" id="top">
  <img class="hero__img" src="{BASE}/assets/hero.jpg" alt="" />
  <div class="hero__scrim" aria-hidden="true"></div>
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
    stats = "".join(
        f'<div><div class="about-stats__num">{esc(v)}</div><div class="about-stats__label">{esc(l)}</div></div>'
        for v, l in t["about"]["stats"]
    )
    chips = "".join(f'<span class="chip">{esc(c)}</span>' for c in t["about"]["chips"])
    return f"""
<section class="section section--parchment" id="about">
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
      <div class="about-portrait"><img src="{BASE}/assets/portrait.jpg" alt="{esc(t["about"]["title"])}" loading="lazy" /></div>
    </div>
  </div>
</section>"""


def render_skills(t: dict) -> str:
    cols = "".join(
        f'<div class="skills-card"><h3>{esc(name)}</h3><ul>'
        + "".join(f"<li>{esc(i)}</li>" for i in items)
        + "</ul></div>"
        for name, items in t["skills"]["cols"]
    )
    return f"""
<section class="section section--dark" id="skills">
  <div class="container">
    <div class="section-head">
      <h2 class="section-title">{esc(t["skills"]["title"])}</h2>
      <p class="section-sub">{esc(t["skills"]["subtitle"])}</p>
    </div>
    <div class="skills-grid">{cols}</div>
  </div>
</section>"""


def render_experience(t: dict) -> str:
    items = "".join(
        f'<div class="timeline__item"><div class="timeline__period">{esc(period)}</div>'
        f'<div><div class="timeline__role">{esc(role)}</div>'
        f'<div class="timeline__company">{esc(company)}</div>'
        f'<p class="timeline__desc">{esc(desc)}</p></div></div>'
        for period, role, company, desc in t["experience"]["items"]
    )
    return f"""
<section class="section" id="experience">
  <div class="container">
    <div class="section-head">
      <h2 class="section-title">{esc(t["experience"]["title"])}</h2>
      <p class="section-sub">{esc(t["experience"]["subtitle"])}</p>
    </div>
    <div class="timeline">{items}</div>
  </div>
</section>"""


def render_work(t: dict) -> str:
    cards = "".join(
        f'<article class="work-card"><div class="work-card__img"><img src="{BASE}/assets/{img}" alt="{esc(name)}" loading="lazy" /></div>'
        f'<h3>{esc(name)}</h3><p>{esc(desc)}</p><div class="work-card__tags">{esc(tags)}</div></article>'
        for name, desc, tags, img in t["work"]["items"]
    )
    return f"""
<section class="section section--parchment" id="work">
  <div class="container">
    <div class="section-head">
      <h2 class="section-title">{esc(t["work"]["title"])}</h2>
      <p class="section-sub">{esc(t["work"]["subtitle"])}</p>
    </div>
    <div class="work-grid">{cards}</div>
  </div>
</section>"""


def render_testimonials(t: dict) -> str:
    cards = "".join(
        f'<figure class="testi-card"><blockquote>{esc(q)}</blockquote><figcaption>{esc(a)}</figcaption></figure>'
        for q, a in t["testi"]["items"]
    )
    return f"""
<section class="section section--dark" id="testimonials">
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
    socials = (
        f'<a href="https://github.com/BerryUIKI">GitHub @BerryUIKI</a>'
        f'<a href="https://www.linkedin.com/">LinkedIn</a>'
        f'<a href="mailto:{esc_attr(email)}">Email</a>'
    )
    return f"""
<section class="contact" id="contact">
  <div class="container">
    <h2>{esc(t["contact"]["title"])}</h2>
    <p>{esc(t["contact"]["subtitle"])}</p>
    <a class="btn btn-primary" href="mailto:{esc_attr(email)}">{esc(email)}</a>
    <div class="contact__socials">{socials}</div>
  </div>
</section>"""


def render_footer(locale: str, t: dict) -> str:
    nav_links = "".join(
        f'<a href="{BASE}/{locale}/#{a}">{esc(label)}</a>'
        for a, label in zip(ANCHORS, [t["nav"]["about"], t["nav"]["skills"], t["nav"]["work"], t["nav"]["contact"]])
    )
    social = "".join(
        f'<a href="{url}">{esc(label)}</a>'
        for label, url in zip(t["footer"]["social"], ["https://github.com/BerryUIKI", "https://www.linkedin.com/", "#"])
    )
    contact_col = "".join(
        f'<a href="{"mailto:" + esc_attr(t["contact"]["email"]) if i == 0 else "#"}">{esc(label)}</a>'
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
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('berry-theme', next); } catch (e) {}
      syncIcon();
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
  function updateHero() {
    if (!hero || !img) return;
    var y = window.scrollY;
    var max = Math.max(hero.offsetHeight, 1);
    var p = Math.min(y / max, 1);
    img.style.transform = 'scale(' + (1 - 0.45 * p) + ') translateY(' + (120 * p) + 'px)';
    img.style.opacity = String(1 - 0.6 * p);
    // 下滑时底部两角渐变圆角（全屏直角 → 卡片圆角）
    var br = Math.round(28 * p);
    img.style.borderRadius = '0 0 ' + br + 'px ' + br + 'px';
    // scrim 随滚动淡出，露出纯色主题背景（亮色=白 / 暗色=黑）
    if (scrim) scrim.style.opacity = String(1 - 0.92 * p);
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
  var SUPPORTED = ['en', 'zh'];
  var DEFAULT = 'en';
  var lang = DEFAULT;
  try {{
    var saved = localStorage.getItem('berry-lang');
    if (saved && SUPPORTED.indexOf(saved) !== -1) {{
      lang = saved;
    }} else {{
      // 英语优先：优先遍历完整语言偏好列表（navigator.languages），
      // 只要列表里出现 en 就选英文；只有纯中文环境才给中文。
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


def page_shell(locale: str, t: dict, title: str, desc: str, body: str) -> str:
    meta = t["meta"]
    full_title = f"{title} — {meta['title']}" if title else meta["title"]
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
<link rel="icon" type="image/svg+xml" href="{BASE}/favicon.svg" />
<link rel="stylesheet" href="{BASE}/styles.css" />
</head>
<body>
{body}
<script src="{BASE}/script.js"></script>
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
    return page_shell(locale, t, "", "", body)


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
    return page_shell(locale, t, t["blog"]["title"], t["blog"]["sub"], body)


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
    return page_shell(locale, t, post["title"], post.get("description", ""), body)


# ============================================================
# 构建入口
# ============================================================
def main():
    # 沙箱环境禁用文件删除（回收站不可用），采用覆盖写入方式构建
    DIST.mkdir(parents=True, exist_ok=True)

    # 静态资源
    shutil.copy(ROOT / "public" / "favicon.svg", DIST / "favicon.svg")
    shutil.copy(SRC / "styles" / "global.css", DIST / "styles.css")
    (DIST / "script.js").write_text(SCRIPT_JS, encoding="utf-8")
    assets = DIST / "assets"
    assets.mkdir(exist_ok=True)
    for f in ASSETS_SRC.iterdir():
        shutil.copy(f, assets / f.name)

    # 根路径：语言检测重定向
    (DIST / "index.html").write_text(INDEX_REDIRECT, encoding="utf-8")

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
