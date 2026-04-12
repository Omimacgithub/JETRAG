import { writable } from 'svelte/store';

// Initial empty array - will be populated from API/user interaction
export const chatMessages = writable<Array<{
	id: number;
	chest_id: number;
	role: 'USER' | 'ASSISTANT';
	content: string;
	sources_used: number[] | null;
	created_at: string;
}>>([]);