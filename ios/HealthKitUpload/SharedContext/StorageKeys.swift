//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

/// Constants shared across the Spezi Teamplate Application to access storage information including the `AppStorage` and `SceneStorage`
enum StorageKeys {
    // MARK: - Onboarding
    /// A `Bool` flag indicating of the onboarding was completed.
    static let onboardingFlowComplete = "onboardingFlow.complete"
    /// A `Step` flag indicating the current step in the onboarding process.
    static let onboardingFlowStep = "onboardingFlow.step"

    // MARK: - Home
    /// The currently selected home tab.
    static let homeTabSelection = "home.tabselection"

    // MARK: - Privacy Controls
    /// The privacy control settings of a user which sample types should be collected
    static let privacyControlsSampleTypes = "privacy.controlsampletypes"
}
