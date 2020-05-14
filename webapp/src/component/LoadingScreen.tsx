import React from 'react';
import { Text, Flex, Spinner } from '@chakra-ui/core';

const LoadingScreen = () => {
    const quips = [
        'Increasing dopeness',
        'Engaging core',
        'Hacking the mainframe',
        'Collecting lacrosse balls',
        'Setting up cones',
        'Carrying the disc bag',
    ];
    return (
        <Flex
            flexDirection="column"
            justifyContent="center"
            alignItems="center"
            h="100vh">
            <Text mb={4} fontSize="xl">
                {quips[Math.floor(Math.random() * quips.length)]}...
            </Text>
            <Spinner size="xl" />
        </Flex>
    );
};

export default LoadingScreen;
