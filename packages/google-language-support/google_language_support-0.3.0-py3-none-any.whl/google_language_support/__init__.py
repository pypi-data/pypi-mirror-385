import difflib
import re
import typing
from enum import StrEnum

__version__ = "0.3.0"


class LanguageCodes(StrEnum):
    ABKHAZ = "ab"
    ACEHNESE = "ace"
    ACHOLI = "ach"
    AFRIKAANS = "af"
    ALBANIAN = "sq"
    ALUR = "alz"
    AMHARIC = "am"
    ARABIC = "ar"
    ARMENIAN = "hy"
    ASSAMESE = "as"
    AWADHI = "awa"
    AYMARA = "ay"
    AZERBAIJANI = "az"
    BALINESE = "ban"
    BAMBARA = "bm"
    BASHKIR = "ba"
    BASQUE = "eu"
    BATAK_KARO = "btx"
    BATAK_SIMALUNGUN = "bts"
    BATAK_TOBA = "bbc"
    BELARUSIAN = "be"
    BEMBA = "bem"
    BENGALI = "bn"
    BETAWI = "bew"
    BHOJPURI = "bho"
    BIKOL = "bik"
    BOSNIAN = "bs"
    BRETON = "br"
    BULGARIAN = "bg"
    BURYAT = "bua"
    CANTONESE = "yue"
    CATALAN = "ca"
    CEBUANO = "ceb"
    CHICHEWA_NYANJA = "ny"
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_SIMPLIFIED_2 = "zh"
    CHINESE_TRADITIONAL = "zh-TW"
    CHUVASH = "cv"
    CORSICAN = "co"
    CRIMEAN_TATAR = "crh"
    CROATIAN = "hr"
    CZECH = "cs"
    DANISH = "da"
    DINKA = "din"
    DIVEHI = "dv"
    DOGRI = "doi"
    DOMBE = "dov"
    DUTCH = "nl"
    DZONGKHA = "dz"
    ENGLISH = "en"
    ESPERANTO = "eo"
    ESTONIAN = "et"
    EWE = "ee"
    FIJIAN = "fj"
    FILIPINO_TAGALOG = "fil"
    FILIPINO_TAGALOG_2 = "tl"
    FINNISH = "fi"
    FRENCH = "fr"
    FRENCH_FR = "fr-FR"
    FRENCH_CA = "fr-CA"
    FRISIAN = "fy"
    FULFULDE = "ff"
    GA = "gaa"
    GALICIAN = "gl"
    GANDA_LUGANDA = "lg"
    GEORGIAN = "ka"
    GERMAN = "de"
    GREEK = "el"
    GUARANI = "gn"
    GUJARATI = "gu"
    HAITIAN_CREOLE = "ht"
    HAKHA_CHIN = "cnh"
    HAUSA = "ha"
    HAWAIIAN = "haw"
    HEBREW = "iw"
    HEBREW_2 = "he"
    HILIGAYNON = "hil"
    HINDI = "hi"
    HMONG = "hmn"
    HUNGARIAN = "hu"
    HUNSRIK = "hrx"
    ICELANDIC = "is"
    IGBO = "ig"
    ILOKO = "ilo"
    INDONESIAN = "id"
    IRISH = "ga"
    ITALIAN = "it"
    JAPANESE = "ja"
    JAVANESE = "jw"
    JAVANESE_2 = "jv"
    KANNADA = "kn"
    KAPAMPANGAN = "pam"
    KAZAKH = "kk"
    KHMER = "km"
    KIGA = "cgg"
    KINYARWANDA = "rw"
    KITUBA = "ktu"
    KONKANI = "gom"
    KOREAN = "ko"
    KRIO = "kri"
    KURDISH_KURMANJI = "ku"
    KURDISH_SORANI = "ckb"
    KYRGYZ = "ky"
    LAO = "lo"
    LATGALIAN = "ltg"
    LATIN = "la"
    LATVIAN = "lv"
    LIGURIAN = "lij"
    LIMBURGAN = "li"
    LINGALA = "ln"
    LITHUANIAN = "lt"
    LOMBARD = "lmo"
    LUO = "luo"
    LUXEMBOURGISH = "lb"
    MACEDONIAN = "mk"
    MAITHILI = "mai"
    MAKASSAR = "mak"
    MALAGASY = "mg"
    MALAY = "ms"
    MALAY_JAWI = "ms-Arab"
    MALAYALAM = "ml"
    MALTESE = "mt"
    MAORI = "mi"
    MARATHI = "mr"
    MEADOW_MARI = "chm"
    MEITEILON_MANIPURI = "mni-Mtei"
    MINANG = "min"
    MIZO = "lus"
    MONGOLIAN = "mn"
    MYANMAR_BURMESE = "my"
    NDEBELE_SOUTH = "nr"
    NEPALBHASA_NEWARI = "new"
    NEPALI = "ne"
    NORTHERN_SOTHO_SEPEDI = "nso"
    NORWEGIAN = "no"
    NUER = "nus"
    OCCITAN = "oc"
    ODIA_ORIYA = "or"
    OROMO = "om"
    PANGASINAN = "pag"
    PAPIAMENTO = "pap"
    PASHTO = "ps"
    PERSIAN = "fa"
    POLISH = "pl"
    PORTUGUESE = "pt"
    PORTUGUESE_PT = "pt-PT"
    PORTUGUESE_BR = "pt-BR"
    PUNJABI = "pa"
    PUNJABI_SHAHMUKHI = "pa-Arab"
    QUECHUA = "qu"
    ROMANI = "rom"
    ROMANIAN = "ro"
    RUNDI = "rn"
    RUSSIAN = "ru"
    SAMOAN = "sm"
    SANGO = "sg"
    SANSKRIT = "sa"
    SCOTS_GAELIC = "gd"
    SERBIAN = "sr"
    SESOTHO = "st"
    SEYCHELLOIS_CREOLE = "crs"
    SHAN = "shn"
    SHONA = "sn"
    SICILIAN = "scn"
    SILESIAN = "szl"
    SINDHI = "sd"
    SINHALA = "si"
    SLOVAK = "sk"
    SLOVENIAN = "sl"
    SOMALI = "so"
    SPANISH = "es"
    SUNDANESE = "su"
    SWAHILI = "sw"
    SWATI = "ss"
    SWEDISH = "sv"
    TAJIK = "tg"
    TAMIL = "ta"
    TATAR = "tt"
    TELUGU = "te"
    TETUM = "tet"
    THAI = "th"
    TIGRINYA = "ti"
    TSONGA = "ts"
    TSWANA = "tn"
    TURKISH = "tr"
    TURKMEN = "tk"
    TWI_AKAN = "ak"
    UKRAINIAN = "uk"
    URDU = "ur"
    UYGHUR = "ug"
    UZBEK = "uz"
    VIETNAMESE = "vi"
    WELSH = "cy"
    XHOSA = "xh"
    YIDDISH = "yi"
    YORUBA = "yo"
    YUCATEC_MAYA = "yua"
    ZULU = "zu"

    def to_instruction(self) -> str:
        special_names = {
            "zh": "Chinese",
            "zh-CN": "Chinese, Simplified, China",
            "zh-TW": "Chinese, Traditional, Taiwan",
            "fr": "French",
            "fr-FR": "French, France",
            "fr-CA": "French, Canada",
            "pt": "Portuguese",
            "pt-PT": "Portuguese, Portugal",
            "pt-BR": "Portuguese, Brazil",
            "fil": "Filipino (Tagalog)",
            "tl": "Filipino (Tagalog)",
            "ms-Arab": "Malay, Jawi (Arabic Script)",
            "mni-Mtei": "Meiteilon (Manipuri)",
            "pa-Arab": "Punjabi (Shahmukhi)",
            "ckb": "Kurdish (Sorani)",
            "ku": "Kurdish (Kurmanji)",
            "jw": "Javanese",
            "jv": "Javanese",
        }

        if self.value in special_names:
            return special_names[self.value]

        return self.name.replace("_", " ").title()

    @staticmethod
    def _normalize_for_comparison(text: str) -> str:
        """
        Normalize text for comparison by removing punctuation and extra spaces.

        Examples:
        - "Chinese, Simplified, China" -> "CHINESE SIMPLIFIED CHINA"
        - "Filipino (Tagalog)" -> "FILIPINO TAGALOG"
        - "Malay, Jawi (Arabic Script)" -> "MALAY JAWI ARABIC SCRIPT"
        """
        # Remove punctuation and normalize spaces
        normalized = re.sub(r"[^\w\s]", " ", text.upper())
        # Replace multiple spaces with single space and strip
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    @classmethod
    def _get_iso_mappings(cls) -> dict[str, "LanguageCodes"]:
        """Get mappings for ISO 639-1 and 639-3 language codes."""
        # Mapping: (iso_639_1, iso_639_3) -> LanguageCode
        iso_pairs = [
            ("af", "afr", cls.AFRIKAANS),
            ("sq", "sqi", cls.ALBANIAN),
            ("ar", "ara", cls.ARABIC),
            ("hy", "hye", cls.ARMENIAN),
            ("az", "aze", cls.AZERBAIJANI),
            ("eu", "eus", cls.BASQUE),
            ("be", "bel", cls.BELARUSIAN),
            ("bn", "ben", cls.BENGALI),
            ("bs", "bos", cls.BOSNIAN),
            ("bg", "bul", cls.BULGARIAN),
            ("ca", "cat", cls.CATALAN),
            ("zh", "zho", cls.CHINESE_SIMPLIFIED_2),
            ("hr", "hrv", cls.CROATIAN),
            ("cs", "ces", cls.CZECH),
            ("da", "dan", cls.DANISH),
            ("nl", "nld", cls.DUTCH),
            ("en", "eng", cls.ENGLISH),
            ("eo", "epo", cls.ESPERANTO),
            ("et", "est", cls.ESTONIAN),
            ("fi", "fin", cls.FINNISH),
            ("fr", "fra", cls.FRENCH),
            ("ga", "gle", cls.IRISH),
            ("ka", "kat", cls.GEORGIAN),
            ("de", "deu", cls.GERMAN),
            ("el", "ell", cls.GREEK),
            ("gu", "guj", cls.GUJARATI),
            ("he", "heb", cls.HEBREW_2),
            ("hi", "hin", cls.HINDI),
            ("hu", "hun", cls.HUNGARIAN),
            ("is", "isl", cls.ICELANDIC),
            ("id", "ind", cls.INDONESIAN),
            ("it", "ita", cls.ITALIAN),
            ("ja", "jpn", cls.JAPANESE),
            ("kk", "kaz", cls.KAZAKH),
            ("ko", "kor", cls.KOREAN),
            ("la", "lat", cls.LATIN),
            ("lv", "lav", cls.LATVIAN),
            ("lt", "lit", cls.LITHUANIAN),
            ("mk", "mkd", cls.MACEDONIAN),
            ("ms", "msa", cls.MALAY),
            ("mi", "mri", cls.MAORI),
            ("mr", "mar", cls.MARATHI),
            ("mn", "mon", cls.MONGOLIAN),
            ("fa", "fas", cls.PERSIAN),
            ("pl", "pol", cls.POLISH),
            ("pt", "por", cls.PORTUGUESE),
            ("pa", "pan", cls.PUNJABI),
            ("ro", "ron", cls.ROMANIAN),
            ("ru", "rus", cls.RUSSIAN),
            ("sr", "srp", cls.SERBIAN),
            ("sn", "sna", cls.SHONA),
            ("sk", "slk", cls.SLOVAK),
            ("sl", "slv", cls.SLOVENIAN),
            ("so", "som", cls.SOMALI),
            ("st", "sot", cls.SESOTHO),
            ("es", "spa", cls.SPANISH),
            ("sw", "swa", cls.SWAHILI),
            ("sv", "swe", cls.SWEDISH),
            ("tl", "tgl", cls.FILIPINO_TAGALOG_2),
            ("ta", "tam", cls.TAMIL),
            ("te", "tel", cls.TELUGU),
            ("th", "tha", cls.THAI),
            ("tn", "tsn", cls.TSWANA),
            ("ts", "tso", cls.TSONGA),
            ("tr", "tur", cls.TURKISH),
            ("uk", "ukr", cls.UKRAINIAN),
            ("ur", "urd", cls.URDU),
            ("vi", "vie", cls.VIETNAMESE),
            ("cy", "cym", cls.WELSH),
            ("xh", "xho", cls.XHOSA),
            ("yo", "yor", cls.YORUBA),
            ("zu", "zul", cls.ZULU),
            ("lg", "lug", cls.GANDA_LUGANDA),
        ]

        mapping = {}
        for iso1, iso3, lang_code in iso_pairs:
            mapping[iso1.upper()] = lang_code
            mapping[iso3.upper()] = lang_code

        # Special cases
        mapping.update(
            {
                "IW": cls.HEBREW,  # Alternative Hebrew code
                "NB": cls.NORWEGIAN,
                "NOB": cls.NORWEGIAN,  # Bokmål
                "NN": cls.NORWEGIAN,
                "NNO": cls.NORWEGIAN,  # Nynorsk
            }
        )

        return mapping

    @classmethod
    def _get_common_name_mappings(cls) -> dict[str, "LanguageCodes"]:
        """Get mappings for common language name variations."""
        return {
            "CHINESE": cls.CHINESE_SIMPLIFIED_2,
            "TAGALOG": cls.FILIPINO_TAGALOG_2,
            "FILIPINO": cls.FILIPINO_TAGALOG_2,
            "GANDA": cls.GANDA_LUGANDA,
            "LUGANDA": cls.GANDA_LUGANDA,
            "SOTHO": cls.SESOTHO,
            "SLOVENE": cls.SLOVENIAN,
            "BOKMAL": cls.NORWEGIAN,
            "NYNORSK": cls.NORWEGIAN,
        }

    @classmethod
    def _get_cultural_name_mappings(cls) -> dict[str, "LanguageCodes"]:
        """Get mappings for cultural/native language names."""
        return {
            # Native language names
            "MANDARIN": cls.CHINESE_SIMPLIFIED_2,
            "FARSI": cls.PERSIAN,
            "DEUTSCH": cls.GERMAN,
            "ESPAÑOL": cls.SPANISH,
            "FRANÇAIS": cls.FRENCH,
            "ITALIANO": cls.ITALIAN,
            "PORTUGUÊS": cls.PORTUGUESE,
            "NEDERLANDS": cls.DUTCH,
            "SVENSKA": cls.SWEDISH,
            "NORSK": cls.NORWEGIAN,
            "SUOMI": cls.FINNISH,
            "ΕΛΛΗΝΙΚΆ": cls.GREEK,
            "TÜRKÇE": cls.TURKISH,
            "עברית": cls.HEBREW_2,
            "العربية": cls.ARABIC,
            "हिन्दी": cls.HINDI,
            "বাংলা": cls.BENGALI,
            "தமிழ்": cls.TAMIL,
            "తెలుగు": cls.TELUGU,
            "ไทย": cls.THAI,
            "TIẾNG VIỆT": cls.VIETNAMESE,
            "BAHASA INDONESIA": cls.INDONESIAN,
            "BAHASA MELAYU": cls.MALAY,
        }

    @classmethod
    def _get_casual_variant_mappings(cls) -> dict[str, "LanguageCodes"]:
        """Get mappings for casual/colloquial language variants."""
        return {
            # Chinese variants
            "CHINESE SIMPLIFIED": cls.CHINESE_SIMPLIFIED,
            "CHINESE TRADITIONAL": cls.CHINESE_TRADITIONAL,
            "SIMPLIFIED CHINESE": cls.CHINESE_SIMPLIFIED,
            "TRADITIONAL CHINESE": cls.CHINESE_TRADITIONAL,
            "MANDARIN CHINESE": cls.CHINESE_SIMPLIFIED_2,
            # Spanish variants
            "MEXICAN SPANISH": cls.SPANISH,
            "LATIN AMERICAN SPANISH": cls.SPANISH,
            "CASTILIAN": cls.SPANISH,
            # Portuguese variants
            "BRAZILIAN PORTUGUESE": cls.PORTUGUESE_BR,
            "EUROPEAN PORTUGUESE": cls.PORTUGUESE_PT,
            # French variants
            "CANADIAN FRENCH": cls.FRENCH_CA,
            "QUEBEC FRENCH": cls.FRENCH_CA,
            # English variants (all map to English)
            "AMERICAN ENGLISH": cls.ENGLISH,
            "BRITISH ENGLISH": cls.ENGLISH,
            "AUSTRALIAN ENGLISH": cls.ENGLISH,
            "INDIAN ENGLISH": cls.ENGLISH,
            # Short forms
            "CHIN": cls.CHINESE_SIMPLIFIED_2,
            "JAP": cls.JAPANESE,
            "SPAN": cls.SPANISH,
            "PORT": cls.PORTUGUESE,
            "RUSS": cls.RUSSIAN,
            # Writing systems/cultural references (map to primary language)
            "PINYIN": cls.CHINESE_SIMPLIFIED_2,  # Chinese romanization
            "KANJI": cls.JAPANESE,  # Japanese writing system
            "HANGUL": cls.KOREAN,  # Korean writing system
            "CYRILLIC": cls.RUSSIAN,  # Slavic script - map to Russian as primary
        }

    @classmethod
    def _get_all_possible_names(cls) -> dict[str, "LanguageCodes"]:
        """Get all possible names mapped to their corresponding LanguageCodes."""
        all_names = {}

        # Combine all mapping methods
        all_names.update(cls._get_iso_mappings())
        all_names.update(cls._get_common_name_mappings())
        all_names.update(cls._get_cultural_name_mappings())
        all_names.update(cls._get_casual_variant_mappings())

        # Add enum names and values
        for lang_code in cls:
            all_names[lang_code.name] = lang_code
            all_names[lang_code.value.upper()] = lang_code
            # Add both original and normalized instruction names
            instruction_original = lang_code.to_instruction().upper()
            instruction_normalized = cls._normalize_for_comparison(
                lang_code.to_instruction()
            )
            all_names[instruction_original] = lang_code
            all_names[instruction_normalized] = lang_code

        return all_names

    @classmethod
    def _find_similar_match(
        cls, target: str, threshold: float = 0.8
    ) -> "LanguageCodes | None":
        """Find the best matching language using character similarity."""
        all_names = cls._get_all_possible_names()
        best_match = None
        best_ratio = 0.0

        for name, lang_code in all_names.items():
            # Try exact similarity
            ratio = difflib.SequenceMatcher(None, target, name).ratio()
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = lang_code

            # Also try partial matching for longer strings
            if len(target) >= 3 and len(name) >= 3:
                # Check if target is a substring of name or vice versa
                if target in name or name in target:
                    substring_ratio = min(len(target), len(name)) / max(
                        len(target), len(name)
                    )
                    if substring_ratio >= 0.6 and substring_ratio > best_ratio:
                        best_ratio = substring_ratio
                        best_match = lang_code

        return best_match if best_ratio >= threshold else None

    @classmethod
    def from_common_name(cls, name: str) -> "LanguageCodes":
        """
        Convert a common language name to a LanguageCodes enum.

        Supports case-insensitive matching for:
        - Enum names (e.g., "ENGLISH", "english")
        - Language codes (e.g., "en", "EN")
        - ISO 639-1/639-3 codes (e.g., "en"/"eng", "es"/"spa")
        - Common name variations (e.g., "Chinese", "Tagalog")
        - Cultural/native names (e.g., "Mandarin", "Farsi", "Deutsch")
        - Casual variants (e.g., "Brazilian Portuguese", "British English")
        - Writing systems (e.g., "Pinyin", "Kanji", "Hangul")
        - Instruction names from to_instruction()
        - Fuzzy matching for typos and variations (e.g., "Englsh" -> "English")

        Uses character similarity as a fallback with 80% threshold for flexibility.
        """
        normalized = name.upper().strip()
        normalized_for_punctuation = cls._normalize_for_comparison(name)

        # Try direct enum name match
        if hasattr(cls, normalized):
            return getattr(cls, normalized)

        # Try direct value match (language codes)
        for lang_code in cls:
            if lang_code.value.upper() == normalized:
                return lang_code

        # Try ISO code mappings
        iso_mappings = cls._get_iso_mappings()
        if normalized in iso_mappings:
            return iso_mappings[normalized]

        # Try common name variations
        common_mappings = cls._get_common_name_mappings()
        if normalized in common_mappings:
            return common_mappings[normalized]

        # Try cultural/native language names
        cultural_mappings = cls._get_cultural_name_mappings()
        if normalized in cultural_mappings:
            return cultural_mappings[normalized]

        # Try casual/colloquial variants
        casual_mappings = cls._get_casual_variant_mappings()
        if normalized in casual_mappings:
            return casual_mappings[normalized]

        # Try instruction names
        for lang_code in cls:
            instruction_normalized = cls._normalize_for_comparison(
                lang_code.to_instruction()
            )
            if instruction_normalized == normalized_for_punctuation:
                return lang_code

        # Try language family fallback (e.g., "ja-JP" -> "ja")
        if "-" in normalized or "_" in normalized:
            # Extract the language part (before delimiter)
            language_part: str = normalized.split("-")[0].split("_")[0].strip()

            if language_part and language_part != normalized:
                # Try direct value match with language part
                for lang_code in cls:
                    if lang_code.value.upper() == language_part:
                        return lang_code

                # Try ISO mappings with language part
                if language_part in iso_mappings:
                    return iso_mappings[language_part]

                # Try common name mappings with language part
                if language_part in common_mappings:
                    return common_mappings[language_part]

                # Try cultural mappings with language part
                if language_part in cultural_mappings:
                    return cultural_mappings[language_part]

                # Try casual mappings with language part
                if language_part in casual_mappings:
                    return casual_mappings[language_part]

        # Try character similarity as final fallback
        similar_match = cls._find_similar_match(normalized_for_punctuation)
        if similar_match:
            return similar_match

        raise ValueError(f"Language '{name}' not found in supported languages")

    @classmethod
    def from_might_common_name(cls, name: str) -> typing.Optional["LanguageCodes"]:
        try:
            return cls.from_common_name(name)
        except ValueError:
            return None
