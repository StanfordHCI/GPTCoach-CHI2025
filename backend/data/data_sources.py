# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

from functools import lru_cache
from firebase import FirebaseManager
firebase_manager = FirebaseManager()

class DataSource:
    def __init__(self, data_source_name, units, data_type, description):
        self.module, self.name = data_source_name.split(".")
        self.units = units
        self.type = data_type 
        self.description = description

    def __str__(self):
        return f"{self.module}.{self.name}: {self.description} (Measured in {self.units})"

    def __repr__(self):
        return self.__str__()

DATA_SOURCES = {
    "health.activeenergyburned": DataSource("health.activeenergyburned", "kcal", "count", "This is an estimate of energy burned over and above your Resting Energy use (see Resting Energy). Active energy includes activity such as walking slowly, pushing your wheelchair and household chores, as well as exercise such as biking and dancing. Your total energy use is the sum of your Resting Energy and Active Energy."),
    "health.appleexercisetime": DataSource("health.appleexercisetime", "min", "count", "Every full minute of movement equal to or exceeding the intensity of a brisk walk for you counts towards your Exercise minutes. "),
    "health.applestandtime": DataSource("health.applestandtime", "min", "count", "Stand minutes are the minutes in each hour that you're standing and moving. Looking at your Stand minutes over time can help you understand how active or sedentary you are. Apple Watch automatically tracks and logs Stand minutes in Health. Earning at least one Stand Minute each hour also earned you the hour in your Stand ring. "),
    "health.basalenergyburned": DataSource("health.basalenergyburned", "kcal", "count", "This is an estimate of the energy your body uses each day while minimally active. Additional physical activity requires more energy over and above Resting Energy (see Active Energy)."),
    "health.distancewalkingrunning": DataSource("health.distancewalkingrunning", "m", "count", "This is an estimate of the distance you've walked or run. It's calculated using the steps you've taken and the distance of your stride."),
    "health.flightsclimbed": DataSource("health.flightsclimbed", "flights", "count", "A flight of stairs is counted as approximately 10 feet (3 meters) of elevation gain (approximately 16 steps). "),
    "health.heartrate": DataSource("health.heartrate", "beats/min", "rate", "Your heart beats approximately 100,000 times per day, accelerating and slowing through periods of rest and exertion. Your heart rate refers to how many times your heart beats per minute and can be an indicator of your cardiovascular health. Health visualizes a history of the heart rate data collected by Apple Watch or a heart rate monitor so you can see your patterns and variability over time and with different activities."),
    "health.heartratevariabilitysdnn": DataSource("health.heartratevariabilitysdnn", "ms", "rate", "Heart Rate Variability (HRV) is a measure of the variation in the time interval between heart beats. Apple Watch calculates HRV by using the standard deviation of beat-to-beat measurements which are captured by the heart rate sensor. HRV is validated for users over the age of 18. Thirty party apps and devices can also add HRV to Health. "),
    "health.oxygensaturation": DataSource("health.oxygensaturation", "%", "rate", "Blood oxygen is a measure of the amount of oxygen in the protein (hemoglobin) in your red blood cells. To function properly, your body needs a certain level of oxygen circulating in the blood. Your red blood cells are loaded (saturated) with oxygen in the lungs and carry it throughout your body."),
    "health.respiratoryrate": DataSource("health.respiratoryrate", "breaths/min", "rate", "Also commonly called respiration rate or breathing rate, this refers to the number of times you breathe in a minute. When you inhale, your lungs fill with air and oxygen is added to your blood stream while carbon dioxide is removed from your blood. The carbon dioxide is then released from your lungs as you exhale. Your respiratory rate can increase when your body needs more oxygen, such as when you're exercising. It can also decrease when you need less-during sleep for example."),
    "health.restingheartrate": DataSource("health.restingheartrate", "beats/min", "rate", "Your resting heart rate is the average heart beats per minute measured when you've been inactive or relaxed for several minutes. A lower resting heart rate typically indicates better heart health and cardiovascular fintess. You may be able to lower your resting heart rate over time by staying active, managing your weight, and reducing everyday stress. Resting heart rate does not include your heart rate while you're asleep and is validated for users over the age of 19"),
    # "health.sleepanalysis": DataSource("health.sleepanalysis", "min", "sleep", "Sleep provides insight into your sleep habits. Sleep trackers and monitors can help you determine the amount of time you are in bed and asleep. These devices estimate your time in bed and your time asleep by analyzing changes in physical activity, including movement during the night. You can also keep track of your sleep by entering your own estimation of your bed time and sleep time manually. The \"In Bed\" period reflects the time period you are lying in bed with the intention to sleep. For most people it starts when you turn the lights off and it ends when you get out of bed. The \"Asleep\" period reflects the period (s) you are asleep."),
    "health.stepcount": DataSource("health.stepcount", "steps", "count", "Step count is the number of steps you take throughout the day. Pedometers and digital activity trackers can help you determine your step count. These devices count steps for any activity that involves step-like movement, including walking, running, stair-climbing, cross-country skiing, and even movement as you go about your daily chores."),
    "health.walkingheartrateaverage": DataSource("health.walkingheartrateaverage", "beats/min", "rate", "Your walking heart rate is the average heart beats per minute measured by your Apple Watch during walks at a steady pace throughout the day. Like resting heart rate, a lower walking heart rate may indicate better heart health and cardiovascular fitness. Walking regularly has many health benefits, and you may see your walking heart rate lower over time by staying active, managing your weight, and reducing everyday stress."),
    "health.workout": DataSource("health.workout", "min", "workout", "Workouts can be logged manually or automatically by your phone or watch. Each workout is logged with a start and end time, type of workout, and duration. Workouts can be used to track physical activity and exercise habits."),
}

@lru_cache(maxsize=128)
def get_user_data_sources(user_id: str) -> list[str]:
    user_doc = firebase_manager.get_user_doc(user_id)
    sources = ["health." + doc.id for doc in user_doc.collection("health").list_documents()]
    
    # TODO: add support for sleep 
    if "sleepanalysis" in sources:
        sources.remove("health.sleepanalysis")
    return sources