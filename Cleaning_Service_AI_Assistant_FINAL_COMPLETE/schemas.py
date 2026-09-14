from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class CleaningItem(BaseModel):
    """One cleaning service extracted from the customer chat."""

    service_name: str = Field(
        description="Nama layanan cleaning; gunakan nama canonical dari katalog jika cocok."
    )
    quantity: Optional[int] = Field(
        default=None,
        ge=1,
        description="Jumlah layanan jika benar-benar disebut customer."
    )
    item_note: Optional[str] = Field(
        default=None,
        description="Catatan khusus untuk layanan ini jika disebut."
    )


class OrderAnalysis(BaseModel):
    """Structured order produced by Gemini."""

    customer_name: Optional[str] = None

    items: List[CleaningItem] = Field(
        default_factory=list,
        description="Daftar layanan cleaning yang diminta customer."
    )

    service_date: Optional[str] = Field(
        default=None,
        description="Tanggal layanan dalam format YYYY-MM-DD jika pasti."
    )
    service_time: Optional[str] = Field(
        default=None,
        description="Jam layanan dalam format HH:MM jika pasti; jangan isi untuk 'pagi/sore' tanpa jam."
    )

    property_type: Optional[str] = Field(
        default=None,
        description="Tipe properti seperti Rumah, Apartemen, Kantor, Ruko, atau Villa jika disebut."
    )
    property_detail: Optional[str] = Field(
        default=None,
        description="Detail properti seperti 2 lantai, luas area, atau lantai tertentu jika disebut."
    )
    address: Optional[str] = Field(
        default=None,
        description="Alamat lokasi cleaning jika disebut customer."
    )

    fulfillment: Literal["onsite", "unknown"] = Field(
        default="unknown",
        description="Cleaning service pada demo ini dilakukan onsite; unknown jika metode belum jelas."
    )

    special_notes: List[str] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)

    order_summary: str = Field(default="")
    follow_up_message: str = Field(default="")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
