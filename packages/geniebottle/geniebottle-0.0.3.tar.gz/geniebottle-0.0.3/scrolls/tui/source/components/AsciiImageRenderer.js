import React, { useState, useEffect } from 'react';
import { Text, Box } from 'ink';
import sharp from 'sharp';
import chalk from 'chalk';

/**
 * Utility function to convert image to ASCII (can be called outside React)
 */
export async function convertImageToAscii(src, width = 40, height = 20, colored = true) {
	try {
		// Convert base64 string to buffer if needed
		let imageBuffer;
		if (typeof src === 'string') {
			imageBuffer = Buffer.from(src, 'base64');
		} else {
			imageBuffer = src;
		}

		// Convert to ASCII using sharp
		const image = sharp(imageBuffer);
		const resizedImage = await image
			.resize(width, height, { fit: 'fill' })
			.raw()
			.toBuffer({ resolveWithObject: true });

		return imageToAscii(resizedImage, colored);
	} catch (e) {
		throw new Error(`Failed to convert image: ${e.message}`);
	}
}

/**
 * ASCII Image Rendering Component
 *
 * Converts images to ASCII art using character-based representation.
 * Works in all terminals without requiring TerminalInfoProvider.
 *
 * Based on src/components/image/Ascii.tsx but way more minimal
 * (doesn't need any terminal detection logic that screws with
 * text inputs. Runs anywhere!)
 *
 * @param {string|Buffer} src - Image source (base64 string or Buffer)
 * @param {number} width - Width in characters (default: 40)
 * @param {number} height - Height in characters (default: 40)
 */
export function AsciiImageRenderer({ src, width = 40, height = 20 }) {
	const [asciiArt, setAsciiArt] = useState(null);
	const [error, setError] = useState(null);

	useEffect(() => {
		const convertToAscii = async () => {
			try {
				// Convert base64 string to buffer if needed
				let imageBuffer;
				if (typeof src === 'string') {
					// Assume it's base64
					imageBuffer = Buffer.from(src, 'base64');
				} else {
					// Already a buffer
					imageBuffer = src;
				}

				// Convert to ASCII using sharp
				const image = sharp(imageBuffer);

				const resizedImage = await image
					.resize(width, height, { fit: 'fill' })
					.raw()
					.toBuffer({ resolveWithObject: true });

				const ascii = imageToAscii(resizedImage, true);
				setAsciiArt(ascii);
			} catch (e) {
				setError(e.message);
			}
		};

		convertToAscii();
	}, [src, width, height]);

	if (error) {
		return (
			<Box>
				<Text color="red">Failed to render image: {error}</Text>
			</Box>
		);
	}

	if (!asciiArt) {
		return (
			<Box>
				<Text color="gray">Loading...</Text>
			</Box>
		);
	}

	return (
		<Box flexDirection="column">
			{asciiArt.split('\n').map((line, idx) => (
				<Text key={idx}>{line}</Text>
			))}
		</Box>
	);
}

/**
 * Convert image data to ASCII art
 */
function imageToAscii(imageData, colored = true) {
	const { data, info } = imageData;
	const { width, height, channels } = info;

	// ASCII characters ordered by brightness (darkest to lightest)
	const asciiChars =
		"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ";

	let result = '';
	for (let y = 0; y < height; y++) {
		for (let x = 0; x < width; x++) {
			const pixelIndex = (y * width + x) * channels;

			const r = data[pixelIndex] || 0;
			const g = data[pixelIndex + 1] || 0;
			const b = data[pixelIndex + 2] || 0;
			const a = channels === 4 ? (data[pixelIndex + 3] || 0) : 255;

			// Calculate intensity
			const intensity = (r + g + b + a) === 0 ? 0 : (r + g + b + a) / (255 * 4);
			const charIndex = Math.floor(intensity * (asciiChars.length - 1));
			const pixelChar = asciiChars[asciiChars.length - 1 - charIndex];

			result += colored ? chalk.rgb(r, g, b)(pixelChar) : pixelChar;
		}
		result += '\n';
	}

	return result;
}
