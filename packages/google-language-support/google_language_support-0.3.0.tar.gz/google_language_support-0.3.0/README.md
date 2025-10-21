# google-language-support

A Python package providing comprehensive language code support for Google services.

## Installation

```bash
pip install google-language-support
```

## Usage

```python
from google_language_support import LanguageCodes

# Access language codes
print(LanguageCodes.ENGLISH)  # "en"
print(LanguageCodes.SPANISH)  # "es"
print(LanguageCodes.CHINESE_SIMPLIFIED)  # "zh-CN"

# Convert to human-readable names
print(LanguageCodes.ENGLISH.to_instruction())  # "English"
print(LanguageCodes.CHINESE_SIMPLIFIED.to_instruction())  # "Chinese, Simplified, China"
print(LanguageCodes.FRENCH_CA.to_instruction())  # "French, Canada"

# Convert from common language names (NEW!)
print(LanguageCodes.from_common_name("English"))  # LanguageCodes.ENGLISH
print(LanguageCodes.from_common_name("spanish"))  # LanguageCodes.SPANISH (case-insensitive)
print(LanguageCodes.from_common_name("zh-CN"))    # LanguageCodes.CHINESE_SIMPLIFIED
print(LanguageCodes.from_common_name("Mandarin")) # LanguageCodes.CHINESE_SIMPLIFIED_2
print(LanguageCodes.from_common_name("Deutsch"))  # LanguageCodes.GERMAN

# Supports various input formats:
print(LanguageCodes.from_common_name("Brazilian Portuguese"))  # LanguageCodes.PORTUGUESE_BR
print(LanguageCodes.from_common_name("Simplified Chinese"))    # LanguageCodes.CHINESE_SIMPLIFIED
print(LanguageCodes.from_common_name("Bahasa Indonesia"))      # LanguageCodes.INDONESIAN

# Fuzzy matching for typos
print(LanguageCodes.from_common_name("Englsh"))    # LanguageCodes.ENGLISH (missing 'i')
print(LanguageCodes.from_common_name("Frech"))     # LanguageCodes.FRENCH (missing 'n')

# Safe version that returns None instead of raising exception
result = LanguageCodes.from_might_common_name("Unknown Language")
print(result)  # None
```

## Features

- **230+ language codes** - Comprehensive coverage of languages supported by Google services
- **Human-readable names** - Convert language codes to readable format with `to_instruction()`
- **Flexible input parsing** - Convert from various language name formats with `from_common_name()`
- **Regional variants** - Support for region-specific language codes (e.g., `zh-CN`, `fr-CA`, `pt-BR`)
- **Multiple aliases** - Some languages have multiple code representations for compatibility
- **Fuzzy matching** - Handles typos and variations in language names (80% similarity threshold)
- **Case-insensitive** - Works with any case combination of language names

### Supported Input Formats for `from_common_name()`

- **Enum names**: "ENGLISH", "SPANISH", "CHINESE_SIMPLIFIED"
- **Language codes**: "en", "es", "zh-CN", "pt-BR"
- **ISO 639-1/639-3 codes**: "en"/"eng", "es"/"spa", "fr"/"fra"
- **Common variations**: "Chinese", "Tagalog", "Ganda", "Sotho"
- **Native names**: "Mandarin", "Farsi", "Deutsch", "Español", "Français"
- **Casual variants**: "Brazilian Portuguese", "Canadian French", "American English"
- **Cultural references**: "Pinyin", "Kanji", "Hangul", "Cyrillic"
- **Instruction names**: "Chinese, Simplified, China", "Filipino (Tagalog)"

## Supported Languages

The package includes language codes for major world languages including:

- European languages (English, Spanish, French, German, etc.)
- Asian languages (Chinese, Japanese, Korean, Hindi, etc.)
- African languages (Swahili, Yoruba, Amharic, etc.)
- Indigenous and regional languages (Quechua, Cherokee, Hawaiian, etc.)

## License

MIT License
