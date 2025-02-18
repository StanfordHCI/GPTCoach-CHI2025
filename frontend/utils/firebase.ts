// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

import { initializeApp } from "@firebase/app";
import { getAuth, signInWithEmailAndPassword, connectAuthEmulator, setPersistence, inMemoryPersistence } from "@firebase/auth";
import type { User } from "@firebase/auth";
import { PROD } from "./config";

const useEmulator = !PROD;

const firebaseConfig = {
    apiKey: "",
    authDomain: "",
    projectId: "",
    storageBucket: "",
    messagingSenderId: "",
    appId: "",
    measurementId: ""
  };

const firebaseApp = initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);
console.log("Firebase app initialized");

if (useEmulator) {
  connectAuthEmulator(auth, "http://localhost:9099");
} 

setPersistence(auth, inMemoryPersistence)
  .catch((error) => {
    console.error("Error setting auth persistence:", error);
  });

export { auth, firebaseApp, signInWithEmailAndPassword, User };

export default firebaseApp;