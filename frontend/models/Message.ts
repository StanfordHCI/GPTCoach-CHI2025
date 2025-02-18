// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

// Class to represent a single message from GPT or the user
export class Message {
    role: 'user' | 'assistant' | 'function';
    content: string;
    state: string;
    strategy: string;

    constructor(role: 'user' | 'assistant' | 'function', content: string, state: string, strategy: string) {
        this.role = role;
        this.content = content;
        this.state = state;
        this.strategy = strategy;
    }
}
