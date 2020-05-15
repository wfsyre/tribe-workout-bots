export const TEAM_NAME = 'Tribe';

export const WORKOUTS = [
    '!throw',
    '!gym',
    '!workout',
    '!cardio',
    '!track',
    '!bike',
    '!pickup',
    '!run',
    '!other',
] as const;

export type WorkoutType = typeof WORKOUTS[number];

export const toWorkoutType = (s: string): WorkoutType => {
    if (!(WORKOUTS as ReadonlyArray<string>).includes(s)) {
        console.log(s);
    }
    return (WORKOUTS as ReadonlyArray<string>).includes(s)
        ? (s as WorkoutType)
        : '!other';
};

export const workoutTypeFill = (x: any): Record<WorkoutType, typeof x> => {
    const out: Partial<Record<WorkoutType, typeof x>> = {};
    WORKOUTS.forEach((t) => {
        if (typeof x === 'function') {
            out[t] = x(t);
        } else {
            out[t] = x;
        }
    });
    return out as Record<WorkoutType, typeof x>;
};

export const workoutTypeCountAdd = (
    a: WorkoutTypeCount,
    b: WorkoutTypeCount,
): WorkoutTypeCount => {
    const out: Partial<WorkoutTypeCount> = {};
    WORKOUTS.forEach((t) => {
        out[t] = a[t] + b[t];
    });
    return out as WorkoutTypeCount;
};

export type WorkoutTypeCount = Record<WorkoutType, number>;

export type WorkoutTimeCountData = WorkoutTypeCount & {
    date: number;
    total: number;
};

export type WorkoutTypeData = {
    type: WorkoutType;
    count: number;
};

export interface WorkoutData {
    name: string;
    type: WorkoutType;
    date: number;
    url: string | null;
}

export interface TournamentData {
    name: string;
    start: Date;
    end: Date;
}
