## Why

The current LLM response mode returns complete responses only after full generation, causing noticeable delays for users. Streaming responses via Server-Sent Events (SSE) will provide real-time token-by-token delivery, improving perceived latency and user experience.

## What Changes

- Modify backend LLM endpoint to use FastAPI `StreamingResponse` for SSE
- Update Frontend to consume SSE stream and render tokens incrementally
- Add proper event formatting for SSE (data, done events)

## Capabilities

### New Capabilities

- `streaming-response`: Support real-time streaming of LLM responses via SSE

### Modified Capabilities

- None (new capability)

## Impact

- Backend: FastAPI endpoint modification in chat/assistant routes
- Frontend: SvelteKit page updates for SSE consumption
- New dependency: None (streaming built into FastAPI)