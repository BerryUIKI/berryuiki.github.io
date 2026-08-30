---
title: 'Designing agents with visible boundaries'
date: 2026-08-29
lang: 'en'
description: 'A field note on capability modes, permissions, and making agent behavior reviewable.'
---

An agent becomes difficult to trust when every mode can read everything, write everywhere, and silently decide what happens next. More capability is not automatically better product design.

## Give modes a job

A useful boundary starts with language people can understand. Archive, query, quote, and review describe different intentions. Each mode can then receive only the tools and data it needs.

## Make the boundary inspectable

- Separate durable evidence from temporary working state
- Make write permissions narrower than read permissions
- Record the path from source material to generated output
- Treat review as a first-class step, not an emergency brake

Axiara explores this structure for valuation research. The domain is specialized, but the interaction lesson travels well: an agent should make its authority visible before asking for trust.
