#!/usr/bin/env node
import React from 'react';
import {render} from 'ink';
import meow from 'meow';
import App from './app.js';

const cli = meow(
	`
		Usage
		  $ tui

		Options
			--api-url  Agent API URL (default: http://127.0.0.1:8080)

		Examples
		  $ tui
		  $ tui --api-url=http://localhost:3000
	`,
	{
		importMeta: import.meta,
		flags: {
			apiUrl: {
				type: 'string',
				default: 'http://127.0.0.1:8080',
			},
		},
	},
);

render(<App apiUrl={cli.flags.apiUrl} />);
