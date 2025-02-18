// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

import { Paper } from "@mantine/core";
import { Message } from "../../../models/Message";
import Markdown from "react-markdown";
import rehypeRaw from 'rehype-raw'; // Import rehype-raw for HTML parsing
import rehypeSanitize from 'rehype-sanitize'; // Import rehype-sanitize for sanitizing HTML
import { useEffect } from "react";

interface MessageBubbleProps {
    message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
    // Inline style for span elements. You can also use a CSS class.
    // const spanStyle = {
    //     fontSize: '0.85rem', // Smaller font size
    //     color: 'gray', // Gray text color
    //     display: 'block', // Display as block element
    //     padding: '0.5rem 0', // Padding
    // };
    const spanStyle = {
        display: 'none'
    }

    return (
        <Paper
            p="xs"
            my="0.5rem"
            bg={message.role == 'user' ? "teal.3" : "white"}
            withBorder={message.role == 'assistant'}
            radius='lg'

            mr={message.role == 'user' ? 0 : "2rem"}
            ml={message.role == 'assistant' ? 0 : "2rem"}
        >
            <div style={{ marginBlock: "-1em"}}>
                {/* <Markdown children={message.content} disallowedElements={["pre"]}/> */}
                {/* Conditional rendering for assistant role specific content */}
                {message.role === 'assistant' && (
                    <span style={spanStyle}>
                        State: {message.state}, Strategy: {message.strategy}
                    </span>
                )}
                <Markdown disallowedElements={["pre"]}>
                    {message.content}
                </Markdown>
            </div>
        </Paper>
    )
}