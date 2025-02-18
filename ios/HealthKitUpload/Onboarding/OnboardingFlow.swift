//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import SpeziAccount
import SpeziFirebaseAccount
import SpeziHealthKit
import SpeziOnboarding
import SwiftUI

/// Displays an multi-step onboarding flow
struct OnboardingFlow: View {
    @Environment(HealthKit.self) private var healthKitDataSource

    @AppStorage(StorageKeys.onboardingFlowComplete) private var completedOnboardingFlow = false

    private var healthKitAuthorization: Bool {
        // As HealthKit not available in preview simulator
        if ProcessInfo.processInfo.isPreviewSimulator {
            return false
        }

        return healthKitDataSource.authorized
    }

    var body: some View {
        OnboardingStack(onboardingFlowComplete: $completedOnboardingFlow) {
            Welcome()
            if !FeatureFlags.disableFirebase {
                AccountOnboarding()
            }
            if HKHealthStore.isHealthDataAvailable() && !healthKitAuthorization {
                HealthKitPermissions()
            }
            NotificationPermissions()
        }
            .interactiveDismissDisabled(!completedOnboardingFlow)
    }
}

#if DEBUG
#Preview {
    OnboardingFlow()
        .environment(Account(MockUserIdPasswordAccountService()))
        .previewWith(standard: HealthKitUploadStandard()) {
            OnboardingDataSource()
            HealthKit()
            AccountConfiguration {
                MockUserIdPasswordAccountService()
            }
        }
}
#endif
