# SUBAGENT EXECUTION RULES & PROTOCOL

Every subagent spawned for the **ShopQ** project MUST strictly adhere to the following rules:

## 1. Zero Token Waste Rule
- **DO NOT** perform a full repository audit or listing.
- **DO NOT** recursively search directories or run global grep across the project.
- **DO NOT** rediscover existing routes, components, data schemas, or architecture already documented in `SHOPQ_CONTEXT.md`.
- Read `SHOPQ_CONTEXT.md` first to obtain the single source of truth.

## 2. Strict File Ownership & Boundaries
- Only edit files explicitly assigned to your subagent role.
- Inspect direct dependencies **only** when strictly required to complete your assigned task.
- Do NOT open or edit files outside your explicit ownership scope.
- Do NOT alter API contracts, database schemas, or frontend UI components unless assigned to your role.

## 3. Action-Oriented Implementation
- Subagents are **IMPLEMENTERS**, not researchers.
- Workflow: **EDIT ➡️ RUN FOCUSED TEST ➡️ VERIFY ➡️ REPORT CONCISELY**.
- Do NOT write lengthy analysis essays or re-explain the architecture.
- Expected subagent output format:
  ```
  - Task completed
  - Files modified
  - Verification performed (build/test status)
  - Errors or unresolved issues (if any)
  ```

## 4. Focused Verification Only
- Run only tests relevant to your changes (e.g. `npm run build` or single unit test).
- Do NOT run redundant global test loops after every minor edit.
- Report exact build status and error counts to the main orchestrator.
