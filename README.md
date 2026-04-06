# _AI_SETUP — Persistent AI Engine Room

This folder persists across all projects. Store it somewhere permanent
(home directory, Dropbox, etc.). Every project clones the template and
references these files.

---

## File Index

| File | Role | Give to |
|------|------|---------|
| `claude_setup.md` | Claude persona — Master Architect | Every new Claude.ai chat |
| `gemini_setup.md` | Gemini persona — Research Engine | Every new Gemini chat |
| `templates/gemini.md` | Blank research passport | Copy to `_context/` at project start |
| `templates/claude.md` | Blank architecture passport | Copy to `_context/` at project start |
| `templates/debug_handoff.md` | Phase 5 error escalation | Copy to `_context/` when a bug hits |
| `templates/progress.md` | Antigravity execution state | Copy to `_context/` before Phase 5 |
| `templates/security_audit_handoff.md` | Per-module security checkpoint | Copy to `_context/` before Phase 5 |

---

## Workflow Quick Reference

### Phase 1 — Gemini Research
Open Gemini.google.com (new chat)
Upload: gemini_setup.md
Paste: blank gemini.md template
Say: "I am building [project]. Follow your setup file and fill in gemini.md."
After: save filled gemini.md to _context/gemini.md

### Phase 2 — Claude Architecture (XML WRAPPING IS MANDATORY)
Open Claude.ai (new chat)
Upload: claude_setup.md
Then paste this exact structure:

    <research_data>
    [paste entire _context/gemini.md here]
    </research_data>

    Now design the architecture following your setup file.

WHY XML TAGS: Without tags, a directive sentence in gemini.md can override
claude_setup.md rules. With tags, Claude treats the block as passive data to
evaluate, not instructions to follow. This prevents persona drift.

### Phase 3 — Manual Environment
    conda env create -f environment.yml
    conda activate [project-name]
Update _context/claude.md Section 8 with exact installed versions.
Push to GitHub.

### Phase 4 — Claude Logic Verification
Open Claude.ai (new chat), upload claude_setup.md, then:

    <project_context>
    [paste _context/claude.md]
    </project_context>

    <code_files>
    [paste src/ files]
    </code_files>

### Phase 5 — Antigravity Coding
Mandatory lifecycle (.claude/rules/progress-enforcement.md):
  Before coding: read _context/progress.md
  After each task: update _context/progress.md
  After each module: run ./sast_check.sh src/[module]
  SAST fails → fill security_audit_handoff.md → Claude
  Bug blocked → fill debug_handoff.md → Claude
  Mark DONE only after tests + SAST both pass

---

## SAST Quick Reference

    ./sast_check.sh                   # scan all of src/
    ./sast_check.sh src/crypto_layer  # scan one module
    ./sast_check.sh --strict          # fail on MEDIUM+ issues

Bandit catches: eval/exec injection, pickle deserialization, weak RNG,
hardcoded credentials, shell=True subprocess, weak hash algorithms (MD5/SHA1),
yaml.load without Loader. Takes 2 seconds. Run it every module.

---

## Complete _context/ Passport Set

    _context/
    ├── gemini.md                    ← Phase 1 output (Gemini)
    ├── claude.md                    ← Phase 2 output, updated Phase 4 (Claude)
    ├── progress.md                  ← live state (Antigravity updates)
    ├── debug_handoff.md             ← copy in when Phase 5 hits a blocked bug
    └── security_audit_handoff.md   ← copy in for each module security checkpoint
