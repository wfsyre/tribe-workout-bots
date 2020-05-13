import React, { useState } from 'react';
import { WorkoutData, WorkoutType } from '../types';
import { toTimeCount, fillDates, toCumulative } from '../transform';
import { fromUnixTime, format } from 'date-fns';
import { AreaChart, XAxis, YAxis, Tooltip, Area, Legend } from 'recharts';

const WorkoutsByDateChart = ({
    workoutData,
    player,
    cumulative,
}: {
    workoutData: WorkoutData[];
    player?: string;
    cumulative: boolean;
}) => {
    const [hidden, setHidden] = useState<Record<WorkoutType, boolean>>({
        '!throw': true,
        '!gym': true,
        '!cardio': true,
        '!workout': true,
        '!other': false,
    });
    if (workoutData == null) return null;
    let tsCount = fillDates(
        toTimeCount(
            workoutData.filter((w) => player == null || w.name === player),
        ),
    );
    if (cumulative) {
        tsCount = toCumulative(tsCount);
    }
    const max = tsCount.reduce((prev, current) =>
        prev.total > current.total ? prev : current,
    ).total;
    return (
        <AreaChart width={1500} height={600} data={tsCount}>
            <XAxis
                dataKey="date"
                domain={['dataMin', 'dataMax']}
                name="Time"
                tickFormatter={(unixTime) => {
                    return format(fromUnixTime(unixTime), 'MM-dd');
                }}
                tickCount={11}
                type="number"
            />
            <YAxis type="number" domain={[0, max]} />
            <Tooltip
                content={({
                    active,
                    payload,
                }: {
                    active: boolean;
                    payload: any[];
                }) => <WorkoutTooltip active={active} payload={payload} />}
            />
            {/* <Area type="linear" dataKey="total" dot={false} /> */}
            <Area
                type="linear"
                stackId="1"
                dataKey={hidden['!throw'] ? '!throw' : ''}
                dot={false}
                stroke={hidden['!throw'] ? '#f5222d' : 'none'}
                fill="#f5222d"
                name="!throw"
            />
            <Area
                type="linear"
                stackId="1"
                dataKey={hidden['!gym'] ? '!gym' : ''}
                dot={false}
                stroke={hidden['!gym'] ? '#fadb14' : 'none'}
                fill="#fadb14"
                name="!gym"
            />
            <Area
                type="linear"
                stackId="1"
                dataKey={hidden['!workout'] ? '!workout' : ''}
                dot={false}
                stroke={hidden['!workout'] ? '#13c2c2' : ''}
                fill="#13c2c2"
                name="!workout"
            />
            <Area
                type="linear"
                stackId="1"
                dataKey={hidden['!cardio'] ? '!cardio' : ''}
                dot={false}
                stroke={hidden['!cardio'] ? '#722ed1' : ''}
                fill="#722ed1"
                name="!cardio"
            />
            <Legend
                onClick={({ value }) => {
                    setHidden({
                        ...hidden,
                        [value]: !hidden[value as WorkoutType],
                    });
                }}
            />
        </AreaChart>
    );
};

interface WorkoutTooltipProps {
    active: boolean;
    payload: any[];
}

const WorkoutTooltip = ({ active, payload }: WorkoutTooltipProps) => {
    if (!active || payload[0] == null) return null;
    const { date, total } = payload[0].payload;
    return (
        <div>
            <p>{format(fromUnixTime(date), 'MM-dd')}</p>
            <p>{total}</p>
            <p>{JSON.stringify(payload[0].payload)}</p>
        </div>
    );
};

export default WorkoutsByDateChart;
