# Ibras Skill Rebrand Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Publish seven collision-free `ibras-*` skills whose complete runtime bundles install through Hermes marketplace identifiers.

**Architecture:** Rename every skill identity while preserving runtime state paths. Reshape unsupported top-level runtime directories into Hermes-supported directories and generate explicit support-file manifests in each `SKILL.md`.

**Tech Stack:** Markdown/YAML skill packages, Bash/Python helpers, Git, Hermes Agent v0.20.2, Incus Ubuntu 24.04.

---

### Task 1: Add the marketplace contract test

**Files:**
- Create: `installer/test-hermes-marketplace.py`

1. Assert the seven canonical `ibras-*` directories exist and old directories do not.
2. Assert each YAML `name` equals its directory.
3. Assert no runtime `lib/`, `hooks/`, or `data/` remains at skill root.
4. Reproduce Hermes support-path extraction and require every shipped support file to be referenced by `SKILL.md`.
5. Run `python3 installer/test-hermes-marketplace.py`; expect failure on the current unprefixed layout.

### Task 2: Rename identities and preserve state compatibility

**Files:**
- Rename: the seven root skill directories to `ibras-*`
- Modify: all seven `SKILL.md`
- Modify: repository and per-skill documentation
- Modify: scripts that discover sibling skills

1. Rename directories and YAML names.
2. Update marketplace commands and cross-skill paths.
3. Keep integration state/config paths unchanged.
4. Run the contract test; expect only layout/manifest failures to remain.

### Task 3: Make bundles compatible with Hermes pruning

**Files:**
- Move: `<skill>/lib/*` to `<skill>/scripts/lib/*`
- Move: `<skill>/hooks/*` to `<skill>/scripts/hooks/*`
- Move: `ibras-social-publishing/data/*` to `ibras-social-publishing/assets/data/*`
- Modify: scripts and `SKILL.md` command paths
- Modify: `installer/sync-from-source.sh`, `installer/install.sh`, `installer/uninstall.sh`, and `installer/make-bundle.sh`

1. Move runtime files into supported directories.
2. Update every path consumer.
3. Generate an explicit manifest section in each `SKILL.md`.
4. Run the contract test and fix only the reported gaps.

### Task 4: Synchronize the development source

**Files:**
- Rename: `<development-repo>/skill-*` to `<development-repo>/skill-ibras-*`
- Modify: `<development-repo>/shared/sync.sh`
- Modify: local tests and documentation that encode skill identities/layout

1. Apply the same identity and layout rules to the development source.
2. Run `bash shared/sync.sh` and `bash shared/sync.sh --check`.
3. Run all existing shared and per-skill tests.
4. Re-run `installer/sync-from-source.sh <development-repo>` in the public worktree and confirm no drift.

### Task 5: Verify and publish

**Files:**
- Modify: `README.md`, `MAINTENANCE.md`, and release instructions

1. Run `bash installer/audit.sh`.
2. Run `python3 installer/test-hermes-marketplace.py`.
3. Run the full repository test matrix.
4. Review `git diff --check` and the complete diff.
5. Commit intentionally, push the branch, and integrate through the approved GitHub workflow.

### Task 6: Reinstall in Incus

1. Reset the test profile or create a fresh container.
2. Install all seven `volfadar/hermes-marketing-skills/ibras-*` identifiers.
3. Verify lock entries, names, scan verdicts, and exact file manifests.
4. Run representative doctor/help/smoke commands.
5. Verify all seven names occur in the generated Hermes system prompt.
6. Run natural-language OpenRouter trigger tests after receiving the temporary key.
