// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

import { ScrollArea, Paper, Text, Center, Title, AppShell } from "@mantine/core";
import { Message } from "../../../models/Message";
import { VisualizationParams } from "../../../models/VisualizationParams";
import VisualizationWrapper from "../Visualization/VisualizationWrapper";
import MessageBubble from "./MessageBubble";
import { useEffect, useRef } from "react";
import { MessageListItem } from "../../../models/MessageListItem";

interface MessageListProps {
    messages: MessageListItem[];
}

export default function MessageList({ messages }: MessageListProps) {

    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Scroll to dummy div at the bottom of the page when `messages` changes
        let lastMessageWasUser = messages.length > 0 && messages[messages.length - 1].role == "user"
        messagesEndRef.current?.scrollIntoView({ behavior: lastMessageWasUser ? "auto" : "smooth" })

    }, [messages])
    return (
        <AppShell.Section
            component={ScrollArea}
            my="md"
            w="100%"
            style={{flexGrow: 1, display: 'flex', flexDirection: 'column', overflowY: 'auto'}} // Adjust this line
        >
            <div style={{flexGrow: 1, display: 'flex', flexDirection: 'column'}}>
                {messages.length > 0 ?
                    messages.map((message, i) => (
                        message instanceof VisualizationParams ?
                            <VisualizationWrapper params={message} key={i} />
                            :
                            <MessageBubble message={message} key={i} />
                    ))
                    :
                    <></>
                }
                <div ref={messagesEndRef} />
            </div>
        </AppShell.Section>
    )
}
