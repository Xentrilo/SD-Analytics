"""
Application settings and configuration parameters.
"""

# File paths
DATA_DIR = "data"
PROCESSED_DIR = "processed"

# Business rules
FIRST_CALL_COMPLETE_GOAL = 0.7  # 70% target
DIAGNOSTIC_ONLY_MIN_GOAL = 0.1  # 10% target
DIAGNOSTIC_ONLY_IDEAL_GOAL = 0.2  # 20% ideal target
RECALL_GOAL = 0.05  # 5% target

# Service pricing
ZONE_1_PRICE = 129
ZONE_2_PRICE = 149
ADDITIONAL_APPLIANCE_PRICE = 60

# Service call pricing by type
SERVICE_CALL_PRICES = {
    "STANDARD": 89,
    "DIAGNOSTIC": 69,
    "WARRANTY": 0,
    "RECALL": 0,
    "FOLLOW_UP": 0
}

# GPS data settings
GPS_MATCH_THRESHOLD = 0.8  # Confidence threshold for address matching
STOP_DURATION_THRESHOLD = 300  # Minimum seconds to consider a valid job stop

# Time windows
DEFAULT_TIME_WINDOW = 30  # Minutes before/after scheduled time to look for GPS stops 