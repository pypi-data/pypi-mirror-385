import React from 'react';
import { Box, Text } from 'ink';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Get version from package.json
 */
function getVersion() {
	try {
		// Try to read from Python package
		const aboutPath = path.join(__dirname, '../../../magic/__about__.py');
		if (fs.existsSync(aboutPath)) {
			const content = fs.readFileSync(aboutPath, 'utf-8');
			const match = content.match(/__version__\s*=\s*["']([^"']+)["']/);
			if (match) {
				return match[1];
			}
		}
	} catch (error) {
		// Ignore errors
	}

	return '0.0.1';
}

/**
 * Get current working directory
 */
function getCwd() {
	const cwd = process.cwd();
	const home = process.env.HOME || process.env.USERPROFILE || '';

	// Replace home directory with ~
	if (home && cwd.startsWith(home)) {
		return '~' + cwd.slice(home.length);
	}

	return cwd;
}

/**
 * Header component for the Genie Agent Chat
 */
export function Header({ apiUrl, isConnected }) {
	const version = getVersion();
	const cwd = getCwd();

	// Construct docs URL from apiUrl (same host/port but /docs path)
	let docsUrl = '';
	if (apiUrl) {
		try {
			const url = new URL(apiUrl);
			docsUrl = `${url.protocol}//${url.host}/docs`;
		} catch {
			docsUrl = 'http://127.0.0.1:8080/docs';
		}
	}

	return (
		<Box flexDirection="column" marginBottom={1}>
			<Box>
				<Box flexDirection="column" marginRight={2}>
					<Text color="cyan">    ~.    </Text>
					<Text color="cyan"> o  (")  o</Text>
					<Text color="cyan"> `-^' `^-'</Text>
					<Text color="cyan">    \ /   </Text>
					<Text color="cyan">     )    </Text>
					<Text color="green">    )(   </Text>
					<Text color="green">   (__)  </Text>
				</Box>
				<Box flexDirection="column">
					<Text bold color="cyan">
						Genie
					</Text>
					<Text dimColor>tui scroll v{version}</Text>
					<Text dimColor>{cwd}</Text>
					{apiUrl && (
						<Box marginTop={1}>
							<Text dimColor>Server: </Text>
							<Text color={isConnected ? 'green' : 'red'}>
								{isConnected ? '● ' : '○ '}
							</Text>
							<Text dimColor>{apiUrl}</Text>
						</Box>
					)}
					{docsUrl && (
						<Text dimColor>Docs: {docsUrl}</Text>
					)}
				</Box>
			</Box>
		</Box>
	);
}
