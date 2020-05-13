import { theme, CustomTheme, DefaultTheme } from '@chakra-ui/core';
import { WorkoutType, workoutTypeFill } from './types';

// Let's say you want to add custom colors
const customTheme = {
    ...theme,
    fonts: {
        ...theme.fonts,
        body: 'Nunito, sans-serif',
        heading: 'Nunito, sans-serif',
    },
    colors: {
        ...theme.colors,
        brand: {
            900: '#1a365d',
            800: '#153e75',
            700: '#2a69ac',
        },
    },
};

export const workoutTypeVariantColors: Record<WorkoutType, string> = {
    '!throw': 'red',
    '!gym': 'orange',
    '!workout': 'yellow',
    '!cardio': 'green',
    '!bike': 'blue',
    '!track': 'purple',
    '!pickup': 'teal',
    '!run': 'cyan',
    '!other': 'gray',
};

export const workoutTypeColors: Record<WorkoutType, string> = {
    ...workoutTypeFill(
        (t: WorkoutType) =>
            theme.colors[
                workoutTypeVariantColors[t] as keyof DefaultTheme['colors']
            ][300],
    ),
};

export default customTheme;
