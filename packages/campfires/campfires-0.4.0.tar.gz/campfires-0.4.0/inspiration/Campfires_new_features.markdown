# Campfires Framework Specification Update: New Features

This document outlines the new features and updates to the Campfires framework specification, building on the core architecture. These additions focus on task decomposition, dynamic role generation, orchestration topologies, configuration via manifest folders, default auditors, and context paths. Provide this to your AI-powered IDE for implementation, ensuring integration with existing components like Campfire, Camper, Torchbearer, Torch, Party Box, MCP, and Zeitgeist.

## New Functional Requirements

### 8. Role-Aware Campfire Orchestration
This module enables dynamic decomposition of tasks into subtasks, generation of role-specific RAG documents, and sequenced execution with auditing.

- **Decomposer Campfire**:
  - Dedicated campfire with a single camper: `TaskPlanner`.
  - Input: High-level task description (e.g., "Build a secure accountancy web app").
  - Process: Uses an LLM (via OpenRouter or similar) augmented with RAG sources on common workflows, team structures, and domain-specific breakdowns (e.g., software development pipelines).
  - Output:
    - List of subtasks (e.g., ["design backend", "audit backend", "design frontend", "audit frontend"]).
    - For each subtask: List of role specifications as dictionaries (e.g., `[{name: 'Backend Dev', focus: 'API design, FastAPI, security'}, {name: 'Auditor', focus: 'validation, errors, logs'}]`).
  - RAG Sources: Pre-defined library templates for task decomposition, plus optional Zeitgeist queries for current trends (e.g., "best practices for web app task breakdown 2025").

- **Campfire Factory**:
  - Utility to automatically instantiate one `Campfire` per subtask from Decomposer output.
  - For each role in a subtask:
    - Create a `Camper` instance with `role=name`, `focus=focus`.
    - Generate and assign RAG document (see RAG Generation Pipeline below).
    - If role includes `auditor: true` (or default), mark camper as auditor (`is_auditor=True`), enabling it to gatekeep torch publication.
  - Integrates with Party Orchestrator for topology-aware wiring.

- **Execution Flow**:
  - Begins with Decomposer Campfire.
  - Each campfire processes its subtask:
    - Campers collaborate via internal torches or shared context.
    - Auditor camper (if present) reviews final output in Party Box.
    - If verified: Publish torch with `{'claim': 'subtask complete', 'path': './party_box/output.json', 'verified': true}`.
    - If failed: Publish torch with `{'claim': 'failed', 'reason': 'specific issue'}` and loop back to the same campfire for refinement.
  - Flow controlled by Party Orchestrator topology (e.g., sequential waits for previous torch).

- **RAG Generation Pipeline**:
  - For each role:
    - Start with base template from library (e.g., `roles/backend.yaml` containing prompt structures and static knowledge).
    - Augment with dynamic sources:
      - Zeitgeist queries (e.g., `Zeitgeist.get_trends(f"{role} best practices 2025")`).
      - Embed task-specific variables (e.g., `{subtask: 'design backend'}` → "You are a backend dev designing APIs for an accountancy app...").
      - Optional web/X searches for role-specific opinions or tools.
    - Output: JSON/YAML RAG document stored in Party Box (e.g., `rag_backend.json`).
    - Loaded automatically when campfire starts: `camper.load_rag('rag_{role}.json')`.

- **Torch Rules**:
  - Publication restricted to Auditor camper (if present).
  - Channel naming: `step:{subtask_id}` (e.g., `step:backend_design`).
  - Listening: Next campfire subscribes to `step:{previous_subtask_id}`—activates only on receipt of verified torch.
  - Error Handling: Unverified torches trigger retries or user notifications.

### 9. Party Orchestrator Topologies
- **Class**: `PartyOrchestrator` – Central manager for all campfires, handling task decomposition, execution, and topology.
- **Initialization**:
  - `PartyOrchestrator(task: str, topology: str = 'sequential')`.
  - Triggers Decomposer to generate subtasks and roles.
  - Builds campfires via Campfire Factory.
- **Supported Topologies**:
  - **Sequential**: Linear execution—each campfire waits for the previous one's verified torch before starting.
    - Use Case: Pipelines like design → code → test → deploy.
    - Implementation: Simple queue of channels; blocks on MCP receive.
  - **Parallel**: Concurrent execution of independent subtasks, with a `MergeFire` campfire for reconciliation.
    - Use Case: Design backend and frontend simultaneously.
    - Implementation: Fork branches (e.g., `branches = [Branch(campfires=[...]), Branch(campfires=[...])]`); `MergeFire` waits for all torches, resolves conflicts (e.g., API/UI mismatches), then proceeds.
  - **Mesh**: Free-form network—all campfires receive initial torch and respond based on relevance.
    - Use Case: Brainstorming or creative ideation.
    - Implementation: Broadcast initial torch; campers self-filter (e.g., via RAG: "Respond only if this matches your focus"); no strict order, convergence via vote or summary in Party Box.
- **Methods**:
  - `run()`: Executes the full workflow, monitors Party Box for completion.
  - `from_folder(path: str)`: Loads from Manifest Folder (see below).

### 10. Manifest Folder Loading
- **Structure**: A physical folder (e.g., `./my-task`) for configuration.
  - `manifest.yaml`: Top-level config.
    - Keys: `task` (str), `topology` (str: 'sequential'|'parallel'|'mesh'), `channel_root` (str), `rules` (dict: e.g., `auto_audit: true`, `rag_pull: 'zeitgeist + local'`, `timeout: 60s`), `folders` (dict: `roles: './roles'`, `assets: './assets'`).
  - `roles/`: Sub-directory with YAML files per camper (e.g., `backend-dev.yaml`).
    - Each file: `role` (str), `prompt_template` (str), `rag_sources` (list: paths, URLs, 'zeitgeist:query'), `channel_in` (str), `channel_out` (str), `auditor: true/false`.
    - Example: `roles/backend-dev.yaml` – "You are a {role} focused on {focus}. Use {tech_stack}."
  - `assets/`: Sub-directory for initial assets (e.g., images, data files)—auto-loaded into Party Box on start.
- **Loading**: `PartyOrchestrator.from_folder('./my-task')` parses YAMLs, builds campfires/campers dynamically, assigns RAGs, wires channels.
- **Defaults**:
  - If `audit` key omitted: `true` (auto-adds Auditor camper using `roles/auditor.yaml` or default template).
  - If `context_path` omitted: Auto-uses `./contexts/{campfire_name}` (see Context Path Support).
  - If `roles:` is empty: Still adds auditor if `audit: true`.
- **Extensibility**: Supports YAML includes (`!include path`) for reusable sections.

### 11. Default Auditor Integration
- **Behavior**: Automatically includes an Auditor camper in every campfire unless explicitly disabled.
- **Configuration**:
  - Default: `audit: true` in `manifest.yaml` or per campfire—triggers Auditor creation.
  - Override: Set `audit: false` to skip Auditor (e.g., for brainstorming campfires where output validation is irrelevant).
- **Auditor Camper**:
  - Loaded with RAG from `roles/auditor.yaml` or default template (e.g., "Review output: {claim}. Check against: {criteria}. Pass?").
  - Criteria examples: API returns 200, no console errors, load time < 2s.
  - Only publishes torch after verification (e.g., `{'verified': true}`) or flags failure with reason.
- **Implementation**: 
  - `CampfireFactory` checks `audit` flag; if true, appends `Auditor` camper with `is_auditor=True`.
  - Integrates with Torch Rules—non-auditor campers cannot publish.

### 12. Context Path Support
- **Configuration**: Each campfire can define a `context_path` in `manifest.yaml` (e.g., `context_path: ./contexts/backend`).
- **Behavior**:
  - Loads `.json`, `.yaml`, `.md` files from the specified path as initial RAG context for all campers in that campfire.
  - Example: `./contexts/backend/` might contain `api_specs.md` and `security_checklist.yaml`.
- **Default**: If `context_path` omitted, auto-uses `./contexts/{campfire_name}`—creates if non-existent, loads if files present.
- **Use Case**: Scoped RAG ensures campers start with task-specific knowledge (e.g., backend campers get API docs, frontend get UI patterns).
- **Integration**: Context loaded via `camper.load_rag(context_path)` before task execution.

## Implementation Notes
- Ensure `PartyOrchestrator` handles topology-specific channel wiring (e.g., sequential queues, parallel forks, mesh broadcasts).
- Validate YAML parsing with PyYAML, handling includes and defaults gracefully.
- Extend `Campfire` to auto-inject Auditor camper with `is_auditor=True` logic.
- Test context_path loading with empty/default paths to avoid runtime errors.
- Leverage existing MCP and Party Box APIs for torch and asset management.

## Example Workflow
- **Task**: "Build a secure accountancy dashboard."
- **Manifest Folder**: `./accountancy-dashboard/`
  - `manifest.yaml`: `task: Build a secure accountancy dashboard, topology: sequential, folders: {roles: ./roles, assets: ./assets}`
  - `roles/backend-dev.yaml`: `role: Backend Dev, prompt_template: Design API for {subtask}, rag_sources: [./docs/api-best-practices.md, zeitgeist:backend trends 2025], channel_out: step:backend`
  - `roles/auditor.yaml`: `role: Auditor, prompt_template: Review output: {claim}. Check: API 200, no errors, channel_out: step:verified`
  - `assets/example_data.json`: Sample accounting data.
- **Execution**:
  - `PartyOrchestrator.from_folder('./accountancy-dashboard').run()`
  - Decomposer splits into `design backend` → `audit backend` → ...
  - Each campfire loads its context (e.g., `./contexts/backend_design/`), runs, and passes torch only after audit.

## Next Steps
- Implement `PartyOrchestrator` with topology logic.
- Develop `from_folder()` method with YAML parsing and default handling.
- Test with a multi-campfire sequential workflow, verifying auditor gates and context loading.
