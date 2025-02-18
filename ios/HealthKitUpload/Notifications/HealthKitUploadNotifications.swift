//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project.
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import Firebase
import FirebaseCore
import Spezi
import SpeziFirebaseConfiguration
import SwiftUI

class HealthKitUploadNotifications: NSObject, Module, NotificationHandler,
                               UNUserNotificationCenterDelegate, EnvironmentAccessible {
    @StandardActor var standard: HealthKitUploadStandard
    @Dependency private var configureFirebaseApp: ConfigureFirebaseApp

    override init() {}

    func handleNotificationsAllowed() async throws {
            let authOptions: UNAuthorizationOptions = [.alert, .badge, .sound]
            try await UNUserNotificationCenter.current().requestAuthorization(options: authOptions)
        }

    /// Sends a local notification to reopen the app to resume HK Data upload.
    func sendHealthKitUploadPausedNotification() {
        let content = UNMutableNotificationContent()
        content.title = "Health Data Upload Paused"
        content.body = "Please open the app to continue the upload of your health data."
        let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil)
        UNUserNotificationCenter.current().add(request)
    }
}
