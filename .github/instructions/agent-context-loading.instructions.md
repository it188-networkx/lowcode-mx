---
description: "Enforce reading associated AGENTS.md files before any operation in the workspace"
applyTo: "**/*"
---

# Agent Context Loading Rules

Before performing any create, edit, or delete operation on any file in this workspace, load the AGENTS.md chain in the following order — do NOT skip any step.

## Mandatory Read Order

- **Step 1 — Target directory AGENTS.md**: Read the `AGENTS.md` in the same directory as the target file (e.g., `src/itsm/module/AGENTS.md` before touching any file in that folder).
- **Step 2 — Parent directory AGENTS.md**: Read the parent namespace's `AGENTS.md` chain upward (e.g., `src/itsm/AGENTS.md`, then `src/AGENTS.md`).
- **Step 3 — lowcode-base reference docs**: Read the `lowcode-base` reference docs matching the operation type (see table below).
- **Step 4 — lowcode-template reference**: When creating new namespace config, also read `lowcode-template/src/AGENTS.md` for the minimal-first principle.
- **Step 5 — Execute**: Only after completing Steps 1–4, perform the requested operation.

## Resource-Type Reference Map

| Target file type | Required reference before operation |
|-----------------|--------------------------------------|
| `module/` files | `lowcode-base/corteza/field/AGENTS.md` + `lowcode-base/process/module/AGENTS.md` |
| `page/` files | `lowcode-base/corteza/block/AGENTS.md` + `lowcode-base/process/page/AGENTS.md` |
| `layout/` files | `lowcode-base/corteza/block/AGENTS.md` + `lowcode-base/process/layout/AGENTS.md` |
| `field/` files | `lowcode-base/corteza/field/AGENTS.md` + `lowcode-base/process/field/AGENTS.md` |
| `workflow/` files | `lowcode-base/corteza/field/AGENTS.md` + `lowcode-base/process/workflow/sop-workflow-add.md` |
| `button/` files | `lowcode-base/process/button/AGENTS.md` |

## Why This Matters

- **ID uniqueness**: Target directory `AGENTS.md` contains the current max ID; skipping it causes ID conflicts.
- **File naming**: Correct sequence numbers and name patterns are recorded in the target AGENTS.md.
- **Schema correctness**: Resource-type references define valid field kinds, block options, and layout coordinates.
- **mx-specific overrides**: `src/{namespace}/AGENTS.md` may contain mx-tenant-specific moduleID or pageID overrides that differ from the template.

## Violations to Avoid

- Do not infer IDs from file counts or guesses — always read the AGENTS.md to get the declared max ID.
- Do not copy field/block configs from another namespace without first verifying the target AGENTS.md.
- Do not create files in a subdirectory without confirming the subdirectory's AGENTS.md exists and is current.
- Do not use moduleIDs or pageIDs from `lowcode-template` directly — mx tenant IDs are different and must be read from `src/{namespace}/AGENTS.md`.
