---
description: "Guidelines for maintaining directory-level AGENTS.md files"
applyTo: "**/AGENTS.md"
---

# AGENTS.md Maintenance Rules

## Format & Style

- Use dash-separated bullet points, not numbered lists.
- One short sentence per rule; avoid paragraphs.
- Group related rules under H2 sections.
- STRICTLY NO emoji or bold emphasis within bullets.
- Start rules directly with the action or constraint (no "Title: description" format).

## Content Principles

- Capture module-specific constraints, not general coding advice.
- Focus on what's different/critical for this directory.
- Don't duplicate L3 global rules from `.github/copilot-instructions.md`.
- Include commands, configs, or IDs specific to this module.

## What to Include

- API conventions unique to this module.
- Test patterns specific to this codebase area.
- Critical constants or configuration values.
- Common mistakes agents made in this module (with brief fix).
- Private access helpers or test utilities location.

## What to Exclude

- Generic best practices (belongs in L2 `.github/instructions/*.instructions.md`).
- Lengthy explanations or rationale (keep it actionable).
- Redundant rules already in parent directory's AGENTS.md.
- One-time ephemeral context not applicable to future work.
