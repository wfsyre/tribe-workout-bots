import { getUnixTime, add, fromUnixTime, isAfter, isBefore } from 'date-fns';
import {
    WorkoutTimeCountData,
    WorkoutData,
    WorkoutType,
    WorkoutTypeData,
    workoutTypeFill,
    workoutTypeCountAdd,
} from './types';

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
            ...workoutTypeFill(
                (x: WorkoutType) => g.filter((t) => t === x).length,
            ),
        });
    });
    retData.sort((a, b) => a.date - b.date);
    return retData;
};

export const minDate = (data: WorkoutData[]) => {
    return data.reduce((min, p) => (p.date < min ? p.date : min), data[0].date);
};

export const maxDate = (data: WorkoutData[]) => {
    return data.reduce((max, p) => (p.date > max ? p.date : max), data[0].date);
};
export const withinRange = (data: WorkoutData[], dateRange: [Date, Date]) => {
    return data.filter((w) => {
        const date = fromUnixTime(w.date);
        return isAfter(date, dateRange[0]) && isBefore(date, dateRange[1]);
    });
};

export const fillDates = (data: WorkoutTimeCountData[]) => {
    const outData: WorkoutTimeCountData[] = [];

    let currDate = data[0].date;
    for (let i = 0; i < data.length; i++) {
        while (currDate < data[i].date) {
            outData.push({
                date: currDate,
                total: 0,
                ...workoutTypeFill(0),
            });

            currDate = getUnixTime(add(fromUnixTime(currDate), { days: 1 }));
        }
        outData.push(data[i]);
        currDate = getUnixTime(add(fromUnixTime(currDate), { days: 1 }));
    }
    return outData;
};

export const toCumulative = (data: WorkoutTimeCountData[]) => {
    const outData: WorkoutTimeCountData[] = [];
    data.reduce(
        (a: WorkoutTimeCountData, b, i) => {
            return (outData[i] = {
                date: b.date,
                total: a.total + b.total,
                ...workoutTypeCountAdd(a, b),
            });
        },
        {
            date: 0,
            total: 0,
            ...workoutTypeFill(0),
        },
    );
    return outData;
};

export const groupByType = (data: WorkoutData[]): WorkoutTypeData[] => {
    const groupedByType: Record<WorkoutType, number> = {
        ...workoutTypeFill(0),
    };
    data.forEach((w) => {
        groupedByType[w.type]++;
    });
    const retData: WorkoutTypeData[] = [];
    Object.keys(groupedByType).forEach((t) => {
        const type = t as WorkoutType;
        retData.push({
            type,
            count: groupedByType[type],
        });
    });
    return retData;
};

export const getPlayers = (data: WorkoutData[]): string[] => {
    const players = new Set<string>();
    data.forEach((w) => {
        players.add(w.name);
    });
    const out = Array.from(players);
    out.sort();
    return out;
};
