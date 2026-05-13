# Never-Forget Memory Archival System

## 🌟 Overview
This system is designed to automatically capture, structure, and permanently archive conversational and system metadata (chats, logs, alerts) into a centralized, durable memory bank (`Project_Never_Forget_Core.md`). It elevates simple logging into actionable knowledge management by semantically analyzing inputs.

## 🎯 Core Functionality
The system operates in a three-stage, automated pipeline:
1.  **Input Buffer:** Ingests raw metadata from chat channels or system sources.
2.  **Extraction Engine:** Uses LLM synthesis combined with external search tools (`total-recall-search`) to identify specific types of knowledge: **Facts**, **Decisions**, **Learnings**, and **Actionable Tasks**.
3.  **Commit Handler:** Ensures data integrity by atomically appending structured Markdown blocks to the core memory file.

## 🛠️ Execution Workflow
The entire process is orchestrated by the `run_memory_pipeline.py` script, which manages the necessary virtual environment and sequential execution:
1.  `run_memory_pipeline.py` is executed (Ideally via `source never_forget_venv/bin/activate && python3 never_forget/run_memory_pipeline.py`).
2.  The process logs its steps, ensuring visibility into the internal logic.

## 🚀 Technical Dependencies
*   **Python Runtime:** Requires Python 3.14+ and an isolated virtual environment (`never_forget_venv`).
*   **Key Modules:** `extraction_engine.py`, `commit_handler.py`, `total_recall_search.py`.

## 💾 Core Artifacts
*   `Project_Never_Forget_Core.md`: The master, append-only record of all archived memory.
*   `NEVER_FORGET_ARCH_DESIGN.md`: The complete technical blueprint for the system.

## 🚧 Maintenance & Debugging
*   **Failure Mode:** The most common point of failure is the Python environment pathing. Always attempt to run the pipeline using the fully activated virtual environment context.
*   **Troubleshooting:** If the commit fails, check for `JSONDecodeError` (Extraction issue) or `Permission Denied` (Commit Handler issue).

---
**Last Run Status:** Successfully archived memory chunk from `telegram:8755120444` (19:02 EDT).
---
