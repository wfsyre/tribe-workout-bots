import React, { useState } from 'react';
import { Checkbox, Flex, Box, Text } from '@chakra-ui/core';
import {
    WorkoutData,
    WorkoutType,
    workoutTypeFill,
    WORKOUTS,
    TEAM_NAME,
    WorkoutTimeCountData,
    TournamentData,
} from '../types';
import { toTimeCount, fillDates, toCumulative } from '../transform';
import { fromUnixTime, format, getUnixTime, isWithinInterval } from 'date-fns';
import {
    AreaChart,
    XAxis,
    YAxis,
    Tooltip,
    Area,
    Legend,
    LegendPayload,
    ReferenceArea,
} from 'recharts';
import { workoutTypeColors, workoutTypeVariantColors } from '../theme';

const WorkoutsByDateChart = ({
    workoutData,
    tournamentData,
    player,
    dateRange,
}: {
    workoutData: WorkoutData[];
    tournamentData: TournamentData[];
    player?: string;
    dateRange: [Date | null, Date | null];
}) => {
    const [hidden, setHidden] = useState<Record<WorkoutType, boolean>>(
        workoutTypeFill(true),
    );
    const [cumulative, setCumulative] = useState(true);
    if (workoutData == null) return null;
    let tsCount = fillDates(
        toTimeCount(
            workoutData.filter((w) => player == null || w.name === player),
        ),
    );
    if (cumulative) {
        tsCount = toCumulative(tsCount);
    }

    const toggleHidden = (w: WorkoutType) => {
        setHidden({
            ...hidden,
            [w]: !hidden[w],
        });
    };

    return (
        <AreaChart
            width={1500}
            height={600}
            data={tsCount}
            margin={{ top: 16 }}>
            <XAxis
                dataKey="date"
                domain={[
                    dateRange[0] ? getUnixTime(dateRange[0]) : 'dataMin',
                    dateRange[1] ? getUnixTime(dateRange[1]) : 'dataMax',
                ]}
                name="Time"
                tickFormatter={(unixTime) => {
                    return format(fromUnixTime(unixTime), 'MM-dd');
                }}
                tickCount={11}
                type="number"
            />
            <YAxis type="number" domain={[0, 'dataMax']} />
            <Tooltip
                content={({
                    active,
                    payload,
                }: {
                    active: boolean;
                    payload: any[];
                }) => (
                    <WorkoutTooltip
                        active={active}
                        payload={payload}
                        name={player}
                        start={tsCount[0].date}
                        cumulative={cumulative}
                        tournamentData={tournamentData}
                    />
                )}
            />
            {WORKOUTS.map((t) => (
                <Area
                    type="linear"
                    stackId="1"
                    fillOpacity="1"
                    dataKey={hidden[t] ? t : ''}
                    dot={false}
                    // stroke={hidden[t] ? workoutTypeColors[t] : 'none'}
                    stroke="none"
                    fill={workoutTypeColors[t]}
                    name={t}
                    key={t}
                />
            ))}
            <Legend
                content={({ payload }) => (
                    <WorkoutLegend
                        payload={payload}
                        toggleHidden={toggleHidden}
                        hidden={hidden}
                        cumulative={cumulative}
                        setCumulative={setCumulative}
                    />
                )}
            />
            {tournamentData.map((t) => (
                <ReferenceArea
                    x1={getUnixTime(t.start)}
                    x2={getUnixTime(t.end)}
                    key={t.name}
                    fill="black"
                    fillOpacity="0.1"
                    ifOverflow="hidden"
                />
            ))}
        </AreaChart>
    );
};

interface WorkoutTooltipProps {
    active: boolean;
    payload: any[];
    name?: string;
    start?: number;
    cumulative: boolean;
    tournamentData: TournamentData[];
}

const WorkoutTooltip = ({
    active,
    payload,
    name,
    start,
    cumulative,
    tournamentData,
}: WorkoutTooltipProps) => {
    if (!active || payload[0] == null) return null;
    const data: WorkoutTimeCountData = payload[0].payload;
    const startDate = format(fromUnixTime(start ?? 0), 'MMM dd');
    const inTourney = tournamentData.find((t) =>
        isWithinInterval(fromUnixTime(data.date), {
            start: t.start,
            end: t.end,
        }),
    );
    return (
        <Box bg="rgba(255, 255, 255, 0.9)" maxW="md" p={3}>
            {inTourney && (
                <Text color="gray.400" as="i">
                    On {format(fromUnixTime(data.date), 'MMM dd')}, {TEAM_NAME}{' '}
                    was attending {inTourney.name}
                </Text>
            )}
            <Text>
                {cumulative
                    ? `Between ${startDate} and ${format(
                          fromUnixTime(data.date),
                          'MMM dd',
                      )}, `
                    : `On ${format(fromUnixTime(data.date), 'MMM dd')}, `}
                {name ?? TEAM_NAME} did {data.total} workout
                {data.total !== 1 && 's'}
                {data.total > 0 ? ':' : '.'}
            </Text>
            {data.total > 0 &&
                Object.entries(
                    workoutTypeFill((w: WorkoutType) => data[w]),
                ).map((x) => {
                    return (
                        x[1] > 0 && (
                            <Text key={x[0]}>
                                {x[1]} {x[0]}
                            </Text>
                        )
                    );
                })}
        </Box>
    );
};

const WorkoutLegend = ({
    payload,
    toggleHidden,
    hidden,
    cumulative,
    setCumulative,
}: {
    payload: readonly LegendPayload[] | undefined;
    toggleHidden: (w: WorkoutType) => void;
    hidden: Record<WorkoutType, boolean>;
    cumulative: boolean;
    setCumulative: React.Dispatch<React.SetStateAction<boolean>>;
}) => {
    if (payload == null) return null;
    return (
        <>
            <Flex justifyContent="center">
                {payload.map((entry) => {
                    const w = entry.value as WorkoutType;
                    return (
                        <Checkbox
                            variantColor={workoutTypeVariantColors[w]}
                            isChecked={hidden[w]}
                            onChange={() => {
                                toggleHidden(entry.value);
                            }}
                            mx={2}
                            key={entry.value}>
                            {entry.value}
                        </Checkbox>
                    );
                })}
            </Flex>
            <Flex justifyContent="center">
                <Checkbox
                    isChecked={cumulative}
                    onChange={() => setCumulative(!cumulative)}>
                    cumulative
                </Checkbox>
            </Flex>
        </>
    );
};

export default WorkoutsByDateChart;
