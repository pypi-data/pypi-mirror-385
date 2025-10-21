import React from 'react';
import { Box, Text } from 'ink';
import TextInput from 'ink-text-input';

/**
 * Chat input component
 * @param {string} value - Current input value
 * @param {function} onChange - Input change handler
 */
export function ChatInput({ value, onChange }) {
	return (
		<Box flexShrink={0}>
			<Text color="green" bold>
				{'> '}
			</Text>
			<TextInput
				value={value}
				onChange={onChange}
				placeholder="Ask me to do anything..."
				showCursor={true}
			/>
		</Box>
	);
}
