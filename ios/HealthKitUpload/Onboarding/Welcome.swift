//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import SpeziOnboarding
import SwiftUI

struct Welcome: View {
    @Environment(OnboardingNavigationPath.self) private var onboardingNavigationPath

    var body: some View {
        Group {
            GeometryReader { geometry in
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(alignment: .center) {
                        title
                        Image(.healthKitUploadIconNoBG)
                            .resizable()
                            .scaledToFit()
                            .frame(width: 0.7 * geometry.size.width)
                            .accessibilityHidden(true)
                        Spacer()
                        description
                        Spacer()
                        OnboardingActionsView("WELCOME_BUTTON") {
                            onboardingNavigationPath.nextStep()
                        }
                        Spacer()
                            .frame(height: 10)
                    }
                        .frame(minHeight: geometry.size.height)
                }
            }
                .padding(24)
        }
    }

    var title: some View {
        return AnyView(
            Text("HealthKit Upload")
            .font(.system(size: 50))
            .fontWeight(.bold)
            .fontDesign(.rounded)
            .padding()
            .multilineTextAlignment(.center)
        )
    }

    var description: some View {
        VStack {
            Text("Welcome!")
                .font(.title)
                .fontWeight(.semibold)
                .opacity(0.7)
            Text("WELCOME_SUBTITLE")
                .padding([.top, .bottom])
        }
    }
}

#if DEBUG
#Preview {
    OnboardingStack {
        Welcome()
    }
}
#endif
