//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import FirebaseFirestore
import Foundation

extension HealthKitUploadStandard {
    /// Stores the user device APNs Token in the user's document directory.
    ///
    /// - Parameter token: The specific device token to be stored as a `String`.
    func storeToken(token: String?) async {
        struct FirebaseDocumentTokenData: Codable {
            let apnsToken: String?
        }

        do {
            let userDocument = try await userDocumentReference.getDocument()
            if userDocument.exists {
                let existingTokenData = try await userDocumentReference.getDocument(as: FirebaseDocumentTokenData.self)

                // Unwrap existingTokenData.apns_token and provide a default value if it's nil
                if existingTokenData.apnsToken != nil {
                    if existingTokenData.apnsToken != token {
                        try await userDocumentReference.updateData(["apnsToken": token ?? ""])
                    }
                }
                // user currently doesn't have apns token, must initialize a new field
                else {
                    try await userDocumentReference.setData(["apnsToken": token ?? ""], merge: true)
                }
            }
        } catch {
            print("Error retrieving user document: \(error)")
        }
    }

    /// Stores the timestamp when a notification was received by
    /// the user's device to the specific notification document.
    ///
    /// - Parameter timestamp: The time which the notification was received by the device
    func addNotificationReceivedTimestamp(timeSent: String, timeReceived: String) async {
        // path = user_id/notifications/data/logs/YYYY-MM-DDThh:mm:ss.mss
        let path: String
        do {
            path = try await getPath(module: .notifications("logs")) + "\(timeSent)"
        } catch {
            print("Failed to define path: \(error.localizedDescription)")
            return
        }

        // try push to Firestore.
        do {
            try await Firestore.firestore().document(path).setData(["received": timeReceived], merge: true)
        } catch {
            print("Failed to set data in Firestore: \(error.localizedDescription)")
        }
    }

    /// Stores the timestamp when a notification was opened by
    /// the user's device to the specific notification document.
    ///
    /// - Parameter timeSent: The time which the notification was sent, used for the path in Firestore.
    /// - Parameter timeOpened: The time which the notification was opened, generated when the user opens the notification.
    func addNotificationOpenedTimestamp(timeSent: String, timeOpened: String) async {
        // path = user_id/notifications/data/logs/YYYY-MM-DDThh:mm:ss.mss
        let path: String
        do {
            path = try await getPath(module: .notifications("logs")) + "\(timeSent)"
        } catch {
            print("Failed to define path: \(error.localizedDescription)")
            return
        }

        // try push to Firestore.
        do {
            try await Firestore.firestore().document(path).setData(["opened": timeOpened], merge: true)
        } catch {
            print("Failed to set data in Firestore: \(error.localizedDescription)")
        }
    }
}
