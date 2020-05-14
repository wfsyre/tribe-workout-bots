import React from 'react';
import { Image, Text } from '@chakra-ui/core';
import { WorkoutData } from '../types';
import { getAvatar, choose } from '../util';
import { format } from 'date-fns';

const PlayerImage = ({
    workoutData,
    player,
    caption,
}: {
    workoutData: WorkoutData[];
    player?: string;
    caption: boolean;
}) => {
    if (player == null) return null;
    const data = workoutData.filter((w) => player == null || w.name === player);
    const chosenWorkout = getAvatar(data);

    if (!chosenWorkout?.url) return null;

    const doing = ['grinding out a', 'hitting that', 'sending a lovely'];
    return (
        <>
            <Image src={chosenWorkout.url} size="150px" objectFit="contain" />
            <Text
                color="gray.400"
                fontSize="xs"
                fontStyle="italic"
                // w={'150px'}
                textAlign="center">
                {player} {choose(doing)} {chosenWorkout.type} on{' '}
                {format(chosenWorkout.date, 'MMMM d')}
            </Text>
        </>
    );
};

export default PlayerImage;
