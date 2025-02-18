//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//
// Created by Bryant Jimenez on 3/28/24.
//

import SpeziHealthKit
import SwiftUI
import SpeziViews

struct ProgressBarStyle: ProgressViewStyle {
    func makeBody(configuration: Configuration) -> some View {
        GeometryReader { geometry in
            ZStack(alignment: .leading) {
                Rectangle()
                    .foregroundColor(Color.secondary.opacity(0.3))
                    .frame(width: geometry.size.width, height: geometry.size.height)
                Rectangle()
                    .frame(width: CGFloat(configuration.fractionCompleted ?? 0) * geometry.size.width, height: geometry.size.height)
                    .animation(.linear, value: configuration.fractionCompleted)
            }
            .clipShape(RoundedRectangle(cornerRadius: 20))
        }
    }
}

struct HKUploadProgress: View {
    @Environment(HealthKit.self) private var healthKit
    @Binding var presentingAccount: Bool
    @Environment(\.scenePhase) private var scenePhase
    @Environment(HealthKitUploadNotifications.self) private var pushNotifications

    var body: some View {
        NavigationStack {
            VStack {
                Spacer()
                VStack {
                    Text("Upload Progress")
                        .font(.title)
                        .fontWeight(.bold)
                        .fontDesign(.rounded)
                        .padding()
                    ProgressView(value: healthKit.progress.fractionCompleted)
                        .progressViewStyle(ProgressBarStyle())
                        .frame(height: 20)
                        .padding(.horizontal)
                    Text("\(Int(healthKit.progress.fractionCompleted * 100))%")
                        .font(.headline)
                        .padding([.top, .bottom])
                    uploadText
                }
                .frame(maxWidth: .infinity)
                .padding()

                Spacer()
            }
            .toolbar {
                if AccountButton.shouldDisplay {
                    AccountButton(isPresented: $presentingAccount)
                }
            }
            .onChange(of: scenePhase) {
                if scenePhase == .background && !healthKit.progress.isFinished {
                    print("Entering background and progress is at \(healthKit.progress).")
                    pushNotifications.sendHealthKitUploadPausedNotification()
                }
            }
        }
    }

    var uploadText: some View {
        if healthKit.progress.fractionCompleted < 1 {
            return AnyView(
                VStack {
                    Text("HK_UPLOAD_TEXT_1")
                        .padding(.bottom)
                        .multilineTextAlignment(.center)
                    Text("HK_UPLOAD_TEXT_2")
                        .foregroundStyle(.gray)
                        .multilineTextAlignment(.center)
                }
            )
        } else {
            return AnyView(
                Text("Your upload is complete!")
                    .multilineTextAlignment(/*@START_MENU_TOKEN@*/.leading/*@END_MENU_TOKEN@*/)
            )
        }
    }
}

#if DEBUG
#Preview {
    HKUploadProgress(presentingAccount: .constant(false))
}
#endif
