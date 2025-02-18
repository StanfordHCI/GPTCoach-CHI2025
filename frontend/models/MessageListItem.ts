// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

// Type to represent a generic object that can appear in the message list

import { Message } from "./Message";
import { VisualizationParams } from "./VisualizationParams";

export type MessageListItem = Message | VisualizationParams;