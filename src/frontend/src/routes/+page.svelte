<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import ChestCard from '$lib/components/ChestCard.svelte';
	import { chestStore } from '$lib/stores/chests';
	import { api } from '$lib/api/client';

	let chests = $chestStore;
	let loading = true;

	onMount(async () => {
		await chestStore.load();
		loading = false;
	});

	async function createChest() {
		const name = `Cofre ${chests.length + 1}`;
		const newChest = await api.createChest(name);
		await chestStore.load();
		goto(`/chest/${newChest.id}`);
	}

	async function deleteChest(id: string) {
		await api.deleteChest(id);
		await chestStore.load();
	}

	async function updateChest(id: string, name: string) {
		await api.updateChest(id, name);
		await chestStore.load();
	}

	function openChest(id: string) {
		goto(`/chest/${id}`);
	}
</script>

<div class="min-h-screen p-8">
	<div class="max-w-4xl mx-auto">
		<header class="mb-8 flex items-center justify-between">
			<div>
				<h1 class="text-3xl font-bold text-slate-100">JETRAG</h1>
				<p class="text-slate-400 mt-1">Tu asistente RAG local</p>
			</div>
			<button class="btn btn-primary" on:click={createChest}>
				Crear nuevo cofre
			</button>
		</header>

		{#if loading}
			<div class="flex items-center justify-center py-20">
				<div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div>
			</div>
		{:else if chests.length === 0}
			<div class="card text-center py-20">
				<p class="text-slate-400 mb-4">No tienes cofres todavía</p>
				<button class="btn btn-primary" on:click={createChest}>
					Crear tu primer cofre
				</button>
			</div>
		{:else}
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each chests as chest (chest.id)}
					<ChestCard
						{chest}
						on:open={() => openChest(chest.id)}
						on:delete={() => deleteChest(chest.id)}
						on:update={(e) => updateChest(chest.id, e.detail)}
					/>
				{/each}
			</div>
		{/if}
	</div>
</div>
