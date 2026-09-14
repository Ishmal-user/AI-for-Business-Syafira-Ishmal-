import os
import urllib.parse
from datetime import date

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from ai_service import analyze_order
from business_rules import (
    calculate_pricing,
    deterministic_missing_fields,
    deterministic_risk_flags,
    order_status,
)

load_dotenv()

st.set_page_config(
    page_title="AI Smart Cleaning Service Assistant",
    page_icon="🧹",
    layout="wide",
)

# ============================================================
# CLEANING SERVICE BUSINESS CONFIGURATION
# ============================================================

SERVICE_CATALOG = {
    "Regular House Cleaning": 100000,
    "Deep Cleaning": 250000,
    "Bathroom Cleaning": 75000,
    "Kitchen Cleaning": 85000,
    "Sofa Cleaning": 120000,
    "Mattress Cleaning": 100000,
    "Carpet Cleaning": 90000,
    "Office Cleaning": 200000,
}

PROPERTY_TYPES = ["Rumah", "Apartemen", "Kantor", "Ruko", "Villa"]

SELLER_WHATSAPP = "6285276133655"
DEFAULT_CUSTOMER_WHATSAPP = "6281350876454"

# Exactly three demo cases required by the assignment:
# A = Complete, B = Missing, C = Ambiguous/Natural.
TEST_CASES = {
    # CASE A — COMPLETE:
    # Semua data operasional yang diminta untuk Cleaning Service disebutkan:
    # customer, layanan, jumlah, tanggal, jam, tipe properti,
    # detail properti, metode onsite, alamat lengkap, dan catatan.
    "Case A — Data Lengkap": (
        "Selamat siang Kak, saya Andi. Saya ingin pesan Deep Cleaning "
        "sebanyak 1 layanan untuk rumah 2 lantai. Mohon tim datang langsung "
        "(onsite) pada Sabtu, 19 September 2026 pukul 09:00. "
        "Alamat lengkapnya Jl. Melati No. 18, Kelurahan Suka Maju, "
        "Kecamatan Medan Johor, Kota Medan. Catatan: tolong fokuskan "
        "pembersihan pada kamar mandi dan dapur."
    ),

    # CASE B — MISSING:
    # Beberapa field penting sengaja tidak diberikan.
    "Case B — Data Belum Lengkap": (
        "Kak, saya mau pesan deep cleaning untuk rumah besok. "
        "Kira-kira bisa datang?"
    ),

    # CASE C — NATURAL / AMBIGUOUS:
    # Ditulis seperti chat customer sehari-hari, dengan informasi yang
    # sebagian masih samar sehingga sistem perlu meminta konfirmasi.
    "Case C — Chat Natural / Masih Samar": (
        "Kak, kalau Sabtu pagi rumah saya dibersihin bisa nggak? "
        "Rumahnya dua lantai, lokasinya kurang lebih daerah Sunggal. "
        "Jamnya fleksibel aja, nanti saya kabarin lagi ya."
    ),
}

if "orders" not in st.session_state:
    st.session_state.orders = []

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "raw_message" not in st.session_state:
    st.session_state.raw_message = ""


def rupiah(value):
    if value is None or pd.isna(value):
        return "-"
    return f"Rp{value:,.0f}".replace(",", ".")


def build_whatsapp_url(phone: str, message: str) -> str:
    clean_phone = (
        phone.replace("+", "")
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )
    if clean_phone.startswith("08"):
        clean_phone = "62" + clean_phone[1:]
    return f"https://wa.me/{clean_phone}?text={urllib.parse.quote(message)}"


st.title("🧹 AI Smart Cleaning Service Assistant")
st.caption(
    "Customer Chat → app.py → Gemini AI → Structured Order → "
    "Business Rules → WhatsApp → Order Dashboard"
)

with st.sidebar:
    st.header("⚙️ Setup")

    api_key = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Gunakan .env. Jangan upload .env atau API key ke GitHub.",
    )

    model_name = st.text_input(
        "Gemini Model",
        value=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
    )

    reference_date = st.date_input(
        "Reference date",
        value=date.today(),
    )

    st.caption(
        "Dipakai AI untuk memahami kata seperti besok, lusa, dan nama hari."
    )

    st.divider()
    st.subheader("🧹 Service Catalog")
    catalog_df = pd.DataFrame(
        [
            {"Layanan": name, "Harga": rupiah(price)}
            for name, price in SERVICE_CATALOG.items()
        ]
    )
    st.dataframe(catalog_df, hide_index=True, use_container_width=True)

    st.divider()
    st.subheader("⚡ Performance")
    st.caption(
        "Client Gemini dipakai ulang dan hasil chat yang sama di-cache. "
        "Case yang sudah pernah diuji akan tampil jauh lebih cepat."
    )
    if st.button("🧹 Clear AI Cache", use_container_width=True):
        from ai_service import clear_analysis_cache
        clear_analysis_cache()
        st.success("Cache AI dibersihkan.")

    st.divider()
    st.subheader("📲 WhatsApp")
    st.write("Nomor Seller / UMKM")
    st.code(SELLER_WHATSAPP)

tab1, tab2, tab3 = st.tabs(
    ["💬 Analyze Order", "📊 Order Dashboard", "🧠 AI vs Business Rules"]
)

# ============================================================
# TAB 1 — ANALYZE ORDER
# ============================================================

with tab1:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("1. Customer Chat")

        sample_name = st.selectbox(
            "Pilih salah satu dari 3 skenario pengujian",
            list(TEST_CASES.keys()),
        )

        if st.button("📋 Gunakan Test Case", use_container_width=True):
            st.session_state.raw_message = TEST_CASES[sample_name]
            st.rerun()

        message = st.text_area(
            "Paste chat WhatsApp / Instagram customer",
            value=st.session_state.raw_message,
            height=220,
            placeholder=(
                "Contoh: Kak, besok jam 10 mau cleaning rumah 2 lantai "
                "di Jalan Setia Budi..."
            ),
        )

        analyze_clicked = st.button(
            "✨ Analyze with Gemini AI",
            type="primary",
            use_container_width=True,
        )

        if analyze_clicked:
            if not message.strip():
                st.warning("Silakan masukkan chat customer terlebih dahulu.")
            elif not api_key:
                st.error("Isi Gemini API Key di sidebar atau file .env.")
            else:
                try:
                    with st.spinner("⚡ Memproses chat dengan Gemini..."):
                        st.session_state.analysis = analyze_order(
                            message=message,
                            api_key=api_key,
                            service_catalog=SERVICE_CATALOG,
                            model_name=model_name,
                            reference_date=reference_date.isoformat(),
                        )
                        st.session_state.raw_message = message

                    st.success("✅ Analisis AI selesai.")
                except Exception as e:
                    st.error(f"Gagal menganalisis order: {e}")

    with right:
        st.subheader("2. Result: AI → Business Rules")
        analysis = st.session_state.analysis

        if analysis is None:
            st.info(
                "Pilih test case atau masukkan chat, lalu klik "
                "**Analyze with Gemini AI**."
            )
        else:
            status = order_status(analysis, SERVICE_CATALOG)
            missing = deterministic_missing_fields(
                analysis, SERVICE_CATALOG
            )
            risk_flags = deterministic_risk_flags(
                analysis, SERVICE_CATALOG
            )

            if status == "READY":
                st.success("✅ ORDER READY")
            else:
                st.warning("⚠️ NEEDS CONFIRMATION")

            # Business Rules is the source of truth for completeness/status.
            required_missing = len(missing)
            total_required = 8
            completeness = max(0, round((total_required - required_missing) / total_required, 2))

            c1, c2, c3 = st.columns(3)
            c1.metric("Data Completeness", f"{completeness:.0%}")
            c2.metric("Tanggal", analysis.service_date or "-")
            c3.metric("Status", status)

            st.markdown("### 📋 Structured Information")

            info_df = pd.DataFrame(
                [
                    ["Customer", analysis.customer_name or "-"],
                    ["Tanggal", analysis.service_date or "-"],
                    ["Jam", analysis.service_time or "-"],
                    ["Tipe Properti", analysis.property_type or "-"],
                    ["Detail Properti", analysis.property_detail or "-"],
                    ["Alamat", analysis.address or "-"],
                    ["Metode", analysis.fulfillment],
                ],
                columns=["Field", "Value"],
            )
            st.dataframe(
                info_df,
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("### 🧹 Layanan & Pricing")

            price_rows, grand_total = calculate_pricing(
                analysis, SERVICE_CATALOG
            )

            if price_rows:
                price_df = pd.DataFrame(price_rows)
                price_df["Harga Satuan"] = price_df["Harga Satuan"].apply(rupiah)
                price_df["Subtotal"] = price_df["Subtotal"].apply(rupiah)
                st.dataframe(
                    price_df,
                    use_container_width=True,
                    hide_index=True,
                )

                incomplete_quantity = any(
                    row["Qty"] == "-" for row in price_rows
                )
                if incomplete_quantity:
                    st.info(
                        "💰 Harga satuan sudah ditemukan dari Service Catalog. "
                        "Subtotal dan total menunggu jumlah layanan."
                    )
                elif any(row["Harga Satuan"] is None for row in price_rows):
                    st.info(
                        "Data layanan belum cocok dengan Service Catalog."
                    )
                else:
                    st.success("💰 Harga berhasil dihitung oleh Business Rules.")
                    st.metric("Calculated Total", rupiah(grand_total))
            else:
                st.info("Belum ada layanan yang dapat dihitung.")

            if missing:
                st.markdown("### 🔎 Missing / Need Confirmation")
                for item in missing:
                    st.write(f"• {item}")
            else:
                st.success("Semua field wajib terpenuhi.")

            if risk_flags:
                st.markdown("### 🚩 Risk Flags")
                for flag in risk_flags:
                    st.write(f"• {flag}")

            if analysis.special_notes:
                st.markdown("### 📝 Catatan")
                for note in analysis.special_notes:
                    st.write(f"• {note}")

            st.markdown("### 🧾 AI Summary")
            st.info(analysis.order_summary or "-")

            st.markdown("### 💬 AI Follow-up")
            st.code(analysis.follow_up_message or "-", language=None)

            # ====================================================
            # WHATSAPP
            # ====================================================

            st.divider()
            st.markdown("## 📲 WhatsApp Customer")

            customer_whatsapp = st.text_input(
                "Nomor WhatsApp Customer",
                value=DEFAULT_CUSTOMER_WHATSAPP,
                key="customer_whatsapp",
                placeholder="Contoh: 081234567890",
            )

            product_lines = []
            for item in analysis.items:
                qty = item.quantity if item.quantity is not None else "?"
                line = f"• {item.service_name} x {qty}"
                if item.item_note:
                    line += f"\n  📝 {item.item_note}"
                product_lines.append(line)

            product_text = "\n".join(product_lines) or "-"

            if status == "READY":
                whatsapp_message = (
                    f"Halo Kak{' ' + analysis.customer_name if analysis.customer_name else ''} 😊\n\n"
                    "Pesanan cleaning service sudah kami catat:\n\n"
                    f"{product_text}\n\n"
                    f"📅 Tanggal: {analysis.service_date}\n"
                    f"🕒 Jam: {analysis.service_time}\n"
                    f"🏠 Tipe properti: {analysis.property_type}\n"
                    f"📍 Alamat: {analysis.address}\n"
                    f"💰 Total: {rupiah(grand_total)}\n\n"
                    "Apakah detail pesanan sudah benar, Kak? 😊"
                )
            else:
                fields = ", ".join(missing)
                whatsapp_message = (
                    f"Halo Kak{' ' + analysis.customer_name if analysis.customer_name else ''} 😊\n\n"
                    "Terima kasih. Kami masih perlu konfirmasi beberapa detail "
                    "sebelum pesanan bisa diproses:\n"
                    f"• {fields}\n\n"
                    "Boleh dikirim detailnya ya, Kak. Terima kasih 🙏"
                )

            st.text_area(
                "Draft pesan WhatsApp",
                value=whatsapp_message,
                height=180,
            )

            st.link_button(
                "📲 Buka WhatsApp Customer",
                build_whatsapp_url(customer_whatsapp, whatsapp_message),
                use_container_width=True,
            )

            # ====================================================
            # SAVE TO DASHBOARD
            # ====================================================

            st.divider()

            if st.button(
                "💾 Save to Order Dashboard",
                use_container_width=True,
                disabled=status != "READY",
            ):
                st.session_state.orders.append(
                    {
                        "Customer": analysis.customer_name or "-",
                        "Layanan": ", ".join(
                            item.service_name for item in analysis.items
                        ),
                        "Tanggal": analysis.service_date or "-",
                        "Jam": analysis.service_time or "-",
                        "Properti": analysis.property_type or "-",
                        "Alamat": analysis.address or "-",
                        "Status": status,
                        "Total": grand_total,
                    }
                )
                st.success(
                    "Order berhasil disimpan ke dashboard session."
                )

# ============================================================
# TAB 2 — DASHBOARD
# ============================================================

with tab2:
    st.subheader("📊 Order Dashboard")

    if not st.session_state.orders:
        st.info(
            "Belum ada order tersimpan. Jalankan Case A sampai READY "
            "lalu tekan Save to Order Dashboard."
        )
    else:
        dashboard_df = pd.DataFrame(st.session_state.orders)
        st.dataframe(
            dashboard_df.assign(
                Total=dashboard_df["Total"].apply(rupiah)
            ),
            use_container_width=True,
            hide_index=True,
        )

        total_orders = len(st.session_state.orders)
        total_revenue = sum(
            row["Total"] for row in st.session_state.orders
        )

        c1, c2 = st.columns(2)
        c1.metric("Jumlah Order", total_orders)
        c2.metric("Potensi Revenue", rupiah(total_revenue))

        csv_data = dashboard_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Dashboard CSV",
            data=csv_data,
            file_name="cleaning_service_orders.csv",
            mime="text/csv",
        )

# ============================================================
# TAB 3 — AI VS BUSINESS RULES
# ============================================================

with tab3:
    st.subheader("🧠 AI vs Business Rules")

    comparison = pd.DataFrame(
        [
            ["Memahami chat natural language", "AI / Gemini"],
            ["Mengenali layanan dan jumlah", "AI / Gemini"],
            ["Memahami kata relatif seperti 'besok'", "AI / Gemini"],
            ["Mendeteksi bahasa ambigu", "AI / Gemini"],
            ["Mengambil harga dari katalog", "Python / Business Rules"],
            ["Menghitung subtotal dan total", "Python / Business Rules"],
            ["Memastikan tanggal dan jam pasti", "Python / Business Rules"],
            ["Memastikan tipe properti", "Python / Business Rules"],
            ["Memastikan alamat onsite", "Python / Business Rules"],
            ["Menentukan READY / NEEDS CONFIRMATION", "Python / Business Rules"],
        ],
        columns=["Pekerjaan", "Penanggung Jawab"],
    )
    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "**AI understands. The system controls.** "
        "Gemini membantu memahami bahasa customer; Python menjaga "
        "keputusan bisnis yang harus konsisten."
    )

    st.markdown("### Minimal 3 Business Rules yang Berbeda dari Bakery")
    rules = [
        "1. Layanan harus cocok dengan katalog cleaning dan memiliki jumlah yang jelas.",
        "2. Layanan onsite wajib memiliki alamat.",
        "3. Tipe properti wajib diketahui dan harus termasuk Rumah/Apartemen/Kantor/Ruko/Villa.",
        "4. Tanggal dan jam harus pasti; 'pagi/sore' tanpa jam tidak dianggap lengkap.",
    ]
    for rule in rules:
        st.write(rule)

    st.markdown("### 🔬 Tiga Skenario Pengujian")
    test_df = pd.DataFrame(
        [
            ["A", "Data Lengkap", "Semua informasi operasional tersedia; targetnya READY."],
            ["B", "Data Belum Lengkap", "Field wajib yang hilang harus terdeteksi."],
            ["C", "Chat Natural / Masih Samar", "Sistem harus memisahkan informasi pasti dan yang perlu dikonfirmasi."],
        ],
        columns=["Case", "Jenis", "Yang Dilihat"],
    )
    st.dataframe(test_df, hide_index=True, use_container_width=True)

    st.caption(
        "Catat hasil aktual testing di assignment.md setelah menjalankan "
        "ketiga case. Jangan mengarang hasil yang belum diuji."
    )
