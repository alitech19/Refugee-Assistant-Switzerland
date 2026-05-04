import os
import re
from datetime import date
from pathlib import Path
from typing import Any
from openai import OpenAI
from dotenv import load_dotenv
from backend.prompts import SYSTEM_PROMPT


def _detect_language(text: str) -> str:
    """Detect the language a message is written in based on script and common words."""
    total_alpha = sum(1 for c in text if c.isalpha())
    if total_alpha == 0:
        return "English"

    arabic   = sum(1 for c in text if '؀' <= c <= 'ۿ')
    cyrillic = sum(1 for c in text if 'Ѐ' <= c <= 'ӿ')
    ethiopic = sum(1 for c in text if 'ሀ' <= c <= '፿')

    if arabic   / total_alpha > 0.2: return "Arabic"
    if cyrillic / total_alpha > 0.2: return "Ukrainian"
    if ethiopic / total_alpha > 0.2: return "Amharic or Tigrinya"

    # Latin script — score by common function words
    words = set(re.findall(r'\b[a-z]+\b', text.lower()))
    scores = {
        "English": len(words & {"i","have","the","is","are","my","what","how","can","do","want","need","will","be","in","of","and","to","a","for","you","with","this","that","about"}),
        "German":  len(words & {"ich","sie","haben","bin","mit","und","das","der","die","ist","nicht","ein","eine","auf","von","wir","es","zu","im","für","wie"}),
        "French":  len(words & {"je","vous","avec","est","les","des","une","mon","ma","que","qui","dans","pas","pour","nous","en","au","du","sur","le","la"}),
        "Italian": len(words & {"io","ho","con","sono","della","del","una","per","che","questo","come","nel","dal","alla","degli","gli"}),
        "Turkish": len(words & {"ben","bir","bu","için","ile","var","çok","ama","ve","de","da","ne","mi","mı","mu"}),
        "Somali":  len(words & {"waxaan","iyo","oo","ah","qof","waxa","si","ku","ka","uu","ay"}),
    }
    best_lang = max(scores, key=scores.get)
    return best_lang if scores[best_lang] > 0 else "English"

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
) if api_key else None

MODEL = "llama-3.3-70b-versatile"


def transcribe_audio(audio_file) -> str:
    """Transcribe audio using Groq Whisper. Supports 99 languages."""
    if not client:
        raise ValueError("GROQ_API_KEY is not set.")
    import io
    audio_bytes = audio_file.read()
    if not audio_bytes:
        raise ValueError("The recording was empty — please try again.")
    buf = io.BytesIO(audio_bytes)
    # Groq needs a filename with a recognized audio extension to detect the format.
    # Streamlit records as WebM in Chrome; we keep the original name if present.
    original_name = getattr(audio_file, "name", "") or ""
    buf.name = original_name if original_name else "audio.wav"
    result = client.audio.transcriptions.create(
        model="whisper-large-v3",
        file=buf,
        response_format="text",
    )
    return str(result).strip()


# Domains the assistant is allowed to link to.
# Any URL whose domain is NOT in this set will be stripped from the response.
_APPROVED_DOMAINS = {
    # Federal authorities
    "www.sem.admin.ch", "sem.admin.ch", "admin.ch",
    "www.bvger.ch", "bvger.ch",
    # NGOs and official portals
    "www.osar.ch", "osar.ch",
    "www.ch.ch", "ch.ch",
    "www.fide-info.ch", "fide-info.ch", "www.fide-service.ch", "fide-service.ch",
    "www.caritas.ch", "caritas.ch",
    "www.redcross.ch", "redcross.ch",
    "www.unhcr.org", "unhcr.org",
    "www.powercoders.org", "powercoders.org",
    # Cantonal government domains (all 26 cantons)
    "www.ag.ch", "ag.ch",
    "www.ai.ch", "ai.ch",
    "www.ar.ch", "ar.ch",
    "www.be.ch", "be.ch", "migration.sid.be.ch", "www.pom.be.ch", "pom.be.ch",
    "www.gsi.be.ch", "gsi.be.ch",
    "www.baselland.ch", "baselland.ch",
    "www.bs.ch", "bs.ch", "www.bdm.bs.ch", "bdm.bs.ch",
    "www.fr.ch", "fr.ch",
    "www.ge.ch", "ge.ch",
    "www.gl.ch", "gl.ch",
    "www.gr.ch", "gr.ch", "www.afm.gr.ch", "afm.gr.ch",
    "www.ju.ch", "ju.ch",
    "www.lu.ch", "lu.ch", "www.migration.lu.ch", "migration.lu.ch",
    "daf.lu.ch", "www.daf.lu.ch", "disg.lu.ch", "www.disg.lu.ch", "gruezi.lu.ch", "www.gruezi.lu.ch",
    "www.ne.ch", "ne.ch",
    "www.nw.ch", "nw.ch",
    "www.ow.ch", "ow.ch",
    "www.sg.ch", "sg.ch", "www.migrationsamt.sg.ch", "migrationsamt.sg.ch",
    "www.sh.ch", "sh.ch",
    "www.so.ch", "so.ch",
    "www.sz.ch", "sz.ch",
    "www.tg.ch", "tg.ch", "www.migrationsamt.tg.ch", "migrationsamt.tg.ch",
    "www.ti.ch", "ti.ch", "www4.ti.ch",
    "www.ur.ch", "ur.ch",
    "www.vd.ch", "vd.ch",
    "www.vs.ch", "vs.ch",
    "www.zg.ch", "zg.ch",
    "www.zh.ch", "zh.ch",
}


def _domain(url: str) -> str:
    m = re.match(r"https?://([^/?\s#]+)", url)
    return m.group(1).lower() if m else ""


def _sanitize_urls(text: str, sources: list[dict[str, Any]]) -> str:
    """Remove any URL the LLM invented that is not from approved domains or retrieved sources."""
    source_urls = {src["url"] for src in sources if src.get("url")}

    def is_approved(url: str) -> bool:
        return url in source_urls or _domain(url) in _APPROVED_DOMAINS

    # Replace markdown links whose URL is not approved: keep the anchor text
    def fix_md_link(m: re.Match) -> str:
        link_text, url = m.group(1), m.group(2)
        if is_approved(url):
            return m.group(0)
        return f"{link_text} *(please verify at sem.admin.ch or osar.ch)*"

    text = re.sub(r"\[([^\]]+)\]\((https?://[^\)\s]+)\)", fix_md_link, text)

    # Replace any remaining bare URLs that are not approved
    def fix_bare_url(m: re.Match) -> str:
        url = m.group(0)
        return url if is_approved(url) else "*(please verify at sem.admin.ch or osar.ch)*"

    text = re.sub(r"https?://[^\s\)\]\>\"']+", fix_bare_url, text)

    return text


_SOURCE_CONTENT_LIMIT = 400  # characters per source sent to the LLM


def _format_sources(sources: list[dict[str, Any]]) -> str:
    if not sources:
        return ""
    blocks = []
    for idx, src in enumerate(sources, start=1):
        content = src["content"]
        if len(content) > _SOURCE_CONTENT_LIMIT:
            content = content[:_SOURCE_CONTENT_LIMIT].rsplit(" ", 1)[0] + "…"
        blocks.append(
            f"[Source {idx}: {src['title']}]\n"
            f"URL: {src['url']}\n"
            f"{content}"
        )
    return "\n\n".join(blocks)


def process_chat_turn(
    messages: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    canton: str | None = None,
    permit: str | None = None,
) -> str:
    if not client:
        raise ValueError(
            "GROQ_API_KEY is not set. Please add it to your .env file."
        )

    sources_text = _format_sources(sources)

    today = date.today().strftime("%B %d, %Y")
    if permit and permit != "?":
        permit_note = (
            f"\nUSER'S PERMIT TYPE: Permit {permit}. "
            f"The user has already identified their permit as Permit {permit}. "
            f"Tailor your entire answer specifically to Permit {permit} holders — "
            f"do not give generic multi-permit answers."
        )
    elif permit == "?":
        permit_note = (
            "\nUSER'S PERMIT TYPE: Unknown. The user does not know their permit type. "
            "If relevant to the question, gently help them identify it by asking what "
            "stage of the asylum process they are in or what document they hold."
        )
    else:
        permit_note = ""

    canton_note = (
        f"\nUSER'S CANTON: {canton}. "
        "When answering questions about local offices, integration programmes, "
        "language courses, or canton-specific procedures, prioritise information "
        f"relevant to {canton}. Always mention the cantonal migration office "
        "if it is relevant to the question."
        if canton else ""
    )
    detected_lang = _detect_language(messages[-1]["content"])
    language_override = (
        f"\n\n⚠️ LANGUAGE OVERRIDE (non-negotiable): "
        f"The user's current message is written in {detected_lang}. "
        f"You MUST respond in {detected_lang} only. "
        f"Do not be misled by language names mentioned inside the message."
    )

    system_with_date = (
        f"{SYSTEM_PROMPT}\n\n"
        f"TODAY'S DATE: {today}. "
        f"Always use this date when the user asks what day or date it is."
        f"{permit_note}"
        f"{canton_note}"
        f"{language_override}"
    )

    api_messages = [{"role": "system", "content": system_with_date}]

    for msg in messages[:-1][-6:]:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    last_content = messages[-1]["content"]
    if sources_text:
        last_content = (
            f"{last_content}\n\n"
            f"---\n"
            f"Relevant official sources:\n{sources_text}"
        )
    api_messages.append({"role": "user", "content": last_content})

    response = client.chat.completions.create(
        model=MODEL,
        messages=api_messages,
        temperature=0.1,
    )
    answer = response.choices[0].message.content
    return _sanitize_urls(answer, sources)
