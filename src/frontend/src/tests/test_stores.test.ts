import { describe, it, expect } from 'vitest';
import { get } from 'svelte/store';
import { chests } from '../lib/stores/chests';
import { sources } from '../lib/stores/sources';
import { chatMessages } from '../lib/stores/chat';

describe('Chests Store', () => {
	it('should initialize as empty array', () => {
		const value = get(chests);
		expect(value).toEqual([]);
	});

	it('should accept new values via set', () => {
		const testData = [
			{ id: 1, name: 'Test Chest', created_at: '2024-01-01', updated_at: null },
		];
		chests.set(testData);
		expect(get(chests)).toEqual(testData);
	});

	it('should update via update function', () => {
		chests.set([{ id: 1, name: 'Chest A', created_at: '2024-01-01', updated_at: null }]);
		chests.update(list => [...list, { id: 2, name: 'Chest B', created_at: '2024-01-02', updated_at: null }]);
		expect(get(chests)).toHaveLength(2);
	});

	it('should filter items via update', () => {
		chests.set([
			{ id: 1, name: 'A', created_at: '2024-01-01', updated_at: null },
			{ id: 2, name: 'B', created_at: '2024-01-02', updated_at: null },
		]);
		chests.update(list => list.filter(c => c.id !== 1));
		expect(get(chests)).toHaveLength(1);
		expect(get(chests)[0].id).toBe(2);
	});

	it('should reset to empty', () => {
		chests.set([{ id: 1, name: 'X', created_at: '2024-01-01', updated_at: null }]);
		chests.set([]);
		expect(get(chests)).toEqual([]);
	});
});

describe('Sources Store', () => {
	it('should initialize as empty array', () => {
		const value = get(sources);
		expect(value).toEqual([]);
	});

	it('should store source data with correct shape', () => {
		const testSource = {
			id: 1,
			chest_id: 1,
			name: 'Test Source',
			type: 'TXT' as const,
			content: 'some content',
			content_hash: 'abc123',
			is_enabled: true,
			created_at: '2024-01-01',
		};
		sources.set([testSource]);
		const value = get(sources);
		expect(value[0].name).toBe('Test Source');
		expect(value[0].type).toBe('TXT');
		expect(value[0].is_enabled).toBe(true);
	});

	it('should handle multiple sources', () => {
		sources.set([
			{ id: 1, chest_id: 1, name: 'S1', type: 'TXT', content: 'c1', content_hash: null, is_enabled: true, created_at: '2024-01-01' },
			{ id: 2, chest_id: 1, name: 'S2', type: 'URL', content: 'https://example.com', content_hash: null, is_enabled: false, created_at: '2024-01-02' },
		]);
		expect(get(sources)).toHaveLength(2);
	});
});

describe('ChatMessages Store', () => {
	it('should initialize as empty array', () => {
		const value = get(chatMessages);
		expect(value).toEqual([]);
	});

	it('should store a chat message', () => {
		const msg = {
			id: 1,
			chest_id: 1,
			role: 'USER' as const,
			content: 'Hello',
			sources_used: null,
			created_at: '2024-01-01',
		};
		chatMessages.set([msg]);
		expect(get(chatMessages)[0].role).toBe('USER');
		expect(get(chatMessages)[0].content).toBe('Hello');
	});

	it('should handle multiple messages', () => {
		chatMessages.set([
			{ id: 1, chest_id: 1, role: 'USER', content: 'Hi', sources_used: null, created_at: '2024-01-01' },
			{ id: 2, chest_id: 1, role: 'ASSISTANT', content: 'Hello!', sources_used: [], created_at: '2024-01-01' },
		]);
		expect(get(chatMessages)).toHaveLength(2);
	});
});
