import React, { useState } from 'react';
import { Box, Text, useInput, useApp } from 'ink';
import { useAgentChat } from './hooks/useAgentChat.js';
import {
	ConnectionError,
	MessageList,
	ChatInput,
} from './components/index.js';

export default function App({ apiUrl = 'http://127.0.0.1:8080' }) {
	const { exit } = useApp();
	const [input, setInput] = useState('');

	const {
		messages,
		isLoading,
		streamingSpells,
		isConnected,
		connectionError,
		sendMessage,
		messageQueue,
	} = useAgentChat(apiUrl);

	// Handle Ctrl+C gracefully
	useInput((input, key) => {
		if (key.ctrl && input === 'c') {
			exit();
		}
	});

	// Handle enter key to send message
	useInput(
		(_, key) => {
			if (key.return) {
				const userMessage = input.trim();
				setInput('');
				if (userMessage) {
					sendMessage(userMessage);
				}
			}
		},
		{ isActive: true }, // Always allow sending messages (they'll be queued if loading)
	);

	// Show connection error screen
	if (connectionError) {
		return <ConnectionError errorMessage={connectionError} />;
	}

	// Main chat interface
	return (
		<Box flexDirection="column" height="100%" paddingX={0}>
			{/* Scrollable content area */}
			<Box flexDirection="column" flexGrow={1} flexShrink={1} overflow="hidden">
				{/* Messages and streaming content (includes header at top) */}
				<MessageList
					apiUrl={apiUrl}
					isConnected={isConnected}
					messages={messages}
					streamingSpells={streamingSpells}
					isLoading={isLoading}
				/>
			</Box>

			{/* Queued messages - above input */}
			{messageQueue.length > 0 && (
				<Box flexShrink={0} marginTop={1}>
					<Text dimColor>Queued: {messageQueue.join(', ')}</Text>
				</Box>
			)}

			{/* Input - always at bottom */}
			<ChatInput value={input} onChange={setInput} />
		</Box>
	);
}
