import React, { useState } from 'react';
import {
    Editable,
    EditablePreview,
    EditableInput,
    useTheme,
} from '@chakra-ui/core';
import {
    format,
    parse,
    isValid,
    isBefore,
    isAfter,
    startOfToday,
} from 'date-fns';

const EditableDate = ({
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
    const theme = useTheme();
    const dispFormat = 'MMMM dd, yyyy';
    const editFormat = 'MM/dd/yy';
    const [inputDate, setInputDate] = useState(format(date, dispFormat));
    const [confirmedDate, setConfirmedDate] = useState(date);

    return (
        <Editable
            value={inputDate}
            selectAllOnFocus={false}
            onSubmit={() => {
                let newDate = parse(inputDate, editFormat, startOfToday());
                if (isValid(newDate)) {
                    if (isBefore(newDate, minDate)) newDate = minDate;
                    if (isAfter(newDate, maxDate)) newDate = maxDate;
                    setInputDate(format(newDate, dispFormat));
                    setConfirmedDate(newDate);
                    setDate(newDate);
                } else {
                    setInputDate(format(confirmedDate, dispFormat));
                }
            }}
            onEdit={() => {
                if (inputDate === format(confirmedDate, dispFormat)) {
                    setInputDate(format(date, editFormat));
                }
            }}
            onChange={(v) => {
                setInputDate(v);
            }}
            d="inline">
            <EditablePreview
                rounded={0}
                borderBottom="1px dotted"
                borderColor="inherit"
            />
            <EditableInput
                w="5em"
                textAlign="center"
                borderBottom="2px"
                borderColor="black"
                rounded={0}
                px="undefined"
                bg="transparent"
                _focus={{
                    zIndex: 1,
                    borderColor: theme.colors.blue[500],
                }}
                _invalid={{ borderColor: theme.colors.blue[500] }}
            />
        </Editable>
    );
};

export default EditableDate;
