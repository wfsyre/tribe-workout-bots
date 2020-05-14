import React, { useState } from 'react';
import { Flex, Heading } from '@chakra-ui/core';
import { TEAM_NAME, WorkoutData } from '../types';
import PlayerSelect from './PlayerSelect';
import WorkoutsByDateChart from './WorkoutByDateChart';
import TextSummary from './TextSummary';
import { getPlayers } from '../transform';
import WorkoutByTypeChart from './WorkoutByTypeChart';

const MainScreen = ({ workoutData }: { workoutData: WorkoutData[] }) => {
    const [selectedPlayer, setSelectedPlayer] = useState<string>();

    const players = getPlayers(workoutData ?? []);
    return (
        <Flex alignItems="center" flexDirection="column">
            <Heading>
                Hey {TEAM_NAME},{' '}
                {
                    <PlayerSelect
                        players={players}
                        setSelectedPlayer={setSelectedPlayer}
                    />
                }{' '}
                here
            </Heading>
            <WorkoutsByDateChart
                workoutData={workoutData}
                player={selectedPlayer}
            />
            <TextSummary workoutData={workoutData} player={selectedPlayer} />
            <WorkoutByTypeChart
                workoutData={workoutData}
                player={selectedPlayer}
            />
        </Flex>
    );
};

export default MainScreen;
