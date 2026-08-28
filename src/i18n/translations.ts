// i18n 翻译字典 —— 与设计稿文案完全对齐
// en: 默认语言（英语优先）| zh: 简体中文

export type Locale = 'en' | 'zh';

export const locales: Locale[] = ['en', 'zh'];
export const defaultLocale: Locale = 'en';

export const siteMeta = {
  en: {
    title: 'Berry Wahlberg — Product Designer & Developer',
    description:
      'Portfolio of Berry Wahlberg (花雨琦): product designer and developer crafting simple, human software.',
  },
  zh: {
    title: '花雨琦 — 产品设计师 & 开发者',
    description: '花雨琦（Berry Wahlberg）的个人网站：设计与开发简洁、快速、以人为本的数字产品。',
  },
};

export const translations = {
  en: {
    nav: {
      about: 'About',
      skills: 'Skills',
      experience: 'Experience',
      work: 'Work',
      contact: 'Contact',
    },
    langSwitch: {
      label: 'Language',
    },
    hero: {
      eyebrow: 'PRODUCT DESIGNER & DEVELOPER',
      badge: 'THE BERRY · Aries',
      title: "Hi, I'm Berry Wahlberg.",
      subtitle:
        'I design and build thoughtful digital products — simple, fast, and human by default.',
      ctaPrimary: 'View My Work',
      ctaSecondary: 'Contact Me',
      scrollHint: 'Scroll — photo shrinks',
    },
    about: {
      title: 'About Me',
      subtitle: 'Designer, developer, and lifelong learner based in Shanghai.',
      p1: "For the past eight years, I've helped startups and product teams turn ambiguous ideas into shipped products. I work across the whole stack — from wireframes and design systems to React and Node.js — because great products are built at the intersection of craft and code.",
      p2: 'My goal is simple: make technology feel human. I care deeply about accessibility, internationalization, and the small details that turn an interface into an experience.',
      stats: [
        { value: '8+', label: 'Years Experience' },
        { value: '40+', label: 'Projects Shipped' },
        { value: '12', label: 'Countries Served' },
      ],
      chips: ['Aries', 'ENFP · Happy Pup', 'Tender Soul'],
    },
    skills: {
      title: 'Skills & Tools',
      subtitle: 'The tools and crafts I reach for every day.',
      columns: [
        { name: 'Design', items: ['Product Design', 'Design Systems', 'Prototyping', 'Usability Testing'] },
        { name: 'Frontend', items: ['React', 'TypeScript', 'Tailwind CSS', 'Web Animations'] },
        { name: 'Backend', items: ['Node.js', 'Python', 'GraphQL', 'PostgreSQL'] },
        { name: 'Platform', items: ['CI/CD', 'Internationalization', 'Performance', 'Accessibility'] },
      ],
    },
    experience: {
      title: 'Experience',
      subtitle: "Where I've been and what I've shipped.",
      items: [
        {
          period: '2021 — Present',
          role: 'Senior Product Designer',
          company: 'Acme Studio · Shanghai',
          description: 'Leading the design system and core product flows for a B2B analytics platform used by 2,000+ teams.',
        },
        {
          period: '2018 — 2021',
          role: 'Product Designer',
          company: 'Nova Labs · Remote',
          description: 'Designed end-to-end experiences for a consumer fintech app, growing activation by 34%.',
        },
        {
          period: '2016 — 2018',
          role: 'Frontend Developer',
          company: 'Pixel Works · Guangzhou',
          description: 'Built responsive marketing sites and internal tools with React, cutting page load times by 60%.',
        },
      ],
    },
    work: {
      title: 'Selected Work',
      subtitle: "A few projects I'm proud of.",
      items: [
        {
          name: 'Aurora Dashboard',
          description: 'Real-time analytics for SaaS teams.',
          tags: 'React · D3 · Design System',
        },
        {
          name: 'Wander',
          description: 'A travel planner that feels like a journal.',
          tags: 'Mobile · iOS · Figma',
        },
        {
          name: 'Echo Notes',
          description: 'AI note-taking that summarizes as you type.',
          tags: 'AI · TypeScript · GraphQL',
        },
      ],
    },
    testimonials: {
      title: 'What People Say',
      subtitle: 'Colleagues and clients on working together.',
      items: [
        {
          quote: "Berry has an eye for detail that most designers only dream of. Every handoff is pixel-perfect and every decision is backed by reasoning.",
          author: 'Sarah Kim — VP Product, Acme Studio',
        },
        {
          quote: "Working with Berry felt like adding a co-founder, not a contractor. She pushed our product to a level we didn't think we could reach.",
          author: 'Daniel Chen — Founder, Nova Labs',
        },
        {
          quote: 'Fast, thoughtful, and endlessly curious. Berry rebuilt our design system and the whole team felt the difference within a week.',
          author: 'Mia Zhou — Engineering Lead, Pixel Works',
        },
      ],
    },
    contact: {
      title: "Let's work together.",
      subtitle: "Have a project in mind? I'd love to hear about it.",
      email: 'berrywahlberg@gmail.com',
      socials: ['GitHub @BerryUIKI', 'LinkedIn', 'Email'],
    },
    footer: {
      tagline: 'Designer & developer crafting simple, human software.',
      navTitle: 'Navigation',
      navLinks: ['About', 'Skills', 'Work', 'Contact'],
      socialTitle: 'Social',
      socialLinks: ['GitHub', 'LinkedIn', 'X / Twitter'],
      contactTitle: 'Contact',
      contactLinks: ['berrywahlberg@gmail.com', 'Shanghai, CN'],
      copyright: 'Copyright 2026 Berry Wahlberg. All rights reserved.',
    },
  },
  zh: {
    nav: {
      about: '关于',
      skills: '技能',
      experience: '经历',
      work: '作品',
      contact: '联系',
    },
    langSwitch: {
      label: '语言',
    },
    hero: {
      eyebrow: '产品设计师 & 开发者',
      badge: 'THE BERRY · 白羊座',
      title: '你好，我是花雨琦。',
      subtitle: '我设计并打造以人为本的数字产品——简洁、快速、自然。',
      ctaPrimary: '查看我的作品',
      ctaSecondary: '联系我',
      scrollHint: '下滑 — 照片缩小',
    },
    about: {
      title: '关于我',
      subtitle: '现居上海的设计师与开发者，终身学习者。',
      p1: '八年来，我帮助初创公司与产品团队把模糊的想法变成落地的产品。我的工作横跨全栈——从线框稿与设计系统，到 React 与 Node.js——因为伟大的产品诞生于设计与代码的交汇处。',
      p2: '我的目标很简单：让技术有人情味。我关注无障碍、国际化，以及那些把界面变成体验的微小细节。',
      stats: [
        { value: '8+', label: '年经验' },
        { value: '40+', label: '交付项目' },
        { value: '12', label: '服务国家/地区' },
      ],
      chips: ['白羊座', 'ENFP · 快乐小狗', '温柔受'],
    },
    skills: {
      title: '技能与工具',
      subtitle: '我每天都会用到的工具与手艺。',
      columns: [
        { name: '设计', items: ['产品设计', '设计系统', '原型制作', '可用性测试'] },
        { name: '前端', items: ['React', 'TypeScript', 'Tailwind CSS', 'Web 动效'] },
        { name: '后端', items: ['Node.js', 'Python', 'GraphQL', 'PostgreSQL'] },
        { name: '平台', items: ['CI/CD', '国际化', '性能优化', '无障碍'] },
      ],
    },
    experience: {
      title: '工作经历',
      subtitle: '走过的路，交付过的产品。',
      items: [
        {
          period: '2021 — 至今',
          role: '资深产品设计师',
          company: 'Acme Studio · 上海',
          description: '负责 B2B 分析平台的设计系统与核心产品流程，服务 2,000+ 团队。',
        },
        {
          period: '2018 — 2021',
          role: '产品设计师',
          company: 'Nova Labs · 远程',
          description: '为消费级金融应用设计端到端体验，激活率提升 34%。',
        },
        {
          period: '2016 — 2018',
          role: '前端开发者',
          company: 'Pixel Works · 广州',
          description: '使用 React 构建响应式营销网站与内部工具，页面加载时间降低 60%。',
        },
      ],
    },
    work: {
      title: '精选作品',
      subtitle: '我引以为豪的几个项目。',
      items: [
        {
          name: 'Aurora Dashboard',
          description: '为 SaaS 团队打造的实时数据分析工具。',
          tags: 'React · D3 · 设计系统',
        },
        {
          name: 'Wander',
          description: '像日记一样自然的旅行规划应用。',
          tags: '移动端 · iOS · Figma',
        },
        {
          name: 'Echo Notes',
          description: '边输入边总结的 AI 笔记工具。',
          tags: 'AI · TypeScript · GraphQL',
        },
      ],
    },
    testimonials: {
      title: '他们怎么说',
      subtitle: '同事与客户眼中的合作体验。',
      items: [
        {
          quote: '花雨琦（Berry）对细节的洞察是大多数设计师梦寐以求的。每次交付都像素级完美，每个决策都有理有据。',
          author: 'Sarah Kim — Acme Studio 产品副总裁',
        },
        {
          quote: '与花雨琦合作就像多了一位联合创始人，而不是外包。她把我们的产品推到了我们以为到不了的高度。',
          author: 'Daniel Chen — Nova Labs 创始人',
        },
        {
          quote: '高效、深思熟虑、永远充满好奇。花雨琦重建了我们的设计系统，整个团队在一周内就感受到了差别。',
          author: 'Mia Zhou — Pixel Works 技术负责人',
        },
      ],
    },
    contact: {
      title: '一起合作吧。',
      subtitle: '有项目想法？很乐意与你聊聊。',
      email: 'berrywahlberg@gmail.com',
      socials: ['GitHub @BerryUIKI', 'LinkedIn', 'Email'],
    },
    footer: {
      tagline: '用设计与代码，打造简洁而有温度的产品。',
      navTitle: '导航',
      navLinks: ['关于', '技能', '作品', '联系'],
      socialTitle: '社交',
      socialLinks: ['GitHub', 'LinkedIn', 'X / Twitter'],
      contactTitle: '联系',
      contactLinks: ['berrywahlberg@gmail.com', '中国 · 上海'],
      copyright: '2026 花雨琦 · 版权所有',
    },
  },
};

export type Translation = (typeof translations)['en'];

export function getTranslation(locale: Locale): Translation {
  return translations[locale];
}
