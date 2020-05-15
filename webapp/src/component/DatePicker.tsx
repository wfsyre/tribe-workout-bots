import React, { useState, useRef, useEffect } from 'react';
import { Box, Input, Text } from '@chakra-ui/core';
import { format, parse, isBefore, isAfter, isValid } from 'date-fns';

const DatePicker = ({
    date,
    setDate,
    minDate,
    maxDate,
}: {
    date: Date;
    setDate: (d: Date) => void;
    minDate: Date;
    maxDate: Date;
}) => {
    const [showInput, setShowInput] = useState(true);
    const [inputDate, setInputDate] = useState(format(date, 'MM/dd/yyyy'));
    useEffect(() => {
        if (showInput && inputEl.current) inputEl.current.focus();
        console.log(date);
    }, [showInput]);
    const inputEl = useRef<HTMLInputElement>(null);

    return (
        <Box d="inline">
            <Text
                onClick={() => {
                    setInputDate(format(date, 'MM/dd/yyyy'));
                    setShowInput(true);
                }}
                d={!showInput ? 'inline' : 'none'}>
                {format(date, 'MMMM d, yyyy')}
            </Text>

            <Input
                onBlur={(e: React.ChangeEvent<HTMLInputElement>) => {
                    let newDate = parse(inputDate, 'MM/dd/yyyy', 0);
                    if (isValid(newDate)) {
                        if (isBefore(newDate, minDate)) newDate = minDate;
                        if (isAfter(newDate, maxDate)) newDate = maxDate;
                        setDate(newDate);
                    }
                    setShowInput(false);
                }}
                ref={inputEl}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    console.log(e.target.value);
                    setInputDate(e.target.value);
                }}
                value={inputDate}
                d={showInput ? 'inline' : 'none'}
                variant="flushed"
            />
        </Box>
    );
};

export default DatePicker;
