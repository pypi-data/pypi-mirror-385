import React from 'react';
import { Box, Text } from 'ink';

/**
 * Welcome message shown when there are no messages yet
 */
export function WelcomeMessage() {
	return (
		<Box flexDirection="column" paddingLeft={2} marginBottom={1}>
			<Text color="magenta">Welcome! Ask me to do anything:</Text>
			<Text dimColor>  • Generate images or text</Text>
			<Text dimColor>  • Search and edit files</Text>
			<Text dimColor>  • Run terminal commands</Text>
			<Text dimColor>  • Search codebases</Text>
			<Text />
		</Box>
	);
}
