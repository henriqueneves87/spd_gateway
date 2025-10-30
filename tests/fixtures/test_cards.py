"""
Test card data for Adiq certification.
Source: docs/CERTIFICATION.md
"""

# Test cards for different scenarios
TEST_CARDS = {
    "visa_approved": {
        "pan": "4761739001010036",
        "brand": "visa",
        "expiration_month": "12",
        "expiration_year": "25",
        "cvv": "123",
        "cardholder_name": "APPROVED TEST"
    },
    "mastercard_approved": {
        "pan": "5453010000066167",
        "brand": "mastercard",
        "expiration_month": "12",
        "expiration_year": "25",
        "cvv": "123",
        "cardholder_name": "APPROVED TEST"
    },
    "elo_approved": {
        "pan": "6362970000457013",
        "brand": "elo",
        "expiration_month": "12",
        "expiration_year": "25",
        "cvv": "123",
        "cardholder_name": "APPROVED TEST"
    },
}

# Antifraud test emails
ANTIFRAUDE_EMAILS = {
    "accept": "accept@test.com",
    "reject": "reject@test.com",
    "review": "review@test.com"
}

# Test amounts (in cents)
TEST_AMOUNTS = {
    "approved": 10000,  # R$ 100.00
    "declined": 5000,   # R$ 50.00
    "minimum": 100,     # R$ 1.00
    "maximum": 1000000  # R$ 10,000.00
}
