//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import FirebaseAuth
import SpeziAccount
import SwiftUI

struct HomeView: View {
    static var accountEnabled: Bool {
        !FeatureFlags.disableFirebase && !FeatureFlags.skipOnboarding
    }

    @Environment(HealthKitUploadStandard.self) private var standard
    @State private var presentingAccount = false

    var body: some View {
        HKUploadProgress(presentingAccount: $presentingAccount)
            .sheet(isPresented: $presentingAccount) {
                AccountSheet()
            }
            .accountRequired(Self.accountEnabled) {
                AccountSheet()
            }
            .verifyRequiredAccountDetails(Self.accountEnabled)
    }
}

#if DEBUG
#Preview {
    let details = AccountDetails.Builder()
        .set(\.userId, value: "lelandstanford@stanford.edu")
        .set(\.name, value: PersonNameComponents(givenName: "Leland", familyName: "Stanford"))

    return HomeView()
        .previewWith(standard: HealthKitUploadStandard()) {
            AccountConfiguration(building: details, active: MockUserIdPasswordAccountService())
        }
}

#Preview {
    CommandLine.arguments.append("--disableFirebase") // make sure the MockWebService is displayed
    return HomeView()
        .previewWith(standard: HealthKitUploadStandard()) {
            AccountConfiguration {
                MockUserIdPasswordAccountService()
            }
        }
}
#endif
