export type WorkoutType = '!throw' | '!gym' | '!cardio' | '!workout' | '!other';
export const toWorkoutType = (s: string): WorkoutType => {
    const allowedKeys: string[] = [
        '!throw',
        '!gym',
        '!cardio',
        '!workout',
        '!other',
    ];
    return allowedKeys.includes(s) ? (s as WorkoutType) : '!other';
};

export type WorkoutTimeCountData = {
    [w in WorkoutType]: number;
} & {
    date: number;
    total: number;
};

export interface WorkoutData {
    name: string;
    type: WorkoutType;
    date: number;
    url: string | null;
}
