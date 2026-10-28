import re
from typing import List
from app.privacy.recognizers.base import BaseRecognizer, RecognizedEntity

VALID_PROVINCE_CODES = {
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "21", # Sumatra
    "31", "32", "33", "34", "35", "36",                         # Java
    "51", "52", "53",                                           # Bali & Nusa Tenggara
    "61", "62", "63", "64", "65",                               # Kalimantan
    "71", "72", "73", "74", "75", "76",                         # Sulawesi
    "81", "82",                                                 # Maluku
    "91", "92", "94", "95", "96", "97"                          # Papua
}

def is_valid_nik(candidate: str) -> bool:
    """
    Validates Indonesian NIK (Nomor Induk Kependudukan):
    - Exactly 16 digits
    - Valid province code (11-97)
    - Valid birth date representation (Day: 1-31 or 41-71 for female, Month: 1-12)
    """
    if len(candidate) != 16 or not candidate.isdigit():
        return False
    
    prov = candidate[:2]
    if prov not in VALID_PROVINCE_CODES:
        return False
        
    day = int(candidate[6:8])
    month = int(candidate[8:10])
    
    # Female day is day + 40
    if not ((1 <= day <= 31) or (41 <= day <= 71)):
        return False
        
    if not (1 <= month <= 12):
        return False
        
    return True

class NIKRecognizer(BaseRecognizer):
    name = "indonesian_nik_recognizer"
    entity_types = ["NIK"]
    
    # Matches 16 digits standalone or preceded by NIK/KTP keyword
    NIK_REGEX = re.compile(
        r'(?:\b(?:NIK|KTP|NO\.?\s*KTP)[\s:]*)?(\b\d{16}\b)',
        re.IGNORECASE
    )

    def analyze(self, text: str) -> List[RecognizedEntity]:
        matches = []
        for match in self.NIK_REGEX.finditer(text):
            digits = match.group(1)
            has_keyword = bool(re.search(r'(?i)(?:NIK|KTP)', match.group(0)))
            if is_valid_nik(digits):
                confidence = 0.98 if has_keyword else 0.88
                matches.append(RecognizedEntity(
                    entity_type="NIK",
                    text=digits,
                    start=match.start(1),
                    end=match.end(1),
                    confidence=confidence,
                    recognizer_id=self.name
                ))
        return matches

class NPWPRecognizer(BaseRecognizer):
    name = "indonesian_npwp_recognizer"
    entity_types = ["NPWP"]
    
    # Format: XX.XXX.XXX.X-XXX.XXX or raw 15-16 digits with NPWP context
    NPWP_FORMATTED_REGEX = re.compile(
        r'\b\d{2}\.\d{3}\.\d{3}\.\d{1}-\d{3}\.\d{3}\b'
    )
    NPWP_CONTEXT_REGEX = re.compile(
        r'(?i)(?:NPWP|NO\.?\s*NPWP)[\s:]*(\b\d{15,16}\b)'
    )

    def analyze(self, text: str) -> List[RecognizedEntity]:
        matches = []
        # Formatted NPWP
        for match in self.NPWP_FORMATTED_REGEX.finditer(text):
            matches.append(RecognizedEntity(
                entity_type="NPWP",
                text=match.group(0),
                start=match.start(),
                end=match.end(),
                confidence=0.98,
                recognizer_id=self.name
            ))
        # Contextual NPWP
        for match in self.NPWP_CONTEXT_REGEX.finditer(text):
            val = match.group(1)
            matches.append(RecognizedEntity(
                entity_type="NPWP",
                text=val,
                start=match.start(1),
                end=match.end(1),
                confidence=0.92,
                recognizer_id=self.name
            ))
        return matches

class IndonesianPhoneRecognizer(BaseRecognizer):
    name = "indonesian_phone_recognizer"
    entity_types = ["INDONESIAN_PHONE"]
    
    # +62 8xx, 62 8xx or 08xx followed by 7-11 digits, optional spaces/dashes
    PHONE_REGEX = re.compile(
        r'(?:\+62\s*|62\s*|0)8[1-9][0-9\s-]{6,12}\b'
    )

    def analyze(self, text: str) -> List[RecognizedEntity]:
        matches = []
        for match in self.PHONE_REGEX.finditer(text):
            raw = match.group(0)
            # Strip trailing space/dash
            clean_text = raw.rstrip(" -")
            cleaned = re.sub(r'[\s-]', '', clean_text)
            # Standard Indonesian mobile length is 10 to 14 digits
            if 10 <= len(cleaned) <= 14:
                matches.append(RecognizedEntity(
                    entity_type="INDONESIAN_PHONE",
                    text=clean_text,
                    start=match.start(),
                    end=match.start() + len(clean_text),
                    confidence=0.95,
                    recognizer_id=self.name
                ))
        return matches

class IndonesianBankAccountRecognizer(BaseRecognizer):
    name = "indonesian_bank_account_recognizer"
    entity_types = ["INDONESIAN_BANK_ACCOUNT"]
    
    # Matches bank account numbers preceded by bank names or 'rekening'/'rek'
    BANK_REGEX = re.compile(
        r'(?i)(?:rekening|rek|no\.?\s*rek|bca|mandiri|bri|bni|cimb|bsi|permata|btn)[\s:/-]+([0-9]{9,16})\b'
    )

    def analyze(self, text: str) -> List[RecognizedEntity]:
        matches = []
        for match in self.BANK_REGEX.finditer(text):
            acc_num = match.group(1)
            # Skip if 16 digits and looks like NIK
            if len(acc_num) == 16 and is_valid_nik(acc_num):
                continue
            matches.append(RecognizedEntity(
                entity_type="INDONESIAN_BANK_ACCOUNT",
                text=acc_num,
                start=match.start(1),
                end=match.end(1),
                confidence=0.90,
                recognizer_id=self.name
            ))
        return matches

class IndonesianPostalCodeRecognizer(BaseRecognizer):
    name = "indonesian_postal_code_recognizer"
    entity_types = ["POSTAL_CODE"]
    
    # Contextual postal code
    POSTAL_REGEX = re.compile(
        r'(?i)(?:kodepos|kode\s*pos|postal\s*code|zip\s*code)[\s:]+(\b[1-9]\d{4}\b)'
    )

    def analyze(self, text: str) -> List[RecognizedEntity]:
        matches = []
        for match in self.POSTAL_REGEX.finditer(text):
            code = match.group(1)
            matches.append(RecognizedEntity(
                entity_type="POSTAL_CODE",
                text=code,
                start=match.start(1),
                end=match.end(1),
                confidence=0.92,
                recognizer_id=self.name
            ))
        return matches
