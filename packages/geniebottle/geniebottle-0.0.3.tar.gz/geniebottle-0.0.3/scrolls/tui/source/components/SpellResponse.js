import React from 'react';
import { Text, Box } from 'ink';
import { marked } from 'marked';
import { markedTerminal } from 'marked-terminal';
import { AsciiImageRenderer } from './AsciiImageRenderer.js';

// Configure marked to use terminal renderer globally
marked.use(markedTerminal());

/**
 * Component to render a spell response, detecting if it's an image or text
 */
export function SpellResponse({ spellResponse }) {
	if (!spellResponse) return null;

	// Check if spell_response is an image or pre-processed ASCII (JSON format from backend)
	// Parse synchronously to avoid state issues
	let imageData = null;
	let asciiData = null;
	try {
		const parsed = JSON.parse(spellResponse);
		if (parsed.type === 'image' && parsed.data) {
			// Pass base64 string directly to renderer (for streaming)
			imageData = parsed.data;
		} else if (parsed.type === 'ascii' && parsed.data) {
			// Pre-processed ASCII art (for static messages)
			asciiData = parsed.data;
		}
	} catch (e) {
		// Not JSON, treat as regular text
	}

	if (asciiData) {
		// Render pre-processed ASCII directly
		return (
			<Box flexDirection="column">
				{asciiData.split('\n').map((line, idx) => (
					<Text key={idx}>{line}</Text>
				))}
			</Box>
		);
	}

	if (imageData) {
		// Render image using async component (for streaming only)
		return <AsciiImageRenderer src={imageData} width={20} height={10} />;
	}

	// Truncate long responses (like base64) for display
	let displayText = spellResponse.length > 30000
		? spellResponse.substring(0, 30000) + '... [truncated]'
		: spellResponse;

	// Replace literal \n strings with actual newlines
	displayText = displayText.replace(/\\n/g, '\n');

	// Parse markdown - markedTerminal returns ANSI-formatted text
	const rendered = marked.parse(displayText).trim();

	// Split by newlines and render each line separately
	// This ensures Ink properly displays multi-line ANSI content
	const lines = rendered.split('\n');

	return (
		<Box flexDirection="column">
			{lines.map((line, idx) => (
				<Text key={idx}>{line}</Text>
			))}
		</Box>
	);
}
