<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Source } from '$lib/api/client';

	export let source: Source;

	const dispatch = createEventDispatcher<{
		delete: void;
		update: string;
		toggle: boolean;
	}>();

	let showActions = false;
	let isEditing = false;
	let editName = source.name;
	let inputEl: HTMLInputElement;

	const typeIcons: Record<string, string> = {
		TXT: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
		URL: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1',
		FILE: 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z'
	};

	function startEdit() {
		editName = source.name;
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
		editName = source.name;
		isEditing = false;
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') saveEdit();
		if (e.key === 'Escape') cancelEdit();
	}

	function handleToggle(e: Event) {
		e.stopPropagation();
		dispatch('toggle', !source.is_enabled);
	}
</script>

<div
	class="bg-slate-800 rounded-lg p-3 border border-slate-700 hover:border-slate-600 transition-colors group"
	role="button"
	tabindex="0"
	on:mouseenter={() => (showActions = true)}
	on:mouseleave={() => (showActions = false)}
	on:focus={() => (showActions = true)}
	on:blur={() => (showActions = false)}
>
	<div class="flex items-center gap-3">
		<input
			type="checkbox"
			checked={source.is_enabled}
			on:change={handleToggle}
			class="w-4 h-4 rounded border-slate-600 bg-slate-700 text-primary-500 focus:ring-primary-500 focus:ring-offset-0"
			title={source.is_enabled ? 'Desactivar' : 'Activar'}
		/>

		<div class="flex-shrink-0 text-slate-400">
			<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={typeIcons[source.type] || typeIcons.FILE} />
			</svg>
		</div>

		<div class="flex-1 min-w-0">
			{#if isEditing}
				<input
					bind:this={inputEl}
					bind:value={editName}
					class="input text-sm py-1"
					on:click|stopPropagation
					on:keydown={handleKeydown}
					on:blur={saveEdit}
				/>
			{:else}
				<p class="text-sm font-medium text-slate-200 truncate" class:opacity-50={!source.is_enabled}>
					{source.name}
				</p>
				<p class="text-xs text-slate-500">{source.type}</p>
			{/if}
		</div>

		{#if showActions && !isEditing}
			<div class="flex gap-1">
				<button
					class="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
					on:click|stopPropagation={startEdit}
					title="Editar nombre"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
					</svg>
				</button>
				<button
					class="p-1.5 rounded hover:bg-red-900/50 text-slate-400 hover:text-red-400 transition-colors"
					on:click|stopPropagation={() => dispatch('delete')}
					title="Eliminar"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
					</svg>
				</button>
			</div>
		{/if}
	</div>
</div>
