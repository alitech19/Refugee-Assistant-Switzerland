import re
from typing import Any

# Matches permit letter in many languages:
# English: "permit N", French: "permis F", German: "Ausweis B / Bewilligung B"
# Italian: "permesso B", Arabic: "تصريح N", Ukrainian: "дозвіл N"
# Also catches bare letter next to a permit word: "N permit", "F ausweis"
PERMIT_PATTERN = re.compile(
    r"(?:permit|ausweis|bewilligung|permis|autorisation|permesso"
    r"|تصريح|تصریح|izin|дозвіл)\s+([a-z])\b"
    r"|\b([nfbcs])\s*(?:permit|ausweis|bewilligung|permis|card|karte|carte)\b",
    re.IGNORECASE,
)

# Maps a canonical English country/group name to the keywords that identify it
# in any language the user might write in.
COUNTRY_KEYWORDS: dict[str, list[str]] = {
    "Syria": [
        "syria", "syrian", "syrians", "syrien", "syrisch", "syrische",
        "syrie", "سوريا", "سوري", "سوريون", "suriye", "suriyeli",
    ],
    "Ukraine": [
        "ukraine", "ukrainian", "ukrainians", "ukraina", "ukrainisch",
        "ukrainische", "ukraine-krieg", "ucraina", "україна",
    ],
    "Afghanistan": [
        "afghanistan", "afghan", "afghans", "afghani", "افغانستان", "افغان",
    ],
    "Eritrea": ["eritrea", "eritrean", "eritreans", "eritreisch", "إريتريا"],
    "Somalia": ["somalia", "somali", "somalis", "صوماليا"],
    "Ethiopia": ["ethiopia", "ethiopian", "äthiopien", "äthiopisch", "إثيوبيا"],
    "Iraq": ["iraq", "iraqi", "iraqis", "irak", "irakisch", "العراق"],
    "Turkey": ["turkey", "turkish", "türkei", "türkisch", "تركيا"],
}

TOPIC_KEYWORDS = {
    "work": [
        # English
        "work", "job", "employment", "employed", "employer", "salary", "earn",
        # German
        "arbeit", "arbeiten", "beschäftigung", "erwerbstätig", "beruf", "lohn",
        # French
        "travail", "emploi", "travailler", "employeur", "salaire",
        # Italian
        "lavoro", "lavorare", "impiego", "occupazione",
        # Arabic
        "عمل", "شغل", "وظيفة", "توظيف", "راتب", "أعمل", "اعمل",
        # Dari / Farsi
        "کار", "شغل", "کارمند", "حقوق",
        # Turkish
        "iş", "çalışma", "istihdam", "çalışmak", "maaş",
        # Somali
        "shaqo", "shaqaale", "mushaharo",
        # Ukrainian
        "робота", "працювати", "зайнятість", "заробіток",
        # Tigrinya
        "ስራ", "ሥራ",
        # Amharic
        "ስራ", "ሥራ", "ደሞዝ",
    ],
    "asylum": [
        # English
        "asylum", "procedure", "interview", "hearing", "application", "refugee",
        "syria", "syrian", "suspended", "reopened", "reopen", "pending case",
        # German
        "asyl", "asylverfahren", "anhörung", "asylantrag", "flüchtling", "verfahren",
        "syrien", "syrisch", "sistiert", "wiederaufnahme",
        # French
        "asile", "procédure", "audition", "demande", "réfugié",
        "syrie", "syrien", "suspendu",
        # Italian
        "asilo", "procedura", "audizione", "domanda", "rifugiato",
        # Arabic
        "لجوء", "إجراء", "طلب لجوء", "مقابلة", "لاجئ", "لاجئين", "طالب لجوء",
        "سوريا", "سوري", "سوريون", "ملف معلق", "استئناف",
        # Dari / Farsi
        "پناه", "پناهندگی", "پناهجو", "اقامت",
        # Turkish
        "iltica", "sığınma", "başvuru", "mülteci", "sığınmacı",
        "suriye", "suriyeli",
        # Somali
        "qaxooti", "codsiga", "qaxootiga",
        # Ukrainian
        "притулок", "процедура", "заява", "біженець",
        # Tigrinya
        "ዑቕባ", "ስደተኛ",
        # Amharic
        "ጥገኝነት", "ስደተኛ",
    ],
    "integration": [
        # English
        "integration", "language", "course", "fide", "vocational", "training", "learn",
        # German
        "integration", "sprache", "kurs", "sprachkurs", "ausbildung", "lernen",
        # French
        "intégration", "langue", "cours", "formation", "linguistique", "apprendre",
        # Italian
        "integrazione", "lingua", "corso", "formazione", "imparare",
        # Arabic
        "اندماج", "لغة", "دورة", "تدريب", "دراسة لغة", "تعلم",
        # Dari / Farsi
        "یکپارچگی", "زبان", "دوره", "آموزش",
        # Turkish
        "entegrasyon", "dil", "kurs", "eğitim", "öğrenmek",
        # Somali
        "is-dhexgalka", "luuqadda", "koorsada",
        # Ukrainian
        "інтеграція", "мова", "курс", "навчання",
    ],
    "healthcare": [
        # English
        "health", "doctor", "medical", "hospital", "insurance", "sick", "medicine", "clinic",
        # German
        "gesundheit", "arzt", "krankenhaus", "krankenkasse", "medizin", "krank", "klinik",
        # French
        "santé", "médecin", "hôpital", "assurance", "maladie", "médical", "clinique",
        # Italian
        "salute", "medico", "ospedale", "assicurazione", "malattia", "clinica",
        # Arabic
        "صحة", "طبيب", "مستشفى", "تأمين صحي", "دواء", "علاج", "مريض", "عيادة",
        # Dari / Farsi
        "صحت", "داکتر", "شفاخانه", "بیمه", "دارو",
        # Turkish
        "sağlık", "doktor", "hastane", "sigorta", "ilaç", "klinik",
        # Somali
        "caafimaad", "dhakhtar", "isbitaal", "caymis",
        # Ukrainian
        "здоров'я", "лікар", "лікарня", "страхування", "ліки",
    ],
    "education": [
        # English
        "school", "education", "children", "child", "study", "university", "kindergarten",
        # German
        "schule", "bildung", "kinder", "kind", "studium", "universität", "kindergarten",
        # French
        "école", "éducation", "enfant", "étude", "université", "maternelle",
        # Italian
        "scuola", "istruzione", "bambini", "studio", "università",
        # Arabic
        "مدرسة", "تعليم", "أطفال", "طفل", "دراسة", "جامعة", "روضة",
        # Dari / Farsi
        "مکتب", "تعلیم", "اطفال", "پوهنتون",
        # Turkish
        "okul", "eğitim", "çocuk", "üniversite", "anaokulu",
        # Somali
        "dugsiga", "waxbarashada", "carruurta", "jaamacadda",
        # Ukrainian
        "школа", "освіта", "діти", "університет", "навчання",
    ],
    "family": [
        # English
        "family", "reunification", "spouse", "wife", "husband", "relatives", "join",
        # German
        "familie", "familiennachzug", "ehepartner", "ehemann", "ehefrau", "zusammenführung",
        # French
        "famille", "regroupement", "conjoint", "époux", "épouse", "rejoindre",
        # Italian
        "famiglia", "ricongiungimento", "coniuge", "moglie", "marito",
        # Arabic
        "عائلة", "لم الشمل", "زوج", "زوجة", "أطفال", "أسرة", "لمّ الشمل",
        # Dari / Farsi
        "خانواده", "وحدت خانوادگی", "همسر", "فرزندان",
        # Turkish
        "aile", "eş", "çocuklar", "aile birleşimi", "katılma",
        # Somali
        "qoyska", "xididdada", "ninka", "naagta", "caruurta",
        # Ukrainian
        "сім'я", "возз'єднання", "чоловік", "дружина", "діти",
    ],
    "appeal": [
        # English
        "appeal", "rejected", "rejection", "negative", "deadline", "court", "lawyer",
        # German
        "beschwerde", "ablehnung", "abgelehnt", "negativ", "frist", "gericht", "anwalt",
        # French
        "recours", "rejet", "refus", "négatif", "délai", "tribunal", "avocat",
        # Italian
        "ricorso", "rifiuto", "negativo", "scadenza", "tribunale", "avvocato",
        # Arabic
        "طعن", "استئناف", "رفض", "قرار سلبي", "موعد نهائي", "محكمة", "محامي",
        # Dari / Farsi
        "اعتراض", "رد شد", "منفی", "محکمه", "وکیل",
        # Turkish
        "itiraz", "ret", "olumsuz", "süre", "mahkeme", "avukat",
        # Somali
        "cabasho", "diidasho", "xeer", "qareen",
        # Ukrainian
        "апеляція", "відмова", "негативне", "суд", "адвокат",
    ],
    "naturalization": [
        # English
        "citizenship", "naturalization", "passport", "swiss citizen", "nationality",
        # German
        "einbürgerung", "staatsbürgerschaft", "pass", "schweizer bürger", "nationalität",
        # French
        "naturalisation", "citoyenneté", "passeport", "nationalité", "citoyen suisse",
        # Italian
        "naturalizzazione", "cittadinanza", "passaporto", "nazionalità",
        # Arabic
        "جنسية", "تجنيس", "جواز سفر", "مواطنة", "الجنسية السويسرية",
        # Dari / Farsi
        "تابعیت", "پاسپورت", "شهروندی",
        # Turkish
        "vatandaşlık", "pasaport", "doğallaştırma", "İsviçre vatandaşı",
        # Somali
        "muwaatinnimada", "baasaboor", "dhalashada",
        # Ukrainian
        "громадянство", "паспорт", "натуралізація",
    ],
    "social_assistance": [
        # English
        "social assistance", "welfare", "financial support", "allowance", "benefit", "money",
        # German
        "sozialhilfe", "unterstützung", "finanzielle hilfe", "geld", "beihilfe",
        # French
        "aide sociale", "assistance", "soutien financier", "argent", "allocation",
        # Italian
        "assistenza sociale", "sostegno", "finanziario", "soldi", "indennità",
        # Arabic
        "مساعدة اجتماعية", "دعم مالي", "مال", "إعانة", "منحة", "مساعدة مالية",
        # Dari / Farsi
        "کمک اجتماعی", "حمایت مالی", "پول",
        # Turkish
        "sosyal yardım", "destek", "para", "ödenek", "yardım",
        # Somali
        "kaalmada bulshada", "taageerada", "lacagta",
        # Ukrainian
        "соціальна допомога", "підтримка", "гроші", "допомога",
    ],
}


def _extract_permits(text: str) -> list[str]:
    matches = PERMIT_PATTERN.findall(text)
    seen = []
    for group1, group2 in matches:
        letter = (group1 or group2).upper()
        permit = f"Permit {letter}"
        if permit not in seen:
            seen.append(permit)
    return seen


def _detect_topics(text: str) -> list[str]:
    lower = text.lower()
    return [
        topic
        for topic, keywords in TOPIC_KEYWORDS.items()
        if any(kw in lower for kw in keywords)
    ]


def _detect_country(text: str) -> str | None:
    lower = text.lower()
    for country, keywords in COUNTRY_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return country
    return None


def _build_search_query(
    user_input: str,
    permits: list[str],
    topics: list[str],
    state: dict[str, Any],
) -> str:
    parts = []

    effective_permit = permits[0] if permits else state.get("current_permit")
    if effective_permit:
        parts.append(effective_permit)

    country = _detect_country(user_input)
    if country:
        parts.append(country)

    parts.extend(topics[:2])

    if parts:
        return " ".join(parts) + " Switzerland"

    # Fallback: only use raw input if it is mostly Latin script
    # (avoids sending Arabic/Cyrillic text into an English keyword search)
    latin_chars = sum(1 for c in user_input if c.isascii() and c.isalpha())
    total_chars = sum(1 for c in user_input if c.isalpha())
    if total_chars > 0 and (latin_chars / total_chars) >= 0.7:
        return user_input.strip()

    # Non-Latin script with no detected topic — return generic Swiss asylum query
    return "asylum permit rights Switzerland"


def resolve_user_query(user_input: str, state: dict[str, Any]) -> dict[str, Any]:
    permits = _extract_permits(user_input)
    topics = _detect_topics(user_input)

    effective_permit = permits[0] if permits else state.get("current_permit")
    standalone_query = _build_search_query(user_input, permits, topics, state)

    return {
        "raw_input": user_input,
        "standalone_query": standalone_query,
        "mentioned_permits": permits,
        "effective_permit": effective_permit,
        "topics": topics,
    }
