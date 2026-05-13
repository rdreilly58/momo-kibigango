# ⚙️ Never-Forget Implementation Plan: Obsidian Integration Protocol

**Objective:** To formalize and enforce the use of Obsidian as the single source of truth (SSOT) for the "never-forget" project, ensuring all project work is captured with structured, retrievable metadata.

**Status:** Defined. Next Step: Implementation Phase.

## 📑 Phase 0: Protocol Definition (Completed)
*   **Mandate:** Use Obsidian/Markdown as the SSOT.
*   **Core Structure:** All project notes must begin with a Mandatory YAML Front Matter block.
*   **Workflow:** Adopt the 3-step process (Initialize $\rightarrow$ Work/Log $\rightarrow$ Conclude).

---

## 🚀 Phase 1: Structural Enforcement (High Priority)

**Goal:** Define and enforce the rules for structured note creation.

**Task 1.1: Defining the YAML Schema**
*   **Action:** Formalize the precise definition of the mandatory front matter fields.
    *   `project_id`: (Integer) Unique identifier for the project.
    *   `project_name`: (String) Human-readable project name.
    *   `project_goal`: (String) Single sentence summary of the ultimate objective.
    *   `priority`: (Enum: High/Medium/Low) Current criticality.
    *   `canonical_tags`: (Array of Strings) Standardized tags (e.g., ["memory-system", "v1"]).
    *   `last_action_required`: (String) The single, immediate, next action item (most critical field).
*   **Deliverable:** A formal `YAML_SCHEMA.md` file defining these fields and validating rules.

**Task 1.2: Developing the `obsidian-writeback` Tool/Script**
*   **Action:** Create a dedicated internal handler or sub-agent script (e.g., `obsidian-writeback.py`).
*   **Functionality:** This script must be called during note creation/modification and must validate that the YAML front matter is present and follows the defined schema before saving.
*   **Dependencies:** Requires access to the Obsidian CLI (`obsidian-cli`) and Python environment.

## 🛠️ Phase 2: Workflow Implementation (Medium Priority)

**Goal:** Update the standard operating procedure (SOP) to use the new protocol in practice.

**Task 2.1: Initialize (Mandatory Step)**
*   **Trigger:** Starting a new project or a major phase change.
*   **Protocol:** Use the `obsidian-writeback` tool to create the initial note with the full YAML structure and set the initial `last_action_required`.
*   **Review:** Update the `never-forget/README.md` with this formalized step.

**Task 2.2: Work/Log (Continuous Step)**
*   **Trigger:** Throughout the work session (e.g., writing a technical design, documenting a decision).
*   **Protocol:** Key outputs must be appended to the active Obsidian note, using markdown headings and clear time/date stamps.
*   **Tooling:** Use the standard `write` tool against the current note path.

**Task 2.3: Conclude (Mandatory Step)**
*   **Trigger:** Ending a session/work block.
*   **Protocol (Triple Write):**
    1.  **Session Flush:** Call standard `SESSION_CONTEXT.md` flush (for real-time chat state).
    2.  **Long-Term Log:** Call `obsidian-writeback` to append a structured "Session Summary" block (including milestones, decisions, and the final state).
    3.  **Memory Write:** Update `MEMORY.md` with a summary of the session's outcome.

## ✅ Go-Forward Action Items
1.  **Priority:** Tackle **Phase 1, Task 1.1** by drafting the canonical `YAML_SCHEMA.md`.
2.  **Next Meeting:** Review the drafted `YAML_SCHEMA.md` and define the inputs/outputs for the `obsidian-writeback` tool.