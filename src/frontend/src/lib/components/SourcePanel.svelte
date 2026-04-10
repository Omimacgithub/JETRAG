<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Source } from '$lib/api/client';
	import SourceWidget from './SourceWidget.svelte';

	export let sources: Source[] = [];
	export let loading = false;

	const dispatch = createEventDispatcher<{
		add: void;
		delete: string;
		update: { id: string; name: string };
		toggle: { id: string; isEnabled: boolean };
	}>();

	let collapsed = false;
</script>

<aside
	class="h-full bg-slate-800/50 border-r border-slate-700 flex flex-col transition-all duration-300"
	style="width: {collapsed ? '48px' : '320px'}"
>
	<div class="p-3 border-b border-slate-700 flex items-center justify-between">
		{#if !collapsed}
			<h2 class="font-medium text-slate-200">Fuentes</h2>
		{/if}
		<button
			class="p-2 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
			on:click={() => (collapsed = !collapsed)}
			title={collapsed ? 'Expandir' : 'Colapsar'}
		>
			<svg class="w-5 h-5 transition-transform" class:rotate-180={collapsed} fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
			</svg>
		</button>
	</div>

	{#if !collapsed}
		<div class="p-3 border-b border-slate-700">
			<button
				class="btn btn-primary w-full flex items-center justify-center gap-2"
				on:click={() => dispatch('add')}
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
				</svg>
				Añadir fuentes
			</button>
		</div>

		<div class="flex-1 overflow-y-auto scrollbar-thin p-3 space-y-2">
			{#if loading}
				<div class="flex justify-center py-8">
					<div class="animate-spin w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full"></div>
				</div>
			{:else if sources.length === 0}
				<p class="text-center text-slate-500 py-8 text-sm">
					No hay fuentes. Añade texto, URLs o archivos.
				</p>
			{:else}
				{#each sources as source (source.id)}
					<SourceWidget
						{source}
						on:delete={() => dispatch('delete', source.id)}
						on:update={(e) => dispatch('update', { id: source.id, name: e.detail })}
						on:toggle={(e) => dispatch('toggle', { id: source.id, isEnabled: e.detail })}
					/>
				{/each}
			{/if}
		</div>
	{/if}
</aside>
