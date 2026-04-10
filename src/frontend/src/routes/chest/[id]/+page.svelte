<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api/client';
	import { sourceStore, chatStore } from '$lib/stores/chat';
	import SourcePanel from '$lib/components/SourcePanel.svelte';
	import ChatArea from '$lib/components/ChatArea.svelte';
	import AddSourceModal from '$lib/components/AddSourceModal.svelte';
	import type { Source } from '$lib/api/client';

	let chestId = '';
	let chestName = '';
	let sources: Source[] = [];
	let loading = true;
	let showAddModal = false;

	sourceStore.subscribe((s) => (sources = s));

	onMount(async () => {
		const unsubscribe = page.subscribe(($page) => {
			chestId = $page.params.id;
		});
		unsubscribe();

		try {
			const chests = await api.getChests();
			const chest = chests.find((c) => c.id === chestId);
			if (!chest) {
				goto('/');
				return;
			}
			chestName = chest.name;
			await Promise.all([
				sourceStore.load(chestId),
				chatStore.load(chestId),
			]);
		} catch {
			goto('/');
		} finally {
			loading = false;
		}
	});

	async function createNewChest() {
		const newChest = await api.createChest(`Cofre ${Date.now()}`);
		await sourceStore.load(newChest.id);
		goto(`/chest/${newChest.id}`);
	}

	async function handleSourceDelete(id: string) {
		await api.deleteSource(id);
		sourceStore.remove(id);
	}

	async function handleSourceUpdate(id: string, name: string) {
		await api.updateSource(id, { name });
		sourceStore.update(id, { name });
	}

	async function handleSourceToggle(id: string, isEnabled: boolean) {
		await api.updateSource(id, { is_enabled: isEnabled });
		sourceStore.toggle(id);
	}

	async function handleSourcesAdded(newSources: Source[]) {
		showAddModal = false;
		await sourceStore.load(chestId);
	}

	function goHome() {
		goto('/');
	}
</script>

<div class="h-screen flex flex-col bg-slate-900">
	<header class="flex-shrink-0 bg-slate-800 border-b border-slate-700 px-4 py-3">
		<div class="flex items-center justify-between h-full">
			<div class="flex items-center gap-4">
				<button
					class="p-2 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
					on:click={goHome}
					title="Volver"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
					</svg>
				</button>
				<h1 class="text-lg font-medium text-slate-100">{chestName}</h1>
			</div>
			<button
				class="btn btn-primary text-sm"
				on:click={createNewChest}
			>
				+ Nuevo cofre
			</button>
		</div>
	</header>

	<div class="flex-1 flex overflow-hidden">
		{#if loading}
			<div class="flex-1 flex items-center justify-center">
				<div class="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
			</div>
		{:else}
			<SourcePanel
				{sources}
				on:add={() => (showAddModal = true)}
				on:delete={(e) => handleSourceDelete(e.detail)}
				on:update={(e) => handleSourceUpdate(e.detail.id, e.detail.name)}
				on:toggle={(e) => handleSourceToggle(e.detail.id, e.detail.isEnabled)}
			/>
			<ChatArea {chestId} {sources} />
		{/if}
	</div>

	{#if showAddModal}
		<AddSourceModal
			{chestId}
			on:close={() => (showAddModal = false)}
			on:added={(e) => handleSourcesAdded(e.detail)}
		/>
	{/if}
</div>
