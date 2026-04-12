<script>
	import { onMount } from 'svelte';
	import { chests } from '../lib/stores/chests';
	import ChestList from '../lib/components/ChestList.svelte';
	import { chestAPI } from '../lib/api/client';
	
	// Load chests from API on mount
	onMount(async () => {
		try {
			const chestData = await chestAPI.getAll();
			chests.set(chestData);
		} catch (error) {
			console.error('Failed to load chests:', error);
			// Keep empty array or show error state
		}
	});
</script>

<ChestList />