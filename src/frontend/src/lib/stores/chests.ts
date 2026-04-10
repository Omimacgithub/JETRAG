import { writable } from 'svelte/store';
import type { Chest } from '$lib/api/client';
import { api } from '$lib/api/client';

function createChestStore() {
	const { subscribe, set } = writable<Chest[]>([]);

	return {
		subscribe,
		load: async () => {
			const chests = await api.getChests();
			set(chests);
		},
	};
}

export const chestStore = createChestStore();
