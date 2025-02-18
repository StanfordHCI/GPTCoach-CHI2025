//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import FirebaseFirestore
import OSLog
import Spezi
import SpeziAccount
import SpeziFirebaseAccountStorage

actor HealthKitUploadStandard: Standard, EnvironmentAccessible {
    enum HealthKitUploadStandardError: Error {
        case userNotAuthenticatedYet
    }

    /// modify this study id to change the Firebase bucket.
    static let STUDYID = "testing"

    static var userCollection: CollectionReference {
        Firestore.firestore().collection("studies").document(STUDYID).collection("users")
    }

    @Dependency var accountStorage: FirestoreAccountStorage?
    @AccountReference var account: Account

    let logger = Logger(subsystem: "HKUpload", category: "Standard")

    init() {
        if !FeatureFlags.disableFirebase {
            _accountStorage = Dependency(wrappedValue: FirestoreAccountStorage(storeIn: HealthKitUploadStandard.userCollection))
        }
    }
}
