from datetime import date
from functools import lru_cache
import re

from google import genai

from schemas import OrderAnalysis


def build_prompt(
    message: str,
    service_catalog: dict,
    reference_date: str | None = None,
) -> str:
    """Build a compact prompt so Gemini has less text to process."""
    reference_date = reference_date or date.today().isoformat()

    catalog_text = "\n".join(
        f"- {name}: Rp{price:,}".replace(",", ".")
        for name, price in service_catalog.items()
    )

    return f"""Anda adalah AI Business Assistant untuk UMKM Cleaning Service Indonesia.

TUGAS:
Ubah chat customer menjadi OrderAnalysis terstruktur. Anda hanya mengekstrak
informasi. Harga dan status order dihitung Python, bukan AI.

REFERENCE DATE: {reference_date}

KATALOG:
{catalog_text}

EKSTRAK:
customer_name, service, quantity, service_date, service_time,
property_type, property_detail, address, special_notes,
missing_fields, risk_flags, order_summary, follow_up_message, confidence.

ATURAN PENTING:
1. Jangan mengarang data. Jika tidak ada, gunakan null.
2. Jangan menganggap quantity = 1 jika customer tidak menyebut jumlah.
3. "pagi/siang/sore/malam" tanpa jam pasti = service_time null + ambigu.
4. "2 lantai" adalah property_detail, bukan quantity.
5. Rumah/kantor/apartemen/ruko/villa = property_type.
6. Salin alamat customer apa adanya; jangan membuat alamat.
7. Gunakan nama layanan yang paling cocok dari katalog.
8. Permintaan pickup jangan diubah menjadi onsite; tandai risk_flags.
9. Jangan menentukan harga, subtotal, total, READY, atau NEEDS CONFIRMATION.
10. follow_up_message hanya meminta informasi yang belum jelas.
11. Pahami "hari ini/besok/lusa/nama hari" berdasarkan reference date jika jelas.
12. Output harus sesuai schema OrderAnalysis dan confidence 0..1.

CHAT:
{message}""".strip()


@lru_cache(maxsize=8)
def _get_client(api_key: str):
    """Reuse the Gemini client between Streamlit reruns."""
    return genai.Client(api_key=api_key)


@lru_cache(maxsize=32)
def _analyze_cached(
    message: str,
    api_key: str,
    catalog_text: str,
    model_name: str,
    reference_date: str,
) -> OrderAnalysis:
    """Cache identical test requests so repeated demos return immediately."""
    client = _get_client(api_key)

    catalog = {}
    for line in catalog_text.split("\n"):
        name, price = line.split("|||", 1)
        catalog[name] = int(price)

    prompt = build_prompt(
        message=message,
        service_catalog=catalog,
        reference_date=reference_date,
    )

    interaction = client.interactions.create(
        model=model_name,
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": OrderAnalysis.model_json_schema(),
        },
    )

    if not interaction.output_text:
        raise ValueError("Gemini tidak mengembalikan hasil.")

    analysis = OrderAnalysis.model_validate_json(interaction.output_text)
    return _normalize_explicit_fields(analysis, message, catalog, reference_date)



def _normalize_explicit_fields(
    analysis: OrderAnalysis,
    message: str,
    service_catalog: dict,
    reference_date: str,
) -> OrderAnalysis:
    """
    Deterministic normalization for facts explicitly written in the chat.
    Gemini still performs natural-language extraction; this layer prevents
    obvious literal values from being lost or corrupted before business rules.
    """
    from schemas import CleaningItem
    from datetime import datetime

    lower = message.lower()

    # --- SERVICE + QUANTITY ---
    matched_service = None
    for name in service_catalog:
        if re.search(rf"\b{re.escape(name.lower())}\b", lower):
            matched_service = name
            break

    # Only accept a quantity that is explicitly tied to a service/order.
    explicit_qty = None
    qty_patterns = [
        r"\bsebanyak\s+(\d+)\s*(?:layanan|jasa|unit)?\b",
        r"\bjumlah\s+(\d+)\s*(?:layanan|jasa|unit)?\b",
        r"\b(?:x|×)\s*(\d+)\b",
        r"\b(\d+)\s*(?:layanan|jasa|unit)\b",
    ]
    for pattern in qty_patterns:
        m = re.search(pattern, lower)
        if m:
            value = int(m.group(1))
            if 1 <= value <= 100:
                explicit_qty = value
                break

    if matched_service and not analysis.items:
        analysis.items = [
            CleaningItem(
                service_name=matched_service,
                quantity=explicit_qty,
            )
        ]
    elif matched_service and analysis.items:
        # Override AI only with an explicit catalog literal / explicit qty.
        analysis.items[0].service_name = matched_service
        if explicit_qty is not None:
            analysis.items[0].quantity = explicit_qty

    # --- EXACT DATE ---
    # Always prefer an exact date written by the customer over an incorrect AI date.
    date_match = re.search(
        r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b",
        message,
    )
    if date_match:
        y, m, d = map(int, date_match.groups())
        try:
            analysis.service_date = datetime(y, m, d).date().isoformat()
        except ValueError:
            pass

    # Indonesian month names, e.g. "19 September 2026".
    month_map = {
        "januari": 1, "februari": 2, "maret": 3, "april": 4,
        "mei": 5, "juni": 6, "juli": 7, "agustus": 8,
        "september": 9, "oktober": 10, "november": 11, "desember": 12,
    }
    month_pattern = (
        r"\b(\d{1,2})\s+(" + "|".join(month_map) + r")\s+(20\d{2})\b"
    )
    date_match = re.search(month_pattern, lower)
    if date_match:
        d = int(date_match.group(1))
        m = month_map[date_match.group(2)]
        y = int(date_match.group(3))
        try:
            analysis.service_date = datetime(y, m, d).date().isoformat()
        except ValueError:
            pass

    # Relative "besok" is deterministic from the selected reference date.
    if not analysis.service_date and re.search(r"\bbesok\b", lower):
        ref = datetime.fromisoformat(reference_date).date()
        analysis.service_date = (ref + __import__("datetime").timedelta(days=1)).isoformat()

    # --- EXACT TIME ---
    time_patterns = [
        r"\bpukul\s+(\d{1,2})(?::(\d{2}))?\b",
        r"\bjam\s+(\d{1,2})(?::(\d{2}))?\b",
        r"\b(\d{1,2})(?::(\d{2}))\s*(?:wib|wit|wita)?\b",
    ]
    for pattern in time_patterns:
        m = re.search(pattern, lower)
        if m:
            hour = int(m.group(1))
            minute = int(m.group(2) or "00")
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                analysis.service_time = f"{hour:02d}:{minute:02d}"
                break

    # Never convert vague dayparts to an exact time.
    if re.search(r"\b(pagi|siang|sore|malam)\b", lower) and not any(
        re.search(p, lower) for p in time_patterns
    ):
        analysis.service_time = None

    # --- FULFILLMENT ---
    if any(
        phrase in lower
        for phrase in ["onsite", "datang langsung", "datang ke rumah", "datang ke lokasi"]
    ):
        analysis.fulfillment = "onsite"

    # --- PROPERTY ---
    property_map = {
        "rumah": "Rumah",
        "apartemen": "Apartemen",
        "apartment": "Apartemen",
        "kantor": "Kantor",
        "ruko": "Ruko",
        "villa": "Villa",
    }
    for word, canonical in property_map.items():
        if re.search(rf"\b{re.escape(word)}\b", lower):
            analysis.property_type = canonical
            break

    m = re.search(r"\b(\d+)\s*lantai\b", lower)
    if m:
        analysis.property_detail = f"{m.group(1)} lantai"

    # --- ADDRESS ---
    address_patterns = [
        r"alamat lengkapnya\s+(.+?)(?:\.\s*catatan\s*:|$)",
        r"alamatnya\s+(.+?)(?:\.\s*catatan\s*:|$)",
        r"alamat\s+(.+?)(?:\.\s*catatan\s*:|$)",
    ]
    for pattern in address_patterns:
        m = re.search(pattern, message, flags=re.IGNORECASE | re.DOTALL)
        if m:
            addr = m.group(1).strip().rstrip(" .")
            if addr:
                analysis.address = addr
                break

    # --- NOTES ---
    m = re.search(r"catatan\s*:\s*(.+)$", message, flags=re.IGNORECASE | re.DOTALL)
    if m:
        note = m.group(1).strip().rstrip(" .")
        if note:
            analysis.special_notes = [note]

    # AI's missing_fields is never trusted for final status.
    analysis.missing_fields = []

    # Displayed completeness is calculated from the same required operational
    # fields used by business rules.
    has_service = bool(analysis.items) and all(
        canonical_item.service_name and canonical_item.quantity is not None
        for canonical_item in analysis.items
    )
    required_fields = [
        bool(analysis.customer_name),
        has_service,
        bool(analysis.service_date),
        bool(analysis.service_time),
        bool(analysis.property_type),
        bool(analysis.property_detail),
        analysis.fulfillment == "onsite",
        bool(analysis.address) if analysis.fulfillment == "onsite" else True,
    ]
    analysis.confidence = round(sum(required_fields) / len(required_fields), 2)
    return analysis

def analyze_order(
    message: str,
    api_key: str,
    service_catalog: dict,
    model_name: str = "gemini-3.6-flash",
    reference_date: str | None = None,
) -> OrderAnalysis:
    if not api_key:
        raise ValueError("GEMINI_API_KEY belum tersedia.")
    if not message.strip():
        raise ValueError("Pesan customer masih kosong.")

    reference_date = reference_date or date.today().isoformat()
    catalog_text = "\n".join(
        f"{name}|||{price}" for name, price in service_catalog.items()
    )

    return _analyze_cached(
        message.strip(),
        api_key,
        catalog_text,
        model_name.strip() or "gemini-3.6-flash",
        reference_date,
    )


def clear_analysis_cache():
    """Clear cached AI results when needed."""
    _analyze_cached.cache_clear()
    _get_client.cache_clear()
