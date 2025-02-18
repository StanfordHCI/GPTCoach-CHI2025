// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

import axios from "axios";
import React, { useState, useEffect } from "react";
import ChatPanel from "../components/ChatPanel/ChatPanel";
import LoginPage from "./login";
import { BACKEND_URL } from "../utils/config";

export default function HomePage() {
  const [loading, setLoading] = useState(true);
  const [uid, setUid] = useState<string | null>(null);

  useEffect(() => {
    const fetchToken = () => {
      const urlToken = new URLSearchParams(window.location.search).get('token');
      const storageToken = localStorage.getItem('token');
      const token = urlToken || storageToken;
      
      if (token) {
        console.log("Fetched token from:", urlToken ? "URL" : "local storage", token);
      } else {
        console.log("No token found in URL parameters or in local storage");
      }
      return token;
    };

    const verifyCustomToken = async (token: string) => {
      try {
        const {data: uid} = await axios.get(BACKEND_URL + "/firebase/verify/", {
          headers: { Authorization: `Bearer ${token}` }
        });
        console.log("Verified token with Firebase user ID:", uid);
        return uid;
      } catch (error) {
        console.error("Failed to verify JWT token", error);
      }
    };

    const signInWithToken = async (token: string) => {
      const uid = await verifyCustomToken(token);
      if (uid) {
        localStorage.setItem('token', token);
        localStorage.setItem('uid', uid);
        setUid(uid);
      } else {
        console.error("Authentication failed.");
      }
      setLoading(false);
    };

    const token = fetchToken();
    if (token) {
      signInWithToken(token).catch(console.error);
    } else {
      console.error("Token not found");
      setLoading(false);
    }
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!uid) return <LoginPage callback={setUid}/>;
  return <ChatPanel firebaseUserID={uid} />
}
