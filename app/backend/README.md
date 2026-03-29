# Backend Runtime Notes

## Responses API store

- `XINQUE_RESPONSES_STORE=true` by default. In this mode, XinQue allows the Responses API to persist conversation-chain state on the model provider side so `previous_response_id` can continue a multi-turn thread.
- If you set `XINQUE_RESPONSES_STORE=false` (also accepts `0`, `off`, `no`), the backend will send `store=false` to Responses and fall back to a stateless request path.
  - The backend will not send `previous_response_id`.
  - The backend will keep `instructions` on each request.
  - Cross-turn continuity falls back to local history replay plus XinQue's own `working_context`.
  - Current-turn tool loops continue by locally appending `function_call_output` items.

## Current summary input shape

- `_generate_summary` currently sends a plain transcript string as `input` to Responses and keeps a local fallback summary path if the LLM call fails. This behavior is the current implementation baseline for the Azure Responses deployment used by the project.
