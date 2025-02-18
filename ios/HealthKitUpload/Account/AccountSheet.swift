//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import SpeziAccount
import SwiftUI

struct AccountSheet: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(Account.self) private var account
    @Environment(\.accountRequired) private var accountRequired

    @State private var isInSetup = false
    @State private var overviewIsEditing = false

    var body: some View {
        NavigationStack {
            ZStack {
                if account.signedIn && !isInSetup {
                    AccountOverview(isEditing: $overviewIsEditing)
                        .onDisappear {
                            overviewIsEditing = false
                        }
                        .toolbar {
                            if !overviewIsEditing {
                                closeButton
                            }
                        }
                } else {
                    AccountSetup { _ in
                        dismiss() // we just signed in, dismiss the account setup sheet
                    } header: {
                        AccountSetupHeader()
                    }
                        .onAppear {
                            isInSetup = true
                        }
                        .toolbar {
                            if !accountRequired {
                                closeButton
                            }
                        }
                }
            }
        }
    }

    var closeButton: some ToolbarContent {
        ToolbarItem(placement: .cancellationAction) {
            Button("CLOSE") {
                dismiss()
            }
        }
    }
}

#if DEBUG
#Preview("AccountSheet") {
    let details = AccountDetails.Builder()
        .set(\.userId, value: "lelandstanford@stanford.edu")
        .set(\.name, value: PersonNameComponents(givenName: "Leland", familyName: "Stanford"))

    return AccountSheet()
        .previewWith {
            AccountConfiguration(building: details, active: MockUserIdPasswordAccountService())
        }
}

#Preview("AccountSheet SignIn") {
    AccountSheet()
        .previewWith {
            AccountConfiguration {
                MockUserIdPasswordAccountService()
            }
        }
}
#endif
