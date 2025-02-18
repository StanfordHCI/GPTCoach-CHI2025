// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

import { Button, Textarea } from "@mantine/core";
import { getHotkeyHandler } from "@mantine/hooks";
import { IconSend, IconReload } from '@tabler/icons-react';
import { useState } from "react";

interface MessageInputProps {
    onSubmit: (messageText: string) => void;
    handleRewind: () => void;
    loading: boolean;
    disableRewind: boolean;
}

export default function MessageInput({ onSubmit, handleRewind, loading, disableRewind }: MessageInputProps) {

    const [message, setMessage] = useState('');

    const handleSubmit = () => {
        // Run when the user presses enter in the textbox
        setMessage('');

        // Call onSubmit callback from parent
        onSubmit(message);
    }

    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Textarea
                autosize
                radius="lg"
                variant="filled"
                placeholder="Enter a message..."
                value={message}
                disabled={loading}
                onChange={(event) => setMessage(event.currentTarget.value)}
                onKeyDown={getHotkeyHandler([
                    ['Enter', (event) => {
                        event.preventDefault();
                        handleSubmit();
                    }]
                ])}
                style={{ flex: 1 }}
            />
            <Button
                onClick={handleSubmit}
                disabled={loading || !message.trim()}
                variant="light"
                color='teal'
                style={{
                    width: '36px', 
                    height: '36px', 
                    padding: 0, 
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                }}
            >
                <IconSend size={18} />
            </Button>
            <Button
                onClick={handleRewind}
                disabled={loading || disableRewind}
                variant="light"
                color='teal'
                style={{
                    height: '36px', // Matching height to the width
                    paddingLeft: '10px',
                    paddingRight: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    // marginLeft: '10px'
                }}
            >
                Undo 
                <IconReload size={18} />
            </Button>
        </div>
    )
}