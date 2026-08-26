import { describe, it, expect, vi, beforeEach } from 'vitest';
import { chestAPI, sourceAPI, chatAPI } from '../lib/api/client';
import type { Chest, Source, RAGResponse } from '../lib/models/schemas';

const mockFetch = vi.fn();
global.fetch = mockFetch;

const API_BASE = 'http://localhost:8000';

function mockResponse(data: unknown, status = 200) {
	return new Response(JSON.stringify(data), {
		status,
		headers: { 'Content-Type': 'application/json' },
	});
}

function mockStreamResponse(chunks: string[]) {
	const encoder = new TextEncoder();
	const stream = new ReadableStream({
		start(controller) {
			for (const chunk of chunks) {
				controller.enqueue(encoder.encode(chunk));
			}
			controller.close();
		},
	});
	return new Response(stream, {
		status: 200,
		headers: { 'Content-Type': 'text/plain' },
	});
}

describe('Chest API Client', () => {
	beforeEach(() => {
		mockFetch.mockReset();
	});

	it('getAll should fetch and return chests', async () => {
		const chests: Chest[] = [
			{ id: 1, name: 'Test', created_at: '2024-01-01', updated_at: null },
		];
		mockFetch.mockResolvedValue(mockResponse(chests));

		const result = await chestAPI.getAll();
		expect(result).toEqual(chests);
		expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/api/chests/`);
	});

	it('getAll should throw on error', async () => {
		mockFetch.mockResolvedValue(new Response(null, { status: 500 }));
		await expect(chestAPI.getAll()).rejects.toThrow('Failed to fetch chests');
	});

	it('create should POST and return new chest', async () => {
		const newChest: Chest = { id: 1, name: 'New', created_at: '2024-01-01', updated_at: null };
		mockFetch.mockResolvedValue(mockResponse(newChest, 201));

		const result = await chestAPI.create({ name: 'New' });
		expect(result).toEqual(newChest);
		expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/api/chests/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ name: 'New' }),
		});
	});

	it('getById should fetch single chest', async () => {
		const chest: Chest = { id: 1, name: 'Single', created_at: '2024-01-01', updated_at: null };
		mockFetch.mockResolvedValue(mockResponse(chest));

		const result = await chestAPI.getById(1);
		expect(result).toEqual(chest);
		expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/api/chests/1`);
	});

	it('update should PATCH and return updated chest', async () => {
		const updated: Chest = { id: 1, name: 'Updated', created_at: '2024-01-01', updated_at: '2024-01-02' };
		mockFetch.mockResolvedValue(mockResponse(updated));

		const result = await chestAPI.update(1, { name: 'Updated' });
		expect(result).toEqual(updated);
		expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/api/chests/1`, {
			method: 'PATCH',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ name: 'Updated' }),
		});
	});

	it('delete should send DELETE request', async () => {
		mockFetch.mockResolvedValue(new Response(null, { status: 204 }));

		await chestAPI.delete(1);
		expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/api/chests/1`, {
			method: 'DELETE',
		});
	});

	it('delete should throw on error', async () => {
		mockFetch.mockResolvedValue(new Response(null, { status: 404 }));
		await expect(chestAPI.delete(999)).rejects.toThrow('Failed to delete chest');
	});
});

describe('Source API Client', () => {
	beforeEach(() => {
		mockFetch.mockReset();
	});

	it('getByChest should fetch sources for a chest', async () => {
		const sources: Source[] = [
			{ id: 1, chest_id: 1, name: 'Src', type: 'TXT', content: 'text', content_hash: null, is_enabled: true, created_at: '2024-01-01' },
		];
		mockFetch.mockResolvedValue(mockResponse(sources));

		const result = await sourceAPI.getByChest(1);
		expect(result).toEqual(sources);
		expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/api/sources/?chest_id=1`);
	});

	it('create should POST and return new source', async () => {
		const newSource: Source = {
			id: 1, chest_id: 1, name: 'New', type: 'TXT', content: 'text',
			content_hash: 'abc', is_enabled: true, created_at: '2024-01-01',
		};
		mockFetch.mockResolvedValue(mockResponse(newSource, 201));

		const result = await sourceAPI.create({ chest_id: 1, name: 'New', type: 'TXT', content: 'text' });
		expect(result).toEqual(newSource);
	});

	it('getById should fetch single source', async () => {
		const src: Source = {
			id: 1, chest_id: 1, name: 'Src', type: 'TXT', content: 'text',
			content_hash: null, is_enabled: true, created_at: '2024-01-01',
		};
		mockFetch.mockResolvedValue(mockResponse(src));

		const result = await sourceAPI.getById(1);
		expect(result).toEqual(src);
		expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/api/sources/1`);
	});

	it('update should PATCH source', async () => {
		mockFetch.mockResolvedValue(mockResponse({}));
		await sourceAPI.update(1, { is_enabled: false });
		expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/api/sources/1`, {
			method: 'PATCH',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ is_enabled: false }),
		});
	});

	it('delete should send DELETE', async () => {
		mockFetch.mockResolvedValue(new Response(null, { status: 204 }));
		await sourceAPI.delete(1);
		expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/api/sources/1`, {
			method: 'DELETE',
		});
	});
});

describe('Chat API Client', () => {
	beforeEach(() => {
		mockFetch.mockReset();
	});

	it('query should POST and return RAG response', async () => {
		const ragResponse: RAGResponse = { answer: 'Test answer', sources_used: [1] };
		mockFetch.mockResolvedValue(mockResponse(ragResponse));

		const result = await chatAPI.query({ question: 'test?', chest_id: 1 });
		expect(result).toEqual(ragResponse);
		expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/api/chat/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ question: 'test?', chest_id: 1 }),
		});
	});

	it('query should throw on error', async () => {
		mockFetch.mockResolvedValue(new Response(null, { status: 500 }));
		await expect(chatAPI.query({ question: 'test?', chest_id: 1 })).rejects.toThrow();
	});

	it('streamQuery should call onChunk and onDone', async () => {
		const sseData = 'data: Hello[ENDLINE]data: World[ENDLINE]data: [DONE][ENDLINE]';
		mockFetch.mockResolvedValue(mockStreamResponse([sseData]));

		const chunks: string[] = [];
		const onChunk = (chunk: string) => chunks.push(chunk);
		const onDone = vi.fn();

		await chatAPI.streamQuery({ question: 'hi', chest_id: 1 }, onChunk, onDone);

		//console.log("CHUNKS: ", chunks)

		expect(chunks).toContain('Hello');
		expect(chunks).toContain('World');
		expect(onDone).toHaveBeenCalled();
	});

	it('streamQuery should throw on HTTP error', async () => {
		mockFetch.mockResolvedValue(new Response(null, { status: 500 }));
		await expect(
			chatAPI.streamQuery({ question: 'hi', chest_id: 1 }, vi.fn(), vi.fn())
		).rejects.toThrow();
	});

	it('streamQuery should throw if no response body', async () => {
		const response = new Response(null, { status: 200 });
		Object.defineProperty(response, 'body', { value: null });
		mockFetch.mockResolvedValue(response);

		await expect(
			chatAPI.streamQuery({ question: 'hi', chest_id: 1 }, vi.fn(), vi.fn())
		).rejects.toThrow('No response body available');
	});

	it('streamQuery should handle empty stream', async () => {
		mockFetch.mockResolvedValue(mockStreamResponse(['data: [DONE][ENDLINE]']));

		const onChunk = vi.fn();
		const onDone = vi.fn();

		await chatAPI.streamQuery({ question: 'hi', chest_id: 1 }, onChunk, onDone);
		expect(onChunk).not.toHaveBeenCalled();
		expect(onDone).toHaveBeenCalled();
	});
});
