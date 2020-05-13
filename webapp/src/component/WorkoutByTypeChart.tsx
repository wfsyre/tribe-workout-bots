import React from 'react';
import { WorkoutData } from '../types';
import { PieChart, Pie, Tooltip, Cell } from 'recharts';
import { groupByType } from '../transform';
import { workoutTypeColors } from '../theme';

const WorkoutTypeTooltip = ({
    active,
    payload,
}: {
    active: boolean;
    payload: any[];
}) => {
    if (!active || payload[0] == null) return null;
    const { date, total } = payload[0].payload;
    return (
        <div>
            <p>{total}</p>
            <p>{JSON.stringify(payload[0].payload)}</p>
        </div>
    );
};

const WorkoutByTypeChart = ({
    workoutData,
    player,
}: {
    workoutData: WorkoutData[];
    player?: string;
}) => {
    const data = groupByType(
        workoutData.filter((w) => player == null || w.name === player),
    );
    return (
        <PieChart width={600} height={600}>
            <Pie data={data} dataKey="count">
                {data.map((entry, index) => (
                    <Cell fill={workoutTypeColors[entry.type]} />
                ))}
            </Pie>
            <Tooltip
                content={({
                    active,
                    payload,
                }: {
                    active: boolean;
                    payload: any[];
                }) => <WorkoutTypeTooltip active={active} payload={payload} />}
            />
        </PieChart>
    );
};

export default WorkoutByTypeChart;
