PATTERNS = {

    "Email":
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",

    "Phone":
        r"\b(?:\+91[- ]?)?[6-9]\d{9}\b",

    "PAN":
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",

    "Aadhaar":
        r"\b\d{4}\s\d{4}\s\d{4}\b",

    "Passport":
        r"\b[A-PR-WYa-pr-wy][1-9]\d{6}\b",

    "IFSC":
        r"\b[A-Z]{4}0[A-Z0-9]{6}\b",

    "Bank Account":
        r"(?i)(?:account\s*(?:number|no)?|a/c\s*no\.?)\s*[:\-]?\s*(\d{9,18})",

    "Credit Card":
        r"\b(?:\d[ -]*?){13,16}\b",

    "IPv4":
        r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",

    "URL":
        r"https?://[^\s]+",

    "JWT":
        r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",

}