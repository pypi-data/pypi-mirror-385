import React from 'react';
import { Box, Text, Static } from 'ink';
import Spinner from 'ink-spinner';
import { marked } from 'marked';
import { markedTerminal } from 'marked-terminal';
import { SpellResponse } from './SpellResponse.js';
import { Header } from './Header.js';
import { WelcomeMessage } from './WelcomeMessage.js';
import { SpellCastingSymbol } from './SpellCastingSymbol.js';

// Configure marked to use terminal renderer
marked.use(markedTerminal());

/**
 * Renders a list of spells (for both streaming and saved messages)
 */
function SpellList({ spells, isStreaming = false }) {
	if (!spells || spells.length === 0) return null;

	return (
		<Box flexDirection="column">
			{spells.map((spell, idx) => {
				const isLastSpell = idx === spells.length - 1;
				const isComplete = spell.spell_response && spell.spell_response !== '';
				const isAnimating = isStreaming && isLastSpell && !isComplete;

				return (
					<Box key={idx} flexDirection="column" marginBottom={1}>
						<Box>
							<SpellCastingSymbol isComplete={isComplete} isAnimating={isAnimating} />
							<Text color="cyan"> {spell.spell_name}</Text>
						</Box>
						{spell.spell_args && (
							<Box paddingLeft={2} marginBottom={1}>
								<Text dimColor>{marked.parse(spell.spell_args.replace(/\\n/g, '\n')).trim()}</Text>
							</Box>
						)}
						{spell.spell_response && <SpellResponse spellResponse={spell.spell_response} />}
					</Box>
				);
			})}
		</Box>
	);
}

/**
 * Message list component that displays all messages and streaming content
 * Uses Static component to prevent re-rendering of old messages (fixes UI shaking)
 * @param {string} apiUrl - API URL for header
 * @param {boolean} isConnected - Connection status for header
 * @param {Array} messages - Array of message objects
 * @param {Array} streamingSpells - Current streaming spells
 * @param {boolean} isLoading - Whether currently loading
 */
export function MessageList({ apiUrl, isConnected, messages, streamingSpells, isLoading }) {
	// Create static items array with header first, then welcome message (if no messages), then messages
	const staticItems = [
		{ id: 'header', type: 'header', apiUrl, isConnected },
		...(messages.length === 0 && !isLoading ? [{ id: 'welcome', type: 'welcome' }] : []),
		...messages,
	];

	return (
		<Box flexDirection="column">
			{/* Static component prevents re-rendering old messages, reducing UI shake */}
			<Static items={staticItems}>
				{(item) => {
					if (item.type === 'header') {
						return <Header key={item.id} apiUrl={item.apiUrl} isConnected />;
					}
					if (item.type === 'welcome') {
						return <WelcomeMessage key={item.id} />;
					}
					// Regular message
					return (
						<Box key={item.id} flexDirection="column">
							{item.role === 'user' && (
								<Box marginBottom={1}>
									<Text>{item.content}</Text>
								</Box>
							)}
							{item.role === 'assistant' && <SpellList spells={item.spells} />}
							{item.role === 'error' && (
								<Text color="red">❌ Error: {item.content}</Text>
							)}
						</Box>
					);
				}}
			</Static>

			{/* Streaming content is rendered separately below static messages */}
			{isLoading && streamingSpells.length === 0 && (
				<Box flexDirection="column" marginBottom={1}>
					<Text color="yellow">
						<Spinner type="dots" />
					</Text>
				</Box>
			)}
			{isLoading && streamingSpells.length > 0 && (
				<Box flexDirection="column">
					<SpellList spells={streamingSpells} isStreaming={true} />
				</Box>
			)}
		</Box>
	);
}
