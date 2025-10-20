Below is the **comprehensive Product Requirements Document (PRD)** for **`open-skills`**, a modular, Anthropic-style Skills subsystem designed for integration with **Vel** or any agent framework.

---

# 🧩 PRD — `open-skills`

## 1. Overview

### **Purpose**

`open-skills` is a standalone Python package that replicates **Anthropic’s Skills** feature — a system that allows agents (LLMs) to dynamically invoke **user-defined, versioned code bundles** to perform complex operations like data processing, file generation, or transformation.

### **Vision**

Skills encapsulate reusable, composable logic — _“folders of capability”_ — that an agent can automatically discover, select, and execute based on user intent.
This project creates an open, self-hosted, and framework-agnostic implementation that can plug into Vel (or any agent runtime) via a clean interface.

---

## 2. Goals & Non-Goals

### ✅ **Goals**

- Provide **exact parity** with Anthropic’s Skills model:

  - Skills as versioned folder bundles with instructions, scripts, and resources.
  - Auto-selection and multi-skill composition.
  - File artifact generation and retrieval.
  - Versioning, publishing, and lifecycle management.

- Ship as a **separate package (`open-skills`)**.
- Provide a **REST API** and **Python/TS SDKs**.
- Include a **web console** (React app) for authoring, publishing, and viewing runs.
- Integrate **Langfuse telemetry** and structured logging.
- Be deployable as a **Kubernetes service** with an optional standalone dev server (`uvicorn main.py`).

### 🚫 **Non-Goals**

- No runtime dependency installations (skills use global environment).
- No heavy isolation (no per-run containers).
- No billing, rate-limiting, or advanced governance (stub hooks only).

---

## 3. Architecture Overview

### **High-Level Components**

```
User / Agent
   │
   ▼
[open-skills API]  ←→  [Postgres]  ←→  [Langfuse]
   │
   ▼
[Skill Executor Runtime (Python)]
   │
   ▼
[Local FS] ←→ [S3 Artifacts]
```

### **Execution Model**

- The **runtime is persistent** — a long-running Python service inside a Kubernetes pod.
- Skills execute via dynamically loaded Python modules inside the same process (sandboxed by code boundaries and resource limits, not containers).
- Each invocation runs within a limited async task context with timeouts and optional signal-based kill protection.

### **Primary Modules**

1. **Skill Manager** – CRUD, versioning, discovery, metadata, embeddings.
2. **Skill Executor** – loads and runs skill code safely; handles I/O and artifacts.
3. **Skill Router** – matches tasks/LLM requests to skills based on metadata and embeddings.
4. **API Layer** – FastAPI router exposing REST endpoints.
5. **Web Console** – minimal React frontend for management.
6. **Telemetry** – Langfuse + structured logging.

---

## 4. Data Model

### **Core Tables**

| Table                 | Key Fields                                                                                                                      | Description                   |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| **skills**            | `id`, `name`, `owner_id`, `org_id`, `visibility` (`user`/`org`), `created_at`                                                   | Top-level skill record.       |
| **skill_versions**    | `id`, `skill_id`, `version`, `metadata_yaml`, `description`, `entrypoint`, `embedding`, `created_at`                            | Each immutable skill version. |
| **skill_runs**        | `id`, `skill_version_id`, `user_id`, `input_json`, `output_json`, `artifact_url`, `status`, `duration_ms`, `logs`, `created_at` | Execution history.            |
| **skill_artifacts**   | `id`, `run_id`, `s3_url`, `mime_type`, `checksum`, `size_bytes`, `created_at`                                                   | File artifacts.               |
| **skill_permissions** | `id`, `user_id`, `org_id`, `role` (`viewer`/`author`/`publisher`/`admin`)                                                       | RBAC.                         |

### **Encryption**

- Sensitive fields (secrets/env vars) encrypted via JWT-signed key.
- Stored encrypted in Postgres (no plaintext persisted).

---

## 5. Skill Bundle Format

### Folder Layout

```
my-skill/
├── SKILL.md          # Metadata (YAML frontmatter + Markdown)
├── scripts/
│   └── main.py       # Entrypoint (Python function)
├── resources/
│   └── template.pptx
└── tests/
    └── sample_input.json
```

### `SKILL.md` Example

```markdown
---
name: excel_to_pptx
version: 1.0.0
entrypoint: scripts/main.py
description: Converts Excel data into a PowerPoint summary.
inputs:
  - type: file
    mime: application/vnd.ms-excel
outputs:
  - type: file
    mime: application/vnd.ms-powerpoint
tags: [excel, pptx, summarize]
allow_network: true
---

This skill generates a PowerPoint presentation from an Excel dataset.
```

---

## 6. Skill Execution Lifecycle

| Step                        | Description                                         |
| --------------------------- | --------------------------------------------------- |
| 1. Agent selects skill(s)   | Based on metadata/embeddings and context.           |
| 2. API receives run request | `POST /runs` with skill id/version + input payload. |
| 3. Executor loads skill     | Reads from local FS or DB cache.                    |
| 4. Code execution           | Python async run with timeouts; logs captured.      |
| 5. Artifacts stored         | Writes to `/tmp` → uploads to S3 (stubbed).         |
| 6. Output streamed          | Logs + artifacts returned to caller.                |
| 7. Telemetry                | Langfuse trace emitted with run metadata.           |

---

## 7. REST API

### **Skills**

```
GET    /skills
POST   /skills
GET    /skills/{id}
PATCH  /skills/{id}
DELETE /skills/{id}
```

### **Skill Versions**

```
POST   /skills/{id}/versions       # Upload bundle
GET    /skills/{id}/versions
GET    /skill-versions/{id}
POST   /skill-versions/{id}/publish
```

### **Runs**

```
POST   /runs                       # Execute skill
GET    /runs/{id}
GET    /skills/{id}/runs
```

### **Artifacts**

```
GET    /artifacts/{id}
```

### **Search & Routing**

```
POST   /skills/search               # Embedding-based or tag-based
```

---

## 8. Skill Routing & Auto-Selection

- **Embedding model**: `text-embedding-3-large` (OpenAI).
- **Storage**: embeddings stored in Postgres as vector column (pgvector).
- **Selection pipeline**:

  1. Generate embedding from user query or agent thought.
  2. Search top-K skill embeddings.
  3. Filter by tags + I/O type.
  4. Agent receives summarized metadata (`name`, `desc`, `inputs`, `outputs`) for contextual reasoning.
  5. If selected, full skill details fetched (“progressive disclosure”).

- Supports **multi-skill composition**:

  - `skill_call` → `skill_call` chaining or parallel execution.

---

## 9. Integration with Vel

### **Integration Points**

| Vel Layer       | Hook                                    | `open-skills` Equivalent                              |
| --------------- | --------------------------------------- | ----------------------------------------------------- |
| Agent Runtime   | Tool call dispatch                      | `SkillRouter.route_call()`                            |
| Event Stream    | `file` / `appGeneration`                | `SkillExecutor.emit_artifact_event()`                 |
| API Composition | FastAPI include                         | `from open_skills.api import router as skills_router` |
| Config          | `.env` variables for embeddings, DB, S3 | Shared via Vel settings loader                        |

### **Usage Example**

```python
from open_skills import SkillRouter, SkillExecutor
from vel.agent import AgentRuntime

skills = SkillRouter(executor=SkillExecutor())
agent = AgentRuntime(skills=skills)
```

---

## 10. Web Console

### **Stack**

- React + Vite
- Axios REST client
- React Query for data fetching
- Tailwind UI (minimal)
- Deployed standalone (optional)

### **Views**

- **Dashboard:** Skill list + stats
- **Skill Editor:** Upload bundles, edit metadata
- **Runs:** Execution logs + artifacts
- **Users:** RBAC management

---

## 11. Observability

- **Langfuse:** Track `run_id`, latency, input/output metrics, agent context.
- **Structured Logs:** JSON to stdout; logs per run (INFO, ERROR).
- **Metrics (stub):**

  - Runs per hour
  - Average latency
  - Success/failure rate
  - File artifact counts

---

## 12. Security & Guardrails (Stubbed)

- Network policy enforcement placeholder.
- Basic validation on Python imports (disallow system or unsafe modules).
- Input/output size limits.
- JWT-encrypted secrets injection.
- Audit trail of run invocations.

---

## 13. Deployment

### **Runtime**

- K8s Deployment (replicas configurable).
- Environment:

  - `POSTGRES_URL`
  - `LANGFUSE_API_KEY`
  - `OPENAI_API_KEY`
  - `JWT_SECRET`
  - `S3_ENDPOINT`, `S3_BUCKET`

- Exposed via `uvicorn main:app --host 0.0.0.0 --port 8000`

### **Dev Mode**

- Local FastAPI + SQLite.
- `python main.py`
- `npm run dev` (for React console).

---

## 14. Future Extensions

| Feature             | Description                                      |
| ------------------- | ------------------------------------------------ |
| Per-run OCI sandbox | True containerized isolation for untrusted code. |
| Dependency graph    | Skill composition visualization.                 |
| Eval suite          | Automated test validation before publish.        |
| Org marketplace     | Skill sharing within or across orgs.             |
| Skill packaging     | `open-skills pack/unpack` CLI commands.          |
| CLI Auth            | JWT auth flow for CLI users.                     |

---

## 15. Success Metrics

- ⏱️ Skill invocation latency < 2s (median)
- 📈 ≥ 90% successful executions
- 🔄 End-to-end skill author → publish → run lifecycle functional in < 3 steps
- 🧠 Embedding-based auto-selection accuracy ≥ 80% on validation queries
- 🔍 Full compatibility with Vel’s tool stream protocol
