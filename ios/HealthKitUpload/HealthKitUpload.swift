//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import Spezi
import SpeziFirebaseAccount
import SwiftUI

@main
struct HealthKitUpload: App {
    @UIApplicationDelegateAdaptor(HealthKitUploadDelegate.self) var appDelegate
    @AppStorage(StorageKeys.onboardingFlowComplete) var completedOnboardingFlow = false

    var body: some Scene {
        WindowGroup {
            ZStack {
                if completedOnboardingFlow {
                    HomeView()
                } else {
                    EmptyView()
                }
            }
                .sheet(isPresented: !$completedOnboardingFlow) {
                    OnboardingFlow()
                }
                .spezi(appDelegate)
        }
    }
}
