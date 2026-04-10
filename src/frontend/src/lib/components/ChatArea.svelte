<script lang="ts">
	import { onMount, afterUpdate } from 'svelte';
	import { api, type ChatMessage } from '$lib/api/client';
	import { chatStore } from '$lib/stores/chat';
	import MessageBubble from './MessageBubble.svelte';

	export let chestId: string;
	export let sources: { id: string; name: string; is_enabled: boolean }[];

	let messages: ChatMessage[] = [];
	let inputValue = '';
	let isStreaming = false;
	let currentResponse = '';
	let chatContainer: HTMLDivElement;

	chatStore.subscribe((m) => (messages = m));
	chatStore.isStreaming.subscribe((v) => (isStreaming = v));
	chatStore.currentResponse.subscribe((v) => (currentResponse = v));

	afterUpdate(() => {
		if (chatContainer) {
			chatContainer.scrollTop = chatContainer.scrollHeight;
		}
	});

	async function sendMessage() {
		if (!inputValue.trim() || isStreaming) return;

		const userMessage = inputValue.trim();
		inputValue = '';
		chatStore.addUserMessage(userMessage);
		chatStore.setStreaming(true);
		currentResponse = '';

		try {
			let fullResponse = '';

			for await (const event of api.chat(chestId, userMessage)) {
				if (event.type === 'token') {
					fullResponse += event.content;
					chatStore.appendResponse(event.content);
				}
			}

			if (fullResponse) {
				chatStore.addAssistantMessage(fullResponse);
			}
		} catch (error) {
			console.error('Chat error:', error);
		} finally {
			chatStore.setStreaming(false);
			chatStore.clearResponse();
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			sendMessage();
		}
	}
</script>

<main class="flex-1 flex flex-col overflow-hidden">
	<div class="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-4" bind:this={chatContainer}>
		{#if messages.length === 0}
			<div class="flex flex-col items-center justify-center h-full text-slate-500">
				<svg class="w-16 h-16 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
				</svg>
				<p>Envía un mensaje para empezar la conversación</p>
				{#if sources.filter(s => s.is_enabled).length === 0}
					<p class="text-sm mt-2">Añade fuentes al cofre para obtener respuestas basadas en ellas</p>
				{/if}
			</div>
		{:else}
			{#each messages as msg (msg.id)}
				<MessageBubble {msg} />
			{/each}

			{#if isStreaming && currentResponse}
				<div class="flex gap-3">
					<div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
						</svg>
					</div>
					<div class="bg-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 max-w-xl">
						<p class="text-slate-200 whitespace-pre-wrap">{currentResponse}<span class="animate-pulse">▍</span></p>
					</div>
				</div>
			{/if}
		{/if}
	</div>

	<div class="flex-shrink-0 p-4 border-t border-slate-700">
		<div class="flex gap-3 max-w-4xl mx-auto">
			<textarea
				bind:value={inputValue}
				on:keydown={handleKeydown}
				placeholder="Escribe tu pregunta..."
				rows="1"
				class="input resize-none flex-1"
				disabled={isStreaming}
			></textarea>
			<button
				class="btn btn-primary px-6"
				on:click={sendMessage}
				disabled={isStreaming || !inputValue.trim()}
			>
				{isStreaming ? '...' : 'Enviar'}
			</button>
		</div>
	</div>
</main>
