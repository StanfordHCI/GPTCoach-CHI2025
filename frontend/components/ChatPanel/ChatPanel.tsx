// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

import { Loader, Center, Space, ScrollArea, AppShell, Button, Group, Text } from "@mantine/core";
import MessageList from "./MessageList/MessageList";
import { useRef, useState } from "react";
import MessageInput from "./MessageInput";
import { Message } from "../../models/Message";
import { VisualizationParams } from "../../models/VisualizationParams";
import { useEffect } from "react";
import { MessageListItem } from "../../models/MessageListItem";
// import { BACKEND_URL } from "../../utils/config";
import useWebSocket from 'react-use-websocket';
import { socketURL, PROD } from "../../utils/config";

interface ChatPanelProps {
    firebaseUserID: string
}


export default function ChatPanel({ firebaseUserID }: ChatPanelProps) {

    // const BACKEND_URL = "127.0.0.1:5000/gpt/ws"

    const [messages, setMessages] = useState<MessageListItem[]>([])
    const [loading, setLoading] = useState(true);
    const [loadingMessage, setLoadingMessage] = useState("");

    const WebSocketURL = PROD ? `wss://${socketURL}/gpt/ws/${firebaseUserID}/` : `ws://${socketURL}/gpt/ws/${firebaseUserID}/`;
    const { sendMessage, lastMessage, readyState } = useWebSocket(WebSocketURL, {
        shouldReconnect: (closeEvent) => true, // Always attempt to reconnect
        onOpen: () => setLoading(false),
        onClose: () => setLoading(true),
        reconnectInterval: 3000, // Reconnect every 3000ms
        reconnectAttempts: 10 // Maximum number of reconnect attempts
    });

    useEffect(() => {
        if (lastMessage !== null) {
            const response = JSON.parse(lastMessage.data);
            
            if (response.type === "reset") {
                setMessages([]);
            } else if (response.type === "message") {
                let gptMessage = new Message(response.role, response.content, response.state, response.strategy);
                setMessages(prevMessages => [...prevMessages, gptMessage]);
                setLoading(false);
                setLoadingMessage("");
                console.log("Received message:", response);
            } else if (response.type === "visualization") {
                let gptViz = new VisualizationParams(
                    firebaseUserID,
                    response.name,
                    response.data_type,
                    response.unit,
                    response.granularity,
                    response.date
                );
                setMessages(prevMessages => [...prevMessages, gptViz]);         
            } else if (response.type === "loading") {
                setLoadingMessage(response.content);
            } else if (response.type === "finish_summary") {
                setMessages([]);
            } else if (response.type == "rewind_confirmation") {
                if (response.content == "success") {
                    console.log("Backend succesfully rewinded conversation!")                    
                }                
            } else {
                console.warn(`Received strange response type '${response.type}'!`);
            }
        }
    }, [lastMessage]);

    const handleSubmit = (messageText: string) => {
        if (messageText.length === 0) return;
        setLoading(true);
        let userMessage = new Message('user', messageText, '', '');
        setMessages(prevMessages => [...prevMessages, userMessage]);

        let request = {
            type: "message",
            user_id: firebaseUserID,
            prompt: messageText
        };

        sendMessage(JSON.stringify(request));
    }

    const handleRewind = () => {
        console.log("rewinding...");
        // Define the rewind request object
        let rewindRequest = {
            type: "rewind",  // An arbitrary type name that the backend will recognize as a rewind command
            user_id: firebaseUserID  // Include any other relevant data the backend may need
        };
        // Send the rewind request to the backend via WebSocket
        // webSocket?.send(JSON.stringify(rewindRequest));       
        sendMessage(JSON.stringify(rewindRequest));
        
        // Find the index of the last message from the user
        console.log("ALL MESSAGES: ", messages)
        let lastUserMessageIndex = -1;
        for (let i = messages.length - 1; i >= 0; i--) {
          if (messages[i].role === 'user') {
            lastUserMessageIndex = i;
            break;
          }
        }
      
        // If a user message is found, remove it and any messages that follow
        if (lastUserMessageIndex !== -1) {
          // Update the messages array without the removed messages
          setMessages(messages.slice(0, lastUserMessageIndex));
        }
        console.log("REMOVED MESSAGES: ", messages)
        // Reset loading state if needed
        setLoading(false);        
      }


    return (
        <AppShell
            p={0}
            m={0}
            w="100%"
            mih="100vh"
            bg="gray.0"
            style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}
        >
            <ScrollArea 
                offsetScrollbars
                style={{ 
                    flexGrow: 1, 
                    overflowY: 'auto',
                    padding: '10px',
                    paddingBottom: '0px'
                }}>
                <MessageList messages={messages} />
                <Center 
                    style={{ 
                        display: 'flex', 
                        flexDirection: 'column', 
                        alignItems: 'center'
                    }}>
                    {loading ? <Loader size="md" type="dots" color='gray'/> : <Space h="xs" />}
                    {loading ? 
                        <div style={{ 
                            color: 'gray',
                            marginBottom: '20px',
                        }}>
                            {loadingMessage}
                        </div> 
                        : <div></div>
                    }
                </Center>
            </ScrollArea>
            <div 
                style={{ 
                    padding: '10px', 
                    background: 'white', 
                    borderTop: '1px solid lightgray',
                    paddingBottom: '10px' 
                }}>
                <MessageInput 
                    onSubmit={handleSubmit} 
                    handleRewind={handleRewind} 
                    loading={loading} 
                    disableRewind={messages.length <= 1}
                />
            </div>
        </AppShell>
    )
}
