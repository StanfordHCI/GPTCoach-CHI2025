//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import SwiftUI

struct AccountButton: View {
    static let shouldDisplay = !FeatureFlags.disableFirebase || ProcessInfo.processInfo.isPreviewSimulator

    @Binding private var isPresented: Bool

    var body: some View {
        Button(action: {
            isPresented = true
        }) {
            Image(systemName: "person.crop.circle")
        }
            .accessibilityLabel("ACCOUNT_TITLE")
    }

    init(isPresented: Binding<Bool>) {
        self._isPresented = isPresented
    }
}

#if DEBUG
#Preview(traits: .sizeThatFitsLayout) {
    AccountButton(isPresented: .constant(false))
}
#endif
