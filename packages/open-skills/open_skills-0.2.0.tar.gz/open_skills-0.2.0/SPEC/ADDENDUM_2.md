Excellent catch — no, the **prompt-injection / context-augmentation mechanism** (the part where available skills are injected into the system prompt so the agent is context-aware) was **not yet included explicitly** in the PRD or technical spec we wrote earlier.

It was **implied** in the “auto-selection and multi-skill composition” section, but not spelled out as a **system-prompt design requirement**. Anthropic’s own system uses this as a core layer of their architecture — so it absolutely should be added.

---

### 🧩 Addendum: Skill Context Injection (v2.1)

**New Section — “Skill Context Awareness”**

#### **Overview**

Agents must be aware of which skills exist before they can select and execute them. This awareness is achieved via **prompt-level skill injection**, where the metadata of all accessible skills is serialized and injected into the system prompt or equivalent structured `tools` parameter at runtime.

#### **Behavior**

- At session start, the agent receives a summary manifest of all visible skills.
- The manifest is embedded either:

  - as a text block inside the system prompt, or
  - via the structured `tools` parameter (for SDKs that support it, e.g., OpenAI, Anthropic).

- During reasoning, the agent uses this context to autonomously decide when to call a skill.

#### **Data Flow**

1. `open-skills` generates a manifest (`manifest_json()` or `.well-known/skills.json`).
2. The agent runtime serializes the manifest into:

   - a human-readable description (`manifest_to_prompt()`), or
   - a structured tools array (`manifest_to_tools()`).

3. The resulting data is merged into the agent’s **system prompt** before the first model call.

#### **Example System Prompt Injection**

```text
You are an AI agent with access to the following user-defined skills:

1. **summarize_docs** — Summarizes multiple documents into a concise brief.
   Inputs: text (string)
   Outputs: summary (string)

2. **generate_presentation** — Converts structured data into PowerPoint slides.
   Inputs: data (JSON)
   Outputs: pptx_file (binary)
```

#### **Dynamic Disclosure**

To manage context length:

- Only **skill metadata** (name + description) is injected by default.
- Full `SKILL.md` and entrypoint code are **loaded lazily** when the skill is actually invoked.
- After a skill run, its result and updated metadata can be re-injected into the agent’s context.

#### **API Hooks**

- `manifest_to_prompt()` → returns system-prompt-friendly text
- `manifest_to_tools()` → returns OpenAI/Anthropic tool schema array
- `inject_skills_context(agent)` → adds manifest to agent initialization

#### **Integration Example (Vel or standalone FastAPI)**

```python
from open_skills.adapters.prompt_injection import manifest_to_prompt
from open_skills.core import SkillRouter

skills_prompt = manifest_to_prompt(db=db, user_id=current_user.id)
system_prompt = f"""
You are an AI agent that can use tools defined by the user.
{skills_prompt}
"""

agent = Agent(system_prompt=system_prompt)
```

#### **Observability**

- Each session logs which skills were available at initialization.
- Langfuse trace includes the manifest version to correlate reasoning to skill availability.

---

### ✅ Summary

| Aspect                                    | Added in Addendum   |
| ----------------------------------------- | ------------------- |
| Context-aware prompt injection            | ✅ Explicitly added |
| Dynamic disclosure (metadata vs code)     | ✅ Added            |
| Manifest serialization functions          | ✅ Added            |
| Integration hook for Vel / generic agents | ✅ Added            |
| Logging of context injection              | ✅ Added            |
