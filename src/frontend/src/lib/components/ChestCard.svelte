<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import type { Chest } from '$lib/api/client';

	export let chest: Chest;

	const dispatch = createEventDispatcher<{
		open: void;
		delete: void;
		update: string;
	}>();

	let isEditing = false;
	let editName = chest.name;
	let showDelete = false;
	let inputEl: HTMLInputElement;

	function startEdit() {
		editName = chest.name;
		isEditing = true;
		setTimeout(() => inputEl?.focus(), 0);
	}

	function saveEdit() {
		if (editName.trim()) {
			dispatch('update', editName.trim());
		}
		isEditing = false;
	}

	function cancelEdit() {
		editName = chest.name;
		isEditing = false;
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') saveEdit();
		if (e.key === 'Escape') cancelEdit();
	}

	function handleDelete() {
		dispatch('delete');
	}

	function handleOpen() {
		dispatch('open');
	}
</script>

<div
	class="card hover:border-slate-500 transition-all cursor-pointer group"
	role="button"
	tabindex="0"
	on:click={handleOpen}
	on:keydown={(e) => e.key === 'Enter' && handleOpen()}
	on:mouseenter={() => (showDelete = true)}
	on:mouseleave={() => (showDelete = false)}
	on:focus={() => (showDelete = true)}
	on:blur={() => (showDelete = false)}
>
	<div class="flex items-start justify-between">
		{#if isEditing}
			<input
				bind:this={inputEl}
				bind:value={editName}
				class="input text-lg font-medium flex-1 mr-2"
				on:click|stopPropagation
				on:keydown={handleKeydown}
				on:blur={saveEdit}
			/>
		{:else}
			<div class="flex-1 min-w-0">
				<h3 class="text-lg font-medium text-slate-100 truncate">
					{chest.name}
				</h3>
				<p class="text-sm text-slate-400 mt-1">
					Creado {new Date(chest.created_at).toLocaleDateString()}
				</p>
			</div>
		{/if}

		{#if showDelete}
			<div class="flex gap-1">
				{#if !isEditing}
					<button
						class="p-1.5 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
						on:click|stopPropagation={startEdit}
						title="Editar nombre"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
						</svg>
					</button>
				{/if}
				<button
					class="p-1.5 rounded-lg hover:bg-red-900/50 text-slate-400 hover:text-red-400 transition-colors"
					on:click|stopPropagation={handleDelete}
					title="Eliminar cofre"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
					</svg>
				</button>
			</div>
		{/if}
	</div>
</div>
