# DEBUG_HANDOFF.MD — [PROJECT NAME]
## Phase 5 Error Escalation Passport
### Escalated: [DATE] | Error Type: [see Section 1] | Status: Unresolved

---

> **How to use this file**
> When Antigravity/Claude Code hits an error it cannot resolve after 2–3 attempts,
> STOP. Do not let it loop. Fill this file and open a new Claude.ai session.
> Upload: `claude_setup.md` + `_context/claude.md` + this file + the specific broken file(s).
> Claude will diagnose the root cause and give you a resolution plan.
> Delete this instruction block before the Claude session.

---

## 1. ERROR CLASSIFICATION

Check all that apply:

- [ ] **Logic Error** — code runs but produces wrong output
- [ ] **Runtime Error** — code crashes with a traceback
- [ ] **Import / Dependency Error** — missing or incompatible package
- [ ] **Type Error** — type mismatch, pydantic validation failure
- [ ] **Config Error** — config.yaml value missing, wrong type, or wrong path
- [ ] **Data Error** — unexpected data shape, null values, schema mismatch
- [ ] **Quantum Error** — circuit error, transpilation failure, backend mismatch
- [ ] **Crypto / Security Error** — key error, signature failure, cert issue
- [ ] **Performance Error** — too slow, out of memory, timeout
- [ ] **Integration Error** — two modules that worked separately break together
- [ ] **Other**: _______________

---

## 2. THE EXACT ERROR

### 2.1 Full Error Message / Traceback
```
[Paste the complete error here — do not summarize, do not truncate.
If it's a traceback, paste all of it including the first line.]
```

### 2.2 File and Line Number
```
File: src/[module]/[file.py]
Line: [number]
Function: [function_name]
```

### 2.3 What the Code Was Trying to Do
[One sentence. Not the error — what was the intention of this code block?]

---

## 3. WHAT ANTIGRAVITY ALREADY TRIED

[List every fix attempt. If you skip this, Claude will suggest the same things.]

| Attempt # | What was tried | Result |
|-----------|---------------|--------|
| 1 | | Still fails / different error |
| 2 | | Still fails / different error |
| 3 | | — stopped here |

---

## 4. CONTEXT SNAPSHOT

### 4.1 The Broken Code Block
```python
# [Paste the specific function or block that is failing]
# Keep it minimal — just the failing code and its immediate dependencies
```

### 4.2 Relevant Config Values
```yaml
# [Paste only the config.yaml sections relevant to this error]
```

### 4.3 Relevant claude.md Section
[Which module in claude.md does this code belong to?
Copy the interface contract for this module from claude.md Section 5.]

```
Module: [name]
Input:  [from claude.md]
Output: [from claude.md]
```

### 4.4 Dependencies in Play
```
# Paste the relevant lines from requirements.txt
# e.g. torch==2.3.0, pennylane==0.36.0
```

### 4.5 Environment
```
OS:
Python version:
venv active: yes / no
Last working commit (if known):
```

---

## 5. WHAT WAS WORKING BEFORE THIS BROKE

[Was this function ever working? What changed?
If this is new code that never worked: say so.
If it broke after a change: describe the change.]

- Was working before: yes / no / never ran before
- Last known good state:
- What changed since then:

---

## 6. IMPACT ASSESSMENT

- [ ] **Blocker** — Phase 5 cannot continue until this is resolved
- [ ] **Partial blocker** — other modules still work, this one is stuck
- [ ] **Non-blocking** — can proceed with other tasks, come back to this

Modules blocked by this error:
1.
2.

---

## 7. HYPOTHESIS (optional — fill if you have one)

[Your best guess at the root cause. Even a wrong hypothesis helps Claude
orient faster. Leave blank if you have no idea — that's fine too.]

---

## 8. CLAUDE'S RESPONSE SECTION
*(Claude fills this in during the debug session)*

### Root Cause
[Claude writes here]

### Resolution Plan
[Claude writes step-by-step fix here — numbered, specific, no ambiguity]

1.
2.
3.

### Files to Change
| File | What to change | Why |
|------|---------------|-----|
| | | |

### Tests to Run After Fix
```bash
# [Claude writes the exact pytest command to verify the fix]
```

### If This Fix Doesn't Work
[Claude writes the fallback approach here]

### claude.md Update Required
- [ ] Yes — Section [N], change: [what]
- [ ] No

---

## 9. RESOLUTION LOG
*(Fill in after the fix is applied)*

| Field | Value |
|-------|-------|
| Resolved by | |
| Resolution date | |
| Fix applied | |
| Tests passed | yes / no |
| claude.md updated | yes / no |

---

*Escalated from Phase 5 | Attach: claude_setup.md + _context/claude.md + broken file(s)*
