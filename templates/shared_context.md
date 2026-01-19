# Shared Context вЂ” [Track ID]

**Last Updated:** [YYYY-MM-DD HH:MM]

This file serves as a shared knowledge base for all subagents in the track. 
It captures discovered patterns, open questions, and architectural decisions that affect multiple tasks.

---

## рџ”Ќ Discovered Patterns

*Patterns or conventions discovered during exploration that should be followed by others.*

### [Pattern Name, e.g., "Error Handling"]
- **Description:** [Description of the pattern]
- **Example:** `try: ... except AppError: ...`
- **Discovered by:** [Task ID]

---

## рџ¤ќ Shared Decisions (Agreements)

*Decisions made by one agent that others must respect.*

### [Decision Name, e.g., "API Versioning"]
- **Decision:** Use `/api/v1` prefix
- **Rationale:** Backward compatibility
- **Made by:** [Task ID]

---

## вќ“ Open Questions (Collaborative)

*Questions that need input from other agents or the user.*

### Q: [Question]
- **Context:** [Context]
- **Asked by:** [Task ID]
- **Responses:**
  - [Task ID]: [Response]

---

## рџ“¦ Global Constants & Config

*Shared configuration values found or established.*

- `MAX_RETRIES`: 3
- `API_TIMEOUT`: 30s
