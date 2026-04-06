# [cite_start]GEMINI.MD — PR Review & Security Audit OpenEnv Environment [cite: 3]
## Research Phase Passport
### Generated: 2026-04-06 | Domain: Cyber/AI | Status: Phase 1 Complete

---

## 0. QUICK SUMMARY
[cite_start]This project is a submission for the Scalar Hackathon by Meta, building an OpenEnv-compliant environment to train and evaluate AI agents on code review and security auditing tasks[cite: 4, 6, 7]. [cite_start]These tasks are essential daily engineering operations, making the environment highly practical for CI/CD pipeline integration to provide automated, fast, first-pass reviews[cite: 8, 15]. [cite_start]The single biggest technical challenge is implementing deterministic, pure-Python graders without relying on LLMs, ensuring accurate and consistent evaluation of agent actions across varying difficulty levels while maintaining strict specification compliance[cite: 26, 46, 52].

---

## 1. PROJECT SCOPE & CONSTRAINTS
### 1.1 What We Are Building
[cite_start]We are building a real-world AI evaluation environment exposing a standard OpenEnv API (`step()`, `reset()`, `state()`)[cite: 7, 9]. [cite_start]The environment tests AI agents on analyzing provided code snippets (functions, web routes, or entire pull requests), identifying bugs and vulnerabilities, and producing structured outputs across three distinct difficulty tiers: Easy, Medium, and Hard[cite: 10, 25, 27].

### 1.2 Hard Constraints
* [cite_start]**No LLMs in Graders:** Graders must strictly use deterministic, pure Python logic (`[CPU-SAFE]`), such as AST parsing, regex matching, and string comparison[cite: 26]. [cite_start]Using models like GPT or Claude for grading will cause immediate disqualification for non-deterministic output[cite: 46, 47].
* [cite_start]**Environment Specs:** The environment must be packaged as a FastAPI application and containerized using Docker (linux/amd64) exposing port 7860[cite: 23, 53].
* [cite_start]**Validation:** The application must strictly pass the `openenv validate` command utilizing metadata from the `openenv.yaml` file[cite: 24, 52].
* [cite_start]**Tech Stack Limit:** Strict adherence to Python 3.11 and Pydantic v2[cite: 49, 51].

### 1.3 Success Criteria
[cite_start]Initial success is gated by passing automated Phase 1 checks: successful HuggingFace Space deployment, functional Docker execution, baseline script reproducibility, and three deterministic tasks[cite: 42, 45]. [cite_start]Scoring highly in Phase 2 depends on real-world utility (30%), task & grader quality (25%), environment design (20%), code quality/spec compliance (15%), and creativity/novelty (10%)[cite: 16, 17, 41].

---

## 2. RESOURCE MAP
[cite_start]*(Note: Per strict system parameters, external search capabilities are restricted. This map reflects only the provided technical brief[cite: 2].)*

### 2.1 Key Papers
*No academic papers were referenced in the provided project brief.*

### 2.2 Primary Libraries & Tools
| Library | Version | Purpose | CPU-Safe? | Actively maintained? |
| :--- | :--- | :--- | :--- | :--- |
| **Python** | 3.11 | [cite_start]Core logic / Graders [cite: 26, 49] | `[CPU-SAFE]` | `[VERIFIED]` |
| **FastAPI** | [UNVERIFIED] | [cite_start]OpenEnv API framework [cite: 50] | `[CPU-SAFE]` | `[VERIFIED]` |
| **Pydantic** | v2 | [cite_start]Data modeling/typing [cite: 51] | `[CPU-SAFE]` | `[VERIFIED]` |
| **Docker** | [UNVERIFIED] | [cite_start]Containerization (port 7860) [cite: 53] | `[CPU-SAFE]` | `[VERIFIED]` |
| **OpenAI API** | [UNVERIFIED] | [cite_start]Baseline inference client [cite: 55] | N/A (API) | `[VERIFIED]` |

### 2.3 Reference Repositories
*No external GitHub repositories were explicitly named for reference in the provided materials.*

### 2.4 Datasets
[cite_start]The environment relies on task episodes loaded from a dataset, though specific sizes, sources, and licenses were not detailed in the brief[cite: 20].

---

## 3. TECHNOLOGY LANDSCAPE
### 3.1 Current State of the Art
The current state of the art within the OpenEnv ecosystem rarely integrates code review and security auditing into a unified environment. [cite_start]Achieving this synthesis contributes directly to the project's novelty and creativity score (10%)[cite: 17, 41].

### 3.2 Technology Options Considered
[cite_start]Alternative technologies were not considered as the project brief strictly dictates the stack to ensure OpenEnv compliance: Python, FastAPI, Pydantic, Docker, and HuggingFace Spaces[cite: 4].

### 3.3 Recommended Stack
The stack must follow the prescribed architecture to pass Phase 1 validations:
* [cite_start]**Language & Data:** Python 3.11 with Pydantic v2[cite: 49, 51].
* [cite_start]**Framework:** FastAPI[cite: 50].
* [cite_start]**Infrastructure:** Docker (linux/amd64) deployed to HuggingFace Spaces[cite: 53, 54].

---

## 4. DOMAIN-SPECIFIC FINDINGS

### 4C.1 Threat Model Research
The security auditing evaluations (Task 2) focus specifically on identifying OWASP Top 10 vulnerabilities within web routes. [cite_start]Key targets include SQL injection, hardcoded secrets, and Cross-Site Scripting (XSS)[cite: 27].

### 4A.1 Model Architecture Options
[cite_start]To maintain system determinism, AI/LLM models must **not** be used in the grading architecture[cite: 46, 47]. [cite_start]The baseline evaluation of the environment itself utilizes an external OpenAI API client[cite: 55].

### 4A.3 Evaluation Metrics & Benchmarks
[cite_start]The reward function is specifically designed to provide meaningful gradient signals across the agent's full trajectory rather than relying on sparse end-of-episode rewards[cite: 29, 30].
* [cite_start]**Task 1 (Easy):** 0.0–1.0 score based on precision when identifying obvious bugs (null pointers, off-by-one errors)[cite: 27].
* [cite_start]**Task 2 (Medium):** Proportional reward per vulnerability found (e.g., ~0.33 for finding 1 of 3, 1.0 for all 3)[cite: 32].
* [cite_start]**Task 3 (Hard):** Uses a weighted composite score for multi-file PR diffs: bug detection (40%), security findings (40%), and review quality (20%)[cite: 37].
* [cite_start]**Penalties:** Minor deductions are applied for undesirable behaviors like low precision (flagging every line), empty outputs, or malformed actions[cite: 35].

---

## 5. RISK REGISTER
| Risk | Likelihood | Impact | Mitigation research found |
| :--- | :--- | :--- | :--- |
| **Grader Non-Determinism** | High | High | [cite_start]Strictly enforce pure Python logic (`[CPU-SAFE]`); never call an LLM for grading[cite: 26, 46, 47]. |
| **HF Space Deployment Fails** | Medium | High | [cite_start]Ensure Docker exposes correct port (7860) and includes all necessary startup files[cite: 45, 53]. |
| **`openenv validate` Fails** | Medium | High | [cite_start]Utilize strict Pydantic v2 typing, verify correct field names, and ensure `openenv.yaml` is valid[cite: 24, 45, 51]. |
| **Docker Build/Run Fails** | Medium | High | [cite_start]Test build/run locally before pushing; remove hardcoded local paths and ensure all dependencies are mapped[cite: 45, 64]. |
| **Baseline Script Fails** | Medium | High | [cite_start]Avoid absolute file paths and hardcoded keys; inject `OPENAI_API_KEY` dynamically via environment variables[cite: 45, 55]. |

---

## 6. PHASE-WISE RESEARCH
[cite_start]The required build sequence to successfully clear Phase 1 validations is explicitly delineated as follows[cite: 57, 58]:

1.  [cite_start]**Data Modeling:** Define Pydantic models and ensure `openenv validate` passes on day one[cite: 59].
2.  [cite_start]**API Skeleton:** Implement `reset()` and `state()` endpoints using static dummy data to confirm API initialization[cite: 60].
3.  [cite_start]**Task 1 Grader:** Construct the deterministic bug detection grader and verify input/output consistency[cite: 61].
4.  [cite_start]**Task 2 & 3 Graders:** Develop graders for vulnerabilities and PRs, ensuring proportional partial reward signals function correctly[cite: 62].
5.  [cite_start]**Baseline Script:** Author and test the baseline OpenAI inference script within a clean Python environment[cite: 63].
6.  [cite_start]**Containerization:** Execute `docker build` and `docker run` locally to confirm container integrity[cite: 64].
7.  [cite_start]**Deployment:** Push the image to HuggingFace Spaces, verifying the live URL responds to the validation spec[cite: 65].
8.  [cite_start]**Final Verification:** Execute the baseline script against the live HuggingFace Space to lock in README scores[cite: 66, 67].

---

## 7. OPEN QUESTIONS
1.  [cite_start]What specific datasets will be sourced and formatted to provide the raw "task episodes" (code snippets and PR diffs)? [cite: 20]
2.  [cite_start]What programmatic logic and metrics will precisely define the "review quality rubric" utilized in Task 3's composite scoring? [cite: 27]
3.  [cite_start]Who is responsible for provisioning the `OPENAI_API_KEY`, and how will it be securely injected into the environment for the baseline tests? [cite: 55]

---

## 8. GLOSSARY
* [cite_start]**OpenEnv:** An environment specification and API standard utilized for training and evaluating AI agents[cite: 7, 9].
* [cite_start]**Observation:** The state object returned by `reset()` or `step()`, containing the current code snippet and task instructions[cite: 20, 21].
* [cite_start]**Action:** The structured analysis output generated by the AI agent under evaluation[cite: 21].
* [cite_start]**Reward:** A float score between 0.0 and 1.0 reflecting the accuracy of the agent's action[cite: 11, 21].
* [cite_start]**Deterministic Grader:** A pure Python evaluation script that relies solely on programmed logic (no LLMs), guaranteeing identical inputs always yield identical scores[cite: 26, 47].

---

## 9. RESEARCH GAPS & CAVEATS
System constraints for this session explicitly disabled active web searches. [cite_start]As a result, this research document is synthesized strictly from the provided `scalar_hackathon_brief(1).docx`[cite: 2]. External dimensions requiring live searches—such as sourcing new academic papers, evaluating comparative state-of-the-art framework benchmarks, or linking active external GitHub reference repositories—could not be completed. All findings, stack verifications, and architectural parameters are rigidly bound to the facts detailed within the provided hackathon brief.

---
*Produced by Gemini Research Engine | Pass this file + claude_setup.md to Claude*