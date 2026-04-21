<script>
	import MessageBubble from './MessageBubble.svelte';
	import { chatMessages } from '../stores/chat';
	import { chatAPI } from '../api/client';
	
	let messageInput = '';
	let isSubmitting = false;
	let isLoading = false;
	export let chestId;
	
	async function handleSubmit() {
		if (!messageInput.trim() || isSubmitting) return;
		
		isSubmitting = true;
		isLoading = true;
		
		// Add user message to chat
		const userMessage = {
			id: Date.now(), // Temporary ID
			role: 'USER',
			content: messageInput,
			timestamp: new Date()
		};
		
		// Update chat store (in a real app, we'd also persist to backend)
		chatMessages.update(messages => [...messages, userMessage]);
		
		// Clear input
		const input = messageInput;
		messageInput = '';
		
		try {
			// Send message to backend and get response
			const ragQuery = {
				question: input,
				chest_id: chestId
			};
			
			const response = await chatAPI.query(ragQuery);
			
			// Add assistant message to chat
			const botMessage = {
				id: Date.now() + 1, // Temporary ID
				role: 'ASSISTANT',
				content: response.answer,
				timestamp: new Date(),
				sourcesUsed: response.sources_used
			};
			
			chatMessages.update(messages => [...messages, botMessage]);
		} catch (error) {
			console.error('Error processing query:', error);
			
			// Add error message to chat
			const errorMessage = {
				id: Date.now() + 1, // Temporary ID
				role: 'ASSISTANT',
				content: `Sorry, I encountered an error: ${error.message}`,
				timestamp: new Date(),
				sourcesUsed: []
			};
			
			chatMessages.update(messages => [...messages, errorMessage]);
		} finally {
			isSubmitting = false;
			isLoading = false;
		}
	}
	
	function handleKeyPress(event) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSubmit();
		}
	}
</script>

<div class="flex flex-col h-[600px] border rounded p-4 overflow-y-auto mb-4">
	{#if $chatMessages.length === 0}
		<div class="flex flex-col items-center justify-center h-full text-gray-500">
			<p>Start a conversation by asking a question...</p>
		</div>
	{:else}
		<div class="flex flex-col space-y-3">
			{#each $chatMessages as message (message.id)}
				<MessageBubble {message} />
			{/each}
		</div>
		{#if isLoading}
			<div class="flex items-center justify-center py-2">
				<span class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></span>
				<span class="ml-2 text-sm">Thinking...</span>
			</div>
		{/if}
	{/if}
</div>

<div class="flex gap-2">
	<textarea 
		id="message-input"
		bind:value={messageInput}
		placeholder="Type a message..."
		class="flex-1 min-h-[60px] p-3 border rounded resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
		on:keydown={handleKeyPress}
		disabled={isSubmitting}
		rows="1"
	/>
	<button 
		on:click={handleSubmit}
		disabled={!messageInput.trim() || isSubmitting || isLoading}
		class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded disabled:opacity-50"
	>
		{isSubmitting ? 'Sending...' : 'Send'}
	</button>
</div>