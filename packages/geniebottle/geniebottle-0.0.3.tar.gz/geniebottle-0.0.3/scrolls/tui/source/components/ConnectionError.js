import React from 'react';
import { Box, Text } from 'ink';

/**
 * Connection error screen
 * @param {string} errorMessage - The error message to display
 */
export function ConnectionError({ errorMessage }) {
	return (
		<Box flexDirection="column" padding={1}>
			<Box
				borderStyle="round"
				borderColor="red"
				padding={1}
				marginBottom={1}
			>
				<Text color="red" bold>
					⚠️ Connection Error
				</Text>
			</Box>
			<Box flexDirection="column" paddingLeft={2}>
				<Text color="red">{errorMessage}</Text>
				<Text dimColor marginTop={1}>
					Press Ctrl+C to exit
				</Text>
			</Box>
		</Box>
	);
}
