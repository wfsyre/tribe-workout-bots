import React from 'react';
import { Text, Flex } from '@chakra-ui/core';
import { WorkoutData, TEAM_NAME } from '../types';
import { minDate, maxDate, groupByType } from '../transform';
import { format, differenceInDays } from 'date-fns';
import PlayerImage from './PlayerImage';

interface TextSummaryProps {
    workoutData: WorkoutData[];
    player?: string;
}

const TextSummary = ({ workoutData, player }: TextSummaryProps) => {
    const [minD, maxD] = [
        new Date(minDate(workoutData)),
        new Date(maxDate(workoutData)),
    ];
    const data = workoutData.filter((w) => player == null || w.name === player);
    const dateRange = differenceInDays(maxD, minD);
    const numWorkouts = data.length;
    const typeData = groupByType(data);
    typeData.sort((a, b) => b.count - a.count);
    return (
        <Flex flexDirection="column" alignItems="center" mt={3}>
            <Text>
                From {format(minD, 'MMMM d')} to {format(maxD, 'MMMM d')},{' '}
                {player ?? TEAM_NAME} did {numWorkouts} workouts. On average,
                that's about {Math.round((numWorkouts / dateRange) * 100) / 100}{' '}
                per day.
            </Text>
            <PlayerImage workoutData={workoutData} player={player} caption />
            <Text>
                Their most favorite workout was {typeData[0].type}, which was{' '}
                {Math.round((typeData[0].count / numWorkouts) * 1000) / 10}% of
                all their workouts.{' '}
            </Text>
        </Flex>
    );
};

export default TextSummary;
