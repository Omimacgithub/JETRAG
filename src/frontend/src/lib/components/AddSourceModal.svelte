<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { api, type Source } from '$lib/api/client';

	export let chestId: string;

	const dispatch = createEventDispatcher<{
		close: void;
		added: Source[];
	}>();

	interface PendingSource {
		name: string;
		type: 'TXT' | 'URL' | 'FILE';
		content: string;
	}

	let pendingSources: PendingSource[] = [];
	let isProcessing = false;
	let error = '';

	function addPendingSource() {
		pendingSources = [
			...pendingSources,
			{ name: `Fuente ${pendingSources.length + 1}`, type: 'TXT', content: '' },
		];
	}

	function removePendingSource(index: number) {
		pendingSources = pendingSources.filter((_, i) => i !== index);
	}

	function updatePendingSource(index: number, field: keyof PendingSource, value: string) {
		pendingSources = pendingSources.map((s, i) =>
			i === index ? { ...s, [field]: value } : s
		);
	}

	async function handleSubmit() {
		if (pendingSources.length === 0) return;

		const validSources = pendingSources.filter((s) => s.content.trim());
		if (validSources.length === 0) {
			error = 'Añade al menos una fuente con contenido';
			return;
		}

		isProcessing = true;
		error = '';

		try {
			const created = await api.createSources(
				chestId,
				validSources.map((s) => ({
					name: s.name,
					type: s.type,
					content: s.content,
				}))
			);
			dispatch('added', created);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error al procesar fuentes';
		} finally {
			isProcessing = false;
		}
	}

	function handleClose() {
		dispatch('close');
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			handleClose();
		}
	}
</script>

<div
	class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
	on:click={handleBackdropClick}
	on:keydown={(e) => e.key === 'Escape' && handleClose()}
	role="dialog"
	tabindex="-1"
>
	<div class="bg-slate-800 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
		<div class="flex items-center justify-between p-4 border-b border-slate-700">
			<h2 class="text-lg font-medium text-slate-100">Añadir fuentes</h2>
			<button
				class="p-2 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-slate-200"
				on:click={handleClose}
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</div>

		<div class="flex-1 overflow-y-auto p-4 space-y-4">
			{#if error}
				<div class="bg-red-900/50 border border-red-700 rounded-lg p-3 text-red-200">
					{error}
				</div>
			{/if}

			{#each pendingSources as source, index (index)}
				<div class="bg-slate-900 rounded-lg p-4 space-y-3">
					<div class="flex items-center justify-between">
						<input
							type="text"
							value={source.name}
							on:input={(e) => updatePendingSource(index, 'name', e.currentTarget.value)}
							placeholder="Nombre de la fuente"
							class="input text-sm flex-1 mr-2"
						/>
						<button
							class="p-2 rounded hover:bg-slate-800 text-slate-400 hover:text-red-400"
							on:click={() => removePendingSource(index)}
						>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
							</svg>
						</button>
					</div>

					<div class="flex gap-2">
						<button
							class="flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors {source.type === 'TXT' ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}"
							on:click={() => updatePendingSource(index, 'type', 'TXT')}
						>
							Texto
						</button>
						<button
							class="flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors {source.type === 'URL' ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}"
							on:click={() => updatePendingSource(index, 'type', 'URL')}
						>
							URL
						</button>
						<button
							class="flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors {source.type === 'FILE' ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}"
							on:click={() => updatePendingSource(index, 'type', 'FILE')}
						>
							Archivo
						</button>
					</div>

					{#if source.type === 'TXT'}
						<textarea
							value={source.content}
							on:input={(e) => updatePendingSource(index, 'content', e.currentTarget.value)}
							placeholder="Pega el texto aquí..."
							rows="4"
							class="input resize-none text-sm"
						></textarea>
					{:else if source.type === 'URL'}
						<input
							type="url"
							value={source.content}
							on:input={(e) => updatePendingSource(index, 'content', e.currentTarget.value)}
							placeholder="https://ejemplo.com/pagina"
							class="input text-sm"
						/>
					{:else}
						<input
							type="file"
							class="text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-slate-700 file:text-slate-200 hover:file:bg-slate-600"
						/>
					{/if}
				</div>
			{/each}

			<button
				class="w-full py-3 border-2 border-dashed border-slate-600 rounded-lg text-slate-400 hover:border-slate-500 hover:text-slate-300 transition-colors flex items-center justify-center gap-2"
				on:click={addPendingSource}
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
				</svg>
				Añadir otra fuente
			</button>
		</div>

		<div class="p-4 border-t border-slate-700 flex justify-end gap-3">
			<button class="btn btn-secondary" on:click={handleClose}>
				Cancelar
			</button>
			<button
				class="btn btn-primary"
				on:click={handleSubmit}
				disabled={isProcessing || pendingSources.length === 0}
			>
				{#if isProcessing}
					<span class="flex items-center gap-2">
						<span class="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></span>
						Procesando...
					</span>
				{:else}
					Añadir {pendingSources.length} fuente{pendingSources.length !== 1 ? 's' : ''}
				{/if}
			</button>
		</div>
	</div>
</div>
