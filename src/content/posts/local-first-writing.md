---
title: 'Local-first is a product decision'
date: 2026-08-30
lang: 'en'
description: 'Why keeping files local changes the UX, architecture, and trust model of a writing tool.'
---

“Local-first” can sound like an implementation detail. In a writing tool, it is closer to a product promise: your work remains understandable and useful even when the app, account, or network disappears.

## The interface follows the trust model

When files stay on disk, the product should make that fact legible. Open, save, search, and workspace behaviors need to match what users already understand about folders and documents. A polished editor that hides file ownership behind an opaque sync state breaks that promise.

## Constraints become design material

- **Offline by default** changes how failure states are designed
- **Plain Markdown** gives users an exit path
- **Zero telemetry** reduces invisible behavior that needs explaining
- **Multiple modes** can serve reading, writing, and source-level control without pretending they are the same task

Lexora is my current exploration of these ideas. It is still evolving, but the principle is stable: trust is part of the interface, not a paragraph in the privacy policy.
