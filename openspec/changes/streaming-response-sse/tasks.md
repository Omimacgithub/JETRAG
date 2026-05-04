## 1. Backend SSE Streaming Implementation

- [ ] 1.1 Modify assistant chat endpoint to support streaming mode (accept stream parameter)
- [ ] 1.2 Create async generator function to yield LLM response chunks and store the full chunk list on database
- [ ] 1.3 Implement SSE formatter utility (data prefix, line formatting)
- [ ] 1.4 Return StreamingResponse with media_type text/event-stream
- [ ] 1.5 Add [DONE] event on completion

## 2. Frontend SSE Consumer Implementation

- [ ] 2.1 Update frontend chat component to detect streaming response
- [ ] 2.2 Implement fetch with ReadableStream for SSE consumption
- [ ] 2.3 Add chunk parsing logic to extract data from SSE events
- [ ] 2.4 Update UI to append chunks incrementally without full re-render
- [ ] 2.5 Handle [DONE] event to show completion state
- [ ] 2.6 Store full LLM response on JavaScript localStorage object

## 3. Testing & Integration

- [ ] 3.1 Test SSE streaming with curl to verify event format
- [ ] 3.2 Test frontend incremental rendering
- [ ] 3.3 Test connection interruption and reconnection
- [ ] 3.4 Verify backward compatibility (non-streaming fallback)