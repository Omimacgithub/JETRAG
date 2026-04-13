<script>
	import { onMount } from 'svelte';
	import { chestAPI, sourceAPI } from '../../../lib/api/client';
	import SourcePanel from '../../../lib/components/SourcePanel.svelte';
	import ChatArea from '../../../lib/components/ChatArea.svelte';
	import { chatMessages } from '../../../lib/stores/chat';
	
	export let params;
	//let { params }: PageProps = $props();
	//let { chest } = $props();
	let chestId = null;
	let chestIdProp = null;
	let chest = null;
	let loading = true;
	let error = null;
	
	// Load chest data on mount
	onMount(async () => {
		chestId = parseInt(params.id);
		if (isNaN(chestId)) {
			error = 'Invalid chest ID';
			loading = false;
			return;
		}
		chestIdProp = chestId;
		
		try {
			const chestData = await chestAPI.getById(chestId);
			chest = chestData;
			
			// Initialize chat store with any existing messages for this chest
			// In a real app, we'd fetch these from the backend
			chatMessages.set([]);
			
		} catch (err) {
			console.error('Failed to load chest:', err);
			error = 'Failed to load chest data';
		} finally {
			loading = false;
		}
	});
	
	function handleSourceAdded(sourceData) {
		// In a real implementation, we would update the source list
		// For now, we'll just show a success message
		alert('Source added successfully! Processing...');
	}
</script>

<div class="flex h-screen bg-gray-50">
	<!-- Sidebar - Chest Info and Sources -->
	<div class="w-64 bg-white border-r border-gray-200 flex flex-col">
		<div class="p-4 border-b">
			<h1 class="text-xl font-bold">{chest?.name || 'Loading chest...'}</h1>
			<p class="text-sm text-gray-500 mt-1">
				ID: {chestId}
			</p>
		</div>
		
		{#if loading}
			<div class="flex-1 flex items-center justify-center">
				<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
			</div>
		{:else if error}
			<div class="flex-1 flex items-center justify-center p-4 text-center text-red-500">
				{error}
			</div>
		{:else}
			<div class="flex-1 overflow-y-auto">
				<SourcePanel 
					{chestIdProp} 
					
				/>
				<!--onSourceAdded={handleSourceAdded}-->
			</div>
		{/if}
	</div>
	
	<!-- Main Content - Chat Interface -->
	<div class="flex-1 flex flex-col">
		<div class="border-t border-gray-200">
			<div class="p-4 bg-white border-b">
				<h2 class="text-lg font-bold flex items-center">
					Chat with "{chest?.name || 'Chest'}"
					{#if chest}
						<span class="ml-2 px-2 py-1 text-xs rounded-full bg-gray-200">
							{chestId} sources
						</span>
					{/if}
				</h2>
			</div>
			
			<div class="flex-1 overflow-hidden">
				<ChatArea/>
					<!--chestId={chestId}-->
				<!--/>-->
			</div>
		</div>
	</div>
</div>