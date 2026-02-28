import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
from datetime import datetime, timedelta

# -----------------------------
# CONFIG
# -----------------------------
FREE_LIMIT = 20                 # 20 requests per 24 hours
WINDOW_HOURS = 24               # rolling window duration

# -----------------------------
# Load API Key
# -----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# -----------------------------
# Select Supported Gemini Model
# -----------------------------
def get_supported_model():
    try:
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                return m.name
    except:
        return None
    return None

MODEL_NAME = get_supported_model()
model = genai.GenerativeModel(MODEL_NAME) if MODEL_NAME else None

# -----------------------------
# Languages
# -----------------------------
global_languages = [
    "English", "Spanish", "French", "German",
    "Chinese", "Arabic", "Japanese",
    "Korean", "Portuguese", "Russian"
]

indian_languages = [
    "Hindi", "Tamil", "Telugu", "Kannada",
    "Malayalam", "Marathi", "Gujarati",
    "Bengali", "Punjabi", "Urdu",
    "Odia", "Assamese"
]

all_languages = global_languages + indian_languages

# LibreTranslate codes
lang_codes = {
    "English": "en", "Spanish": "es", "French": "fr",
    "German": "de", "Chinese": "zh", "Arabic": "ar",
    "Japanese": "ja", "Korean": "ko",
    "Portuguese": "pt", "Russian": "ru",
    "Hindi": "hi", "Tamil": "ta", "Telugu": "te",
    "Kannada": "kn", "Malayalam": "ml",
    "Marathi": "mr", "Gujarati": "gu",
    "Bengali": "bn", "Punjabi": "pa",
    "Urdu": "ur", "Odia": "or", "Assamese": "as"
}

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

if "source_lang" not in st.session_state:
    st.session_state.source_lang = "English"

if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Hindi"

# rolling 24h window tracking
if "request_timestamps" not in st.session_state:
    st.session_state.request_timestamps = []

# -----------------------------
# RATE LIMIT (24h Rolling Window)
# -----------------------------
def clean_old_requests():
    now = datetime.now()
    st.session_state.request_timestamps = [
        t for t in st.session_state.request_timestamps
        if now - t < timedelta(hours=WINDOW_HOURS)
    ]

def remaining_requests():
    clean_old_requests()
    return FREE_LIMIT - len(st.session_state.request_timestamps)

def time_until_reset():
    if not st.session_state.request_timestamps:
        return 0
    oldest = min(st.session_state.request_timestamps)
    reset_time = oldest + timedelta(hours=WINDOW_HOURS)
    return int((reset_time - datetime.now()).total_seconds())

# -----------------------------
# GEMINI TRANSLATE (FAST FAIL)
# -----------------------------
def gemini_translate(text, source_language, target_language):
    if not model:
        return None

    try:
        prompt = f"Translate from {source_language} to {target_language}:\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        if "429" in str(e):
            return "QUOTA_EXCEEDED"
        return None

# -----------------------------
# LIBRE TRANSLATE
# -----------------------------
def libre_translate(text, source_language, target_language):
    try:
        url = "https://libretranslate.de/translate"

        payload = {
            "q": text,
            "source": lang_codes.get(source_language, "auto"),
            "target": lang_codes.get(target_language),
            "format": "text"
        }

        response = requests.post(url, data=payload, timeout=5)

        if response.status_code != 200:
            return None

        return response.json().get("translatedText")
    except:
        return None

# -----------------------------
# AUTO DETECT
# -----------------------------
def detect_language(text):
    if not model:
        return None
    try:
        prompt = f"Detect the language:\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return None

# -----------------------------
# SWAP
# -----------------------------
def swap_languages():
    if st.session_state.source_lang != "Auto Detect":
        st.session_state.source_lang, st.session_state.target_lang = (
            st.session_state.target_lang,
            st.session_state.source_lang
        )

# -----------------------------
# UI
# -----------------------------
def main():

    st.set_page_config(page_title="AI Translator", page_icon="🌐")

    st.title("🌐 AI-Powered Language Translator")
    st.caption("Gemini (Primary) • LibreTranslate (Fallback)")

    # -----------------------------
    # Quota Display
    # -----------------------------
    remaining = remaining_requests()
    st.info(f"🆓 Free Translations Remaining (24h window): {max(0, remaining)} / {FREE_LIMIT}")

    if remaining <= 0:
        seconds_left = time_until_reset()
        hours = seconds_left // 3600
        minutes = (seconds_left % 3600) // 60

        st.warning(
            f"🚦 Daily free-tier limit reached.\n\n"
            f"Quota resets in approximately {hours}h {minutes}m."
        )

        st.markdown("### 💎 Upgrade to Premium")
        st.markdown("""
        - Unlimited translations  
        - Faster AI responses  
        - No daily limits  
        - Priority processing  
        """)
        st.button("🚀 Upgrade Now (Demo)")
        return

    # -----------------------------
    # Upload TXT
    # -----------------------------
    uploaded_file = st.file_uploader("📄 Upload .txt file", type=["txt"])
    file_text = ""
    if uploaded_file:
        file_text = uploaded_file.read().decode("utf-8")

    text = st.text_area("📝 Enter text to translate:", value=file_text)

    col1, col2, col3 = st.columns([3,1,3])

    with col1:
        st.session_state.source_lang = st.selectbox(
            "🌍 Source Language:",
            ["Auto Detect"] + all_languages,
            index=(["Auto Detect"] + all_languages).index(st.session_state.source_lang)
        )

    with col2:
        st.write("")
        st.write("")
        st.button("⇄", on_click=swap_languages)

    with col3:
        st.session_state.target_lang = st.selectbox(
            "🌎 Target Language:",
            all_languages,
            index=all_languages.index(st.session_state.target_lang)
        )

    # -----------------------------
    # TRANSLATE
    # -----------------------------
    if st.button("🔄 Translate"):

        if not text.strip():
            st.warning("⚠️ Please enter text.")
            return

        source = st.session_state.source_lang

        # Auto detect
        if source == "Auto Detect":
            detected = detect_language(text)
            if detected:
                st.info(f"🔍 Detected Language: {detected}")
                source = detected
            else:
                source = "auto"

        translated = None
        engine_used = None

        # Try Gemini
        result = gemini_translate(text, source, st.session_state.target_lang)

        if result == "QUOTA_EXCEEDED":
            translated = None
        elif result:
            translated = result
            engine_used = "🤖 Gemini AI"

        # Fallback
        if not translated:
            translated = libre_translate(text, source, st.session_state.target_lang)
            if translated:
                engine_used = "🌍 LibreTranslate"

        if not translated:
            st.warning(
                "⚠️ Free-tier quota exceeded or translation servers are currently busy.\n\n"
                "Please try again later."
            )
            return

        # Store request timestamp
        st.session_state.request_timestamps.append(datetime.now())

        st.session_state.translated_text = translated
        st.success(f"Engine Used: {engine_used}")

        st.session_state.history.append({
            "Original": text,
            "From": source,
            "To": st.session_state.target_lang,
            "Translated": translated,
            "Engine": engine_used
        })

    # -----------------------------
    # OUTPUT
    # -----------------------------
    if st.session_state.translated_text:
        st.subheader("🗣️ Translated Text")
        st.text_area("", st.session_state.translated_text, height=150)

        st.download_button(
            label="📥 Download Translated TXT",
            data=st.session_state.translated_text,
            file_name="translated.txt",
            mime="text/plain"
        )

    # -----------------------------
    # HISTORY
    # -----------------------------
    if st.session_state.history:
        st.divider()
        st.subheader("📜 Translation History")

        for item in reversed(st.session_state.history[-5:]):
            st.markdown(
                f"""
                **Engine:** {item['Engine']}  
                **From:** {item['From']} → **To:** {item['To']}  
                **Original:** {item['Original']}  
                **Translated:** {item['Translated']}
                """
            )
            st.divider()

if __name__ == "__main__":
    main()
