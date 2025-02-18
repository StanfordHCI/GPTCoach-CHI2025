// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

import '@mantine/core/styles.css';
import type { AppProps } from 'next/app';
import Head from 'next/head';
import { MantineProvider } from '@mantine/core';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <MantineProvider>
      <Head>
        <title>Physical Activity Chatbot</title>
        <meta
          name="viewport"
          content="minimum-scale=1, initial-scale=1, width=device-width, user-scalable=no"
        />
        {/* <link rel="shortcut icon" href="/favicon.svg" /> */}
      </Head>
      <Component {...pageProps} />
    </MantineProvider>
  );
}