import re
import ipaddress
from typing import List
from app.privacy.recognizers.base import BaseRecognizer, RecognizedEntity

def luhn_checksum_valid(card_number_str: str) -> bool:
    digits = [int(c) for c in card_number_str if c.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    # Luhn algorithm
    checksum = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = digit * 2
            checksum += (doubled - 9) if doubled > 9 else doubled
        else:
            checksum += digit
    return checksum % 10 == 0

def iban_checksum_valid(iban_str: str) -> bool:
    clean = re.sub(r'[\s-]', '', iban_str).upper()
    if len(clean) < 14 or len(clean) > 34:
        return False
    # Move first 4 chars to end
    rearranged = clean[4:] + clean[:4]
    # Convert letters to digits A=10, B=11...
    numeric = ""
    for ch in rearranged:
        if ch.isalpha():
            numeric += str(ord(ch) - 55)
        elif ch.isdigit():
            numeric += ch
        else:
            return False
    # Modulo 97 check
    try:
        return int(numeric) % 97 == 1
    except ValueError:
        return False

class EmailRecognizer(BaseRecognizer):
    name = "email_recognizer"
    entity_types = ["EMAIL_ADDRESS"]
    EMAIL_REGEX = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
        re.IGNORECASE
    )

    def analyze(self, text: str) -> List[RecognizedEntity]:
        matches = []
        for match in self.EMAIL_REGEX.finditer(text):
            matches.append(RecognizedEntity(
                entity_type="EMAIL_ADDRESS",
                text=match.group(0),
                start=match.start(),
                end=match.end(),
                confidence=0.98,
                recognizer_id=self.name
            ))
        return matches

class PhoneRecognizer(BaseRecognizer):
    name = "international_phone_recognizer"
    entity_types = ["PHONE_NUMBER"]
    PHONE_REGEX = re.compile(
        r'(?:\+?[1-9]\d{0,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b'
    )

    def analyze(self, text: str) -> List[RecognizedEntity]:
        matches = []
        for match in self.PHONE_REGEX.finditer(text):
            val = match.group(0)
            digits = re.sub(r'\D', '', val)
            if 7 <= len(digits) <= 15:
                # Discard common non-phones (e.g. 2024-10-28)
                if "-" in val and len(val.split("-")[0]) == 4 and int(val.split("-")[0]) > 1900:
                    continue
                matches.append(RecognizedEntity(
                    entity_type="PHONE_NUMBER",
                    text=val,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.85,
                    recognizer_id=self.name
                ))
        return matches

class IPAddressRecognizer(BaseRecognizer):
    name = "ip_address_recognizer"
    entity_types = ["IP_ADDRESS"]
    IP_CANDIDATE_REGEX = re.compile(
        r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b|\b(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}\b'
    )

    def analyze(self, text: str) -> List[RecognizedEntity]:
        matches = []
        for match in self.IP_CANDIDATE_REGEX.finditer(text):
            cand = match.group(0)
            try:
                ipaddress.ip_address(cand)
                matches.append(RecognizedEntity(
                    entity_type="IP_ADDRESS",
                    text=cand,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95,
                    recognizer_id=self.name
                ))
            except ValueError:
                continue
        return matches

class CreditCardRecognizer(BaseRecognizer):
    name = "credit_card_recognizer"
    entity_types = ["CREDIT_CARD"]
    CC_REGEX = re.compile(
        r'\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{13,19}\b'
    )

    def analyze(self, text: str) -> List[RecognizedEntity]:
        matches = []
        for match in self.CC_REGEX.finditer(text):
            cand = match.group(0)
            if luhn_checksum_valid(cand):
                matches.append(RecognizedEntity(
                    entity_type="CREDIT_CARD",
                    text=cand,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.99,
                    recognizer_id=self.name
                ))
        return matches

class DateOfBirthRecognizer(BaseRecognizer):
    name = "dob_recognizer"
    entity_types = ["DATE_OF_BIRTH"]
    DOB_REGEX = re.compile(
        r'(?i)(?:dob|born|birth(?:day|date)?|tgl lahir|tanggal lahir)[\s:]+([0-3]?\d[-/.][01]?\d[-/.](?:19|20)\d{2})\b'
    )

    def analyze(self, text: str) -> List[RecognizedEntity]:
        matches = []
        for match in self.DOB_REGEX.finditer(text):
            date_part = match.group(1)
            start_idx = match.start(1)
            end_idx = match.end(1)
            matches.append(RecognizedEntity(
                entity_type="DATE_OF_BIRTH",
                text=date_part,
                start=start_idx,
                end=end_idx,
                confidence=0.90,
                recognizer_id=self.name
            ))
        return matches

class PassportRecognizer(BaseRecognizer):
    name = "passport_recognizer"
    entity_types = ["PASSPORT"]
    PASSPORT_REGEX = re.compile(
        r'(?i)(?:passport|paspor)[\s#:]{1,4}([A-Z]{1,2}[0-9]{7,8})\b'
    )

    def analyze(self, text: str) -> List[RecognizedEntity]:
        matches = []
        for match in self.PASSPORT_REGEX.finditer(text):
            pnum = match.group(1)
            matches.append(RecognizedEntity(
                entity_type="PASSPORT",
                text=pnum,
                start=match.start(1),
                end=match.end(1),
                confidence=0.92,
                recognizer_id=self.name
            ))
        return matches

class IBANRecognizer(BaseRecognizer):
    name = "iban_recognizer"
    entity_types = ["IBAN"]
    IBAN_REGEX = re.compile(
        r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}[A-Z0-9]{7,26}\b'
    )

    def analyze(self, text: str) -> List[RecognizedEntity]:
        matches = []
        for match in self.IBAN_REGEX.finditer(text):
            cand = match.group(0)
            if iban_checksum_valid(cand):
                matches.append(RecognizedEntity(
                    entity_type="IBAN",
                    text=cand,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.99,
                    recognizer_id=self.name
                ))
        return matches

class SensitiveURLRecognizer(BaseRecognizer):
    name = "sensitive_url_recognizer"
    entity_types = ["SENSITIVE_URL"]
    URL_SENSITIVE_REGEX = re.compile(
        r'https?://[^\s/?#]+[^\s]*[?&](?:token|key|api_?key|secret|password|access_?token)=[^\s&]+',
        re.IGNORECASE
    )

    def analyze(self, text: str) -> List[RecognizedEntity]:
        matches = []
        for match in self.URL_SENSITIVE_REGEX.finditer(text):
            matches.append(RecognizedEntity(
                entity_type="SENSITIVE_URL",
                text=match.group(0),
                start=match.start(),
                end=match.end(),
                confidence=0.95,
                recognizer_id=self.name
            ))
        return matches
