"""
Categories and keywords for cancellation reasons.
"""

CANCEL_CATEGORIES = {
    "CUSTOMER_INITIATED": [
        "customer cancel", 
        "client cancel", 
        "cust canceled", 
        "cancelled by customer",
        "cstmr declined",
        "customer declined"
    ],
    "FIXED_ITSELF": [
        "appliance starting working", 
        "started working", 
        "fixed itself",
        "working after",
        "unplugging"
    ],
    "SCHEDULING_CONFLICT": [
        "reschedule", 
        "schedule conflict", 
        "not available",
        "changed appmnt",
        "chngd appmnt"
    ],
    "PAYMENT_ISSUE": [
        "payment", 
        "credit card", 
        "cc for service",
        "service"
    ],
    "NO_SHOW": [
        "no show",
        "not home",
        "customer not present",
        "nobody home",
        "not at home"
    ],
    "PRICE_TOO_HIGH": [
        "too expensive", 
        "cost too high", 
        "price too high",
        "cheaper elsewhere",
        "not worth"
    ],
    "CHANGED_MIND": [
        "changed mind", 
        "decided against",
        "decided not to",
        "will try later",
        "will fix later"
    ],
    "OTHER": []
}

# Priority order for cancellation categories (in case of multiple matches)
CATEGORY_PRIORITY = [
    "CUSTOMER_INITIATED",
    "PRICE_TOO_HIGH", 
    "NO_SHOW",
    "SCHEDULING_CONFLICT",
    "CHANGED_MIND",
    "FIXED_ITSELF",
    "PAYMENT_ISSUE",
    "OTHER"
] 