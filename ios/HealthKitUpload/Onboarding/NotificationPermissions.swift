//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import SpeziOnboarding
import SpeziScheduler
import SwiftUI

struct NotificationPermissions: View {
    @Environment(OnboardingNavigationPath.self) private var onboardingNavigationPath
    @Environment(HealthKitUploadNotifications.self) private var pushNotifications

    @State private var notificationProcessing = false

    var descriptionText =  LocalizedStringKey("STUDY_NOTIFICATION_PERMISSIONS_DESCRIPTION")
    var body: some View {
        OnboardingView(
            contentView: {
                VStack {
                    OnboardingTitleView(
                        title: "NOTIFICATION_PERMISSIONS_TITLE",
                        subtitle: "NOTIFICATION_PERMISSIONS_SUBTITLE"
                    )
                    Spacer()
                    Image(systemName: "bell.square.fill")
                        .font(.system(size: 150))
                        .foregroundColor(.accentColor)
                        .accessibilityHidden(true)
                    Text(descriptionText)
                        .multilineTextAlignment(.center)
                        .padding(.vertical, 16)
                    Spacer()
                }
            }, actionView: {
                OnboardingActionsView(
                    "NOTIFICATION_PERMISSIONS_BUTTON",
                    action: {
                        do {
                            notificationProcessing = true

                            try await pushNotifications.handleNotificationsAllowed()
                        } catch {
                            print("Could not request notification permissions.")
                        }
                        notificationProcessing = false

                        onboardingNavigationPath.nextStep()
                    }
                )
            }
        )
            .navigationBarBackButtonHidden(notificationProcessing)
            // Small fix as otherwise "Login" or "Sign up" is still shown in the nav bar
            .navigationTitle(Text(verbatim: ""))
    }
}

#if DEBUG
#Preview {
    OnboardingStack {
        NotificationPermissions()
    }
        .previewWith(standard: HealthKitUploadStandard()) {
            HealthKitUploadNotifications()
        }
}
#endif
