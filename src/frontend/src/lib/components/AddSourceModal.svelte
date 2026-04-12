<script>
	import { onMount } from 'svelte';
	import { createEventDispatcher } from 'svelte';
	
	const dispatch = createEventDispatcher();
	
	export let open = false;
	
	let name = '';
	let type = 'TXT';
	let content = '';
	let loading = false;
	
	function handleSubmit() {
		if (!name.trim()) {
			alert('Please enter a source name');
			return;
		}
		
		// Validate content based on type
		if (type === 'TXT' && !content.trim()) {
			alert('Please enter content for text source');
			return;
		}
		
		if (type === 'URL' && !content.trim()) {
			alert('Please enter a URL');
			return;
		}
		
		if (type === 'FILE') {
			alert('File upload functionality to be implemented');
			return;
		}
		
		loading = true;
		
		// TODO: Implement actual API call
		setTimeout(() => {
			// Mock successful submission
			dispatch('sourceAdded', {
				id: Date.now(),
				name: name,
				type: type,
				content: content,
				is_enabled: true
			});
			
			// Close modal and reset
			open = false;
			loading = false;
			name = '';
			type = 'TXT';
			content = '';
		}, 1000);
	}
	
	function handleCancel() {
		open = false;
		// Reset form
		name = '';
		type = 'TXT';
		content = '';
		dispatch('close');
	}
	
	function handleTypeChange() {
		// Reset content when type changes
		content = '';
	}
</script>

{#if open}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
		<div class="bg-white rounded-lg p-6 w-full max-w-md">
			<h2 class="text-xl font-bold mb-4">Add New Source</h2>
			
			<form on:submit|preventDefault={handleSubmit}>
				<div class="mb-4">
					<label class="block text-sm font-medium mb-2">Source Name</label>
					<input 
						type="text" 
						bind:value={name}
						class="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
						required
					/>
				</div>
				
				<div class="mb-4">
					<label class="block text-sm font-medium mb-2">Source Type</label>
					<select 
						bind:value={type}
						on:change={handleTypeChange}
						class="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
					>
						<option value="TXT">Plain Text</option>
						<option value="URL">URL</option>
						<option value="FILE">File</option>
					</select>
				</div>
				
				{#if type === 'TXT'}
					<div class="mb-4">
						<label class="block text-sm font-medium mb-2">Content</label>
						<textarea 
							bind:value={content}
							class="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 h-32"
							placeholder="Enter text content..."
							required
						></textarea>
					</div>
				{:else if type === 'URL'}
					<div class="mb-4">
						<label class="block text-sm font-medium mb-2">URL</label>
						<input 
							type="url"
							bind:value={content}
							class="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
							placeholder="Enter URL (e.g., https://example.com)"
							required
						/>
					</div>
				{:else if type === 'FILE'}
					<div class="mb-4">
						<label class="block text-sm font-medium mb-2">File</label>
						<input 
							type="file"
							class="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
						/>
						<p class="text-xs text-gray-500 mt-1">File upload functionality to be implemented</p>
					</div>
				{/if}
				
				<div class="flex justify-end space-x-3">
					<button 
						type="button"
						on:click={handleCancel}
						class="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded disabled:opacity-50"
						disabled={loading}
					>
						Cancel
					</button>
					<button 
						type="submit"
						class="px-4 py-2 bg-blue-500 hover:bg-blue-700 text-white rounded disabled:opacity-50"
						disabled={loading}
					>
						{#if loading}
							Adding...
						{:else}
							Add Source
						{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}