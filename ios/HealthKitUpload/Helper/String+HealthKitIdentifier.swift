//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import Foundation

extension String {
    /// converts a HKSample Type string representation to a lower cased id.
    /// e.g. "HKQuantityTypeIdentifierStepCount" => "stepcount".
    var healthKitDescription: String {
        if self == "workout" || self == "HKWorkoutTypeIdentifier" {
            return "workout"
        }

        let prefixes = ["HKQuantityTypeIdentifier", "HKCategoryTypeIdentifier", "HKCorrelationTypeIdentifier", "HKWorkoutTypeIdentifier"]
        for prefix in prefixes where self.hasPrefix(prefix) {
            return self.dropFirst(prefix.count).lowercased()
        }
        // return "unknown"
        return self
    }
}
