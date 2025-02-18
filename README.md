<!--
SPDX-FileCopyrightText: 2025 Stanford University

SPDX-License-Identifier: MIT
-->

# GPTCoach: Towards LLM-Based Physical Activity Coaching (CHI 2025)

__GPTCoach is an LLM-based health coaching chatbot designed to develop a physical activity plan that is tailored to the needs, abilities, and goals of a client.__ GPTCoach implements the onboarding conversation from [Active Choices](https://med.stanford.edu/healthyaging/active-choices-program.html), an evidence-based health coaching program, uses counseling strategies from motivational interviewing, and can query and visualize a user's health data from a wearable device through tool use. 

![Example of a GPTCoach conversation and step count visualization. This figure consists of two parts: a text-based conversation and a bar chart. On the left, a chat interface shows a conversation between a user named Alex and GPTCoach. GPTCoach asks Alex about their physical activity goals and reassures them about the challenges of balancing exercise with parenting. Alex responds by sharing their struggle as a new parent to find time to exercise, and GPTCoach provides supportive feedback, emphasizing the importance of a personalized plan and small, consistent steps toward physical activity. On the right, a bar chart labeled “Step Count” for March 2024 shows the number of steps taken each day, ranging from 0 to 20,000 steps. The X-axis represents days in March, and the Y-axis represents the number of steps. A toggle at the top right allows switching between day, week, and month views, with the month currently selected. A brief message from GPTCoach below the chart mentions that Alex averaged around 6,738 steps per day in March and providing encouragement that they are still staying active amidst their busy schedule as a new parent.](./assets/cover.jpg)

This reposity contains code that accompanies the publication:

> Matthew Jörke, Shardul Sapkota, Lyndsea Warkenthien, Niklas Vainio, Paul Schmiedmayer, Emma Brunskill, James A. Landay. 2025. [GPTCoach: Towards LLM-Based Physical Activity Coaching](), In *CHI Conference on Human Factors in Computing Systems (CHI '25)*. 

## Overview
![GPTCoach’s System Architecture Diagram. The diagram illustrates how data flows between the components. The iOS Application (left) receives HealthKit data from connected devices like smartwatches and smartphones, which is then sent to the database (middle-left). The backend Server (middle-right): The backend server interacts with the OpenAI API (below the server) and sends data visualizations and chat messages to the frontend (right).](./assets/system.jpg)
Our system architecture consists of four main components:
1. A [Google Cloud Firestore](https://firebase.google.com/docs/firestore) __database__ containing health data and conversation histories. We also use Firebase Authentication to manage user accounts.
2. An __iOS application__ that fetches three months of historical data using Apple's HealthKit API and uploads the data to our database. This application is built using the [Stanford Spezi Template Application](https://github.com/StanfordSpezi/SpeziTemplateApplication).
3. A Python/FastAPI __backend server__ that handles all LLM logic and tool call execution.
4. A Typescript/React a __frontend web interface__ that displays the chat interface and interactive data visualizations.

### Repository Structure

- `backend/` contains the code for our Python/FastAPI backend server.
- `frontend/` contains the code for our Typescript/React frontend web interface.
- `ios/` contains the code for our iOS application.
- `prompts/` contains the prompt templates used by our backend server. Please see our copyright notice below regarding the use of the [Active Choices](https://med.stanford.edu/healthyaging/active-choices-program.html) materials.

## Installation

### Firestore Database
1. Create a new [Google Cloud Firestore](https://firebase.google.com/docs/firestore) project.
2. In your Firebase project settings:
    - Add a new web app and copy the Firebase config into `frontend/utils/firebase.ts`.
    - Add a new iOS application with the appropriate bundle ID and copy the `GoogleService-Info.plist` file into `ios/HealthKitUpload/Supporting Files`.
    - Add a new Firebase Admin SDK service account and download the private key JSON file. Copy this file into `backend/serviceAccount.json`. Copy your Firebase project name into `backend/firebase.py`.
3. If you would like to use the Firebase emulator, you can follow [these instructions](https://firebase.google.com/docs/emulator-suite/connect_and_prototype) to configure the emulator. 
    - You will need to run `firebase init` from the root directory, select the Firestore and Emulators options, and configure your project.
    - Then, you can run the emulator with `firebase emulators:start`. 
    - The backend and frontend are configured to connect to the emulator by default, unless the `PROD` environment variable is set to `True`. You can manually override this behavior in `firebase.py` and `firebase.ts`.
    - The iOS application is configured to connect to the emulator whenever the app is running on a simulator. You can override this behavior by setting the `useFirebaseEmulator` in `FeatureFlags.swift`

### Backend
1. Create a new [OpenAI](https://platform.openai.com/) account and generate an API key. Copy this key into `backend/gpt/openai_client.py`.
2. Install the required Python packages with `pip install -r requirements.txt`. We recommend using a virtual environment or conda.
3. Start the backend server from the `backend` directory with `uvicorn main:app --port 5000 --reload`.

### Frontend
1. Install the required Node packages with `npm install` from the `frontend` directory.
2. Start the frontend server with `npm run dev`.

### iOS Application
1. Open the `ios/HealthKitUpload.xcodeproj` file in Xcode.
2. Select your development team in the Signing & Capabilities tab and make sure that the bundle ID matches the one you used to register your iOS app in the Firebase console.
3. Choose your target (simulator or physical device) and build the application.

__Note:__ You will need a Mac to build and run the iOS application. You will need to install Xcode from the App Store. By default, the simulator does not have any HealthKit data available, though you can add sample data using the Health app. To test with real data, you will need to run the application on a physical iPhone.

## Licensing
Our project uses the [REUSE Standard](https://reuse.software) for copyright and licensing. Please note that not all files may be licensed under the same terms:

1. **Open-Source Code (MIT License)**  
All code in `backend`, `frontend`, and `ios` is licensed under the [MIT license](LICENSES/MIT.txt).

2. **Active Choices Prompts (Proprietary)**  
The dialogue state prompts in [`prompts/dialogue`](prompts/dialogue/)  are **not** open source and are © 2025 Board of Trustees of the Leland Stanford Junior University.  Any use or adaptation requires prior written approval from the Stanford HEARTS Lab Faculty Director. See [`LICENSES/ActiveChoices.txt`](LICENSES/ActiveChoices.txt) for details.

## Contact
For questions, please contact Matthew Jörke at [joerke@stanford.edu](mailto:joerke@stanford.edu). Please note that GPTCoach is a research prototype and will not be actively maintained. We can provide limited technical support and cannot guarantee that the software will run in the future. 

## Contributors
[Matthew Jörke](https://github.com/mjoerke), [Shardul Sapkota](https://github.com/sapkotashardul), [Niklas Vainio](https://github.com/niklas-vainio), [Paul Schmiedmayer](https://github.com/PSchmiedmayer) were the primary developers of the project.

[Niall Kehoe](https://github.com/niallkehoe) and [Anthony Xie](https://github.com/anthonyxie) made significant contributions to the frontend and backend codebase during a summer 2023 CURIS internship. [Romuald Thomas](https://github.com/romualdthomas) significantly contributed to the backend in a Fall 2023 research internship.

[Evelyn Hur](https://github.com/evelyn-hur),
[Bryant Jimenez](https://github.com/bryant-jimenez), 
[Dhruv Naik](https://github.com/dhruvna1k),
[Evelyn Song](https://github.com/EvelynBunnyDev), and
[Caroline Tran](https://github.com/carolinentran) contributed to the iOS application as part of the course CS342: Building for Digital Health in Winter 2024. 
[Bryant Jimenez](https://github.com/bryant-jimenez) made subsantial contributions to the `BulkUpload` functionality in `SpeziHealthKit`.
We thank the CS342 course staff for supervising the student team, including 
[Paul Schmiedmayer](https://github.com/PSchmiedmayer),
[Andreas Bauer](https://github.com/Supereg),
[Philipp Zagar](https://github.com/philippzagar), and
[Nikolai Madlener](https://github.com/NikolaiMadlener).
