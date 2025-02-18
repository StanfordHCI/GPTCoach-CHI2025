//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import FirebaseStorage
import PDFKit
import SpeziOnboarding

extension HealthKitUploadStandard: OnboardingConstraint {
    private var userBucketReference: StorageReference {
        get async throws {
            guard let details = await account.details else {
                throw HealthKitUploadStandardError.userNotAuthenticatedYet
            }

            return Storage.storage().reference().child("users/\(details.accountId)")
        }
    }

    /// Stores the given consent form in the user's document directory with a unique timestamped filename.
    ///
    /// - Parameter consent: The consent form's data to be stored as a `PDFDocument`.
    func store(consent: PDFDocument) async {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd_HHmmss"
        let dateString = formatter.string(from: Date())

        guard !FeatureFlags.disableFirebase else {
            guard let basePath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else {
                logger.error("Could not create path for writing consent form to user document directory.")
                return
            }

            let filePath = basePath.appending(path: "consentForm_\(dateString).pdf")
            consent.write(to: filePath)

            return
        }

        do {
            guard let consentData = consent.dataRepresentation() else {
                logger.error("Could not store consent form.")
                return
            }

            let metadata = StorageMetadata()
            metadata.contentType = "application/pdf"
            _ = try await userBucketReference.child("consent/\(dateString).pdf").putDataAsync(consentData, metadata: metadata)
        } catch {
            logger.error("Could not store consent form: \(error)")
        }
    }
}
