import { WorkoutData } from './types';

export const getAvatar = (data: WorkoutData[]): WorkoutData | null => {
    const hasUrl = data.filter((w) => w.url);
    if (hasUrl.length === 0) return null;
    return choose(hasUrl);
};

export const choose = <T>(arr: T[]): T => {
    return arr[Math.floor(Math.random() * arr.length)];
};
