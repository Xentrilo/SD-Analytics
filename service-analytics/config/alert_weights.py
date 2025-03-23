"""
Configuration for alert type weights in driving behavior scoring.
"""

# Weights for different alert types (-10 to 10 scale, negative values are penalties)
ALERT_WEIGHTS = {
    "Harsh Braking": -5,
    "Harsh Cornering": -3,
    "Harsh Acceleration": -4,
    "Speeding Over": -7,
    "Engine Idle": -2,
    "After Hours": -6
}

# Thresholds for overall driving score
DRIVING_SCORE_THRESHOLDS = {
    "EXCELLENT": 90,
    "GOOD": 75,
    "AVERAGE": 60,
    "BELOW_AVERAGE": 40,
    "POOR": 0
}

# Time decay factor for alerts (older alerts have less impact)
ALERT_DECAY_DAYS = 30  # How many days until an alert has half the impact 