import { writable } from 'svelte/store';

// Initial empty array - will be populated from API
export const chests = writable<Array<{
	id: number;
	name: string;
	created_at: string;
	updated_at: string | null;
}>>([]);