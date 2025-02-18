// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

export const prod = process.env.PROD || 'False';

const strToBool = (value: string | undefined): boolean => {
    return value?.toLowerCase() !== 'false' && Boolean(value);
};

export const PROD: boolean = strToBool(prod);

// set backend url depending on production or local env
export const BACKEND_URL = PROD ? 'YOUR_PROD_URL' : 'http://127.0.0.1:5000';
export const socketURL = BACKEND_URL.replace(/.*\/\//, '')

console.log("PROD: ", PROD)
console.log("BACKEND_URL: ", BACKEND_URL)
console.log("socketURL: ", socketURL)