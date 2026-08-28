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
 * 客户端语言检测：
 * 1. localStorage('berry-lang') 手动选择优先（覆盖系统）
 * 2. navigator.language 匹配支持列表
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
  return normalizeLang(navigator.language || defaultLocale);
}
