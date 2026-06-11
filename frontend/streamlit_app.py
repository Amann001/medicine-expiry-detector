import streamlit as st
import requests
from PIL import Image
import io
import time
import base64
import os

st.set_page_config(
    page_title="MedScan — Medicine Expiry Detector",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Merriweather:wght@300;400;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background: #F7F9FC !important;
    color: #1A2340 !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── NAV BAR ── */
.navbar {
    background: #FFFFFF;
    border-bottom: 1px solid #E4EAF4;
    padding: 0 2rem;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 1px 12px rgba(26,35,64,0.06);
}
.nav-logo {
    display: flex;
    align-items: center;
    gap: 10px;
}
.nav-logo-icon {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #005EB8 0%, #00A3A1 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    box-shadow: 0 4px 12px rgba(0,94,184,0.25);
}
.nav-logo-text {
    font-size: 1.2rem;
    font-weight: 800;
    color: #005EB8;
    letter-spacing: -0.02em;
}
.nav-logo-text span { color: #00A3A1; }
.nav-badge {
    background: #EBF5FF;
    color: #005EB8;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 0.3rem 0.8rem;
    border-radius: 100px;
    border: 1px solid #C5DEFF;
}

/* ── HERO SECTION ── */
.hero-section {
    background: linear-gradient(135deg, #003F8A 0%, #005EB8 40%, #007CC2 70%, #00A3A1 100%);
    padding: 4rem 2rem 3rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.hero-section::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 300px; height: 300px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.hero-section::after {
    content: '';
    position: absolute;
    bottom: -100px; left: -60px;
    width: 250px; height: 250px;
    background: rgba(0,163,161,0.15);
    border-radius: 50%;
}
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    color: rgba(255,255,255,0.9);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.35rem 1rem;
    border-radius: 100px;
    margin-bottom: 1.25rem;
}
.hero-title {
    font-family: 'Merriweather', serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.2;
    letter-spacing: -0.02em;
    margin-bottom: 1rem;
    position: relative;
    z-index: 1;
}
.hero-title em {
    font-style: normal;
    color: #7EE8E7;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: rgba(255,255,255,0.75);
    max-width: 480px;
    margin: 0 auto 2rem;
    line-height: 1.65;
    font-weight: 300;
    position: relative;
    z-index: 1;
}
.hero-stats {
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    position: relative;
    z-index: 1;
    flex-wrap: wrap;
}
.stat-item { text-align: center; }
.stat-num {
    font-size: 1.6rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1;
    letter-spacing: -0.03em;
}
.stat-label {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.55);
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 3px;
}
.stat-div {
    width: 1px;
    background: rgba(255,255,255,0.15);
    height: 40px;
    margin: auto 0;
}

/* ── MAIN CONTENT AREA ── */
.main-area {
    max-width: 680px;
    margin: 0 auto;
    padding: 2.5rem 1.5rem 4rem;
}

/* ── UPLOAD CARD ── */
.upload-card {
    background: #FFFFFF;
    border-radius: 20px;
    box-shadow: 0 2px 20px rgba(26,35,64,0.08), 0 1px 4px rgba(26,35,64,0.04);
    overflow: hidden;
    margin-bottom: 1.25rem;
}
.upload-card-header {
    padding: 1.25rem 1.5rem 0;
}
.card-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #8A95B0;
    margin-bottom: 0.3rem;
}
.card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1A2340;
    margin-bottom: 1rem;
}

[data-testid="stFileUploader"] {
    background: #F7F9FC !important;
    border: 2px dashed #C5DEFF !important;
    border-radius: 14px !important;
    margin: 0 1.5rem 1.5rem !important;
    transition: border-color 0.2s ease !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #005EB8 !important;
}
[data-testid="stFileUploader"] section {
    padding: 1.5rem !important;
}
[data-testid="stFileUploader"] label p {
    color: #8A95B0 !important;
}
[data-testid="stFileUploadDropzoneInput"] + div > div > small {
    color: #B0BAD0 !important;
}

/* ── IMAGE PREVIEW ── */
.preview-wrap {
    background: #F0F4FA;
    border-radius: 12px;
    overflow: hidden;
    margin: 0 1.5rem 1rem;
    position: relative;
}
.preview-tag {
    position: absolute;
    top: 10px; left: 10px;
    background: rgba(0,94,184,0.85);
    color: white;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 6px;
    backdrop-filter: blur(4px);
}
.file-meta {
    padding: 0.6rem 1.5rem;
    font-size: 0.75rem;
    color: #B0BAD0;
    font-family: 'Inter', monospace;
    background: #FAFBFD;
    border-top: 1px solid #EEF2FA;
}

/* ── SCAN BUTTON ── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #005EB8 0%, #007CC2 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.9rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.01em !important;
    font-family: 'Inter', sans-serif !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 6px 20px rgba(0,94,184,0.3) !important;
    margin-bottom: 1.5rem !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #004A99 0%, #006BB0 100%) !important;
    box-shadow: 0 8px 28px rgba(0,94,184,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── PROGRESS BAR ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #005EB8, #00A3A1) !important;
    border-radius: 100px !important;
}
.stProgress > div > div {
    background: #EEF2FA !important;
    border-radius: 100px !important;
}

/* ── RESULT CARDS ── */
.result-main {
    background: #FFFFFF;
    border-radius: 20px;
    box-shadow: 0 2px 20px rgba(26,35,64,0.08);
    overflow: hidden;
    margin-bottom: 1rem;
}
.result-top {
    padding: 1.5rem 1.75rem 1.25rem;
    border-bottom: 1px solid #F0F4FA;
}
.result-top.valid   { background: linear-gradient(135deg, #F0FBF8 0%, #FFFFFF 100%); border-top: 4px solid #00A878; }
.result-top.expired { background: linear-gradient(135deg, #FFF5F5 0%, #FFFFFF 100%); border-top: 4px solid #E53E3E; }
.result-top.soon    { background: linear-gradient(135deg, #FFFBF0 0%, #FFFFFF 100%); border-top: 4px solid #DD6B20; }
.result-top.unknown { background: #F7F9FC; border-top: 4px solid #CBD5E0; }

.result-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.28rem 0.75rem;
    border-radius: 100px;
    margin-bottom: 0.75rem;
}
.pill-valid   { background: #D4F5EC; color: #00815A; }
.pill-expired { background: #FED7D7; color: #C53030; }
.pill-soon    { background: #FEEBC8; color: #C05621; }
.pill-unknown { background: #EDF2F7; color: #718096; }

.result-expiry-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #8A95B0;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.2rem;
}
.result-expiry-date {
    font-size: 2.6rem;
    font-weight: 800;
    color: #1A2340;
    letter-spacing: -0.04em;
    line-height: 1.1;
    font-variant-numeric: tabular-nums;
    margin-bottom: 0.4rem;
}
.result-status-line {
    font-size: 0.95rem;
    font-weight: 500;
    color: #4A5568;
}
.result-status-line.valid   { color: #00815A; }
.result-status-line.expired { color: #C53030; }
.result-status-line.soon    { color: #C05621; }

.result-details {
    padding: 1rem 1.75rem;
}
.detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid #F4F7FC;
}
.detail-row:last-child { border-bottom: none; }
.detail-key {
    font-size: 0.75rem;
    font-weight: 600;
    color: #A0AAC0;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.detail-val {
    font-size: 0.82rem;
    font-weight: 600;
    color: #4A5568;
}
.detail-val.blue { color: #005EB8; }

/* ── ERROR / TIPS CARD ── */
.tips-card {
    background: #FFFFFF;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(26,35,64,0.06);
    padding: 1.25rem 1.5rem;
    margin-top: 0.75rem;
}
.tips-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 0.9rem;
}
.tips-icon {
    width: 28px; height: 28px;
    background: #EBF5FF;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}
.tips-title {
    font-size: 0.82rem;
    font-weight: 700;
    color: #1A2340;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.tip-row {
    display: flex;
    align-items: flex-start;
    gap: 0.65rem;
    padding: 0.4rem 0;
    font-size: 0.85rem;
    color: #5A6480;
    line-height: 1.5;
    border-bottom: 1px solid #F4F7FC;
}
.tip-row:last-child { border-bottom: none; }
.tip-num {
    width: 20px; height: 20px;
    background: #EBF5FF;
    color: #005EB8;
    border-radius: 6px;
    font-size: 0.65rem;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
}

/* ── HOW IT WORKS ── */
.how-section {
    margin-top: 2rem;
}
.how-title {
    font-size: 0.72rem;
    font-weight: 700;
    color: #A0AAC0;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    text-align: center;
    margin-bottom: 1rem;
}
.how-steps {
    display: flex;
    gap: 0;
    background: #FFFFFF;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(26,35,64,0.06);
    overflow: hidden;
}
.how-step {
    flex: 1;
    padding: 1.25rem 1rem;
    text-align: center;
    border-right: 1px solid #F0F4FA;
    position: relative;
}
.how-step:last-child { border-right: none; }
.how-step-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    line-height: 1;
}
.how-step-label {
    font-size: 0.78rem;
    font-weight: 700;
    color: #1A2340;
    margin-bottom: 0.2rem;
}
.how-step-sub {
    font-size: 0.68rem;
    color: #A0AAC0;
    line-height: 1.4;
}
.how-arrow {
    position: absolute;
    right: -8px;
    top: 50%;
    transform: translateY(-50%);
    width: 16px;
    height: 16px;
    background: #F0F4FA;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 8px;
    color: #A0AAC0;
    z-index: 2;
}

/* ── FOOTER ── */
.app-footer {
    text-align: center;
    padding: 1.5rem 0 0;
    font-size: 0.75rem;
    color: #B0BAD0;
}
.app-footer strong { color: #8A95B0; }

/* ── SPINNER TEXT ── */
.scan-status {
    text-align: center;
    font-size: 0.82rem;
    color: #8A95B0;
    font-weight: 500;
    margin: 0.4rem 0 0.75rem;
    letter-spacing: 0.02em;
}

/* ── DIVIDER ── */
.light-div {
    height: 1px;
    background: #EEF2FA;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── NAVBAR ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div class="nav-logo">
        <div class="nav-logo-icon">🏥</div>
        <span class="nav-logo-text">Med<span>Scan</span></span>
    </div>
    <span class="nav-badge">AI Health Tool</span>
</div>
""", unsafe_allow_html=True)

# ── HERO ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-eyebrow">
        ✦ &nbsp; Powered by YOLOv8 + EasyOCR
    </div>
    <h1 class="hero-title">
        Know if your medicine<br>is <em>safe to take</em>
    </h1>
    <p class="hero-subtitle">
        Upload a photo of any medicine packaging. MedScan reads the expiry date in seconds using computer vision — no typing required.
    </p>
    <div class="hero-stats">
        <div class="stat-item">
            <div class="stat-num">7+</div>
            <div class="stat-label">OCR variants</div>
        </div>
        <div class="stat-div"></div>
        <div class="stat-item">
            <div class="stat-num">4</div>
            <div class="stat-label">Rotations tried</div>
        </div>
        <div class="stat-div"></div>
        <div class="stat-item">
            <div class="stat-num">YOLOv8</div>
            <div class="stat-label">Detection model</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── MAIN CONTENT ───────────────────────────────────────────────────────────
st.markdown('<div class="main-area">', unsafe_allow_html=True)

# How it works
st.markdown("""
<div class="how-section">
    <div class="how-title">How it works</div>
    <div class="how-steps">
        <div class="how-step">
            <div class="how-step-icon">📸</div>
            <div class="how-step-label">Upload</div>
            <div class="how-step-sub">Photo of medicine label</div>
            <div class="how-arrow">›</div>
        </div>
        <div class="how-step">
            <div class="how-step-icon">🔍</div>
            <div class="how-step-label">Detect</div>
            <div class="how-step-sub">YOLO finds label region</div>
            <div class="how-arrow">›</div>
        </div>
        <div class="how-step">
            <div class="how-step-icon">🔤</div>
            <div class="how-step-label">Read</div>
            <div class="how-step-sub">OCR extracts date text</div>
            <div class="how-arrow">›</div>
        </div>
        <div class="how-step">
            <div class="how-step-icon">✅</div>
            <div class="how-step-label">Result</div>
            <div class="how-step-sub">Valid, expired or soon</div>
        </div>
    </div>
</div>
<div class="light-div"></div>
""", unsafe_allow_html=True)

# Upload card
st.markdown("""
<div class="upload-card">
    <div class="upload-card-header">
        <div class="card-label">Step 1</div>
        <div class="card-title">Upload medicine image</div>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    label="upload",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="collapsed",
    help="Works best with clear photos in good lighting"
)

if uploaded_file:
    img = Image.open(uploaded_file)
    w, h = img.size
    size_kb = len(uploaded_file.getvalue()) / 1024
    st.markdown('<div class="preview-wrap"><span class="preview-tag">Preview</span>', unsafe_allow_html=True)
    st.image(img, use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="file-meta">{uploaded_file.name} &nbsp;·&nbsp; {w} × {h} px &nbsp;·&nbsp; {size_kb:.0f} KB</div>',
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)  # close upload-card

if uploaded_file:
    scan = st.button("🔍 &nbsp; Scan for Expiry Date", use_container_width=True)

    if scan:
        progress = st.progress(0)
        status_ph = st.empty()

        steps = [
            (12, "Preprocessing image..."),
            (28, "Running YOLO detection..."),
            (48, "Extracting text with OCR..."),
            (68, "Applying rotation variants..."),
            (85, "Parsing expiry date..."),
            (95, "Checking medicine status..."),
        ]
        for pct, msg in steps:
            progress.progress(pct)
            status_ph.markdown(f'<p class="scan-status">{msg}</p>', unsafe_allow_html=True)
            time.sleep(0.22)

        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "image/jpeg")}
            API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

            # then use:
            response = requests.post(
                f"{API_URL}/detect-expiry",
                files=files,
                timeout=120
            )
            result = response.json()
            progress.progress(100)
            time.sleep(0.15)
            progress.empty()
            status_ph.empty()

            st.markdown('<div class="light-div"></div>', unsafe_allow_html=True)

            if result.get("success"):
                expiry  = result.get("expiry_date", "—")
                status  = result.get("status", "")
                method  = result.get("detection_method", "ocr")

                if "EXPIRED" in status:
                    top_cls, pill_cls, pill_text, status_cls, icon = "expired", "pill-expired", "Expired", "expired", "⚠️"
                elif "EXPIRING SOON" in status:
                    top_cls, pill_cls, pill_text, status_cls, icon = "soon", "pill-soon", "Expiring Soon", "soon", "⏰"
                else:
                    top_cls, pill_cls, pill_text, status_cls, icon = "valid", "pill-valid", "Safe to Use", "valid", "✅"

                method_label = {
                    "yolo": "YOLOv8 + OCR",
                    "fallback_full_image": "OCR Full Image",
                    "fallback_ocr": "OCR Fallback",
                }.get(method, method.upper())

                st.markdown(f"""
                <div class="result-main">
                    <div class="result-top {top_cls}">
                        <div class="result-pill {pill_cls}">{icon} &nbsp; {pill_text}</div>
                        <div class="result-expiry-label">Expiry Date Detected</div>
                        <div class="result-expiry-date">{expiry}</div>
                        <div class="result-status-line {status_cls}">{status}</div>
                    </div>
                    <div class="result-details">
                        <div class="detail-row">
                            <span class="detail-key">Expiry date</span>
                            <span class="detail-val blue">{expiry}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-key">Status</span>
                            <span class="detail-val">{status}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-key">Detection method</span>
                            <span class="detail-val">{method_label}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-key">File analysed</span>
                            <span class="detail-val">{uploaded_file.name}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.markdown("""
                <div class="result-main">
                    <div class="result-top unknown">
                        <div class="result-pill pill-unknown">— &nbsp; Not Detected</div>
                        <div class="result-expiry-label">Expiry Date</div>
                        <div class="result-expiry-date" style="font-size:1.4rem;color:#A0AAC0;">Could not read</div>
                        <div class="result-status-line" style="color:#718096;">The expiry text was not clearly visible.</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div class="tips-card">
                    <div class="tips-header">
                        <div class="tips-icon">💡</div>
                        <div class="tips-title">How to improve accuracy</div>
                    </div>
                    <div class="tip-row">
                        <div class="tip-num">1</div>
                        Hold the camera steady — blur is the most common cause of failure
                    </div>
                    <div class="tip-row">
                        <div class="tip-num">2</div>
                        Make the EXP or Expiry text fill at least 30% of the frame
                    </div>
                    <div class="tip-row">
                        <div class="tip-num">3</div>
                        Use natural daylight or a bright lamp — avoid shadows and glare on foil
                    </div>
                    <div class="tip-row">
                        <div class="tip-num">4</div>
                        For bottle caps, shoot straight down from above
                    </div>
                    <div class="tip-row">
                        <div class="tip-num">5</div>
                        For blister strips, flip to the foil back side where EXP is stamped
                    </div>
                </div>
                """, unsafe_allow_html=True)

        except requests.exceptions.ConnectionError:
            progress.empty()
            status_ph.empty()
            st.markdown("""
            <div class="tips-card">
                <div class="tips-header">
                    <div class="tips-icon">🔌</div>
                    <div class="tips-title">Backend not running</div>
                </div>
                <div class="tip-row">
                    <div class="tip-num">!</div>
                    Start uvicorn first: <code style="background:#EBF5FF;padding:2px 7px;border-radius:4px;color:#005EB8;font-size:0.8rem;">uvicorn backend.app:app --reload</code>
                </div>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            progress.empty()
            status_ph.empty()
            st.error(f"Error: {e}")

else:
    # Empty state tips
    st.markdown("""
    <div class="tips-card">
        <div class="tips-header">
            <div class="tips-icon">💊</div>
            <div class="tips-title">Supported formats</div>
        </div>
        <div class="tip-row"><div class="tip-num">✓</div>Flat medicine boxes — Crocin, Dolo, Combiflam, etc.</div>
        <div class="tip-row"><div class="tip-num">✓</div>Blister / strip packs — flip to the foil back side</div>
        <div class="tip-row"><div class="tip-num">✓</div>Syrup bottles — rotate so the label faces the camera</div>
        <div class="tip-row"><div class="tip-num">✓</div>Date formats: EXP 01/2026 · Expiry Date JUL 2028 · EXP.SEP.2027</div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="app-footer">
    <strong>MedScan</strong> &nbsp;·&nbsp; YOLOv8 + EasyOCR + FastAPI &nbsp;·&nbsp;
    Built for medicine safety
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)