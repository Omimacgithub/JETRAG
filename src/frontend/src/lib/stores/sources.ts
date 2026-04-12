import { writable } from 'svelte/store';

// Initial empty array - will be populated from API
export const sources = writable<Array<{
	id: number;
	chest_id: number;
	name: string;
	type: 'TXT' | 'URL' | 'FILE';
	content: string | null;
	content_hash: string | null;
	is_enabled: boolean;
	created_at: string;
}>>([]);