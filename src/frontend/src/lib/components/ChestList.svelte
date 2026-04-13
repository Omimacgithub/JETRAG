<script>
	import { onMount } from 'svelte';
	import { chests } from '../stores/chests';
	import { goto } from '$app/navigation';
	import { chestAPI } from '../../lib/api/client';
	
	let searchTerm = '';
	let loading = false;
	
	async function loadChests() {
		loading = true;
		try {
			const chestData = await chestAPI.getAll();
			chests.set(chestData);
		} catch (error) {
			console.error('Failed to load chests:', error);
			// Could show error state here
		} finally {
			loading = false;
		}
	}
	
	async function handleCreateChest() {
		const name = prompt('Enter chest name:');
		if (name && name.trim()) {
			try {
				const newChest = await chestAPI.create({ name: name.trim() });
				// Update the store with the new chest
				chests.update(existing => [...existing, newChest]);
				// Navigate to the new chest
				goto(`/chest/${newChest.id}`);
			} catch (error) {
				console.error('Failed to create chest:', error);
				alert('Failed to create chest. Please try again.');
			}
		}
	}
	
	function handleViewChest(chestId) {
		goto(`/chest/${chestId}`);
	}
	
	async function handleDeleteChest(chestId) {
		if (confirm('Are you sure you want to delete this chest?')) {
			try {
				await chestAPI.delete(chestId);
				// Remove from store
				chests.update(existing => existing.filter(chest => chest.id !== chestId));
			} catch (error) {
				console.error('Failed to delete chest:', error);
				alert('Failed to delete chest. Please try again.');
			}
		}
	}
	
	async function handleRenameChest(chestId, currentName) {
		const newName = prompt('Enter new chest name:', currentName);
		if (newName && newName.trim() && newName !== currentName) {
			try {
				const updatedChest = await chestAPI.update(chestId, { name: newName.trim() });
				// Update in store
				chests.update(existing => 
					existing.map(chest => 
						chest.id === chestId ? updatedChest : chest
					)
				);
			} catch (error) {
				console.error('Failed to rename chest:', error);
				alert('Failed to rename chest. Please try again.');
			}
		}
	}
</script>

<div class="p-4">
	<h1 class="text-2xl font-bold mb-4">Chests</h1>
	
	<div class="flex justify-between items-center mb-4">
		<button 
			on:click={handleCreateChest}
			class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
			disabled={loading}
		>
			{#if loading}
				Creating...
			{:else}
				Create New Chest
			{/if}
		</button>
	</div>
	
	{#if loading && $chests.length === 0}
		<p class="text-gray-500">Loading chests...</p>
	{:else if $chests.length === 0}
		<p class="text-gray-500">No chests found. Create your first chest!</p>
	{:else}
		<div class="space-y-2">
			{#each $chests as chest (chest.id)}
				<div 
					class="p-3 border rounded hover:bg-gray-50 cursor-pointer transition-colors"
					on:click={() => handleViewChest(chest.id)}
					on:keypress={() => handleViewChest(chest.id)}
				>
					<div class="flex justify-between items-start">
						<div>
							<h2 class="font-semibold">{chest.name}</h2>
							<p class="text-sm text-gray-500">
								Created: {new Date(chest.created_at).toLocaleDateString()}
							</p>
						</div>
						<div class="flex space-x-2 text-sm">
							<button 
								on:click={(e) => {
									e.stopPropagation();
									handleRenameChest(chest.id, chest.name);
								}}
								on:keypress={(e) => {
									e.stopPropagation();
									handleRenameChest(chest.id, chest.name);
								}}
								class="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-1 px-2 rounded"
							>
								Rename
							</button>
							<button 
								on:click={(e) => {
									e.stopPropagation();
									handleDeleteChest(chest.id);
								}}
								class="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-2 rounded"
							>
								Delete
							</button>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>