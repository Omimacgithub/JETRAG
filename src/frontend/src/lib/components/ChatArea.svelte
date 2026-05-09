<style>

.autoscroll {
  display: flex;
  flex-direction: column;
  height: 600px;
  border-width: 1px;
  border-style: solid;
  border-color: #d1d5db; /* Tailwind default gray-300 */
  border-radius: 0.25rem; /* Tailwind rounded = 4px */
  padding: 1rem; /* p-4 */
  overflow-y: auto;
  margin-bottom: 1rem; /* mb-4 */
}

</style>
<script lang='ts'>
	import MessageBubble from './MessageBubble.svelte';
	//import { chatMessages } from '../stores/chat';
	import { writable } from 'svelte/store';
	import { chatAPI } from '../api/client';
	import { browser } from '$app/environment';
    import { onMount } from 'svelte';
	
	//The bottom console log enables MessageBubble to be loaded, otherwise ReferenceError :P 
	console.log(MessageBubble);

	let messageInput = '';
	let isSubmitting = false;
	let isLoading = false;
	let streamingContent = '';
	let isStreaming = false;
	let currentStreamingId : number = 0;
	export let chestId : number;
	//let messageId = 0;

	function getAllItems() {
		try {
			var values = [], 
			//Because localStorage keys don't follow any order, we sort the keys in order to print chat messages accordingly
			keys = Object.keys(localStorage).sort(), 
			top = keys.length, 
			i=0;

			if (top<1) {
				return [];
			}
	
			while ( i < top ) {
				const item = JSON.parse(localStorage.getItem(keys[i]));
				values.push( item );
				i++;
				//values[0].content;
			}

			return values;

		} catch (e) {
			console.error('Error while retrieving items:', e);
		}
	}

	function storeMessage(message) {
		//console.log("MESSAGE TO STORE (should be JSON object): ", message)
		try {
			//Example localStorage.setItem(14, JSON.stringify({id: 0, chest_id: 2, role: 'USER', content: 'Hey', created_at: '14'}))
			localStorage.setItem(message.id, JSON.stringify(message));
		} catch (e) {
			console.error('Error storing message:', e);
		}
	}

	let values = [];
	
	//Ensure the bottom code is executed on browser context (not server)
	if (browser){
		values = getAllItems();
	}
	
	let chatMessages = writable<Array<{
		id: number;
		chest_id: number;
		role: 'USER' | 'ASSISTANT';
		content: string;
		sources_used: number[] | null;
		timestamp: string;
		is_streaming: boolean;
	}>>(values);
	
	chatMessages.subscribe((value) => {
		//console.log(value)
		if (browser && value.length > 0) {
			let lastOnTheList = value[value.length-1]
			//console.log(JSON.stringify(lastOnTheList))
			storeMessage(lastOnTheList);	
		}
	});
	
	async function handleSubmit() {
		if (!messageInput.trim() || isSubmitting) return;
		
		isSubmitting = true;
		isLoading = true;
		isStreaming = true;
		streamingContent = '';
		
		const userMessage = {
			id: Date.now(),
			role: 'USER',
			content: messageInput,
			timestamp: new Date()
		};
		
		
		chatMessages.update((messages) => [...messages, userMessage]);
		/*for (const msg of $chatMessages){
			console.log(JSON.stringify(msg))
		}*/
		
		const input = messageInput;
		messageInput = '';
		
		currentStreamingId = Date.now() + 1;
		
		const assistantMessage = {
			id: currentStreamingId,
			role: 'ASSISTANT',
			content: '',
			timestamp: new Date(),
			sources_used: [],
			is_streaming: true
		};
		
		chatMessages.update((messages) => [...messages, assistantMessage]);
		
		
		try {
			const ragQuery = {
				question: input,
				chest_id: chestId
			};
			
			await chatAPI.streamQuery(
				ragQuery,
				(chunk) => {
					streamingContent += chunk;
					//console.log(streamingContent);
		/*			chatMessages.update(messages => {
messages[messages.length-1].content = streamingContent;
//console.log("LENGTH: "  + messages.length);
					});
*/
					
					chatMessages.update(messages => 
						messages.map(m => 
							m.id === currentStreamingId 
								? { ...m, content: streamingContent }
								: m
						)
					);
					//console.log("Streaming content: " + streamingContent);
					//console.log("Chat messages list: " + $chatMessages);
				
				},
				() => {
/*					chatMessages.update(messages => {
						messages[messages.length-1].is_streaming = false;
						//messages[messages.length-1].sources_used = [];
					});
*/
					
					chatMessages.update(messages => 
						messages.map(m => 
							m.id === currentStreamingId 
								? { ...m, is_streaming: false, sources_used: [] }
								: m
						)
					);
					
					isStreaming = false;
					isLoading = false;
					isSubmitting = false;
				}
			);
		} catch (error) {
			console.error('Error processing query:', error);
			
			const errorMessage = {
				id: Date.now() + 2,
				role: 'ASSISTANT',
				content: `Sorry, I encountered an error: ${error.message}`,
				timestamp: new Date(),
				sources_used: []
			};
			
			chatMessages.update(messages => [...messages, errorMessage]);
			
			isStreaming = false;
			isLoading = false;
			isSubmitting = false;
		}
	}
	
	function handleKeyPress(event) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSubmit();
		}
	}
	
	//Code to autoscroll down to the last chat messages (https://medium.com/@heatherbooker/how-to-auto-scroll-to-the-bottom-of-a-div-415e967e7a24)
	onMount(() => {
		if (browser) {
			var someElement = document.querySelector(".autoscroll");
			function scrollToBottom() {
				someElement.scrollTop = someElement.scrollHeight;
			}
			var observer = new MutationObserver(scrollToBottom);
			var config = { childList: true, subtree: true, characterData: true };
			observer.observe(someElement, config);
		}
	});
	
</script>

<div class="autoscroll">
	{#if $chatMessages.length === 0 && !isStreaming}
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
				<span class="ml-2 text-sm">
					{isStreaming ? 'Generating response...' : 'Thinking...'}
				</span>
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