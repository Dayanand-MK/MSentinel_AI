RISK_WEIGHTS = {
    "Email": 2,
    "Phone": 2,
    "PAN": 5,
    "Aadhaar": 6,
    "Passport": 6,
    "Driving License": 6,
    "IFSC": 5,
    "Bank Account": 7,
    "Credit Card": 8,
    "Debit Card": 8,
    "CVV": 9,
    "Password": 10,
    "API Keys": 10,
    "JWT": 10,
    "AWS Keys": 10,
    "Employee IDs": 4,
    "IPv4": 4,
    "URL": 2,
    
    # spaCy Categories
    "Person": 3,
    "Organization": 4,
    "Location": 2,
    "Date": 1,
    "Money": 5,

    # LLM Validation Categories
    "Business Confidential": 7,
    "Internal Documents": 4,
    "Trade Secrets": 9,
    "Contracts": 6,
    "Legal Documents": 7,
    "Sensitive Business Risks": 8
}