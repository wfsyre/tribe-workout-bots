import React, { useEffect, useState } from 'react';
import { parse } from 'date-fns';

import { WorkoutData, toWorkoutType, TournamentData } from '../types';
import LoadingScreen from './LoadingScreen';
import MainScreen from './MainScreen';
import { minDate, maxDate } from '../transform';

function App() {
    const [workoutData, setWorkoutData] = useState<WorkoutData[] | null>(null);
    const [tournamentData, setTournamentData] = useState<TournamentData[]>();
    const [dateRange, setDateRange] = useState<[Date | null, Date | null]>([
        null,
        null,
    ]);

    useEffect(() => {
        fetch('/api/data')
            .then((response) => response.json())
            .then((data) => {
                const retData = data.map((w: any[]) => ({
                    name: w[0],
                    type: toWorkoutType(w[2]),
                    date: parse(
                        w[3].replace(' GMT', ''),
                        'EEE, dd MMM yyyy HH:mm:ss',
                        new Date(),
                    ),
                    url: w[4] === 'NULL' ? null : w[4],
                }));
                setWorkoutData(retData);
                setDateRange([
                    new Date(minDate(retData)),
                    new Date(maxDate(retData)),
                ]);
            })
            .catch(console.error);
        fetch('/api/tournaments')
            .then((response) => response.json())
            .then((data) => {
                const retData = data.map((w: any[]) => ({
                    name: w[0],
                    start: parse(
                        w[1].replace(' GMT', ''),
                        'EEE, dd MMM yyyy HH:mm:ss',
                        new Date(),
                    ),
                    end: parse(
                        w[2].replace(' GMT', ''),
                        'EEE, dd MMM yyyy HH:mm:ss',
                        new Date(),
                    ),
                }));
                setTournamentData(retData);
            })
            .catch(console.error);
    }, []);

    return workoutData && tournamentData ? (
        <MainScreen
            workoutData={workoutData}
            tournamentData={tournamentData}
            dateRange={dateRange}
            setDateRange={setDateRange}
        />
    ) : (
        <LoadingScreen />
    );
}

export default App;
