<script>
	import { chestAPI } from '../lib/api/client';
	
	export let chest;
	export let onView;
	export let onDelete;
	export let onRename;
	
	let deleteLoading = false;
	let renameLoading = false;
	
	async function handleDelete() {
		deleteLoading = true;
		try {
			await chestAPI.delete(chest.id);
			onDelete(chest.id);
		} catch (error) {
			console.error('Failed to delete chest:', error);
			alert('Failed to delete chest. Please try again.');
		} finally {
			deleteLoading = false;
		}
	}
	
	async function handleRename() {
		const newName = prompt('Enter new chest name:', chest.name);
		if (newName && newName.trim() && newName !== chest.name) {
			renameLoading = true;
			try {
				await chestAPI.update(chest.id, { name: newName.trim() });
				onRename(chest.id, newName.trim());
			} catch (error) {
				console.error('Failed to rename chest:', error);
				alert('Failed to rename chest. Please try again.');
			} finally {
				renameLoading = false;
			}
		}
	}
</script>

<div class="p-3 border rounded hover:bg-gray-50 cursor-pointer transition-colors" on:click={onView}>
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
					handleRename();
				}}
				class="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-1 px-2 rounded disabled:opacity-50"
				disabled={renameLoading}
			>
				{#if renameLoading}
					Renaming...
				{:else}
					Rename
				{/if}
			</button>
			<button 
				on:click={(e) => {
					e.stopPropagation();
					handleDelete();
				}}
				class="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-2 rounded disabled:opacity-50"
				disabled={deleteLoading}
			>
				{#if deleteLoading}
					Deleting...
				{:else}
					Delete
				{/if}
			</button>
		</div>
	</div>
</div>