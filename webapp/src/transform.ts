import { getUnixTime, add, fromUnixTime } from 'date-fns';
import { WorkoutTimeCountData, WorkoutData, WorkoutType } from './types';
import { waitForDomChange } from '@testing-library/react';

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

export const fillDates = (data: WorkoutTimeCountData[]) => {
    const outData: WorkoutTimeCountData[] = [];

    let currDate = data[0].date;
    for (let i = 0; i < data.length; i++) {
        while (currDate < data[i].date) {
            outData.push({
                date: currDate,
                total: 0,
                '!throw': 0,
                '!gym': 0,
                '!cardio': 0,
                '!workout': 0,
                '!other': 0,
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
                '!throw': a['!throw'] + b['!throw'],
                '!gym': a['!gym'] + b['!gym'],
                '!cardio': a['!cardio'] + b['!cardio'],
                '!workout': a['!workout'] + b['!workout'],
                '!other': a['!other'] + b['!other'],
            });
        },
        {
            date: 0,
            total: 0,
            '!throw': 0,
            '!gym': 0,
            '!cardio': 0,
            '!workout': 0,
            '!other': 0,
        },
    );
    return outData;
};

export const getPlayers = (data: WorkoutData[]): string[] => {
    const players = new Set<string>();
    data.forEach((w) => {
        players.add(w.name);
    });
    return Array.from(players);
};
