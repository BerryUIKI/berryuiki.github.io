# THE BERRY — Berry Wahlberg / 花雨琦 个人网站

部署于 **GitHub Pages** 的纯静态个人网站（**零依赖**，无需 npm/Node）：

- 🌐 双语言 **EN / 中文**——检测系统语言自动切换，**默认英语优先**；导航栏可手动切换（localStorage 持久化）
- 🌗 **暗色 / 亮色**双主题——跟随系统偏好，可手动切换（localStorage 持久化）
- 📷 Apple 产品页式 Hero——照片默认全屏，**向下滚动时缩小**（scroll-shrink）
- 📝 **博客**——Markdown 编写，按语言分版（`src/content/posts/`）

## 本地构建（纯 Python，无需安装依赖）

```bash
python build_site.py     # 输出到 dist/
python -m http.server 8080 -d dist   # 本地预览 http://localhost:8080
```

## 部署

推送 `main` 分支后，GitHub Actions（Python 构建）自动发布：

- 线上地址：<https://berryuiki.github.io/BerryUIKI/>
- 根路径 `/` 会按系统语言重定向到 `/en/` 或 `/zh/`

## 目录结构

```
build_site.py        # 微型静态站点生成器（标准库 only，数据+模板+博客解析都在这里）
public/              # favicon 等静态资源
src/
├── assets/          # 图片（hero 全屏图 / About 肖像 / 项目图）
├── content/posts/   # 博客文章（frontmatter: title/date/lang/description）
├── i18n/translations.ts   # Astro 版翻译字典（备用）
└── styles/global.css      # 设计系统（Apple 风格 tokens，Light/Dark）
```

> **关于 Astro 源码**：`src/components|layouts|pages` 与 `package.json` 是此前规划的 Astro 版本，因当前网络环境 npm 安装不可用（registry 请求被限速至数分钟/个），已改用上方零依赖的 Python 构建器产出同等功能（相同文案、相同样式、相同交互）。日后网络恢复，可 `npm install && npm run build` 平滑迁移。

## 内容更新

- **文章**：在 `src/content/posts/` 新建 `.md`，frontmatter 写 `lang: en|zh`，同篇文章中英文用不同文件名（如 `hello-world.md` / `hello-world-zh.md`），然后重新运行 `python build_site.py`
- **文案**：编辑 `build_site.py` 顶部 `T` 字典
- **颜色主题**：改 `src/styles/global.css` 里的 CSS 变量（亮色 `:root` / 暗色 `[data-theme="dark"]`）
