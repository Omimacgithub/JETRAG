<script>
	export let message;
	
	function getRoleClass(role) {
		return role === 'USER' ? 'ml-auto bg-blue-500 bg-opacity-20' : 'mr-auto bg-gray-500 bg-opacity-10';
	}
	
	function getAvatarColor(role) {
		return role === 'USER' ? 'blue' : 'gray';
	}
	
	function formatTimestamp(timestamp) {
		if (!timestamp) return '';
		const date = new Date(timestamp);
		return date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
	}
</script>

<div class="flex mb-2 max-w-[80%]">
	{#if message.role === 'ASSISTANT'}
		<div class="flex-shrink-0">
			<div class="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center text-gray-600">
				🤖
			</div>
		</div>
	{/if}
	
	<div class="flex-1 ml-2">
		<div class="flex justify-between mb-1">
			<div class="font-medium">
				{#if message.role === 'USER'}
					You
				{:else}
					Assistant
				{/if}
			</div>
			<div class="text-xs text-gray-500">
				{formatTimestamp(message.timestamp)}
			</div>
		</div>
		<div 
			class={`p-3 rounded-lg max-w-xl break-words ${getRoleClass(message.role)}`}
		>
			{message.content}
			
			{#if message.role === 'ASSISTANT' && message.sourcesUsed && message.sourcesUsed.length > 0}
				<div class="mt-2 pt-2 border-t border-gray-200">
					<p class="text-xs font-medium text-gray-600">Sources used:</p>
					<ul class="text-xs space-y-1 pl-4 list-disc">
						{#if message.sourcesUsed.length > 0}
							{#each message.sourcesUsed as sourceId}
								<li>Source #{sourceId}</li>
							{/each}
						{:else}
							<li>Unknown sources</li>
						{/if}
					</ul>
				</div>
			{/if}
		</div>
	</div>
	
	{#if message.role === 'USER'}
		<div class="flex-shrink-0">
			<div class="h-8 w-8 rounded-full bg-blue-300 flex items-center justify-center text-white">
				👤
			</div>
		</div>
	{/if}
</div>