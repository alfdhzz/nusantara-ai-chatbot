# ============================================================
#  NUSANTARA.AI - Asisten Wisata Pintar
#  Modern Streamlit chat interface
# ============================================================
import html
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

APP_NAME = "Nusantara.ai"
MODEL_NAME = "gemini-2.5-flash"

st.set_page_config(
    page_title=f"{APP_NAME} - Asisten Wisata Pintar",
    page_icon="logo.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------
# Session state
# ------------------------------------------------------------
defaults = {
    "messages": [],
    "quick_prompt": None,
    "total": 0,
    "persona": "formal",
    "language": "id",
    "theme": "dark",
    "active_page": "home",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ------------------------------------------------------------
# Content
# ------------------------------------------------------------
hour = datetime.now().hour
if hour < 11:
    greeting = "Selamat pagi"
elif hour < 15:
    greeting = "Selamat siang"
elif hour < 18:
    greeting = "Selamat sore"
else:
    greeting = "Selamat malam"

PERSONAS = {
    "formal": {
        "label": "Pemandu profesional",
        "system": (
            "Anda adalah Nusa, pemandu wisata profesional Indonesia. "
            "Gunakan gaya formal, sapaan yang sopan, dan informasi terstruktur. "
            "Fokus pada destinasi wisata, kuliner lokal, itinerary, transportasi, "
            "akomodasi, dan budaya Indonesia. Jika pertanyaan di luar topik, "
            "arahkan kembali dengan sopan."
        ),
    },
    "casual": {
        "label": "Teman trip santai",
        "system": (
            "Kamu adalah Nusa, teman wisata yang santai, hangat, dan praktis. "
            "Gunakan gaya kasual, rekomendasi yang konkret, dan tetap mudah diikuti. "
            "Fokus pada destinasi, kuliner, hidden gems, itinerary, transportasi, "
            "akomodasi, dan budaya Indonesia. Jika ditanya di luar wisata Indonesia, "
            "ajak kembali ke topik dengan ramah."
        ),
    },
}

if "persona_sel" in st.session_state and st.session_state.persona_sel in PERSONAS:
    st.session_state.persona = st.session_state.persona_sel

LANGUAGES = {
    "id": {"label": "Bahasa Indonesia", "short": "ID"},
    "en": {"label": "English", "short": "EN"},
}

if "language_sel" in st.session_state and st.session_state.language_sel in LANGUAGES:
    st.session_state.language = st.session_state.language_sel
if st.session_state.language not in LANGUAGES:
    st.session_state.language = "id"

GREETINGS = {
    "id": greeting,
    "en": "Good morning" if hour < 11 else "Good afternoon" if hour < 18 else "Good evening",
}

PERSONA_LABELS = {
    "id": {
        "formal": "Pemandu profesional",
        "casual": "Teman trip santai",
    },
    "en": {
        "formal": "Professional guide",
        "casual": "Casual trip buddy",
    },
}

UI_TEXT = {
    "id": {
        "brand_tagline": "Asisten wisata Indonesia",
        "new_chat": "Chat baru",
        "light_mode": "Mode terang",
        "dark_mode": "Mode gelap",
        "summary": "Ringkasan",
        "messages": "Pesan",
        "mode": "Mode",
        "website_language": "Bahasa",
        "navigation": "Navigasi",
        "session_history": "Riwayat sesi",
        "empty_history": "Belum ada percakapan. Mulai dari prompt cepat atau tulis pertanyaan di bawah.",
        "local_time": "Waktu lokal",
        "answer_style": "Gaya jawaban",
        "active_menu": "Menu aktif",
        "total_messages": "Total pesan",
        "assistant_persona": "Persona asisten",
        "website_language_field": "Bahasa website",
        "gemini_api_key": "Gemini API key",
        "api_key_active": "API key aktif dari file .env. Input manual disembunyikan untuk menjaga tampilan tetap bersih.",
        "api_key_placeholder": "Tempel Gemini API key di sini...",
        "api_key_missing": "Masukkan Gemini API key agar Nusa bisa menjawab. Simpan sebagai GEMINI_API_KEY di file .env agar tidak perlu mengisi ulang.",
        "use_prompt": "Gunakan",
        "active_chat": "Percakapan aktif",
        "messages_in_session": "{count} pesan dalam sesi ini",
        "clear": "Bersihkan",
        "chat_placeholder": "Tanyakan destinasi, kuliner, itinerary, budget, atau tips liburan...",
        "spinner": "Nusa sedang menyusun jawaban...",
        "api_error": "Masukkan Gemini API key terlebih dahulu.",
        "invalid_key": "API key tidak valid. Periksa kembali key Gemini yang digunakan.",
        "quota": "Quota API habis. Coba lagi nanti atau gunakan key lain.",
        "generic_error": "Terjadi error",
        "fine_print": "AI dapat membuat kesalahan. Verifikasi informasi penting sebelum merencanakan perjalanan.",
    },
    "en": {
        "brand_tagline": "Indonesia travel assistant",
        "new_chat": "New chat",
        "light_mode": "Light mode",
        "dark_mode": "Dark mode",
        "summary": "Summary",
        "messages": "Messages",
        "mode": "Mode",
        "website_language": "Language",
        "navigation": "Navigation",
        "session_history": "Session history",
        "empty_history": "No conversation yet. Start from a quick prompt or ask a question below.",
        "local_time": "Local time",
        "answer_style": "Answer style",
        "active_menu": "Active menu",
        "total_messages": "Total messages",
        "assistant_persona": "Assistant persona",
        "website_language_field": "Website language",
        "gemini_api_key": "Gemini API key",
        "api_key_active": "API key is active from the .env file. Manual input is hidden to keep the interface clean.",
        "api_key_placeholder": "Paste your Gemini API key here...",
        "api_key_missing": "Enter a Gemini API key so Nusa can answer. Save it as GEMINI_API_KEY in the .env file to avoid entering it again.",
        "use_prompt": "Use prompt",
        "active_chat": "Active conversation",
        "messages_in_session": "{count} messages in this session",
        "clear": "Clear",
        "chat_placeholder": "Ask about destinations, food, itineraries, budget, or travel tips...",
        "spinner": "Nusa is preparing your answer...",
        "api_error": "Please enter your Gemini API key first.",
        "invalid_key": "The API key is invalid. Please check your Gemini key.",
        "quota": "API quota has run out. Try again later or use another key.",
        "generic_error": "An error occurred",
        "fine_print": "AI can make mistakes. Verify important information before planning your trip.",
    },
}

NAV_ITEMS_BY_LANG = {
    "id": [
        {"key": "home", "label": "Beranda chat", "tag": "Live"},
        {"key": "destinations", "label": "Destinasi", "tag": "Guide"},
        {"key": "itinerary", "label": "Itinerary", "tag": "Plan"},
        {"key": "budget", "label": "Budget trip", "tag": "Tips"},
    ],
    "en": [
        {"key": "home", "label": "Chat home", "tag": "Live"},
        {"key": "destinations", "label": "Destinations", "tag": "Guide"},
        {"key": "itinerary", "label": "Itinerary", "tag": "Plan"},
        {"key": "budget", "label": "Trip budget", "tag": "Tips"},
    ],
}

PAGE_CONTENT_BY_LANG = {
    "id": {
        "home": {
            "title": "Rencanakan trip Indonesia dengan lebih rapi.",
            "subtitle": (
                f"{APP_NAME} membantu menyusun destinasi, kuliner, itinerary, transportasi, "
                "dan tips perjalanan lokal dalam format yang mudah dipakai."
            ),
            "panel_title": f"{GREETINGS['id']}, mau mulai dari mana?",
            "panel_subtitle": (
                "Pilih salah satu prompt cepat atau langsung tulis kebutuhan trip kamu. "
                "Nusa bisa membantu membuat rencana yang realistis, runtut, dan sesuai gaya perjalanan."
            ),
            "prompt_label": "Prompt cepat",
            "prompts": [
                {
                    "title": "Kuliner Jogja",
                    "desc": "Tempat makan legendaris dan rute kuliner satu hari.",
                    "prompt": "Rekomendasikan kuliner legendaris wajib coba di Yogyakarta lengkap dengan area dan waktu terbaik.",
                },
                {
                    "title": "Hidden gems Bali",
                    "desc": "Spot tenang, scenic, dan tidak terlalu ramai.",
                    "prompt": "Apa saja hidden gems di Bali yang jarang diketahui wisatawan? Sertakan tips akses dan waktu kunjungan.",
                },
                {
                    "title": "Itinerary Bandung",
                    "desc": "Rencana 2 hari 1 malam yang padat tapi nyaman.",
                    "prompt": "Buatkan itinerary 2 hari 1 malam di Bandung dengan kuliner, wisata alam, dan estimasi waktu.",
                },
                {
                    "title": "Labuan Bajo",
                    "desc": "Panduan 3 hari 2 malam untuk pemula.",
                    "prompt": "Buat itinerary 3 hari 2 malam di Labuan Bajo untuk pemula, termasuk aktivitas, transportasi, dan tips biaya.",
                },
            ],
        },
        "destinations": {
            "title": "Temukan destinasi yang paling cocok.",
            "subtitle": (
                "Bandingkan pilihan tempat berdasarkan suasana, akses, waktu terbaik, "
                "dan gaya liburan yang kamu inginkan."
            ),
            "panel_title": "Pusat rekomendasi destinasi",
            "panel_subtitle": (
                "Gunakan menu ini untuk mencari pantai, gunung, kota budaya, hidden gems, "
                "atau destinasi ramah keluarga di Indonesia."
            ),
            "prompt_label": "Prompt destinasi",
            "prompts": [
                {
                    "title": "Trip alam tenang",
                    "desc": "Destinasi alam yang tidak terlalu ramai untuk healing.",
                    "prompt": "Rekomendasikan destinasi alam Indonesia yang tenang, tidak terlalu ramai, dan cocok untuk healing 3 hari.",
                },
                {
                    "title": "Wisata keluarga",
                    "desc": "Tempat nyaman untuk anak, orang tua, dan rombongan.",
                    "prompt": "Rekomendasikan destinasi wisata keluarga di Indonesia yang aman, nyaman, dan aksesnya mudah.",
                },
                {
                    "title": "Kota budaya",
                    "desc": "Kota dengan sejarah, museum, kuliner, dan tradisi lokal.",
                    "prompt": "Bandingkan kota budaya terbaik di Indonesia untuk liburan 3 hari, lengkap dengan aktivitas utama.",
                },
                {
                    "title": "Pantai alternatif",
                    "desc": "Pantai cantik selain destinasi mainstream.",
                    "prompt": "Berikan rekomendasi pantai cantik di Indonesia selain Bali dan Lombok, lengkap dengan tips akses.",
                },
            ],
        },
        "itinerary": {
            "title": "Susun itinerary yang realistis.",
            "subtitle": (
                "Buat rencana perjalanan harian dengan urutan tempat, estimasi waktu, "
                "transportasi, dan jeda istirahat yang masuk akal."
            ),
            "panel_title": "Generator itinerary",
            "panel_subtitle": (
                "Pilih template itinerary, lalu Nusa akan menyusun rencana perjalanan yang runtut "
                "dan mudah diikuti."
            ),
            "prompt_label": "Prompt itinerary",
            "prompts": [
                {
                    "title": "2 hari 1 malam",
                    "desc": "Rencana singkat untuk weekend getaway.",
                    "prompt": "Buatkan itinerary 2 hari 1 malam di kota wisata Indonesia yang cocok untuk weekend getaway.",
                },
                {
                    "title": "3 hari hemat",
                    "desc": "Itinerary murah tapi tetap nyaman.",
                    "prompt": "Buatkan itinerary 3 hari 2 malam yang hemat di Yogyakarta, termasuk kuliner, transportasi, dan estimasi biaya.",
                },
                {
                    "title": "Trip pasangan",
                    "desc": "Agenda santai, scenic, dan tidak terlalu padat.",
                    "prompt": "Buat itinerary liburan pasangan 3 hari 2 malam di Indonesia dengan suasana romantis dan tempo santai.",
                },
                {
                    "title": "Backpacker",
                    "desc": "Rute efisien dengan transportasi umum.",
                    "prompt": "Buat itinerary backpacker 4 hari di Indonesia dengan transportasi umum dan budget terbatas.",
                },
            ],
        },
        "budget": {
            "title": "Perkirakan budget sebelum berangkat.",
            "subtitle": (
                "Pecah biaya transportasi, makan, tiket masuk, akomodasi, dan cadangan "
                "agar rencana liburan lebih terkendali."
            ),
            "panel_title": "Budget planner",
            "panel_subtitle": (
                "Pakai menu ini untuk membuat estimasi biaya, versi hemat, atau perbandingan "
                "budget beberapa destinasi."
            ),
            "prompt_label": "Prompt budget",
            "prompts": [
                {
                    "title": "Budget hemat",
                    "desc": "Estimasi biaya liburan murah per kategori.",
                    "prompt": "Buat estimasi budget hemat untuk liburan 3 hari 2 malam di Bandung untuk 2 orang.",
                },
                {
                    "title": "Bandingkan biaya",
                    "desc": "Komparasi budget antar destinasi.",
                    "prompt": "Bandingkan estimasi biaya liburan 3 hari ke Bali, Lombok, dan Yogyakarta untuk traveler pemula.",
                },
                {
                    "title": "Rincian harian",
                    "desc": "Breakdown biaya makan, tiket, transportasi, dan hotel.",
                    "prompt": "Buat rincian budget harian liburan ke Labuan Bajo 3 hari 2 malam untuk satu orang.",
                },
                {
                    "title": "Tips menekan biaya",
                    "desc": "Cara hemat tanpa mengorbankan kenyamanan.",
                    "prompt": "Berikan tips menekan biaya liburan di Indonesia tanpa mengorbankan kenyamanan dan keamanan.",
                },
            ],
        },
    },
    "en": {
        "home": {
            "title": "Plan your Indonesia trip with more clarity.",
            "subtitle": (
                f"{APP_NAME} helps organize destinations, local food, itineraries, transportation, "
                "and travel tips in a format that is easy to use."
            ),
            "panel_title": f"{GREETINGS['en']}, where should we start?",
            "panel_subtitle": (
                "Choose a quick prompt or type your travel needs directly. "
                "Nusa can help create a realistic plan that matches your travel style."
            ),
            "prompt_label": "Quick prompts",
            "prompts": [
                {
                    "title": "Jogja food",
                    "desc": "Legendary food spots and a one-day culinary route.",
                    "prompt": "Recommend must-try legendary food in Yogyakarta, including areas and the best time to visit.",
                },
                {
                    "title": "Bali hidden gems",
                    "desc": "Quiet scenic spots away from the busiest crowds.",
                    "prompt": "What hidden gems in Bali are less known by tourists? Include access tips and the best time to visit.",
                },
                {
                    "title": "Bandung itinerary",
                    "desc": "A packed but comfortable 2-day, 1-night plan.",
                    "prompt": "Create a 2-day, 1-night Bandung itinerary with food, nature spots, and estimated timing.",
                },
                {
                    "title": "Labuan Bajo",
                    "desc": "A beginner-friendly 3-day, 2-night guide.",
                    "prompt": "Create a beginner-friendly 3-day, 2-night Labuan Bajo itinerary with activities, transport, and budget tips.",
                },
            ],
        },
        "destinations": {
            "title": "Find the destination that fits best.",
            "subtitle": (
                "Compare places by atmosphere, access, best season, and the type of trip "
                "you want to take."
            ),
            "panel_title": "Destination recommendation hub",
            "panel_subtitle": (
                "Use this section to explore beaches, mountains, culture cities, hidden gems, "
                "or family-friendly destinations in Indonesia."
            ),
            "prompt_label": "Destination prompts",
            "prompts": [
                {
                    "title": "Quiet nature trip",
                    "desc": "Less crowded nature destinations for a calm getaway.",
                    "prompt": "Recommend quiet nature destinations in Indonesia that are not too crowded and suitable for a 3-day healing trip.",
                },
                {
                    "title": "Family travel",
                    "desc": "Comfortable places for children, parents, and groups.",
                    "prompt": "Recommend family-friendly destinations in Indonesia that are safe, comfortable, and easy to access.",
                },
                {
                    "title": "Culture cities",
                    "desc": "Cities with history, museums, food, and local traditions.",
                    "prompt": "Compare the best culture cities in Indonesia for a 3-day trip, including the main activities.",
                },
                {
                    "title": "Alternative beaches",
                    "desc": "Beautiful beaches beyond the mainstream choices.",
                    "prompt": "Recommend beautiful beaches in Indonesia outside Bali and Lombok, including access tips.",
                },
            ],
        },
        "itinerary": {
            "title": "Build an itinerary that makes sense.",
            "subtitle": (
                "Create a day-by-day travel plan with place order, timing, transport, "
                "and realistic breaks."
            ),
            "panel_title": "Itinerary generator",
            "panel_subtitle": (
                "Pick an itinerary template and Nusa will turn it into a clear, practical travel plan."
            ),
            "prompt_label": "Itinerary prompts",
            "prompts": [
                {
                    "title": "2 days 1 night",
                    "desc": "A short plan for a weekend getaway.",
                    "prompt": "Create a 2-day, 1-night itinerary in an Indonesian travel city suitable for a weekend getaway.",
                },
                {
                    "title": "3-day budget trip",
                    "desc": "A low-cost itinerary that still feels comfortable.",
                    "prompt": "Create a budget-friendly 3-day, 2-night itinerary in Yogyakarta, including food, transportation, and estimated costs.",
                },
                {
                    "title": "Couple trip",
                    "desc": "Relaxed, scenic, and not too packed.",
                    "prompt": "Create a 3-day, 2-night couple trip itinerary in Indonesia with a romantic atmosphere and a relaxed pace.",
                },
                {
                    "title": "Backpacker route",
                    "desc": "Efficient route using public transport.",
                    "prompt": "Create a 4-day backpacker itinerary in Indonesia using public transport and a limited budget.",
                },
            ],
        },
        "budget": {
            "title": "Estimate the budget before you go.",
            "subtitle": (
                "Break down transportation, meals, tickets, accommodation, and backup funds "
                "so the trip is easier to control."
            ),
            "panel_title": "Budget planner",
            "panel_subtitle": (
                "Use this section to estimate costs, create a low-budget version, or compare "
                "several destinations."
            ),
            "prompt_label": "Budget prompts",
            "prompts": [
                {
                    "title": "Budget trip",
                    "desc": "Estimated low-cost trip expenses by category.",
                    "prompt": "Create a low-budget estimate for a 3-day, 2-night trip to Bandung for 2 people.",
                },
                {
                    "title": "Compare costs",
                    "desc": "Budget comparison across destinations.",
                    "prompt": "Compare estimated costs for a 3-day trip to Bali, Lombok, and Yogyakarta for beginner travelers.",
                },
                {
                    "title": "Daily breakdown",
                    "desc": "Meals, tickets, transport, and hotel costs.",
                    "prompt": "Create a daily budget breakdown for a 3-day, 2-night Labuan Bajo trip for one person.",
                },
                {
                    "title": "Saving tips",
                    "desc": "Spend less without sacrificing comfort.",
                    "prompt": "Give tips to reduce travel costs in Indonesia without sacrificing comfort and safety.",
                },
            ],
        },
    },
}

if st.session_state.active_page not in PAGE_CONTENT_BY_LANG["id"]:
    st.session_state.active_page = "home"


# ------------------------------------------------------------
# Theme tokens
# ------------------------------------------------------------
is_dark = st.session_state.theme == "dark"
if is_dark:
    colors = {
        "BG": "#050505",
        "BG_SOFT": "#0A0A0A",
        "SURFACE": "#121212",
        "SURFACE_2": "#171717",
        "SIDEBAR": "#0A0A0A",
        "TEXT": "#FAFAFA",
        "MUTED": "#A1A1AA",
        "SUBTLE": "#71717A",
        "BORDER": "rgba(255, 255, 255, 0.08)",
        "BORDER_STRONG": "rgba(255, 255, 255, 0.15)",
        "INPUT": "rgba(255, 255, 255, 0.05)",
        "SHADOW": "rgba(0, 0, 0, 0.5)",
        "ACCENT": "#3B82F6",
        "ACCENT_2": "#60A5FA",
        "WARM": "#F59E0B",
        "DANGER": "#EF4444",
        "USER_TEXT": "#FFFFFF",
        "CODE_BG": "#171717",
    }
else:
    colors = {
        "BG": "#F9FAFB",
        "BG_SOFT": "#F3F4F6",
        "SURFACE": "#FFFFFF",
        "SURFACE_2": "#F9FAFB",
        "SIDEBAR": "#FFFFFF",
        "TEXT": "#09090B",
        "MUTED": "#52525B",
        "SUBTLE": "#A1A1AA",
        "BORDER": "rgba(0, 0, 0, 0.06)",
        "BORDER_STRONG": "rgba(0, 0, 0, 0.12)",
        "INPUT": "rgba(0, 0, 0, 0.03)",
        "SHADOW": "rgba(0, 0, 0, 0.04)",
        "ACCENT": "#2563EB",
        "ACCENT_2": "#3B82F6",
        "WARM": "#D97706",
        "DANGER": "#DC2626",
        "USER_TEXT": "#FFFFFF",
        "CODE_BG": "#F3F4F6",
    }


def apply_theme() -> None:
    css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg: __BG__;
    --bg-soft: __BG_SOFT__;
    --surface: __SURFACE__;
    --surface-2: __SURFACE_2__;
    --sidebar: __SIDEBAR__;
    --text: __TEXT__;
    --muted: __MUTED__;
    --subtle: __SUBTLE__;
    --border: __BORDER__;
    --border-strong: __BORDER_STRONG__;
    --input: __INPUT__;
    --shadow: __SHADOW__;
    --accent: __ACCENT__;
    --accent-2: __ACCENT_2__;
    --warm: __WARM__;
    --danger: __DANGER__;
    --user-text: __USER_TEXT__;
    --code-bg: __CODE_BG__;
}

*, *::before, *::after { box-sizing: border-box; }

/* Force main backgrounds */
html, body, .stApp, 
[data-testid="stAppViewContainer"], 
[data-testid="stMain"], 
[data-testid="stMainBlockContainer"] {
    background: var(--bg) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* Hide Streamlit Native Header */
[data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stToolbar"], 
[data-testid="stSidebarHeader"], [data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] {
    display: none !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--sidebar) !important;
    background-color: var(--sidebar) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 280px !important;
    max-width: 280px !important;
}
[data-testid="stSidebarContent"] {
    background: var(--sidebar) !important;
    background-color: var(--sidebar) !important;
    padding: 0 !important;
}

/* Typography */
p, li, span, label, td, th, div { color: var(--text); }
h1, h2, h3, h4 { color: var(--text) !important; letter-spacing: -0.02em !important; font-weight: 700 !important; }
hr { border: 0 !important; border-top: 1px solid var(--border) !important; margin: 20px 0 !important; }
a { color: var(--accent) !important; text-decoration: none !important; }
code { background: var(--code-bg) !important; color: var(--text) !important; border: 1px solid var(--border) !important; border-radius: 6px !important; padding: 3px 6px !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 999px; }

/* BaseWeb / Selectbox Overrides for Native Dark Mode bleeding */
[data-baseweb="popover"], [data-baseweb="menu"], ul[role="listbox"] {
    background-color: var(--surface) !important;
    background: var(--surface) !important;
}
[data-baseweb="menu"] li, ul[role="listbox"] li {
    color: var(--text) !important;
    background-color: transparent !important;
}
[data-baseweb="menu"] li:hover, ul[role="listbox"] li:hover, [aria-selected="true"] {
    background-color: var(--bg-soft) !important;
    color: var(--accent) !important;
}
[data-testid="stSelectbox"] label, [data-testid="stTextInput"] label { display: none !important; }
[data-baseweb="select"] > div, [data-testid="stTextInput"] input {
    background: var(--surface) !important;
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    min-height: 44px !important;
    box-shadow: 0 2px 4px var(--shadow) !important;
}
[data-baseweb="select"] span, [data-baseweb="select"] svg, [data-testid="stTextInput"] input::placeholder { color: var(--muted) !important; }

/* App Specific Classes */
.sidebar-brand { padding: 28px 24px 20px; }
.brand-row { display: flex; align-items: center; gap: 14px; }
.brand-mark { width: 40px; height: 40px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.brand-name { font-size: 1.15rem; font-weight: 700; line-height: 1.2; color: var(--text) !important; letter-spacing: -0.02em; }
.brand-kicker { margin-top: 4px; color: var(--muted) !important; font-size: 0.8rem; }
.sidebar-section { padding: 8px 16px 12px; }
.sidebar-label { padding: 0 8px 8px; color: var(--subtle) !important; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.stat-card { border: 1px solid var(--border); background: var(--surface); border-radius: 10px; padding: 12px; }
.stat-value { color: var(--text) !important; font-size: 1rem; font-weight: 600; }
.stat-caption { color: var(--muted) !important; font-size: 0.75rem; margin-top: 4px; }
.side-link { display: flex; align-items: center; justify-content: space-between; gap: 10px; border-radius: 8px; padding: 10px 12px; color: var(--muted) !important; font-size: 0.9rem; font-weight: 500; border: 1px solid transparent; }
.history-item { padding: 8px 12px; border-radius: 8px; color: var(--muted) !important; font-size: 0.85rem; line-height: 1.4; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.history-item:hover { background: var(--bg-soft); color: var(--text) !important; }
.empty-history { border: 1px dashed var(--border-strong); color: var(--subtle) !important; border-radius: 10px; padding: 16px; font-size: 0.85rem; text-align: center; }
.sidebar-footer { padding: 16px 24px 24px; color: var(--subtle) !important; font-size: 0.75rem; }

.workspace-header { display: flex; flex-direction: row; align-items: flex-start; justify-content: space-between; gap: 24px; padding: 12px 0 24px; border-bottom: 1px solid var(--border); margin-bottom: 24px; width: 100%; }
.eyebrow { display: inline-flex; align-items: center; gap: 8px; color: var(--muted) !important; font-size: 0.85rem; font-weight: 500; margin-bottom: 8px; }
.status-light { width: 8px; height: 8px; border-radius: 999px; background: var(--accent); }
.workspace-title { margin: 0 0 8px 0 !important; font-size: 2.2rem !important; line-height: 1.2 !important; font-weight: 700 !important; color: var(--text) !important; }
.workspace-subtitle { max-width: 600px; color: var(--muted) !important; font-size: 1.05rem; line-height: 1.6; margin: 0; }
.header-meta { min-width: 240px; border-left: 1px solid var(--border); padding-left: 24px; display: flex; flex-direction: column; gap: 12px; }
.meta-line { display: flex; align-items: center; justify-content: space-between; gap: 16px; color: var(--muted) !important; font-size: 0.85rem; }
.meta-line strong { color: var(--text) !important; font-weight: 600; }
.field-label { margin: 0 0 8px; color: var(--muted) !important; font-size: 0.8rem; font-weight: 600; }

.home-panel { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 32px; margin-bottom: 32px; box-shadow: 0 4px 6px -1px var(--shadow); }
.home-title { margin: 0 0 12px; font-size: 1.8rem; line-height: 1.2; font-weight: 700; color: var(--text) !important; }
.home-subtitle { margin: 0; color: var(--muted) !important; font-size: 1.05rem; line-height: 1.6; }

.prompt-section-title { margin: 32px 0 16px; color: var(--subtle) !important; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
.prompt-card { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; min-height: 140px; padding: 20px; box-shadow: 0 2px 4px var(--shadow) !important; }
.prompt-title { color: var(--text) !important; font-size: 1.05rem; font-weight: 600; margin-bottom: 8px; }
.prompt-desc { color: var(--muted) !important; font-size: 0.9rem; line-height: 1.5; margin: 0; }

/* Buttons */
.stButton > button { 
    border-radius: 10px !important; 
    border: 1px solid var(--border-strong) !important; 
    background: var(--surface) !important; 
    background-color: var(--surface) !important; 
    color: var(--text) !important; 
    font-weight: 600 !important; 
    min-height: 40px !important; 
}
[data-testid="stBaseButton-primary"], 
[data-testid="baseButton-primary"], 
.stButton > button[kind="primary"],
.stButton > button[data-testid*="primary"] { 
    background: var(--accent) !important; 
    background-color: var(--accent) !important; 
    border: 0 !important; 
    color: #ffffff !important; 
    font-weight: 600 !important; 
}

/* Chat Output */
[data-testid="stChatMessage"] { background: transparent !important; padding: 12px 0 !important; }
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] { border: 1px solid var(--border); background: var(--surface); }
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] { background: var(--surface) !important; border: 1px solid var(--border); border-radius: 12px; padding: 16px 20px; }
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p { color: var(--text) !important; line-height: 1.6 !important; font-size: 0.95rem !important; margin-bottom: 0.8rem !important; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { display: flex !important; justify-content: flex-end !important; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stMarkdownContainer"] { background: var(--accent) !important; border: 0 !important; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stMarkdownContainer"] p { color: #ffffff !important; }

/* Bottom Chat Input Overrides for Native Dark Mode bleeding */
[data-testid="stBottom"], 
[data-testid="stBottom"] > div,
.stChatFloatingInputContainer,
div:has(> [data-testid="stChatInput"]),
div:has(> div > [data-testid="stChatInput"]) { 
    background: var(--bg) !important; 
    background-color: var(--bg) !important; 
    border-top: none !important;
}

[data-testid="stBottom"] {
    border-top: 1px solid var(--border) !important; 
    padding: 16px 0 !important; 
    z-index: 100; 
}

[data-testid="stBottomBlockContainer"] { 
    max-width: 1000px !important; 
    padding: 0 40px !important; 
    margin: 0 auto !important; 
    background: transparent !important;
    background-color: transparent !important;
}

[data-testid="stChatInput"] { 
    background: transparent !important; 
    background-color: transparent !important; 
}

[data-testid="stChatInput"] > div,
[data-testid="stChatInputContainer"], 
div[class*="chatInputContainer"] { 
    background: var(--surface) !important; 
    background-color: var(--surface) !important; 
    border: 1px solid var(--border) !important; 
    border-radius: 12px !important; 
    box-shadow: 0 4px 12px var(--shadow) !important; 
}

[data-testid="stChatInputTextArea"],
[data-testid="stChatInput"] textarea { 
    color: var(--text) !important; 
    font-size: 1rem !important; 
    padding: 16px 20px !important; 
    background: transparent !important; 
    background-color: transparent !important; 
    -webkit-text-fill-color: var(--text) !important;
}

[data-testid="stChatInputTextArea"]::placeholder,
[data-testid="stChatInput"] textarea::placeholder { 
    color: var(--muted) !important; 
    -webkit-text-fill-color: var(--muted) !important;
}

[data-testid="stChatInputSubmitButton"],
[data-testid="stChatInputSubmitButton"] > button,
[data-testid="stChatInput"] button { 
    background: var(--accent) !important; 
    background-color: var(--accent) !important; 
    color: #ffffff !important; 
    border-radius: 8px !important; 
    border: none !important; 
}

[data-testid="stChatInputSubmitButton"] svg,
[data-testid="stChatInput"] button svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}

.notice { border: 1px solid var(--border); background: var(--surface); color: var(--text) !important; border-radius: 10px; padding: 14px 16px; margin: 12px 0; font-size: 0.9rem; }
.fine-print { text-align: center; padding: 12px 0 0; color: var(--subtle) !important; font-size: 0.75rem; }
</style>
"""
    for key, value in colors.items():
        css = css.replace(f"__{key}__", value)
    st.markdown(css, unsafe_allow_html=True)


apply_theme()


def escaped_short_text(text: str, limit: int = 46) -> str:
    clipped = text.strip().replace("\n", " ")
    if len(clipped) > limit:
        clipped = f"{clipped[:limit - 3]}..."
    return html.escape(clipped)


def reset_chat() -> None:
    st.session_state.messages = []
    st.session_state.total = 0
    st.session_state.quick_prompt = None


def render_prompt_cards(
    prompts: list[dict[str, str]],
    label: str,
    key_prefix: str,
    button_label: str,
) -> None:
    st.markdown(
        f'<div class="prompt-section-title">{html.escape(label)}</div>',
        unsafe_allow_html=True,
    )
    prompt_cols = st.columns(4, gap="small")
    for index, (col, item) in enumerate(zip(prompt_cols, prompts)):
        with col:
            st.markdown(
                f"""
                <article class="prompt-card">
                    <div class="prompt-title">{html.escape(item["title"])}</div>
                    <p class="prompt-desc">{html.escape(item["desc"])}</p>
                </article>
                """,
                unsafe_allow_html=True,
            )
            if st.button(button_label, key=f"{key_prefix}_{index}", use_container_width=True):
                st.session_state.quick_prompt = item["prompt"]


ui = UI_TEXT[st.session_state.language]
persona_labels = PERSONA_LABELS[st.session_state.language]
nav_items = NAV_ITEMS_BY_LANG[st.session_state.language]
page_content = PAGE_CONTENT_BY_LANG[st.session_state.language]
active_language = LANGUAGES[st.session_state.language]


# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="brand-row">
                <div class="brand-mark">
                    <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect width="40" height="40" rx="10" fill="color-mix(in srgb, var(--accent) 15%, transparent)" />
                        <path d="M13 27V13L25 27V13" stroke="var(--accent)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="29" cy="27" r="3.5" fill="var(--warm)"/>
                    </svg>
                </div>
                <div>
                    <div class="brand-name">Nusantara.ai</div>
                    <div class="brand-kicker">{html.escape(ui["brand_tagline"])}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    if st.button(ui["new_chat"], use_container_width=True, type="primary"):
        reset_chat()
        st.rerun()

    theme_label = ui["light_mode"] if is_dark else ui["dark_mode"]
    if st.button(theme_label, use_container_width=True):
        st.session_state.theme = "light" if is_dark else "dark"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    st.markdown(
        f"""
        <div class="sidebar-section">
            <div class="sidebar-label">{html.escape(ui["summary"])}</div>
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-value">{len(st.session_state.messages)}</div>
                    <div class="stat-caption">{html.escape(ui["messages"])}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{html.escape(persona_labels[st.session_state.persona].split()[0])}</div>
                    <div class="stat-caption">{html.escape(ui["mode"])}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{active_language["short"]}</div>
                    <div class="stat-caption">{html.escape(ui["website_language"])}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-label">{html.escape(ui["navigation"])}</div>', unsafe_allow_html=True)
    for item in nav_items:
        is_active = item["key"] == st.session_state.active_page
        button_label = f'{item["label"]}  |  {item["tag"]}'
        if st.button(
            button_label,
            key=f'nav_{item["key"]}',
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.active_page = item["key"]
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    recent_messages = [m for m in st.session_state.messages if m["role"] == "user"]
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-label">{html.escape(ui["session_history"])}</div>', unsafe_allow_html=True)
    if recent_messages:
        for message in recent_messages[-6:][::-1]:
            st.markdown(
                f'<div class="history-item">{escaped_short_text(message["content"])}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f'<div class="empty-history">{html.escape(ui["empty_history"])}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="sidebar-footer">
            {APP_NAME} v3.0<br>
            Powered by {MODEL_NAME}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# Main layout
# ------------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY", "")
active_content = page_content[st.session_state.active_page]

st.markdown(
    f"""
    <div class="workspace-header">
        <div>
            <div class="eyebrow"><span class="status-light"></span>{MODEL_NAME} online</div>
            <h1 class="workspace-title">{html.escape(active_content["title"])}</h1>
            <p class="workspace-subtitle">{html.escape(active_content["subtitle"])}</p>
        </div>
        <div class="header-meta">
            <div class="meta-line"><span>{html.escape(ui["local_time"])}</span><strong>{datetime.now().strftime("%H:%M")}</strong></div>
            <div class="meta-line"><span>{html.escape(ui["answer_style"])}</span><strong>{html.escape(persona_labels[st.session_state.persona])}</strong></div>
            <div class="meta-line"><span>{html.escape(ui["website_language"])}</span><strong>{active_language["label"]}</strong></div>
            <div class="meta-line"><span>{html.escape(ui["active_menu"])}</span><strong>{html.escape(active_content["prompt_label"].replace("Prompt ", "").title())}</strong></div>
            <div class="meta-line"><span>{html.escape(ui["total_messages"])}</span><strong>{len(st.session_state.messages)}</strong></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

persona_col, language_col, key_col = st.columns([1, 1, 1.2])
with persona_col:
    st.markdown(f'<p class="field-label">{html.escape(ui["assistant_persona"])}</p>', unsafe_allow_html=True)
    selected_persona = st.selectbox(
        ui["assistant_persona"],
        options=list(PERSONAS.keys()),
        format_func=lambda key: persona_labels[key],
        label_visibility="collapsed",
        key="persona_sel",
    )
    st.session_state.persona = selected_persona

with language_col:
    st.markdown(f'<p class="field-label">{html.escape(ui["website_language_field"])}</p>', unsafe_allow_html=True)
    selected_language = st.selectbox(
        ui["website_language_field"],
        options=list(LANGUAGES.keys()),
        format_func=lambda key: LANGUAGES[key]["label"],
        label_visibility="collapsed",
        key="language_sel",
    )
    st.session_state.language = selected_language

with key_col:
    st.markdown(f'<p class="field-label">{html.escape(ui["gemini_api_key"])}</p>', unsafe_allow_html=True)
    if api_key:
        st.markdown(
            f'<div class="notice">{html.escape(ui["api_key_active"])}</div>',
            unsafe_allow_html=True,
        )
    else:
        api_key = st.text_input(
            ui["gemini_api_key"],
            type="password",
            placeholder=ui["api_key_placeholder"],
            label_visibility="collapsed",
        )

if not api_key:
    st.markdown(
        f'<div class="notice">{html.escape(ui["api_key_missing"])}</div>',
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# Home and chat states
# ------------------------------------------------------------
show_context_panel = not st.session_state.messages or st.session_state.active_page != "home"

if show_context_panel:
    st.markdown(
        f"""
        <section class="home-panel">
            <div class="home-copy">
                <h2 class="home-title">{html.escape(active_content["panel_title"])}</h2>
                <p class="home-subtitle">{html.escape(active_content["panel_subtitle"])}</p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    render_prompt_cards(
        active_content["prompts"],
        active_content["prompt_label"],
        f'prompt_{st.session_state.active_page}',
        ui["use_prompt"],
    )

if st.session_state.messages:
    st.markdown(
        f"""
        <div class="chat-toolbar">
            <div>
                <div class="chat-toolbar-title">{html.escape(ui["active_chat"])}</div>
                <div class="chat-toolbar-subtitle">{html.escape(ui["messages_in_session"].format(count=len(st.session_state.messages)))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    clear_left, clear_right = st.columns([5, 1])
    with clear_right:
        if st.button(ui["clear"], use_container_width=True):
            reset_chat()
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# ------------------------------------------------------------
# Gemini call
# ------------------------------------------------------------
def send_message(text: str) -> None:
    if not api_key:
        st.error(ui["api_error"])
        return

    with st.chat_message("user"):
        st.markdown(text)

    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.total += 1

    history = [
        types.Content(
            role="user" if item["role"] == "user" else "model",
            parts=[types.Part(text=item["content"])],
        )
        for item in st.session_state.messages
    ]

    client = genai.Client(api_key=api_key)
    system_instruction = (
        f'{PERSONAS[st.session_state.persona]["system"]}\n\n'
        "Language behavior: the website language selector only changes the interface. "
        "Answer in the same language as the user's latest message, unless the user explicitly asks for another language."
    )

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        try:
            with st.spinner(ui["spinner"]):
                stream = client.models.generate_content_stream(
                    model=MODEL_NAME,
                    contents=history,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.8,
                        max_output_tokens=2048,
                    ),
                )

            for chunk in stream:
                if chunk.text:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "...")
            placeholder.markdown(full_response)
        except Exception as exc:
            error_text = str(exc)
            if "API_KEY_INVALID" in error_text or "not valid" in error_text:
                full_response = ui["invalid_key"]
            elif "quota" in error_text.lower():
                full_response = ui["quota"]
            else:
                full_response = f'{ui["generic_error"]}: {error_text}'
            placeholder.error(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.total += 1


if st.session_state.quick_prompt:
    prompt = st.session_state.quick_prompt
    st.session_state.quick_prompt = None
    send_message(prompt)
    st.rerun()

if user_input := st.chat_input(ui["chat_placeholder"]):
    send_message(user_input)
    st.rerun()

st.markdown(
    f'<div class="fine-print">{html.escape(ui["fine_print"])}</div>',
    unsafe_allow_html=True,
)
