<script lang="ts">
    import {
            PromptInput,
            PromptInputAction,
            PromptInputActions,
            PromptInputTextarea,
        } from "$lib/components/prompt-kit/prompt-input";
    import {
        Message,
        MessageAvatar,
        MessageContent,
        MessageActions,
        MessageAction
    } from '$lib/components/prompt-kit/message/index.js';
    import { Button } from "$lib/components/ui/button";
    import { ArrowUp, Square, Copy } from "@lucide/svelte";

    interface Message {
        id: string;
        content: string;
        timestamp: string;
        type: 'user' | 'assistant';
    }

    let input = $state("");
    let isLoading = $state(false);
    let messages = $state<Message[]>([]);

    async function handleSubmit() {
        if (!input.trim()) return;
        
        isLoading = true;
        
        const userMessage: Message = {
            id: crypto.randomUUID(),
            content: input,
            timestamp: new Date().toISOString(),
            type: 'user'
        };
        
        messages = [...messages, userMessage];
        const currentInput = input;
        input = "";
        
        try {
            const response = await fetch('/api/agent/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input: currentInput })
            });
            
            if (!response.ok) {
                throw new Error('Failed to get response');
            }
            
            const data = await response.json();
            
            const assistantMessage: Message = {
                id: crypto.randomUUID(),
                content: data.content,
                timestamp: data.timestamp || new Date().toISOString(),
                type: 'assistant'
            };
            
            messages = [...messages, assistantMessage];
        } catch (error) {
            console.error('Error:', error);
            const errorMessage: Message = {
                id: crypto.randomUUID(),
                content: 'Sorry, there was an error processing your request.',
                timestamp: new Date().toISOString(),
                type: 'assistant'
            };
            messages = [...messages, errorMessage];
        } finally {
            isLoading = false;
        }
    }
    
    function handleValueChange(value: string) {
        input = value;
    }
    
    function handleCopy(content: string) {
        navigator.clipboard.writeText(content);
    }
</script>

<div class="flex flex-1 flex-col">
	<div class="flex-1 overflow-y-auto p-4">
		<div class="mx-auto max-w-4xl">
			<div class="flex flex-col gap-8">
				{#each messages as message}
					{#if message.type === 'user'}
						<Message class="justify-end">
							<MessageContent>{message.content}</MessageContent>
						</Message>
					{:else}
						<Message class="justify-start">
							<MessageAvatar src="/avatars/ai.png" alt="AI" fallback="AI" />
							<div class="flex flex-col gap-2">
								<MessageContent class="bg-transparent p-0">
									{message.content}
								</MessageContent>

								<MessageActions>
									<MessageAction>
										{#snippet tooltip()}
											Copy
										{/snippet}
										<Button
											variant="ghost"
											size="icon"
											class="h-8 w-8"
											onclick={() => handleCopy(message.content)}
										>
											<Copy class="h-4 w-4" />
										</Button>
									</MessageAction>
								</MessageActions>
							</div>
						</Message>
					{/if}
				{/each}
			</div>
		</div>
	</div>
	<div class="p-4">
		<div class="mx-auto max-w-4xl">
			<PromptInput
				value={input}
				onValueChange={handleValueChange}
				{isLoading}
				onSubmit={handleSubmit}
				class="w-full"
			>
				<PromptInputTextarea placeholder="Ask me anything..." />
				<PromptInputActions class="justify-end pt-2">
					<PromptInputAction>
						{#snippet tooltip()}
							{isLoading ? "Stop generation" : "Send message"}
						{/snippet}
						<Button
							variant="default"
							size="icon"
							class="h-8 w-8 rounded-full"
							onclick={handleSubmit}
						>
							{#if isLoading}
								<Square class="size-5 fill-current" />
							{:else}
								<ArrowUp class="size-5" />
							{/if}
						</Button>
					</PromptInputAction>
				</PromptInputActions>
			</PromptInput>
		</div>
	</div>
</div>
