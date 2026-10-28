# Privacy Model & Data Handling Guarantees

## 1. Guiding Principles

1. **Privacy by Default:** Sensitive personal information and credentials must not leave the perimeter without explicit administrative policy authorization.
2. **Zero Raw Prompt Persistence:** Neither prompts nor completions are stored in the database by default.
3. **Collision Resistance:** Placeholders like `[EMAIL_1]` and `[NIK_1]` are distinct, consistent within a single request, and collision-checked against prompt tokens.
4. **Isolated Transient Vault:** Mapping between placeholders and original values exists exclusively in ephemeral memory for the duration of the request.

---

## 2. Supported Identifiers & Recognizers

### International Identifiers
- **Email Addresses:** Standard RFC 5322 regex validation.
- **Phone Numbers:** International E.164 and local formatted phone numbers.
- **Credit Cards:** 13 to 19 digits validated with the Luhn checksum algorithm.
- **IP Addresses:** IPv4 and IPv6 parsed through `ipaddress`.
- **Passports:** International passport alphanumeric sequences.
- **Date of Birth:** Contextual DOB markers.
- **Bank IBAN:** International Bank Account Numbers validated with MOD-97 algorithm.
- **Sensitive URLs:** Query strings containing tokens, keys, or passwords.

### Indonesian Identifiers
- **NIK (Nomor Induk Kependudukan):** 16-digit national identity numbers validated with province code (11-97) and date-of-birth parsing (including female DD+40 offset).
- **NPWP (Nomor Pokok Wajib Pajak):** Formatted and unformatted 15-16 digit Indonesian tax identification numbers.
- **Indonesian Phone Numbers:** Mobile numbers matching `+628...`, `628...`, or `08...`.
- **Indonesian Bank Accounts:** Account numbers contextualized by Indonesian bank names (BCA, Mandiri, BRI, BNI, CIMB, Permata, BSI).
- **Indonesian Postal Codes:** 5-digit postal codes contextualized by address or kodepos keywords.

### API Secrets & Tokens
- **OpenAI Keys:** `sk-...`
- **AWS Access Keys:** `AKIA...`
- **Bearer Tokens:** Authorization headers and generic bearer tokens.
- **Private Keys:** RSA/EC/OpenSSH private key headers.

---

## 3. Privacy Limitations
While the AI Privacy Gateway significantly mitigates data leakage risks:
- Natural language PII without deterministic structure (e.g. uncommon human names in obscure languages) may require custom NLP model plugins.
- Obfuscated PII (e.g., spelled-out numbers like "four one one one") is not detected by regex-based recognizers.
- The gateway acts as a technical DLP safeguard, but organizations must also establish internal data classification policies.
