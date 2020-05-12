import { getUnixTime } from 'date-fns';
import { WorkoutTimeCountData, WorkoutData, WorkoutType } from './types';

export const toTimeCount = (data: WorkoutData[]): WorkoutTimeCountData[] => {
    const groupedByTime: { [d: string]: WorkoutType[] } = {};
    data.forEach((w) => {
        const d = getUnixTime(w.date);
        if (d in groupedByTime) {
            groupedByTime[d].push(w.type);
        } else {
            groupedByTime[d] = [w.type];
        }
    });
    const retData: WorkoutTimeCountData[] = [];
    Object.keys(groupedByTime).forEach((d) => {
        const g: WorkoutType[] = groupedByTime[d];
        retData.push({
            date: Number(d),
            total: g.length,
            '!gym': g.filter((t) => t === '!gym').length,
            '!throw': g.filter((t) => t === '!throw').length,
            '!workout': g.filter((t) => t === '!workout').length,
            '!cardio': g.filter((t) => t === '!cardio').length,
            '!other': g.filter((t) => t === '!other').length,
        });
    });
    retData.sort((a, b) => a.date - b.date);
    return retData;
};
