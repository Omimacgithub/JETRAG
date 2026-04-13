<script>
	import { onMount } from 'svelte';
	import SourceWidget from './SourceWidget.svelte';
	import { sources } from '../stores/sources';
	import { sourceAPI } from '../../lib/api/client';
	
	let chestId = null;
	let sourcesList = [];
	let addingSource = false;
	let sourceName = '';
	let sourceType = 'TXT';
	let sourceContent = '';
	let loading = false;
	
	// This would typically come from route params or store
	// We'll receive chestId as a prop
	export let chestIdProp = null;
	
	onMount(() => {
		// Get chestId from prop (will be set by parent component)
		if (chestIdProp) {
			chestId = chestIdProp;
			loadSources();
		}
	});
	
	async function loadSources() {
		if (!chestId) return;
		
		loading = true;
		try {
			const sourcesData = await sourceAPI.getByChest(chestId);
			sourcesList = sourcesData;
		} catch (error) {
			console.error('Failed to load sources:', error);
			// Could show error state
		} finally {
			loading = false;
		}
	}
	
	function toggleAddSource() {
		addingSource = !addingSource;
		if (!addingSource) {
			// Reset form
			sourceName = '';
			sourceType = 'TXT';
			sourceContent = '';
		}
	}
	
	function handleSourceTypeChange(event) {
		sourceType = event.target.value;
	}
	
	async function handleAddSource() {
		if (!sourceName.trim()) {
			alert('Please enter a source name');
			return;
		}
		
		// Validate content based on type
		if (sourceType === 'TXT' && !sourceContent.trim()) {
			alert('Please enter content for text source');
			return;
		}
		
		if (sourceType === 'URL' && !sourceContent.trim()) {
			alert('Please enter a URL');
			return;
		}
		
		if (sourceType === 'FILE') {
			// File handling would be more complex
			alert('File upload functionality to be implemented');
			return;
		}
		
		try {
			const newSource = await sourceAPI.create({
				chest_id: chestId,
				name: sourceName.trim(),
				type: sourceType,
				content: sourceType === 'FILE' ? '' : sourceContent.trim() // For file, content might be handled differently
			});
			
			// Show success message and reset
			alert('Source added successfully! It will be available after processing.');
			
			// Reset form
			addingSource = false;
			sourceName = '';
			sourceType = 'TXT';
			sourceContent = '';
			
			// Reload sources to show the new one
			loadSources();
		} catch (error) {
			console.error('Failed to add source:', error);
			alert('Failed to add source. Please try again.');
		}
	}
	
	function handleDeleteSource(sourceId) {
		if (confirm('Are you sure you want to delete this source?')) {
			sourceAPI.delete(sourceId).then(() => {
				// Reload sources after deletion
				loadSources();
			}).catch(error => {
				console.error('Failed to delete source:', error);
				alert('Failed to delete source. Please try again.');
			});
		}
	}
	
	function handleToggleSourceEnabled(source) {
		sourceAPI.update(source.id, { is_enabled: !source.is_enabled }).then(updatedSource => {
			// Update the source in our list
			const index = sourcesList.findIndex(s => s.id === updatedSource.id);
			if (index !== -1) {
				sourcesList[index] = updatedSource;
			}
		}).catch(error => {
			console.error('Failed to toggle source enabled status:', error);
			alert('Failed to update source status. Please try again.');
		});
	}
</script>

<div class="p-4">
	<h2 class="text-xl font-bold mb-4">Sources</h2>
	
	{#if addingSource}
		<div class="bg-white p-4 rounded mb-4 shadow">
			<h3 class="font-semibold mb-2">Add New Source</h3>
			<div class="mb-2">
				<label class="block text-sm font-medium mb-1">Source Name</label>
				<input 
					type="text" 
					bind:value={sourceName}
					class="w-full p-2 border rounded"
					placeholder="Enter source name"
				/>
			</div>
			<div class="mb-2">
				<label class="block text-sm font-medium mb-1">Source Type</label>
				<select 
					bind:value={sourceType}
					on:change={handleSourceTypeChange}
					class="w-full p-2 border rounded"
				>
					<option value="TXT">Plain Text</option>
					<option value="URL">URL</option>
					<option value="FILE">File</option>
				</select>
			</div>
			{#if sourceType === 'TXT'}
				<div class="mb-2">
					<label class="block text-sm font-medium mb-1">Content</label>
					<textarea 
						bind:value={sourceContent}
						class="w-full p-2 border rounded h-24"
						placeholder="Enter text content..."
					></textarea>
				</div>
			{:else if sourceType === 'URL'}
				<div class="mb-2">
					<label class="block text-sm font-medium mb-1">URL</label>
					<input 
						type="url"
						bind:value={sourceContent}
						class="w-full p-2 border rounded"
						placeholder="Enter URL (e.g., https://example.com)"
					/>
				</div>
			{:else if sourceType === 'FILE'}
				<div class="mb-2">
					<label class="block text-sm font-medium mb-1">File</label>
					<input 
						type="file"
						class="w-full p-2 border rounded"
					/>
					<p class="text-xs text-gray-500 mt-1">File upload functionality to be implemented</p>
				</div>
			{/if}
			<div class="flex justify-end space-x-2">
				<button 
					on:click={toggleAddSource}
					class="bg-gray-500 hover:bg-gray-600 text-white font-bold py-1 px-3 rounded"
				>
					Cancel
				</button>
				<button 
					on:click={handleAddSource}
					class="bg-green-500 hover:bg-green-600 text-white font-bold py-1 px-3 rounded"
				>
					Add Source
				</button>
			</div>
		</div>
	{/if}
	
	<button 
		on:click={toggleAddSource}
		class="mb-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full"
	>
		{addingSource ? 'Cancel Adding Source' : 'Add New Source'}
	</button>
	
	<div class="mt-4">
		{#if loading}
			<div class="text-center py-4">
				<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
				<p class="mt-2 text-sm text-gray-500">Loading sources...</p>
			</div>
		{:else if sourcesList.length === 0}
			<p class="text-gray-500 text-center py-4">No sources added yet.</p>
		{:else}
			<div class="space-y-2">
				{#each sourcesList as source (source.id)}
					<SourceWidget 
						{source} 
						onDelete={handleDeleteSource}
						onToggleEnabled={handleToggleSourceEnabled}
					/>
				{/each}
			</div>
		{/if}
	</div>
</div>