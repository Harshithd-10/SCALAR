# SECURITY_AUDIT_HANDOFF.MD — [PROJECT NAME]
## Phase 5.5 Security Checkpoint
### Module: [module name] | Audited: [DATE] | Status: Pending

---

> **When to use this**:
> After Antigravity completes each module (not the whole project — per module),
> open a new Claude.ai session and upload:
> `claude_setup.md` + `_context/claude.md` + this file + the completed module files.
>
> Claude will audit for execution-level vulnerabilities that architecture review misses.
> Do not proceed to the next module until this audit returns a PASS or ACCEPTED RISK.

---

## 1. MODULE BEING AUDITED

- **Module name**: `src/[module]/`
- **Files included in this audit**:
  - `src/[module]/[file1].py`
  - `src/[module]/[file2].py`
- **What this module does** (one sentence):
- **Domain**: Quantum / Cyber / AI / DS

---

## 2. THREAT SURFACE FOR THIS MODULE

[Answer these before sending to Claude — they focus the audit.]

Does this module:
- [ ] Accept any external input (user, file, network, API)?
- [ ] Handle cryptographic keys, tokens, or credentials?
- [ ] Execute system commands or subprocesses?
- [ ] Deserialize data (pickle, json.loads, yaml.load)?
- [ ] Write to files or databases?
- [ ] Make network requests?
- [ ] Run quantum circuits (timing side-channel risk)?
- [ ] Use random number generation (must be crypto-safe if in Cyber)?

---

## 3. PASTE MODULE CODE HERE

```python
# [Paste the complete module code — all files listed in Section 1]
# Do not summarize. Claude needs the actual code, not a description.
```

---

## 4. KNOWN CONTEXT FROM CLAUDE.MD

[Copy the interface contract for this module from `_context/claude.md` Section 5]

```
Module: [name]
Input:
Output:
Raises:
Side effects:
```

---

## 5. CLAUDE'S SECURITY AUDIT RESPONSE
*(Claude fills this section)*

### Summary Verdict
- [ ] **PASS** — no significant issues found
- [ ] **PASS WITH NOTES** — minor issues, acceptable risk, documented below
- [ ] **FAIL** — critical issues must be fixed before proceeding

### Findings

| # | Severity | Vulnerability Type | File:Line | Description | Fix Required |
|---|----------|-------------------|-----------|-------------|-------------|
| 1 | CRITICAL / HIGH / MEDIUM / LOW | | | | yes / no |

**Severity definitions**:
- `CRITICAL`: Can be exploited remotely or causes data/key exposure. Block release.
- `HIGH`: Exploitable under realistic conditions. Fix before next module.
- `MEDIUM`: Exploitable under specific conditions. Fix before Phase 5 ends.
- `LOW`: Best practice violation, not exploitable. Document and move on.

### Specific Checks for This Domain

**Quantum modules** — Claude checks for:
- Timing side-channels in measurement loops
- Determinism of random seed in circuit sampling
- Classical data leakage through quantum output

**Crypto modules** — Claude checks for:
- Use of deprecated primitives (MD5, SHA1, ECB mode, pycrypto)
- Constant-time comparison (never `==` for secrets — use `hmac.compare_digest`)
- Key material in logs, exceptions, or serialized output
- RNG source (`secrets` module or `os.urandom`, never `random`)

**AI/ML modules** — Claude checks for:
- Pickle deserialization of untrusted model files
- Prompt injection surface in LLM-facing code
- Data leakage in training logs or experiment artifacts

**Data modules** — Claude checks for:
- SQL/command injection in query construction
- Path traversal in file operations
- Sensitive data in log output

### Recommended Fixes
[Claude writes specific, line-level fixes here]

### claude.md Update Required
- [ ] Yes — Security notes to add: [what]
- [ ] No

---

## 6. RESOLUTION LOG
*(Fill after fixes are applied)*

| Finding # | Fixed | Fix Description | Verified by test |
|-----------|-------|-----------------|-----------------|
| | | | |

**Final status after fixes**: PASS / PASS WITH ACCEPTED RISK

---

*Phase 5.5 audit complete — proceed to next module*
*Attach: claude_setup.md + _context/claude.md + module files*
