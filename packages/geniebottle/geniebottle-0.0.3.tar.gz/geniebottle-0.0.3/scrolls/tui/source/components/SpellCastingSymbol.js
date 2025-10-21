import React, { useState, useEffect } from 'react';
import { Text } from 'ink';

/**
 * Animated spell casting symbol component
 * Cycles through casting animation: . * ･ ｡ﾟ
 * Shows solid circle ● when finished
 */
export function SpellCastingSymbol({ isComplete, isAnimating }) {
	const [frameIndex, setFrameIndex] = useState(0);
	const castingFrames = ['.', '*', '･', '｡ﾟ'];

	useEffect(() => {
		if (!isAnimating) return;

		const interval = setInterval(() => {
			setFrameIndex((prev) => (prev + 1) % castingFrames.length);
		}, 200);

		return () => clearInterval(interval);
	}, [isAnimating, castingFrames.length]);

	let symbol;
	if (isComplete) {
		symbol = '●';
	} else if (isAnimating) {
		symbol = castingFrames[frameIndex];
	} else {
		symbol = castingFrames[0];
	}

	return <Text color="cyan">{symbol}</Text>;
}
