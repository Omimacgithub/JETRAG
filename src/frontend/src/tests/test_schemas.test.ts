import { describe, it, expect } from 'vitest';
import type {
	Chest,
	ChestCreate,
	ChestUpdate,
	Source,
	SourceCreate,
	SourceUpdate,
	ChatMessage,
	ChatMessageCreate,
	RAGQuery,
	RAGResponse,
} from '../lib/models/schemas';

describe('TypeScript Schemas (compile-time type checks)', () => {
	it('should define Chest interface correctly', () => {
		const chest: Chest = {
			id: 1,
			name: 'Test Chest',
			created_at: '2024-01-01T00:00:00Z',
			updated_at: null,
		};
		expect(chest.id).toBe(1);
		expect(chest.name).toBe('Test Chest');
	});

	it('should allow Chest with updated_at', () => {
		const chest: Chest = {
			id: 1,
			name: 'Updated',
			created_at: '2024-01-01T00:00:00Z',
			updated_at: '2024-01-02T00:00:00Z',
		};
		expect(chest.updated_at).toBeTruthy();
	});

	it('should define ChestCreate extending name only', () => {
		const data: ChestCreate = { name: 'New Chest' };
		expect(data.name).toBe('New Chest');
	});

	it('should define ChestUpdate with optional name', () => {
		const full: ChestUpdate = { name: 'Renamed' };
		const empty: ChestUpdate = {};
		expect(full.name).toBe('Renamed');
		expect(empty.name).toBeUndefined();
	});

	it('should define Source with all fields', () => {
		const source: Source = {
			id: 1,
			chest_id: 1,
			name: 'Test Source',
			type: 'TXT',
			content: 'text content',
			content_hash: 'abc123',
			is_enabled: true,
			created_at: '2024-01-01T00:00:00Z',
		};
		expect(source.type).toBe('TXT');
		expect(source.is_enabled).toBe(true);
	});

	it('should allow URL type for Source', () => {
		const source: Source = {
			id: 2,
			chest_id: 1,
			name: 'URL Source',
			type: 'URL',
			content: 'https://example.com',
			content_hash: null,
			is_enabled: true,
			created_at: '2024-01-01T00:00:00Z',
		};
		expect(source.type).toBe('URL');
	});

	it('should allow FILE type for Source', () => {
		const source: Source = {
			id: 3,
			chest_id: 1,
			name: 'File Source',
			type: 'FILE',
			content: null,
			content_hash: null,
			is_enabled: false,
			created_at: '2024-01-01T00:00:00Z',
		};
		expect(source.type).toBe('FILE');
	});

	it('should define SourceUpdate with optional fields', () => {
		const update: SourceUpdate = { is_enabled: false };
		const full: SourceUpdate = { name: 'New', type: 'URL', content: 'url', is_enabled: true };
		expect(update.is_enabled).toBe(false);
		expect(full.name).toBe('New');
	});

	it('should define ChatMessage', () => {
		const msg: ChatMessage = {
			id: 1,
			chest_id: 1,
			role: 'USER',
			content: 'Hello',
			sources_used: null,
			created_at: '2024-01-01T00:00:00Z',
		};
		expect(msg.role).toBe('USER');
	});

	it('should define ChatMessage with sources', () => {
		const msg: ChatMessage = {
			id: 2,
			chest_id: 1,
			role: 'ASSISTANT',
			content: 'Answer',
			sources_used: [1, 2, 3],
			created_at: '2024-01-01T00:00:00Z',
		};
		expect(msg.sources_used).toHaveLength(3);
	});

	it('should define RAGQuery', () => {
		const query: RAGQuery = { question: 'What is?', chest_id: 1 };
		expect(query.question).toBe('What is?');
		expect(query.chest_id).toBe(1);
	});

	it('should define RAGResponse', () => {
		const response: RAGResponse = { answer: 'Answer', sources_used: [1] };
		expect(response.answer).toBe('Answer');
	});
});
