<script>
	import { sourceAPI } from '../../lib/api/client';
	
	export let source;
	
	function formatType(type) {
		const types = {
			TXT: 'Plain Text',
			URL: 'URL',
			FILE: 'File'
		};
		return types[type] || type;
	}
	
	function getTypeColor(type) {
		const colors = {
			TXT: 'blue',
			URL: 'green',
			FILE: 'purple'
		};
		return colors[type] || 'gray';
	}
	
	async function handleDelete() {
		if (confirm('Are you sure you want to delete this source?')) {
			try {
				await sourceAPI.delete(source.id);
				// Dispatch event to parent to refresh the list
				const event = new CustomEvent('sourceDeleted', { detail: source.id });
				dispatchEvent(event);
			} catch (error) {
				console.error('Failed to delete source:', error);
				alert('Failed to delete source. Please try again.');
			}
		}
	}
	
	async function handleToggleEnabled() {
		try {
			const updatedSource = await sourceAPI.update(source.id, { 
				is_enabled: !source.is_enabled 
			});
			// Dispatch event to parent to update the source in the list
			const event = new CustomEvent('sourceToggled', { detail: updatedSource });
			dispatchEvent(event);
		} catch (error) {
			console.error('Failed to toggle source enabled status:', error);
			alert('Failed to update source status. Please try again.');
		}
	}
</script>

<div class="p-3 border rounded hover:bg-gray-50 transition-colors">
	<div class="flex justify-between items-start">
		<div class="flex-1">
			<div class="flex items-start">
				<div class="flex-shrink-0">
					<span 
						class={`px-2 py-1 text-xs font-semibold rounded-full bg-${getTypeColor(source.type)}-100 text-${getTypeColor(source.type)}-800`}
					>
						{formatType(source.type)}
					</span>
				</div>
				<div class="ml-3">
					<h3 class="font-medium">{source.name}</h3>
					<p class="text-xs text-gray-500 truncate">
						{#if source.type === 'TXT'}
							{source.content.length > 50 ? source.content.substring(0, 50) + '...' : source.content}
						{:else if source.type === 'URL'}
							{source.content}
						{:else}
							[File]
						{/if}
					</p>
				</div>
			</div>
			
			{#if source.content_hash}
				<p class="text-xs text-gray-400 mt-1">Processed: {source.content_hash.substring(0, 8)}...</p>
			{/if}
		</div>
		
		<div class="flex items-center space-x-2">
			<label class="flex items-center text-sm">
				<input 
					type="checkbox" 
					checked={source.is_enabled}
					on:change={handleToggleEnabled}
					class="form-checkbox h-4 w-4 text-blue-600"
				>
				<span class="ml-1">Use in chat</span>
			</label>
			
			<button 
				on:click={handleDelete}
				class="text-red-500 hover:text-red-700"
			>
				<!-- Simple trash icon -->
				<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
				</svg>
			</button>
		</div>
	</div>
</div>