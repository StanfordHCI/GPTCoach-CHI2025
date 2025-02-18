//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import FirebaseCore
import FirebaseMessaging
import Spezi
import SpeziAccount
import SpeziFirebaseAccount
import SpeziFirebaseStorage
import SpeziFirestore
import SpeziHealthKit
import SpeziOnboarding
import SpeziScheduler
import SwiftUI

class HealthKitUploadDelegate: SpeziAppDelegate {
    // https://developer.apple.com/documentation/healthkit/data_types#2939032
    static let healthKitSampleTypes = [
        // Activity
        HKQuantityType(.stepCount),
        HKQuantityType(.distanceWalkingRunning),
        HKQuantityType(.basalEnergyBurned),
        HKQuantityType(.activeEnergyBurned),
        HKQuantityType(.flightsClimbed),
        HKQuantityType(.appleExerciseTime),
        HKQuantityType(.appleMoveTime),
        HKQuantityType(.appleStandTime),

        // Vital Signs
        HKQuantityType(.heartRate),
        HKQuantityType(.restingHeartRate),
        HKQuantityType(.heartRateVariabilitySDNN),
        HKQuantityType(.walkingHeartRateAverage),
        HKQuantityType(.oxygenSaturation),
        HKQuantityType(.respiratoryRate),
        HKQuantityType(.bodyTemperature),

        // Other events
        HKCategoryType(.sleepAnalysis),
        HKWorkoutType.workoutType()
    ]

    override var configuration: Configuration {
        Configuration(standard: HealthKitUploadStandard()) {
            if !FeatureFlags.disableFirebase {
                AccountConfiguration(configuration: [
                    .requires(\.userId),
                    .requires(\.name)
                ])
                if FeatureFlags.useFirebaseEmulator {
                    FirebaseAccountConfiguration(
                        authenticationMethods: [.emailAndPassword, .signInWithApple],
                        emulatorSettings: (host: "localhost", port: 9099)
                    )
                } else {
                    FirebaseAccountConfiguration(authenticationMethods: [.emailAndPassword])
                }
                firestore
                if FeatureFlags.useFirebaseEmulator {
                    FirebaseStorageConfiguration(emulatorSettings: (host: "localhost", port: 9199))
                } else {
                    FirebaseStorageConfiguration()
                }
            }
            if HKHealthStore.isHealthDataAvailable() {
                healthKit
            }
            OnboardingDataSource()
            HealthKitUploadNotifications()
        }
    }

    private var firestore: Firestore {
        let settings = FirestoreSettings()
        if FeatureFlags.useFirebaseEmulator {
            settings.host = "localhost:8080"
            settings.cacheSettings = MemoryCacheSettings()
            settings.isSSLEnabled = false
        }

        return Firestore(
            settings: settings
        )
    }

    private var healthKit: HealthKit {
        HealthKit {
            BulkUpload(
                Set(HealthKitUploadDelegate.healthKitSampleTypes),
                /// predicate to request data from one month in the past to present.
                predicate: HKQuery.predicateForSamples(
                    withStart: Calendar.current.date(byAdding: .month, value: -3, to: .now),
                    end: Date(),
                    options: .strictEndDate
                ),
                bulkSize: 500,
                deliveryStartSetting: .automatic
            )
            CollectSamples(
                Set(HealthKitUploadDelegate.healthKitSampleTypes),
                deliverySetting: .anchorQuery(.automatic)
            )
        }
    }
}
