import pytest
from app.privacy.recognizers.international import (
    EmailRecognizer, PhoneRecognizer, IPAddressRecognizer,
    CreditCardRecognizer, DateOfBirthRecognizer, IBANRecognizer,
    luhn_checksum_valid
)
from app.privacy.recognizers.indonesian import (
    NIKRecognizer, NPWPRecognizer, IndonesianPhoneRecognizer,
    IndonesianBankAccountRecognizer, is_valid_nik
)
from app.privacy.recognizers.secrets import SecretRecognizer

def test_email_recognizer():
    rec = EmailRecognizer()
    text = "Send reports to alice.smith@corp.example.com and dev@company.co.id please."
    results = rec.analyze(text)
    assert len(results) == 2
    assert results[0].text == "alice.smith@corp.example.com"
    assert results[1].text == "dev@company.co.id"

def test_credit_card_luhn_algorithm():
    rec = CreditCardRecognizer()
    # Valid Visa test number
    valid_cc = "4111-1111-1111-1111" # Luhn valid
    assert luhn_checksum_valid(valid_cc)
    
    # Invalid card number
    invalid_cc = "4111-1111-1111-1112"
    assert not luhn_checksum_valid(invalid_cc)

    text = f"My card is {valid_cc} and fake is {invalid_cc}."
    results = rec.analyze(text)
    assert len(results) == 1
    assert results[0].text == valid_cc

def test_ip_address_recognizer():
    rec = IPAddressRecognizer()
    text = "Server IP 192.168.1.10 and public 8.8.8.8, invalid 999.999.999.999."
    results = rec.analyze(text)
    assert len(results) == 2
    assert results[0].text == "192.168.1.10"
    assert results[1].text == "8.8.8.8"

def test_indonesian_nik_validation():
    # 320101 (Bogor, Java Barat), 150890 (15 Aug 1990), 0001
    valid_male_nik = "3201011508900001"
    assert is_valid_nik(valid_male_nik)

    # Female: day + 40 -> 15 + 40 = 55
    valid_female_nik = "3171015508950002"
    assert is_valid_nik(valid_female_nik)

    # Invalid province 00
    invalid_nik_prov = "0001011508900001"
    assert not is_valid_nik(invalid_nik_prov)

    # Invalid month 13
    invalid_nik_month = "3201011513900001"
    assert not is_valid_nik(invalid_nik_month)

    rec = NIKRecognizer()
    text = f"Nomor KTP user: {valid_male_nik} dan user 2: {invalid_nik_prov}"
    results = rec.analyze(text)
    assert len(results) == 1
    assert results[0].text == valid_male_nik

def test_indonesian_npwp_recognizer():
    rec = NPWPRecognizer()
    text = "NPWP Perusahaan adalah 01.234.567.8-123.000 untuk faktur."
    results = rec.analyze(text)
    assert len(results) == 1
    assert results[0].text == "01.234.567.8-123.000"

def test_indonesian_phone_recognizer():
    rec = IndonesianPhoneRecognizer()
    text = "Hubungi customer care di +62 812-3456-7890 atau 081987654321 sekarang."
    results = rec.analyze(text)
    assert len(results) == 2
    assert "+62 812-3456-7890" in [r.text for r in results]
    assert "081987654321" in [r.text for r in results]

def test_indonesian_bank_account():
    rec = IndonesianBankAccountRecognizer()
    text = "Transfer ke rekening BCA 1234567890 atas nama Budi."
    results = rec.analyze(text)
    assert len(results) == 1
    assert results[0].text == "1234567890"

def test_secret_recognizer():
    rec = SecretRecognizer()
    text = "Don't leak sk-proj-1234567890abcdefghijklmnopqrstuvwxyz or AKIAIOSFODNN7EXAMPLE"
    results = rec.analyze(text)
    assert len(results) == 2
    types = [r.entity_type for r in results]
    assert "API_KEY" in types
