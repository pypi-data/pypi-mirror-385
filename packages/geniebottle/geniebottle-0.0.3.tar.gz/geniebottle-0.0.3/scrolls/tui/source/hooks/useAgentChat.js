import { useState, useEffect, useCallback, useRef } from 'react';
import { convertImageToAscii } from '../components/AsciiImageRenderer.js';

/**
 * Custom hook for managing agent chat with SSE streaming
 * @param {string} apiUrl - The API URL for the agent
 * @returns {Object} Chat state and methods
 */
export function useAgentChat(apiUrl) {
	const [messages, setMessages] = useState([]);
	const [isLoading, setIsLoading] = useState(false);
	const [streamingSpells, setStreamingSpells] = useState([]);
	const streamingSpellsRef = useRef([]);
	const [isConnected, setIsConnected] = useState(false);
	const [connectionError, setConnectionError] = useState(null);
	const [messageQueue, setMessageQueue] = useState([]);
	const messageQueueRef = useRef([]);
	const messageIdCounter = useRef(0);

	// Check API connection on mount
	useEffect(() => {
		const checkConnection = async () => {
			try {
				const response = await fetch(`${apiUrl}/health`);
				if (response.ok) {
					setIsConnected(true);
					setConnectionError(null);
				} else {
					throw new Error('Health check failed');
				}
			} catch (error) {
				setIsConnected(false);
				setConnectionError(
					`Cannot connect to agent API at ${apiUrl}\n` +
					`Make sure the agent server is running on port 8080`,
				);
			}
		};

		checkConnection();
	}, [apiUrl]);

	// Use a ref to track loading state for the callback
	const isLoadingRef = useRef(false);

	useEffect(() => {
		isLoadingRef.current = isLoading;
	}, [isLoading]);

	const sendMessage = useCallback(async (userMessage) => {
		if (!userMessage.trim() || !isConnected) return;

		// If currently loading, queue the message
		if (isLoadingRef.current) {
			setMessageQueue(prev => {
				const updated = [...prev, userMessage];
				messageQueueRef.current = updated;
				return updated;
			});
			return;
		}

		setMessages(prev => [...prev, { id: messageIdCounter.current++, role: 'user', content: userMessage }]);
		setIsLoading(true);
		setStreamingSpells([]);
		streamingSpellsRef.current = [];

		try {
			// Use fetch for SSE streaming
			const response = await fetch(`${apiUrl}/cast/agent`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					user_input: userMessage,
				}),
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			// Read SSE stream
			const reader = response.body.getReader();
			const decoder = new TextDecoder();
			let buffer = '';

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				// Decode and add to buffer
				buffer += decoder.decode(value, { stream: true });

				// Process complete SSE messages
				const messages = buffer.split('\n\n');
				buffer = messages.pop() || ''; // Keep incomplete message in buffer

				for (const message of messages) {
					const lines = message.split('\n');
					for (const line of lines) {
						if (line.startsWith('data: ')) {
							const dataStr = line.slice(6); // Remove 'data: ' prefix

							try {
								// Parse the JSON data from the SSE stream
								// Format: {type: "...", payload: ...}
								const event = JSON.parse(dataStr);

								// Just append to the streaming context
								switch (event.type) {
									case 'spell_name':
										if (event.payload !== 'done') {
											setStreamingSpells(prev => {
												const updated = [...prev, {
													spell_name: event.payload,
													spell_args: '',
													spell_response: ''
												}];
												streamingSpellsRef.current = updated;
												return updated;
											});
										}
										break;

									case 'spell_args_chunk':
										// Stream spell args chunks as they arrive
										if (event.payload !== 'done=true') {
											setStreamingSpells(prev => {
												const updated = [...prev];
												if (updated.length > 0) {
													updated[updated.length - 1].spell_args += event.payload;
												}
												streamingSpellsRef.current = updated;
												return updated;
											});
										}
										break;

									case 'spell_args':
										// Final complete spell args (in case chunks weren't sent)
										if (event.payload !== 'done=true') {
											setStreamingSpells(prev => {
												const updated = [...prev];
												if (updated.length > 0) {
													// Only set if we don't already have args from chunks
													if (!updated[updated.length - 1].spell_args) {
														updated[updated.length - 1].spell_args = event.payload;
													}
												}
												streamingSpellsRef.current = updated;
												return updated;
											});
										}
										break;

									case 'output':
										setStreamingSpells(prev => {
											const updated = [...prev];
											if (updated.length > 0) {
												updated[updated.length - 1].spell_response += event.payload;
											}
											streamingSpellsRef.current = updated;
											return updated;
										});
										break;
								}
							} catch (e) {
								// Log parsing errors for debugging
								console.error('Failed to parse SSE data:', dataStr, e);
							}
						}
					}
				}
			}
		} catch (error) {
			const errorMsg = error.message || 'Unknown error';
			setMessages(prev => [
				...prev,
				{
					id: messageIdCounter.current++,
					role: 'error',
					content: `Failed to get response: ${errorMsg}`,
				},
			]);
		} finally {
			// Save the final message using the ref (before clearing it)
			if (streamingSpellsRef.current.length > 0) {
				const spellsToSave = [...streamingSpellsRef.current];

				// Pre-process images to ASCII before saving to messages
				const processedSpells = await Promise.all(
					spellsToSave.map(async (spell) => {
						if (!spell.spell_response) return spell;

						try {
							const parsed = JSON.parse(spell.spell_response);
							if (parsed.type === 'image' && parsed.data) {
								// Convert image to ASCII now, store as processed response
								const ascii = await convertImageToAscii(parsed.data, 20, 10, true);
								return {
									...spell,
									spell_response: JSON.stringify({ type: 'ascii', data: ascii }),
								};
							}
						} catch (e) {
							// Not JSON or conversion failed, keep original
						}

						return spell;
					})
				);

				setMessages(prev => [
					...prev,
					{
						id: messageIdCounter.current++,
						role: 'assistant',
						spells: processedSpells,
					},
				]);
			}

			setIsLoading(false);
			setStreamingSpells([]);
			streamingSpellsRef.current = [];
		}
	}, [isConnected, apiUrl]);

	// Process queued messages when agent becomes available
	useEffect(() => {
		if (!isLoading && messageQueueRef.current.length > 0) {
			const nextMessage = messageQueueRef.current[0];
			setMessageQueue(prev => {
				const updated = prev.slice(1);
				messageQueueRef.current = updated;
				return updated;
			});
			sendMessage(nextMessage);
		}
	}, [isLoading, sendMessage]);

	return {
		messages,
		isLoading,
		streamingSpells,
		isConnected,
		connectionError,
		sendMessage,
		messageQueue,
	};
}
