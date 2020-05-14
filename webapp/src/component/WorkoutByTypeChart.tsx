import React from 'react';
import { WorkoutData } from '../types';
import { PieChart, Pie, Tooltip, Cell, TooltipPayload } from 'recharts';
import { groupByType } from '../transform';
import { workoutTypeColors } from '../theme';
import { Box } from '@chakra-ui/core';

const WorkoutTypeTooltip = ({
    active,
    payload,
    numWorkouts,
}: {
    active: boolean;
    payload: TooltipPayload[];
    numWorkouts: number;
}) => {
    if (!active || payload[0] == null) return null;
    console.log(JSON.stringify(payload));
    const { type, count } = payload[0].payload.payload;
    console.log(numWorkouts);
    return (
        <Box bg="rgba(255, 255, 255, 0.9)" maxW="md" p={3}>
            <p>
                {type}: {count} ({Math.round((count / numWorkouts) * 1000) / 10}
                %)
            </p>
        </Box>
    );
};

const WorkoutByTypeChart = ({
    workoutData,
    player,
}: {
    workoutData: WorkoutData[];
    player?: string;
}) => {
    const playerWorkouts = workoutData.filter(
        (w) => player == null || w.name === player,
    );
    const data = groupByType(playerWorkouts);
    return (
        <PieChart width={600} height={600}>
            <Pie data={data} dataKey="count">
                {data.map((entry, index) => (
                    <Cell
                        fill={workoutTypeColors[entry.type]}
                        key={entry.type}
                    />
                ))}
            </Pie>
            <Tooltip
                content={({
                    active,
                    payload,
                }: {
                    active: boolean;
                    payload: TooltipPayload[];
                }) => (
                    <WorkoutTypeTooltip
                        active={active}
                        payload={payload}
                        numWorkouts={playerWorkouts.length}
                    />
                )}
            />
        </PieChart>
    );
};

export default WorkoutByTypeChart;
