import { writable, derived } from 'svelte/store';
import type { ChatMessage } from '$lib/api/client';
import { api } from '$lib/api/client';

export interface Source {
	id: string;
	chest_id: string;
	name: string;
	type: 'TXT' | 'URL' | 'FILE';
	content: string | null;
	content_hash: string | null;
	is_enabled: boolean;
	created_at: string;
}

function createSourceStore() {
	const { subscribe, set, update } = writable<Source[]>([]);

	return {
		subscribe,
		load: async (chestId: string) => {
			const sources = await api.getSources(chestId);
			set(sources);
		},
		add: (source: Source) => {
			update((sources) => [source, ...sources]);
		},
		remove: (id: string) => {
			update((sources) => sources.filter((s) => s.id !== id));
		},
		toggle: (id: string) => {
			update((sources) =>
				sources.map((s) =>
					s.id === id ? { ...s, is_enabled: !s.is_enabled } : s
				)
			);
		},
		update: (id: string, data: Partial<Source>) => {
			update((sources) =>
				sources.map((s) => (s.id === id ? { ...s, ...data } : s))
			);
		},
	};
}

function createChatStore() {
	const { subscribe, set, update } = writable<ChatMessage[]>([]);
	const isStreaming = writable(false);
	const currentResponse = writable('');

	return {
		subscribe,
		messages: { subscribe },
		isStreaming: { subscribe: isStreaming.subscribe },
		currentResponse: { subscribe: currentResponse.subscribe },
		load: async (chestId: string) => {
			const messages = await api.getMessages(chestId);
			set(messages);
		},
		addUserMessage: (content: string) => {
			const userMsg: ChatMessage = {
				id: `temp-${Date.now()}`,
				chest_id: '',
				role: 'USER',
				content,
				sources_used: null,
				created_at: new Date().toISOString(),
			};
			update((msgs) => [...msgs, userMsg]);
		},
		addAssistantMessage: (content: string, sources?: string[]) => {
			const assistantMsg: ChatMessage = {
				id: `temp-${Date.now()}`,
				chest_id: '',
				role: 'ASSISTANT',
				content,
				sources_used: sources || null,
				created_at: new Date().toISOString(),
			};
			update((msgs) => [...msgs, assistantMsg]);
		},
		clearResponse: () => currentResponse.set(''),
		setStreaming: (value: boolean) => isStreaming.set(value),
		appendResponse: (chunk: string) => {
			currentResponse.update((r) => r + chunk);
		},
	};
}

export const sourceStore = createSourceStore();
export const chatStore = createChatStore();
