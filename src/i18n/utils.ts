// 语言工具：支持的语言与检测逻辑
// 检测优先级：localStorage 手动选择 > navigator.language 系统语言 > 默认 en

import type { Locale } from './translations';
import { locales, defaultLocale } from './translations';

/** 归一化系统语言，例如 zh-CN → zh, en-US → en */
export function normalizeLang(raw: string): Locale {
  const lower = raw.toLowerCase().split('-')[0];
  return (locales as string[]).includes(lower) ? (lower as Locale) : defaultLocale;
}

/**
 * 客户端语言检测（英语优先）：
 * 1. localStorage('berry-lang') 手动选择优先（覆盖系统）
 * 2. 遍历 navigator.languages 完整偏好列表——只要出现 en 就选英文；
 *    只有纯中文环境（仅 zh 无 en）才给中文
 * 3. 都不匹配 → 回退 en（默认英语优先）
 */
export function detectLocale(): Locale {
  try {
    const saved = localStorage.getItem('berry-lang');
    if (saved && (locales as string[]).includes(saved)) {
      return saved as Locale;
    }
  } catch {
    /* ignore */
  }
  const list: string[] =
    typeof navigator !== 'undefined' && navigator.languages?.length
      ? navigator.languages
      : [navigator.language || defaultLocale];
  let hasZh = false;
  for (const lang of list) {
    const code = String(lang).toLowerCase().split('-')[0];
    if (code === 'en') return 'en';
    if (code === 'zh') hasZh = true;
  }
  return hasZh ? 'zh' : defaultLocale;
}
