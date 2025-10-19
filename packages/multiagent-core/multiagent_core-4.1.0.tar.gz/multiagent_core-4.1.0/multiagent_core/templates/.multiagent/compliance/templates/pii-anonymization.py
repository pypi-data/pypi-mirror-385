"""
PII Anonymization Utilities
Purpose: Detect and anonymize personally identifiable information
Techniques: Hashing, masking, tokenization, pseudonymization
"""

import re
import hashlib
import secrets
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass


@dataclass
class PIIPattern:
    """PII pattern definition."""
    name: str
    regex: str
    anonymizer: Callable


class PIIAnonymizer:
    """
    Detect and anonymize PII in text, logs, and databases.

    Supports:
    - Email addresses
    - Phone numbers
    - Credit card numbers
    - Social Security Numbers (SSN)
    - IP addresses
    - Names
    - Addresses
    """

    # PII Detection Patterns
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
        "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        "zip_code": r'\b\d{5}(?:-\d{4})?\b',
    }

    def __init__(self, salt: Optional[str] = None):
        """Initialize anonymizer with optional salt for hashing."""
        self.salt = salt or secrets.token_hex(16)

    def hash_pii(self, value: str) -> str:
        """
        Hash PII using SHA-256 with salt.
        Use for irreversible anonymization.
        """
        salted = f"{value}{self.salt}"
        return hashlib.sha256(salted.encode()).hexdigest()

    def mask_email(self, email: str) -> str:
        """
        Mask email address.
        Example: john.doe@example.com -> j***@example.com
        """
        if not email or "@" not in email:
            return email

        local, domain = email.split("@", 1)
        if len(local) <= 2:
            masked_local = local[0] + "***"
        else:
            masked_local = local[0] + "***" + local[-1]

        return f"{masked_local}@{domain}"

    def mask_phone(self, phone: str) -> str:
        """
        Mask phone number.
        Example: +1-555-123-4567 -> ***-***-4567
        """
        # Extract last 4 digits
        digits = re.sub(r'\D', '', phone)
        if len(digits) >= 4:
            return f"***-***-{digits[-4:]}"
        return "***-***-****"

    def mask_ssn(self, ssn: str) -> str:
        """
        Mask SSN.
        Example: 123-45-6789 -> ***-**-6789
        """
        parts = ssn.split("-")
        if len(parts) == 3:
            return f"***-**-{parts[2]}"
        return "***-**-****"

    def mask_credit_card(self, cc: str) -> str:
        """
        Mask credit card number.
        Example: 1234-5678-9012-3456 -> ****-****-****-3456
        """
        digits = re.sub(r'\D', '', cc)
        if len(digits) >= 4:
            return f"****-****-****-{digits[-4:]}"
        return "****-****-****-****"

    def mask_ip(self, ip: str) -> str:
        """
        Mask IP address.
        Example: 192.168.1.100 -> 192.168.*.*
        """
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.*"
        return "***.*.*.*"

    def pseudonymize_name(self, name: str) -> str:
        """
        Pseudonymize name using consistent hashing.
        Same input always produces same output.
        """
        hashed = self.hash_pii(name)
        return f"USER_{hashed[:8].upper()}"

    def tokenize(self, value: str, pii_type: str) -> str:
        """
        Generate reversible token for PII.
        Store mapping in secure token vault.
        """
        token = secrets.token_urlsafe(16)
        # TODO: Store (token -> value) mapping in secure vault
        return f"TOKEN_{pii_type.upper()}_{token}"

    def anonymize_text(
        self,
        text: str,
        pii_types: Optional[List[str]] = None,
        method: str = "mask"
    ) -> str:
        """
        Anonymize all PII in text.

        Args:
            text: Input text containing PII
            pii_types: List of PII types to anonymize (default: all)
            method: Anonymization method ('mask', 'hash', 'tokenize')

        Returns:
            Text with PII anonymized
        """
        if pii_types is None:
            pii_types = list(self.PATTERNS.keys())

        anonymized = text

        # Email
        if "email" in pii_types:
            anonymized = re.sub(
                self.PATTERNS["email"],
                lambda m: self._anonymize_match(m.group(), "email", method),
                anonymized
            )

        # Phone
        if "phone" in pii_types:
            anonymized = re.sub(
                self.PATTERNS["phone"],
                lambda m: self._anonymize_match(m.group(), "phone", method),
                anonymized
            )

        # SSN
        if "ssn" in pii_types:
            anonymized = re.sub(
                self.PATTERNS["ssn"],
                lambda m: self._anonymize_match(m.group(), "ssn", method),
                anonymized
            )

        # Credit Card
        if "credit_card" in pii_types:
            anonymized = re.sub(
                self.PATTERNS["credit_card"],
                lambda m: self._anonymize_match(m.group(), "credit_card", method),
                anonymized
            )

        # IP Address
        if "ip_address" in pii_types:
            anonymized = re.sub(
                self.PATTERNS["ip_address"],
                lambda m: self._anonymize_match(m.group(), "ip_address", method),
                anonymized
            )

        return anonymized

    def _anonymize_match(self, value: str, pii_type: str, method: str) -> str:
        """Anonymize matched PII value using specified method."""
        if method == "mask":
            maskers = {
                "email": self.mask_email,
                "phone": self.mask_phone,
                "ssn": self.mask_ssn,
                "credit_card": self.mask_credit_card,
                "ip_address": self.mask_ip,
            }
            return maskers.get(pii_type, lambda x: "***")(value)

        elif method == "hash":
            return self.hash_pii(value)

        elif method == "tokenize":
            return self.tokenize(value, pii_type)

        else:
            return "[REDACTED]"

    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """
        Detect all PII in text without anonymizing.

        Returns:
            Dictionary of PII type -> list of detected values
        """
        detected = {}

        for pii_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                # Handle tuple matches (e.g., phone groups)
                if isinstance(matches[0], tuple):
                    matches = ["".join(m) for m in matches]
                detected[pii_type] = matches

        return detected

    def anonymize_database_column(
        self,
        cursor,
        table: str,
        column: str,
        pii_type: str,
        method: str = "mask"
    ):
        """
        Anonymize PII in database column.

        Example:
            anonymizer.anonymize_database_column(
                cursor,
                table="users",
                column="email",
                pii_type="email",
                method="mask"
            )
        """
        # Fetch all rows
        cursor.execute(f"SELECT id, {column} FROM {table}")
        rows = cursor.fetchall()

        # Anonymize and update
        for row_id, value in rows:
            if value:
                anonymized = self._anonymize_match(value, pii_type, method)
                cursor.execute(
                    f"UPDATE {table} SET {column} = %s WHERE id = %s",
                    (anonymized, row_id)
                )


# Example Usage
if __name__ == "__main__":
    anonymizer = PIIAnonymizer()

    # Example text with PII
    text = """
    Customer Support Log:
    User john.doe@example.com called from 555-123-4567.
    SSN on file: 123-45-6789
    Credit card ending in 1234-5678-9012-3456
    IP address: 192.168.1.100
    """

    print("Original text:")
    print(text)

    # Detect PII
    detected = anonymizer.detect_pii(text)
    print("\nDetected PII:")
    for pii_type, values in detected.items():
        print(f"  {pii_type}: {values}")

    # Anonymize with masking
    masked = anonymizer.anonymize_text(text, method="mask")
    print("\nMasked text:")
    print(masked)

    # Anonymize with hashing
    hashed = anonymizer.anonymize_text(text, method="hash")
    print("\nHashed text:")
    print(hashed)

    # Individual operations
    print("\nIndividual masking:")
    print(f"Email: {anonymizer.mask_email('john.doe@example.com')}")
    print(f"Phone: {anonymizer.mask_phone('555-123-4567')}")
    print(f"SSN: {anonymizer.mask_ssn('123-45-6789')}")
    print(f"Credit Card: {anonymizer.mask_credit_card('1234-5678-9012-3456')}")
    print(f"IP: {anonymizer.mask_ip('192.168.1.100')}")
