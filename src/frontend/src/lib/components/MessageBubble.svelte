<script lang="ts">
	import type { ChatMessage } from '$lib/api/client';

	export let msg: ChatMessage;

	const isUser = msg.role === 'USER';
</script>

<div class="flex gap-3 {isUser ? 'flex-row-reverse' : ''}">
	{#if !isUser}
		<div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
			<svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
			</svg>
		</div>
	{/if}

	<div class="max-w-xl {isUser ? 'text-right' : ''}">
		<div class="{isUser ? 'bg-blue-600' : 'bg-slate-800'} rounded-2xl px-4 py-3 {isUser ? 'rounded-tr-sm' : 'rounded-tl-sm'}">
			<p class="text-slate-100 whitespace-pre-wrap">{msg.content}</p>
		</div>
		<p class="text-xs text-slate-500 mt-1 px-1">
			{new Date(msg.created_at).toLocaleTimeString()}
		</p>
	</div>

	{#if isUser}
		<div class="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center flex-shrink-0">
			<svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
			</svg>
		</div>
	{/if}
</div>
