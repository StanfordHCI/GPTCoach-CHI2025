// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

import { auth } from "../utils/firebase";
import React, { useState } from 'react';
import { signInWithEmailAndPassword } from "@firebase/auth";
import { FirebaseError } from "@firebase/app";

export type LoginProps = {
  callback: (uid: string) => void;
}

const LoginPage = ({ callback }: LoginProps) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');

  const handleLogin = async () => {
    setLoginError(''); // Reset login error state before attempting to log in
    try {
      const { user } = await signInWithEmailAndPassword(auth, email, password);
      const token = await user.getIdToken();

      localStorage.setItem('uid', user.uid);
      localStorage.setItem('token', token);

      callback(user.uid);
      console.log('Authentication successful:', user);
    } catch (error) {
      if (error instanceof FirebaseError) {
        // Handle specific error for incorrect password
        if (error.code === 'auth/wrong-password') {
          setLoginError('Incorrect password. Please try again.');
        } else {
          setLoginError('Login failed. Please try again.'); // General error message for other login failures
        }
      } else {
        const message = error instanceof Error ? error.message : 'An unknown error occurred.';
        console.error('Authentication failed:', error);
      }
    }
  };

  return (
    <div className="container">
      <h2>Login</h2>
      <input
        className="input"
        type="text"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Username"
      />
      <input
        className="input"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      {loginError && <div className="error-message">{loginError}</div>}
      <button className="button" onClick={handleLogin}>Login</button> {/* Call handleLogin on button click */}

      <style jsx>{`
        .container {
          margin-top: 50px;
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .input {
          margin: 10px 0;
          padding: 10px;
          border-radius: 5px;
          border: 1px solid #ccc;
        }
        .input.error {
          border-color: red; // Highlight the input border in red
        }
        .error-message {
          color: red; // Set the error message color to red
          margin-bottom: 10px;
        }
        .button {
          padding: 10px 20px;
          border-radius: 5px;
          border: none;
          background-color: #007bff;
          color: white;
          cursor: pointer;
        }
      `}</style>
    </div>
  );
};

export default LoginPage;
