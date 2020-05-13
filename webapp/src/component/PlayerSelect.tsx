import React, { useRef, useEffect, useState } from 'react';
import { Select } from '@chakra-ui/core';

const defaultSelect = 'Tribe';

const PlayerSelect = ({
    players,
    setSelectedPlayer,
}: {
    players: string[];
    setSelectedPlayer: React.Dispatch<React.SetStateAction<string | undefined>>;
}) => {
    const fakeSelect = useRef(null);
    const [selected, setSelected] = useState<string>(defaultSelect);
    const [w, setW] = useState<number>(
        ((fakeSelect.current as unknown) as HTMLSelectElement)?.parentElement
            ?.offsetWidth ?? 180,
    );
    useEffect(() => {
        setSelectedPlayer(selected === defaultSelect ? undefined : selected);
        setW(
            ((fakeSelect.current as unknown) as HTMLSelectElement)
                ?.parentElement?.offsetWidth ?? 180,
        );
    }, [selected, setSelectedPlayer]);
    return (
        <>
            <Select
                variant="flushed"
                d="inline"
                fontSize="inherit"
                height="auto"
                rootProps={{
                    width: `${w}px`,
                    d: 'inline-block',
                    transition: 'width 0.2s ease-out',
                }}
                onChange={(e) => setSelected(e.target.value)}
                defaultValue={defaultSelect}>
                <option value={defaultSelect} key={defaultSelect}>
                    {defaultSelect}
                </option>
                {players.map((p) => (
                    <option value={p} key={p}>
                        {p}
                    </option>
                ))}
            </Select>
            <Select
                visibility="hidden"
                d="inline"
                fontSize="inherit"
                position="absolute"
                rootProps={{
                    width: 'auto',
                    d: 'inline-block',
                    visibility: 'hidden',
                }}
                ref={fakeSelect}>
                <option>{selected}</option>
            </Select>
        </>
    );
};

export default PlayerSelect;
