//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import FirebaseFirestore
import HealthKitOnFHIR
import ModelsR4
import SpeziFirestore
import SpeziHealthKit

extension HealthKitUploadStandard: BulkUploadConstraint, HealthKitConstraint {
    // Converts an HKSample to a Firestore-compatible resource and returns the path and resource dictionary
    private func convertToFirestoreResource(sample: HKSample) async throws -> (path: String, resource: [String: Any]) {
        let effectiveTimestamp = sample.startDate.toISOFormat()
        let path = try await getPath(module: .health(sample.sampleType.identifier)) + "raw/\(effectiveTimestamp)"

        let deviceName = sample.sourceRevision.source.name
        let timeIndex = Date.constructTimeIndex(startDate: sample.startDate, endDate: sample.endDate)

        let resource = try sample.resource
        let encoder = FirebaseFirestore.Firestore.Encoder()
        var firestoreResource = try encoder.encode(resource)

        firestoreResource["device"] = deviceName
        firestoreResource.merge(timeIndex as [String: Any]) { _, new in new }
        firestoreResource["datetimeStart"] = effectiveTimestamp

        return (path, firestoreResource)
    }

    /// Notifies the `Standard` about the addition of a batch of HealthKit ``HKSample`` samples instance.
    /// - Parameter samplesAdded: The batch of `HKSample`s that should be added.
    /// - Parameter objectsDeleted: The batch of `HKSample`s that were deleted from the HealthStore. Included if needed to account for rate limiting
    /// when uploading to a cloud provider.
    func processBulk(samplesAdded: [HKSample], samplesDeleted: [HKDeletedObject]) async {
        let startTime = DispatchTime.now()

        var documentsToAdd: [(String, [String: Any])] = []
        await withTaskGroup(of: Optional<(String, [String: Any])>.self) { group in
            for sample in samplesAdded {
                group.addTask {
                    do {
                        return try await self.convertToFirestoreResource(sample: sample)
                    } catch {
                        self.logger.error("Error converting sample to Firestore resource: \(error.localizedDescription)")
                        return nil
                    }
                }
            }

            for await result in group {
                if let result = result {
                    documentsToAdd.append(result)
                }
            }
        }

        await uploadBatch(documents: documentsToAdd, retryCount: 0)

        let endTime = DispatchTime.now()
        let elapsedTime = endTime.uptimeNanoseconds - startTime.uptimeNanoseconds
        let minimumDuration: UInt64 = 1_200_000_000 // 1s = 1,000,000,000ns (with 0.2s buffer time)

        if elapsedTime < minimumDuration {
           let sleepDuration = minimumDuration - elapsedTime
           try? await _Concurrency.Task.sleep(nanoseconds: sleepDuration)
        }
    }

    private func uploadBatch(documents: [(String, [String: Any])], retryCount: Int) async {
        do {
            let db = Firestore.firestore()
            let batch = db.batch()

            for (path, data) in documents {
                let docRef = db.document(path)
                batch.setData(data, forDocument: docRef)
            }

            try await batch.commit()
            logger.info("Batch write succeeded.")
        } catch {
            logger.error("Error writing batch: \(error)")
            if retryCount < 5 {
                let backoffTime = UInt64(pow(2.0, Double(retryCount))) * 1_000_000_000 // Exponential backoff in seconds
                logger.info("Retrying batch upload in \(backoffTime / 1_000_000_000) seconds...")
                try? await _Concurrency.Task.sleep(nanoseconds: backoffTime)
                await uploadBatch(documents: documents, retryCount: retryCount + 1)
            } else {
                logger.error("Reached maximum retry attempts for batch upload.")
            }
        }
    }

    /// Adds a new `HKSample` to the Firestore.
    /// - Parameter response: The `HKSample` that should be added.
    func add(sample: HKSample) async {
        do {
            let (path, resource) = try await convertToFirestoreResource(sample: sample)
            try await Firestore.firestore().document(path).setData(resource)
        } catch {
            logger.error("Failed to add data in Firestore: \(error.localizedDescription)")
        }
    }

    func remove(sample: HKDeletedObject) async {}

    func toggleHideFlag(sampleType: HKSampleType, documentId: String, alwaysHide: Bool) async throws {
        let firestore = Firestore.firestore()
        let path: String

        do {
            // call getPath to get the path for this user, up until this specific quantityType
            path = try await getPath(module: .health(sampleType.identifier)) + "raw/\(documentId)"
            logger.debug("Selected identifier: \(sampleType.identifier)")
            logger.debug("Path from getPath: \(path)")
        } catch {
            logger.error("Failed to define path: \(error.localizedDescription)")
            throw error
        }

        do {
            let document = firestore.document(path)
            let docSnapshot = try await document.getDocument()

            // If hideFlag exists, update its value
            if let hideFlagExists = docSnapshot.data()?["hideFlag"] as? Bool {
                if alwaysHide {
                    // If alwaysHide is true, always set hideFlag to true regardless of original value
                    try await document.setData(["hideFlag": true], merge: true)
                    logger.debug("AlwaysHide is enabled; set hideFlag to true.")
                } else {
                    // Toggle hideFlag if alwaysHide is not true
                    try await document.setData(["hideFlag": !hideFlagExists], merge: true)
                    logger.debug("Toggled hideFlag to \(!hideFlagExists).")
                }
            } else {
                // If hideFlag does not exist, create it and set to true
                try await document.setData(["hideFlag": true], merge: true)
                logger.debug("hideFlag was missing; set to true.")
            }
        } catch {
            logger.error("Failed to set data in Firestore: \(error.localizedDescription)")
            throw error
        }
    }

    func fetchRecentSamples(for sampleType: HKSampleType, limit: Int = 50) async -> [QueryDocumentSnapshot] {
        guard !ProcessInfo.processInfo.isPreviewSimulator else {
            return []
        }

        do {
            let path = try await getPath(module: .health(sampleType.identifier)) + "raw/"
            logger.debug("Selected identifier: \(sampleType.identifier)")
            logger.debug("Path from getPath: \(path)")

            #warning("The logic should ideally not be based on the issued date but rather datetimeStart once this is reflected in the mock data.")
            let querySnapshot = try await Firestore
                .firestore()
                .collection(path)
                .order(by: "issued", descending: true)
                .limit(to: limit)
                .getDocuments()

            return querySnapshot.documents
        } catch {
            logger.error("Failed to fetch documents or define path: \(error.localizedDescription)")
            return []
        }
    }

    // Fetches timestamp based on documentID date
    func hideSamples(sampleType: HKSampleType, startDate: Date, endDate: Date) async {
        do {
            let path = try await getPath(module: .health(sampleType.identifier)) + "raw/"
            logger.debug("Selected identifier: \(sampleType.identifier)")
            logger.debug("Path from getPath: \(path)")

            #warning("The logic should ideally not be based on the issued date but rather datetimeStart once this is reflected in the mock data.")
            let querySnapshot = try await Firestore
                .firestore()
                .collection(path)
                .whereField("issued", isGreaterThanOrEqualTo: startDate.toISOFormat())
                .whereField("issued", isLessThanOrEqualTo: endDate.toISOFormat())
                .getDocuments()

            #warning("This execution is slow. We should have a clound function or backend endpoint for this.")
            for document in querySnapshot.documents {
                try await toggleHideFlag(sampleType: sampleType, documentId: document.documentID, alwaysHide: true)
            }
        } catch {
            if let firestoreError = error as? FirestoreError {
                logger.error("Error fetching documents: \(firestoreError.localizedDescription)")
            } else {
                logger.error("Unexpected error: \(error.localizedDescription)")
            }
        }
    }
}
