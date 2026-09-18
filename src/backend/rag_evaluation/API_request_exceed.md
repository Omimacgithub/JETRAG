================================================================================
RAG EVALUATION PIPELINE - API REQUEST LIMIT EXCEED ANALYSIS
================================================================================

Context:
--------
The RAG evaluation pipeline (run_experiment.py, lines 151-153) frequently hits
OpenAI-compatible API rate limits (5000 requests/minute on most Qwen models).
This document identifies the 5 most common causes and provides recommendations.

================================================================================
CAUSE 1: RAGAS @experiment() Decorator - Unbounded Parallel Execution
================================================================================

Location: eval.py:40-41, RAGAS experiment.py:170-180

Problem:
The @experiment() decorator creates ALL async tasks simultaneously for the 
entire dataset and runs them with asyncio.as_completed() without any 
concurrency limit:

    tasks = []
    for item in dataset:
        tasks.append(self(item, *args, **kwargs))  # All tasks created at once
    
    for future in asyncio.as_completed(tasks):  # All run in parallel
        result = await future

With 65 rows in the dataset, this means 65 concurrent evaluation tasks 
start immediately, each making multiple LLM API calls.

Recommendation:
- Implement asyncio.Semaphore to limit concurrent tasks (e.g., max 5-10)
- Process dataset rows in controlled batches instead of all at once
- Consider using asyncio.gather() with explicit concurrency limits

Example fix:
    semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent tasks
    async def limited_task(item, *args, **kwargs):
        async with semaphore:
            return await self(item, *args, **kwargs)
    
    tasks = [limited_task(item, *args, **kwargs) for item in dataset]

================================================================================
CAUSE 2: Multiple LLM Calls Per Evaluation Row
================================================================================

Location: eval.py:84-98

Problem:
Each dataset row triggers AT LEAST 2 LLM API calls:
  - Call 1: RAG query via process_rag_query() or chat API (line 84-86)
  - Call 2: Correctness evaluation via correctness_metric.ascore() (line 93-98)

With 65 rows, this results in:
  65 rows × 2 LLM calls = 130 LLM API calls

All these calls are fired in rapid succession when running in parallel, 
easily exceeding the 5000 requests/minute limit.

Recommendation:
- Implement rate limiting between the two LLM calls per row
- Add small delays (asyncio.sleep) between RAG query and evaluation
- Consider caching RAG responses to avoid redundant queries during re-runs
- If possible, batch the correctness evaluations separately

================================================================================
CAUSE 3: No Rate Limiting or Concurrency Control
================================================================================

Location: run_experiment.py:151-153, eval.py:40-123

Problem:
The evaluation pipeline lacks all forms of rate control:
  - No semaphores to limit concurrent async tasks
  - No rate limiters to throttle API requests per minute
  - No batching to process rows in controlled chunks
  - No delays between requests to spread load over time

All async operations run as fast as possible without respecting the 
5000 requests/minute limit configured on Qwen models.

Recommendation:
- Implement a token bucket or sliding window rate limiter
- Use asyncio.Semaphore with a reasonable limit (5-10 concurrent tasks)
- Add asyncio.sleep() delays between batches (e.g., 1-2 seconds)
- Process dataset in chunks of 10-20 rows with pauses between chunks

Example implementation:
    import asyncio
    from datetime import datetime
    
    class RateLimiter:
        def __init__(self, max_requests: int, period: float):
            self.max_requests = max_requests
            self.period = period
            self.requests = []
        
        async def acquire(self):
            now = datetime.now().timestamp()
            self.requests = [t for t in self.requests if now - t < self.period]
            
            if len(self.requests) >= self.max_requests:
                sleep_time = self.period - (now - self.requests[0])
                await asyncio.sleep(sleep_time)
            
            self.requests.append(now)

================================================================================
CAUSE 4: AsyncOpenAI Client with Minimal Configuration
================================================================================

Location: run_experiment.py:34-35

Problem:
The AsyncOpenAI client is created with minimal configuration:

    client = AsyncOpenAI(
        base_url="http://localhost:8080", 
        api_key=config.OPENAI_API_KEY, 
        default_headers={"X-DashScope-Async": "disable"}
    )

Missing critical configurations:
  - No max_retries for handling rate limit responses (429 status)
  - No timeout configurations for long-running requests
  - No rate limit headers parsing (e.g., X-RateLimit-Remaining)
  - No exponential backoff strategies for 429 responses

Recommendation:
- Configure max_retries with exponential backoff
- Set appropriate timeout values
- Implement custom retry logic that respects Retry-After headers
- Monitor rate limit headers from API responses

Example fix:
    from openai import AsyncOpenAI
    import asyncio
    
    client = AsyncOpenAI(
        base_url="http://localhost:8080",
        api_key=config.OPENAI_API_KEY,
        max_retries=5,  # Retry up to 5 times on rate limit
        timeout=60.0,   # 60 second timeout
        default_headers={"X-DashScope-Async": "disable"}
    )
    
    # Custom wrapper with exponential backoff
    async def api_call_with_backoff(func, *args, **kwargs):
        for attempt in range(5):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if "429" in str(e) or "rate limit" in str(e).lower():
                    wait_time = (2 ** attempt) + random.random()
                    await asyncio.sleep(wait_time)
                else:
                    raise

================================================================================
CAUSE 5: Large Dataset Processed in Single Burst
================================================================================

Location: create_dataset.py:10-25, run_experiment.py:137-153

Problem:
The pipeline loads all 65 Q&A pairs from the parquet file and processes 
them in ONE asyncio.run() call with no chunking or batching:

    dataset = create_ragas_dataset()  # Loads all 65 rows
    results = asyncio.run(
        evaluate_rag.arun(dataset, ...)  # Processes all at once
    )

This creates a massive burst of API calls instead of spreading them 
over time, which is particularly problematic for rate-limited APIs.

Recommendation:
- Split dataset into smaller batches (e.g., 10-20 rows per batch)
- Add delays between batches (e.g., 10-30 seconds)
- Process batches sequentially or with limited parallelism
- Consider running evaluation over multiple sessions for large datasets

Example implementation:
    BATCH_SIZE = 15
    BATCH_DELAY = 30  # seconds
    
    async def evaluate_in_batches(dataset, batch_size, delay):
        all_results = []
        items = list(dataset)
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(items) + batch_size - 1)//batch_size}")
            
            batch_results = await evaluate_rag.arun(batch, ...)
            all_results.extend(batch_results)
            
            if i + batch_size < len(items):
                print(f"Waiting {delay} seconds before next batch...")
                await asyncio.sleep(delay)
        
        return all_results

================================================================================
SUMMARY OF RECOMMENDATIONS
================================================================================

Priority Actions (in order of impact):

1. IMMEDIATE: Add asyncio.Semaphore to limit concurrent tasks (Cause 1 & 3)
   - Start with max 5 concurrent tasks
   - Monitor API rate limit headers to adjust

2. HIGH: Implement batch processing with delays (Cause 5)
   - Process 10-20 rows per batch
   - Add 30-60 second delays between batches

3. HIGH: Configure AsyncOpenAI client with retries and backoff (Cause 4)
   - Set max_retries=5
   - Implement exponential backoff for 429 responses

4. MEDIUM: Add rate limiting between LLM calls per row (Cause 2)
   - Small delays between RAG query and evaluation
   - Consider caching RAG responses

5. LOW: Monitor and adjust based on actual rate limit headers
   - Parse X-RateLimit-Remaining from responses
   - Dynamically adjust concurrency based on remaining quota

Expected Impact:
- Reduces peak request rate from ~130+ requests/minute to ~50-100 requests/minute
- Stays well within 5000 requests/minute limit
- Improves reliability and reduces failed requests
- Allows for larger datasets without hitting limits

Additional Considerations:
- Consider using a local LLM for evaluation to avoid API limits entirely
- Implement request queuing with priority for interactive vs batch requests
- Add monitoring to track API usage and rate limit hits
- Consider using multiple API keys with round-robin distribution

================================================================================
END OF DOCUMENT
================================================================================
