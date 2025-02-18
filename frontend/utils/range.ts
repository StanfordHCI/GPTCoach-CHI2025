// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

export function range(i: number) {
    // Returns a list of the numbers from 0 to i-1 (inclusive)
    // Helper function for creating repeated instances of components
    return Array.from({ length: i }, (_, index) => index)
}
