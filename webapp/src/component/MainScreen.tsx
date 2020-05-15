import React, { useState } from 'react';
import { Flex, Heading, Text } from '@chakra-ui/core';
import { TEAM_NAME, WorkoutData } from '../types';
import PlayerSelect from './PlayerSelect';
import WorkoutsByDateChart from './WorkoutByDateChart';
import TextSummary from './TextSummary';
import { getPlayers, minDate, maxDate } from '../transform';
import WorkoutByTypeChart from './WorkoutByTypeChart';
import { isWithinInterval } from 'date-fns';
import EditableDate from './EditableDate';

const MainScreen = ({
    workoutData,
    dateRange,
    setDateRange,
}: {
    workoutData: WorkoutData[];
    dateRange: [Date | null, Date | null];
    setDateRange: React.Dispatch<
        React.SetStateAction<[Date | null, Date | null]>
    >;
}) => {
    const [selectedPlayer, setSelectedPlayer] = useState<string>();

    const minD = new Date(minDate(workoutData));
    const maxD = new Date(maxDate(workoutData));
    const rangeData = workoutData.filter((w) =>
        dateRange[0] != null && dateRange[1] != null
            ? isWithinInterval(w.date, {
                  start: dateRange[0],
                  end: dateRange[1],
              })
            : true,
    );

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
            {dateRange[0] && dateRange[1] && (
                <Text>
                    Workout data from{' '}
                    {
                        <EditableDate
                            date={dateRange[0]}
                            setDate={(x) => {
                                setDateRange([x, dateRange[1]]);
                            }}
                            minDate={minD}
                            maxDate={maxD}
                        />
                    }{' '}
                    to{' '}
                    {
                        <EditableDate
                            date={dateRange[1]}
                            setDate={(x) => {
                                setDateRange([dateRange[0], x]);
                            }}
                            minDate={minD}
                            maxDate={maxD}
                        />
                    }
                </Text>
            )}
            <WorkoutsByDateChart
                workoutData={rangeData}
                player={selectedPlayer}
            />
            <TextSummary workoutData={rangeData} player={selectedPlayer} />
            <WorkoutByTypeChart
                workoutData={rangeData}
                player={selectedPlayer}
            />
        </Flex>
    );
};

export default MainScreen;
