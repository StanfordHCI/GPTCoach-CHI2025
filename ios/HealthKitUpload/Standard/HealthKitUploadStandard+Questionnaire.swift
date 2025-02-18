//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import FirebaseFirestore
import Spezi
import SpeziFirestore
import SpeziQuestionnaire

/// Implementation of the  `QuestionnaireConstraint` from the Spezi Standard.
extension HealthKitUploadStandard {
    /// Adds a new `QuestionnaireResponse` to the Firestore.
    /// - Parameter response: The `QuestionnaireResponse` that should be added.
    func add(response: ModelsR4.QuestionnaireResponse) async {
        // fetching the Spezi tag (e.g. "midday/affect").
        guard let tag = response.item?[0].linkId.value else {
            return
        }

        // extracts the first item as that is the id.
        let rootTag = String("\(tag)".split(separator: "/")[0])
        let effectiveTimestamp = Date().toISOFormat()

        let path: String
        do {
            path = try await getPath(module: .questionnaire(rootTag)) + "raw/\(effectiveTimestamp)"
        } catch {
            print("Failed to define path: \(error.localizedDescription)")
            return
        }

        do {
            try await Firestore.firestore().document(path).setData(from: response)
        } catch {
            logger.error("Failed to set data in Firestore: \(error)")
            return
        }
    }
}
