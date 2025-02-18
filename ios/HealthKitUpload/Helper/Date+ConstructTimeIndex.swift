//
// This source file is part of the Stanford GPTCoach Application based on the Stanford Spezi Template Application Project
//
// SPDX-FileCopyrightText: 2023 Stanford University
//
// SPDX-License-Identifier: MIT
//

import Foundation

extension Date {
    static func constructTimeIndex(startDate: Date, endDate: Date) -> [String: Any?] {
        let calendar = Calendar.current
        // extract the calendar components from the startDate and the endDate
        let startComponents = calendar.dateComponents([.year, .month, .day, .hour, .minute, .second, .timeZone], from: startDate)
        let endComponents = calendar.dateComponents([.year, .month, .day, .hour, .minute, .second, .timeZone], from: endDate)
        let isRange = startDate != endDate

        // initialize a dictionary for timeIndex and populate with info extracted above
        var timeIndex: [String: Any?] = [
            "range": isRange,
            "timezone": startComponents.timeZone?.identifier,
            "datetimeStart": startDate.toISOFormat(),
            "datetimeEnd": endDate.toISOFormat()
        ]

        // passing the timeIndex dictionary by reference so the changes persist
        addTimeIndexComponents(&timeIndex, dateComponents: startComponents, suffix: "Start")
        addTimeIndexComponents(&timeIndex, dateComponents: endComponents, suffix: "End")
        addTimeIndexRangeComponents(&timeIndex, startComponents: startComponents, endComponents: endComponents)

        return timeIndex
    }

    // populate timeIndex dict with individual components from DateComponents (startComponents for this case)
    // "inout" parameter means the argument is passed by reference (dict is modified inside the funct and changes persist)
    private static func addTimeIndexComponents(_ timeIndex: inout [String: Any?], dateComponents: DateComponents, suffix: String) {
        timeIndex["year" + suffix] = dateComponents.year
        timeIndex["month" + suffix] = dateComponents.month
        timeIndex["day" + suffix] = dateComponents.day
        timeIndex["hour" + suffix] = dateComponents.hour
        timeIndex["minute" + suffix] = dateComponents.minute
        timeIndex["second" + suffix] = dateComponents.second
        timeIndex["dayMinute" + suffix] = calculateDayMinute(hour: dateComponents.hour, minute: dateComponents.minute)
        timeIndex["fifteenMinBucket" + suffix] = calculate15MinBucket(hour: dateComponents.hour, minute: dateComponents.minute)
    }

    // if the start/end time shows that we have a time RANGE and not a time STAMP
    // then add the range-related components to the timeIndex
    private static func addTimeIndexRangeComponents(
        _ timeIndex: inout [String: Any?],
        startComponents: DateComponents,
        endComponents: DateComponents
    ) {
        timeIndex["yearRange"] = getRange(
            start: startComponents.year,
            end: endComponents.year,
            maxValue: Int.max
        )
        timeIndex["monthRange"] = getRange(
            start: startComponents.month,
            end: endComponents.month,
            maxValue: 12,
            startValue: 1 // months are 1-indexed
        )
        timeIndex["dayRange"] = getRange(
            start: startComponents.day,
            end: endComponents.day,
            maxValue: daysInMonth(month: startComponents.month, year: startComponents.year),
            startValue: 1 // days are 1-indexed
        )
        timeIndex["hourRange"] = getRange(
            start: startComponents.hour,
            end: endComponents.hour,
            maxValue: 23
        )
        timeIndex["dayMinuteRange"] = getRange(
            start: calculateDayMinute(hour: startComponents.hour, minute: startComponents.minute),
            end: calculateDayMinute(hour: endComponents.hour, minute: endComponents.minute),
            maxValue: 1439
        )
        timeIndex["fifteenMinBucketRange"] = getRange(
            start: calculate15MinBucket(hour: startComponents.hour, minute: startComponents.minute),
            end: calculate15MinBucket(hour: endComponents.hour, minute: endComponents.minute),
            maxValue: 95
        )

        // Minute and second ranges are not likely to be accurate since they often will fill the whole range.
        // We will also never query on individual minutes or seconds worth of data.
    }

    // swiftlint:disable discouraged_optional_collection
    // passed the start and end bounds, returns the range in whichever unit passed in
    private static func getRange(start: Int?, end: Int?, maxValue: Int?, startValue: Int = 0) -> [Int]? {
        guard let startInt = start, let endInt = end, let maxValueInt = maxValue else {
            return nil
        }

        if startInt <= endInt {
            return Array(startInt...endInt)
        } else {
            return Array(startInt...maxValueInt) + Array(startValue...endInt)
        }
    }

    private static func daysInMonth(month: Int?, year: Int?) -> Int? {
        let dateComponents = DateComponents(year: year, month: month)
        let calendar = Calendar.current
        guard let date = calendar.date(from: dateComponents),
              let range = calendar.range(of: .day, in: .month, for: date) else {
            return nil // Provide a default value in case of nil
        }
        return range.count
    }

    private static func calculateDayMinute(hour: Int?, minute: Int?) -> Int? {
        guard let hour = hour, let minute = minute else {
            return nil
        }
        return hour * 60 + minute
    }

    private static func calculate15MinBucket(hour: Int?, minute: Int?) -> Int? {
        guard let hour = hour, let minute = minute else {
            return nil
        }
        return hour * 4 + minute / 15
    }
}
