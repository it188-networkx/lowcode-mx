---
description: "Guidelines for creating high-quality custom instruction files for GitHub Copilot"
applyTo: "**/*.instructions.md"
---

# Custom Instructions File Guidelines

## Required Frontmatter

```yaml
---
description: "Brief description of the instruction purpose and scope"
applyTo: "glob pattern for target files (e.g., **/*.ts, **/*.py)"
---
```

- **description**: 1-500 characters, single-quoted
- **applyTo**: Glob pattern(s) — single: `'**/*.ts'`, multiple: `'**/*.ts, **/*.tsx'`

## File Naming

- Use lowercase with hyphens: `react-best-practices.instructions.md`
- Location: `.github/instructions/` directory

## File Structure

- **Title**: Clear `#` heading with brief intro
- **Core Sections**: Group by domain (Best Practices, Code Standards, Common Patterns, etc.)
- **Validation** (optional): Build/lint/test commands to verify compliance

## Content Principles

- **Action Oriented**: Write in imperative mood (e.g., "Use", "Avoid", not "should", "might").
- **Single Rule**: One actionable rule per bullet; avoid paragraphs.
- **Structured Format**: Start each bullet point with a bold keyword or title, followed by a colon (e.g., **- **Naming**: Use camelCase...**).
- **Decision Matrices**: Use tables for decision matrices (Scenario → Prefer → Avoid).
- **Code Examples**: Include code examples only when they clarify ambiguous rules.
- **Authoritative Sources**: Link to official docs and authoritative sources.
- **Strict Specificity**: Exclude generic software engineering advice (e.g., "ensure accessibility", "git workflow"). Only include rules unique to this specific technical context.

## What to Include

- Naming conventions specific to this domain
- Preferred libraries and patterns
- Error handling patterns specific to the framework/domain
- File organization rules
- Critical "Don't" patterns with brief rationale
- Target language/framework versions when relevant

## What to Exclude

- Generic best practices AI already knows (e.g., "Clean Code" principles, accessibility standards, localization, version control hygiene).
- Meta-process instructions (e.g., "Establish a feedback loop", "Test templates in real-world").
- Lengthy explanations or rationale (keep actionable).
- Redundant rules covered by language-specific instruction files.
- Outdated patterns or deprecated features.

## Authoring Anti-patterns

| Anti-pattern                | Why                    | Instead                         |
| --------------------------- | ---------------------- | ------------------------------- |
| Overly verbose explanations | Hard to scan           | Keep concise and actionable     |
| Missing code examples       | Abstract rules unclear | Show concrete good/bad examples |
| Contradictory advice        | Confuses AI            | Ensure consistency throughout   |
| Copy-paste from docs        | No added value         | Distill and contextualize       |
| Outdated patterns           | Misleads generation    | Reference current versions      |

## Scope Boundaries

Distinguish between **reusable** and **repository-specific** instruction files:

| File Type               | Scope                        | Examples                                                | Location                          |
| ----------------------- | ---------------------------- | ------------------------------------------------------- | --------------------------------- |
| Reusable instructions   | Portable across repositories | `.github/instructions/*`                                |
| Repository instructions | This repo only               | Workspace architecture, crate purposes, FDB key layouts | `.github/copilot-instructions.md` |

### Reusable Instruction Files (`.github/instructions/`)

These files should be **portable** — usable in any project with the same language/tool/domain:

- Keep content generic; no repo-specific types, paths, or crate names
- Preserve comprehensive coverage; do not delete existing valuable content
- Include authority references (official docs, RFCs, style guides)

### Repository Instruction Files (`.github/copilot-instructions.md`)

Content that only applies to **this specific repository**:

- Workspace architecture and crate/module purposes
- Repository-specific patterns (e.g., `Vs10`/`Vs16` versionstamps, FDB transaction handling)
- Concrete build/test commands with actual crate names
- References to ADRs and design docs

## Validation

- Test instructions with actual Copilot prompts
- Verify code examples compile/run
- Confirm `applyTo` glob matches intended files

## Maintenance

- Review when dependencies or frameworks update
- Remove deprecated patterns promptly
- Add emerging community patterns
- Keep glob patterns accurate as project structure evolves

## References

- [Custom Instructions Documentation](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [Awesome Copilot Instructions](https://github.com/github/awesome-copilot/tree/main/instructions)
