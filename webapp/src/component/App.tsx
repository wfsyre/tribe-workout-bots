import React, { useEffect, useState } from 'react';
import { parse } from 'date-fns';

import { WorkoutData, toWorkoutType } from '../types';

import WorkoutsByDateChart from './WorkoutByDateChart';
import { Heading, Flex, Checkbox } from '@chakra-ui/core';
import { getPlayers } from '../transform';
import PlayerSelect from './PlayerSelect';

function App() {
    const [workoutData, setWorkoutData] = useState<WorkoutData[] | null>(null);
    const [selectedPlayer, setSelectedPlayer] = useState<string>();
    const [cumulative, setCumulative] = useState<boolean>(false);

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
                    url: w[4],
                }));
                setWorkoutData(retData);
            })
            .catch(console.error);
    }, []);

    const players = getPlayers(workoutData ?? []);

    return (
        <Flex alignItems="center" flexDirection="column">
            <Heading>
                Hey Tribe,{' '}
                {
                    <PlayerSelect
                        players={players}
                        setSelectedPlayer={setSelectedPlayer}
                    />
                }{' '}
                here
            </Heading>
            {workoutData && (
                <WorkoutsByDateChart
                    workoutData={workoutData}
                    player={selectedPlayer}
                    cumulative={cumulative}
                />
            )}
            <Checkbox
                isChecked={cumulative}
                onChange={() => setCumulative(!cumulative)}>
                cumulative
            </Checkbox>
        </Flex>
    );
}

export default App;
