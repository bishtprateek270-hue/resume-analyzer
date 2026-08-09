import streamlit as st
import streamlit.components.v1 as components
import os
import json
import hashlib
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file (enable override on refresh)
load_dotenv(override=True)

# Import custom modules
import database
import auth
import parser
import analyzer
import llm_helper
import report_generator

# Page Configuration
st.set_page_config(
    page_title="AI Resume Analyzer & ATS Optimizer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Initialize database
database.init_db()

# ----------------- SESSION STATE SETUP & AUTO-LOGIN -----------------
SECRET_KEY = "super_secret_resume_analyzer_key_123"

def generate_session_token(username: str) -> str:
    signature = hashlib.sha256((username + SECRET_KEY).encode()).hexdigest()[:16]
    return f"{username}:{signature}"

def verify_session_token(token: str) -> str:
    try:
        username, signature = token.split(":")
        expected_signature = hashlib.sha256((username + SECRET_KEY).encode()).hexdigest()[:16]
        if signature == expected_signature:
            return username
    except Exception:
        pass
    return ""

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "gemini_api_key" not in st.session_state:
    try:
        st.session_state.gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        st.session_state.gemini_api_key = ""
    if not st.session_state.gemini_api_key:
        st.session_state.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
if "active_analysis" not in st.session_state:
    st.session_state.active_analysis = None
if "current_view" not in st.session_state:
    st.session_state.current_view = "new_analysis"

# Auto-login check on page load / browser refresh
if not st.session_state.logged_in:
    saved_token = st.query_params.get("session_token")
    if saved_token:
        autologin_username = verify_session_token(saved_token)
        if autologin_username:
            user_info = database.get_user(autologin_username)
            if user_info:
                st.session_state.logged_in = True
                st.session_state.user = {
                    "id": user_info["id"],
                    "username": user_info["username"],
                    "email": user_info["email"]
                }

# Base & Theme CSS (CSS Variables for Instant Zero-Delay Client-Side Switching)
_current_theme = "dark" if st.session_state.get("dark_mode", False) else "light"

st.markdown(r"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Typography */
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* ==================== LIGHT THEME (DEFAULT) ==================== */
    :root,
    html[data-theme="light"],
    body[data-theme="light"],
    .stApp[data-theme="light"] {
        --bg-app: #F8FAFC;
        --bg-card: #FFFFFF;
        --bg-sidebar: #FFFFFF;
        --border-card: #CBD5E1;
        --border-sidebar: #E2E8F0;
        --border-input: #94A3B8;
        --shadow-card: 0 2px 12px rgba(0,0,0,0.06);
        --text-heading: #0F172A;
        --text-main: #0F172A;
        --text-sub: #334155;
        --text-muted: #64748B;
        --circle-ring: #E2E8F0;
        --divider: #E2E8F0;
        --input-bg: #FFFFFF;
        --dropzone-bg: #FFFFFF;
        --expander-bg: #FFFFFF;
        --expander-border: #E2E8F0;
        --btn-sec-bg: #FFFFFF;
        --btn-sec-text: #0F172A;
        --btn-sec-border: #CBD5E1;
        --btn-sec-hover-bg: #EFF6FF;
        --btn-sec-hover-text: #0284C7;
        --btn-sec-hover-border: #0284C7;
        --sidebar-btn-bg: #F1F5F9;
        --sidebar-btn-text: #0F172A;
        --sidebar-btn-border: #CBD5E1;
        --sidebar-btn-hover-bg: #E0F2FE;
        --sidebar-btn-hover-text: #0284C7;
        --sidebar-btn-hover-border: #0284C7;
        --tab-text: #475569;
        --tab-active: #0284C7;
        --alert-bg: #FFFFFF;
        --alert-border: #CBD5E1;
        --alert-text: #334155;
        --tag-matched-bg: #dcfce7;
        --tag-matched-text: #166534;
        --tag-matched-border: #bbf7d0;
        --tag-missing-bg: #fef9c3;
        --tag-missing-text: #713f12;
        --tag-missing-border: #fef08a;
        --tag-section-bg: #e0f2fe;
        --tag-section-text: #075985;
        --tag-section-border: #bae6fd;
    }

    /* ==================== DARK THEME ==================== */
    html[data-theme="dark"],
    body[data-theme="dark"],
    .stApp[data-theme="dark"],
    [data-theme="dark"] {
        --bg-app: #0F172A !important;
        --bg-card: #1E293B !important;
        --bg-sidebar: #1E293B !important;
        --border-card: #334155 !important;
        --border-sidebar: #334155 !important;
        --border-input: #475569 !important;
        --shadow-card: 0 4px 20px rgba(0,0,0,0.3) !important;
        --text-heading: #F1F5F9 !important;
        --text-main: #F1F5F9 !important;
        --text-sub: #CBD5E1 !important;
        --text-muted: #94A3B8 !important;
        --circle-ring: #334155 !important;
        --divider: #334155 !important;
        --input-bg: #1E293B !important;
        --dropzone-bg: #1E293B !important;
        --expander-bg: #1E293B !important;
        --expander-border: #334155 !important;
        --btn-sec-bg: #1E293B !important;
        --btn-sec-text: #F1F5F9 !important;
        --btn-sec-border: #475569 !important;
        --btn-sec-hover-bg: #0F172A !important;
        --btn-sec-hover-text: #38BDF8 !important;
        --btn-sec-hover-border: #38BDF8 !important;
        --sidebar-btn-bg: #1E293B !important;
        --sidebar-btn-text: #F1F5F9 !important;
        --sidebar-btn-border: #475569 !important;
        --sidebar-btn-hover-bg: #0F172A !important;
        --sidebar-btn-hover-text: #38BDF8 !important;
        --sidebar-btn-hover-border: #38BDF8 !important;
        --tab-text: #94A3B8 !important;
        --tab-active: #38BDF8 !important;
        --alert-bg: #1E293B !important;
        --alert-border: #334155 !important;
        --alert-text: #CBD5E1 !important;
        --tag-matched-bg: rgba(22, 101, 52, 0.35) !important;
        --tag-matched-text: #4ade80 !important;
        --tag-matched-border: rgba(74, 222, 128, 0.3) !important;
        --tag-missing-bg: rgba(113, 63, 18, 0.35) !important;
        --tag-missing-text: #facc15 !important;
        --tag-missing-border: rgba(250, 204, 21, 0.3) !important;
        --tag-section-bg: rgba(7, 89, 133, 0.35) !important;
        --tag-section-text: #38bdf8 !important;
        --tag-section-border: rgba(56, 189, 248, 0.3) !important;
    }

    /* Zero-delay instant theme switching & zero animations */
    *, *::before, *::after {
        transition: none !important;
        animation: none !important;
    }

    .instant-toggle-slider:before {
        position: absolute;
        content: "";
        height: 16px;
        width: 16px;
        left: 3px;
        bottom: 3px;
        background-color: white;
        border-radius: 50%;
        transition: none !important;
    }
    input:checked + .instant-toggle-slider {
        background-color: #0284C7 !important;
    }
    input:checked + .instant-toggle-slider:before {
        transform: translateX(22px) !important;
    }

    /* App & Sidebar background */
    .stApp,
    .stApp > div,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background-color: var(--bg-app) !important;
        color: var(--text-main) !important;
    }

    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        background-color: var(--bg-sidebar) !important;
        border-right: 1.5px solid var(--border-sidebar) !important;
    }

    /* Hide top right header toolbar & footers */
    header[data-testid="stHeader"],
    div[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    #MainMenu,
    header,
    footer,
    [data-testid="stAppViewerFooter"],
    .stAppViewerFooter,
    div[class*="stAppViewerFooter"],
    div[class*="viewerBadge"],
    button[title="Manage app"],
    button[aria-label="Manage app"],
    div[aria-label="Manage app"],
    .viewerBadge_container__1S-5D,
    .viewerBadge_link__1S-5D,
    div[data-testid="stDecoration"],
    #stDecoration,
    [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        height: 0px !important;
        width: 0px !important;
    }

    /* Force all form submit buttons and standard buttons to be visible and styled */
    [data-testid="stFormSubmitButton"],
    [data-testid="stFormSubmitButton"] button,
    div.stFormSubmitButton > button,
    .stButton > button {
        display: inline-block !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        cursor: pointer !important;
    }

    /* Headings & Text */
    .stApp h1, .stApp h2, .stApp h3,
    .stApp h4, .stApp h5, .stApp h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: var(--text-heading) !important;
        font-weight: 700 !important;
    }

    .stApp p, .stApp label,
    .stApp li, .stApp small, .stApp span,
    .stMarkdown p, .stMarkdown label, .stMarkdown span,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--text-sub) !important;
    }

    /* Text inputs & textareas */
    .stTextInput input,
    .stTextArea textarea,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea,
    [data-baseweb="base-input"] input,
    [data-baseweb="base-input"] textarea {
        background-color: var(--input-bg) !important;
        color: var(--text-main) !important;
        border: 1.5px solid var(--border-input) !important;
        border-radius: 8px !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: var(--text-muted) !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: #0284C7 !important;
        box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.2) !important;
    }

    .stTextInput label,
    .stTextArea label,
    .stFileUploader label,
    .stSelectbox label {
        color: var(--text-heading) !important;
        font-weight: 700 !important;
    }

    /* File Uploader Dropzone */
    [data-testid="stFileUploaderDropzone"] {
        background-color: var(--dropzone-bg) !important;
        border: 2px dashed var(--border-input) !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileUploaderDropzone"] p,
    [data-testid="stFileUploaderDropzone"] span,
    [data-testid="stFileUploaderDropzone"] small {
        color: var(--text-sub) !important;
        font-weight: 500 !important;
    }

    /* Select / Dropdown */
    [data-baseweb="select"] > div,
    [data-baseweb="popover"] {
        background-color: var(--input-bg) !important;
        color: var(--text-main) !important;
        border: 1.5px solid var(--border-input) !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background-color: var(--expander-bg) !important;
        border: 1px solid var(--expander-border) !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] p {
        color: var(--text-sub) !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        color: var(--tab-text) !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--tab-active) !important;
        border-bottom-color: var(--tab-active) !important;
    }
    [data-testid="stTabs"] { background-color: transparent !important; }

    /* Primary & Form Submit Buttons */
    [data-testid="stFormSubmitButton"] button,
    div.stFormSubmitButton > button,
    button[kind="primary"], button[data-testid="baseButton-primary"] {
        background-color: #0284C7 !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        width: 100% !important;
        box-shadow: 0 2px 6px rgba(2, 132, 199, 0.2) !important;
    }
    [data-testid="stFormSubmitButton"] button:hover,
    div.stFormSubmitButton > button:hover,
    button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {
        background-color: #0369A1 !important;
        color: #FFFFFF !important;
    }

    /* Secondary Buttons */
    button[kind="secondary"], button[data-testid="baseButton-secondary"] {
        background-color: var(--btn-sec-bg) !important;
        color: var(--btn-sec-text) !important;
        border: 1.5px solid var(--btn-sec-border) !important;
        font-weight: 600 !important;
    }
    button[kind="secondary"]:hover, button[data-testid="baseButton-secondary"]:hover {
        background-color: var(--btn-sec-hover-bg) !important;
        color: var(--btn-sec-hover-text) !important;
        border-color: var(--btn-sec-hover-border) !important;
    }

    /* Sidebar Navigation Buttons */
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
        background-color: var(--sidebar-btn-bg) !important;
        color: var(--sidebar-btn-text) !important;
        border: 1.5px solid var(--sidebar-btn-border) !important;
        font-weight: 700 !important;
    }
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {
        background-color: var(--sidebar-btn-hover-bg) !important;
        color: var(--sidebar-btn-hover-text) !important;
        border-color: var(--sidebar-btn-hover-border) !important;
    }

    /* Tags */
    .tag { display: inline-block; padding: 5px 12px; border-radius: 9999px; font-size: 0.82rem; font-weight: 600; margin: 3px; }
    .tag-matched { background: var(--tag-matched-bg); color: var(--tag-matched-text); border: 1px solid var(--tag-matched-border); }
    .tag-missing { background: var(--tag-missing-bg); color: var(--tag-missing-text); border: 1px solid var(--tag-missing-border); }
    .tag-section  { background: var(--tag-section-bg); color: var(--tag-section-text); border: 1px solid var(--tag-section-border); }

    /* Score Circle */
    .score-circle {
        display: flex; align-items: center; justify-content: center;
        width: 130px; height: 130px; border-radius: 50%;
        margin: 0 auto 12px auto; font-size: 2rem; font-weight: 800;
        box-shadow: inset 0 0 0 10px var(--circle-ring);
    }

    /* Metric Cards */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 14px;
        box-shadow: var(--shadow-card);
        color: var(--text-main);
    }
    .metric-card:hover { }
    .metric-card h4 { color: var(--text-heading) !important; margin-top: 0; }
    .metric-card p  { color: var(--text-sub) !important; }

    /* Feedback Rows */
    .feedback-item { padding: 7px 0; border-bottom: 1px solid var(--divider); }

    /* Title styles */
    .app-title { font-weight: 800; font-size: 2.2rem; margin-bottom: 6px; color: var(--text-heading); }
    .app-subtitle { font-size: 1rem; color: var(--text-muted); margin-bottom: 24px; }

    /* Alerts & Dividers */
    [data-testid="stAlert"] {
        background-color: var(--alert-bg) !important;
        color: var(--alert-text) !important;
        border: 1px solid var(--alert-border) !important;
    }
    hr { border-color: var(--divider) !important; }
</style>
""", unsafe_allow_html=True)

components.html("""
<script>
(function() {
    try {
        var pDoc = window.parent.document;
        var savedTheme = window.parent.localStorage.getItem('app_theme_preference') || 'light';
        pDoc.documentElement.setAttribute('data-theme', savedTheme);
        pDoc.body.setAttribute('data-theme', savedTheme);
        var app = pDoc.querySelector('.stApp');
        if (app) app.setAttribute('data-theme', savedTheme);
        var sidebar = pDoc.querySelector('section[data-testid="stSidebar"]');
        if (sidebar) sidebar.setAttribute('data-theme', savedTheme);
    } catch(e) {}
})();
</script>
""", height=0, width=0)

# Logout function
def handle_logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.active_analysis = None
    st.session_state.current_view = "new_analysis"
    # Securely clear url session parameters
    st.query_params.clear()
    st.rerun()

# ----------------- AUTHENTICATION VIEWS -----------------
def render_login_register():
    st.markdown('<h1 style="text-align: center; font-weight:800; margin-top: 30px;">🔍 AI Resume Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1rem; font-weight: 500;">Upload resumes, evaluate ATS fit, get bridging projects suggestions, and download PDF reports.</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to your account")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                user_data, msg = auth.login_user(username, password)
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.query_params["session_token"] = generate_session_token(user_data["username"])
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        
    with tab2:
        st.subheader("Create a new account")
        with st.form("register_form"):
            reg_username = st.text_input("Username", placeholder="3-20 characters, no spaces")
            reg_email = st.text_input("Email Address", placeholder="e.g. name@example.com")
            reg_password = st.text_input("Password", type="password", placeholder="At least 6 characters")
            submit = st.form_submit_button("Register Now", use_container_width=True)
            
            if submit:
                success, msg = auth.register_user(reg_username, reg_email, reg_password)
                if success:
                    # Auto-login immediately upon registration and land on dashboard
                    user_data = database.get_user(reg_username)
                    if user_data:
                        st.session_state.logged_in = True
                        st.session_state.user = {
                            "id": user_data["id"],
                            "username": user_data["username"],
                            "email": user_data["email"]
                        }
                        st.query_params["session_token"] = generate_session_token(user_data["username"])
                        st.success("🎉 Account created successfully! Logging you in...")
                        st.rerun()
                    else:
                        st.success(msg)
                else:
                    st.error(msg)

# ----------------- MAIN LOGGED IN APP -----------------
def render_main_app():
    user = st.session_state.user
    
    # --- Sidebar Setup ---
    with st.sidebar:
        st.markdown(f"### 👋 Welcome, **{user['username']}**")
        st.markdown(f"<span style='color: #64748B; font-size: 0.85rem;'>{user['email']}</span>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Navigation Options
        if st.button("🔍 New Resume Analysis", use_container_width=True, type="primary" if st.session_state.current_view == "new_analysis" else "secondary"):
            st.session_state.current_view = "new_analysis"
            st.session_state.active_analysis = None
            st.rerun()
            
        if st.button("📜 Analysis History", use_container_width=True, type="primary" if st.session_state.current_view == "history" else "secondary"):
            st.session_state.current_view = "history"
            st.session_state.active_analysis = None
            st.rerun()
            
        if st.button("⚙️ App Settings", use_container_width=True, type="primary" if st.session_state.current_view == "settings" else "secondary"):
            st.session_state.current_view = "settings"
            st.session_state.active_analysis = None
            st.rerun()
            
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("---")
            
        if st.button("🚪 Logout", use_container_width=True):
            handle_logout()

    # Route based on navigation selection
    if st.session_state.current_view == "new_analysis":
        render_new_analysis_page()
    elif st.session_state.current_view == "history":
        render_history_page()
    elif st.session_state.current_view == "settings":
        render_settings_page()

# ----------------- NEW ANALYSIS VIEW -----------------
def render_new_analysis_page():
    st.markdown('<h1 class="app-title">🔍 Resume ATS Match & AI Optimizer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Upload your resume PDF and match it against any job description. Get detailed keyword matching, code-based ATS scoring, and LLM-powered bridging suggestions.</p>', unsafe_allow_html=True)
    
    # Check if analysis detail is active
    if st.session_state.active_analysis:
        render_analysis_result(st.session_state.active_analysis)
        return

    # Entry Form
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📋 Step 1: Paste Job Description")
        job_title = st.text_input("Target Job Title", placeholder="e.g. Senior Full Stack Engineer", key="target_job_title")
        job_desc = st.text_area("Job Description Requirements", height=320, placeholder="Paste the job description keywords, responsibilities, and skill requirements here...", key="target_job_desc")
        
    with col2:
        st.markdown("### 📄 Step 2: Upload Resume")
        uploaded_file = st.file_uploader("Upload Resume (PDF format)", type=["pdf"], key="resume_uploader")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        analyze_btn = st.button("🚀 Analyze Fit & Optimize Resume", use_container_width=True)

    if analyze_btn:
        # Validation checks
        if not job_title.strip():
            st.error("Please enter the Target Job Title.")
            return
        if not job_desc.strip():
            st.error("Please paste the Job Description.")
            return
        if not uploaded_file:
            st.error("Please upload a PDF resume.")
            return
            
        # Retrieve key from secrets or env
        gemini_key = ""
        try:
            gemini_key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            pass
        if not gemini_key:
            gemini_key = st.session_state.gemini_api_key or os.getenv("GEMINI_API_KEY", "")
            
        if not gemini_key.strip():
            st.error("⚠️ Gemini API Key is missing. Please add it to the `.env` file in your project directory or configure it in your Streamlit dashboard secrets.")
            return
            
        with st.spinner("Processing PDF and analyzing ATS match score..."):
            try:
                # 1. Parse text from PDF
                raw_text = parser.extract_text_from_pdf(uploaded_file)
                if not raw_text.strip():
                    st.error("Could not extract any text from the PDF file. Please verify it is not an image-only PDF.")
                    return
                
                # 2. Run Code-based ATS Analyzer
                match_results = analyzer.calculate_ats_score(raw_text, job_desc, job_title)
                
                # 3. Call Gemini LLM for suggestions
                llm_results = llm_helper.get_llm_analysis(
                    resume_text=raw_text,
                    jd_text=job_desc,
                    score_details=match_results,
                    api_key=gemini_key
                )
                
                # Assemble final document
                analysis_results = {
                    "resume_name": uploaded_file.name,
                    "job_title": job_title,
                    "job_description": job_desc,
                    "ats_score": match_results["ats_score"],
                    "match_details": match_results,
                    "llm_feedback": llm_results,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Save to database
                database.save_analysis(
                    user_id=st.session_state.user["id"],
                    resume_name=uploaded_file.name,
                    job_title=job_title,
                    job_description=job_desc,
                    ats_score=match_results["ats_score"],
                    analysis_results=analysis_results
                )
                
                # Display Results
                st.session_state.active_analysis = analysis_results
                st.success("Analysis complete!")
                st.rerun()
                
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")

# ----------------- ANALYSIS RESULTS COMPONENT -----------------
def render_analysis_result(analysis):
    # Action buttons at top
    col_back, col_dl = st.columns([6, 2])
    with col_back:
        if st.button("⬅️ Back to Analysis", type="secondary"):
            st.session_state.active_analysis = None
            st.rerun()
            
    with col_dl:
        # Generate PDF bytes
        pdf_stream = report_generator.generate_resume_report(
            resume_name=analysis["resume_name"],
            job_title=analysis["job_title"],
            score_details=analysis["match_details"],
            llm_details=analysis["llm_feedback"]
        )
        
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_stream.getvalue(),
            file_name=f"ATS_Report_{analysis['job_title'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/octet-stream",
            use_container_width=True
        )
        
    st.markdown("---")
    
    # Metadata Overview
    st.markdown(f"## Target Role: **{analysis['job_title']}**")
    st.markdown(f"<p style='color: #64748B; font-size: 0.95rem;'>Analyzed file: <b>{analysis['resume_name']}</b> | Analysis Date: {analysis['created_at']}</p>", unsafe_allow_html=True)
    
    # Main Dashboards (Score & Summary)
    col_score, col_summary = st.columns([1, 2])
    
    with col_score:
        score = analysis["ats_score"]
        # Set dynamic colors based on score
        if score >= 75:
            circle_color = "#16A34A"  # Green
            text_color = "#16A34A"
            fit_label = "STRONG FIT"
        elif score >= 50:
            circle_color = "#EA580C"  # Amber/Orange
            text_color = "#EA580C"
            fit_label = "MODERATE FIT"
        else:
            circle_color = "#DC2626"  # Red
            text_color = "#DC2626"
            fit_label = "LOW MATCH"
            
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <h4 style="margin-bottom: 20px;">ATS MATCH SCORE</h4>
            <div class="score-circle" style="box-shadow: inset 0 0 0 10px var(--circle-ring), 0 0 0 4px {circle_color}; color: {text_color};">
                {score}%
            </div>
            <div style="font-weight: 800; font-size: 1.1rem; color: {text_color}; letter-spacing: 1px;">
                {fit_label}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_summary:
        decision = analysis['llm_feedback']['hiring_recommendation']
        # Colour-code badge by decision tier
        _badge_colors = {
            "Strong Hire":    ("background:#dcfce7; color:#166534; border:1px solid #86efac;", "✅"),
            "Hire":           ("background:#dbeafe; color:#1e40af; border:1px solid #93c5fd;", "👍"),
            "Borderline":     ("background:#fef9c3; color:#854d0e; border:1px solid #fde047;", "⚠️"),
            "No Hire":        ("background:#fee2e2; color:#991b1b; border:1px solid #fca5a5;", "❌"),
            "Strong No Hire": ("background:#fce7f3; color:#9d174d; border:1px solid #f9a8d4;", "🚫"),
        }
        badge_style, badge_icon = _badge_colors.get(decision, _badge_colors["Borderline"])
        st.markdown(f"""
        <div class="metric-card" style="height: 100%;">
            <h4 style="margin-top:0;">Evaluation Summary</h4>
            <p><b>Hiring Decision:</b>&nbsp;
                <span style="{badge_style} padding: 5px 12px; border-radius: 6px; font-weight:700; font-size:0.95rem;">
                    {badge_icon} {decision}
                </span>
            </p>
            <p style="line-height: 1.6;">{analysis['llm_feedback']['hiring_explanation']}</p>
        </div>
        """, unsafe_allow_html=True)


    # Breakdown Section via Tabs
    st.markdown("<br><h3>Detailed Evaluation Metrics</h3>", unsafe_allow_html=True)
    tab_skills, tab_detailed, tab_projects, tab_extraction = st.tabs([
        "🧩 Skills Gap Analysis", 
        "📝 Detailed Feedback", 
        "🛠️ Recommended Projects", 
        "ℹ️ Extracted Profile Details"
    ])
    
    # --- Tab 1: Skills Gap Analysis ---
    with tab_skills:
        st.markdown("Evaluate matching and missing skills required for this job description.")
        
        md_skills = analysis["match_details"]["matched_skills"]
        ms_skills = analysis["match_details"]["missing_skills"]
        
        sub_c1, sub_c2 = st.columns([1, 1])
        
        with sub_c1:
            st.markdown(f"#### ✅ Matched Skills ({len(md_skills)})")
            if md_skills:
                tags_html = "".join([f'<span class="tag tag-matched">{skill}</span>' for skill in sorted(md_skills)])
                st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
            else:
                st.info("No matching skills detected from our keyword dictionary. Try optimizing your resume keywords.")
                
        with sub_c2:
            st.markdown(f"#### ❌ Missing Skills ({len(ms_skills)})")
            if ms_skills:
                tags_html = "".join([f'<span class="tag tag-missing">{skill}</span>' for skill in sorted(ms_skills)])
                st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
            else:
                st.success("Excellent! You match all major skills identified from this job description.")
                
        # Category Breakdown
        st.markdown("<br><h4>Breakdown by Technical Categories</h4>", unsafe_allow_html=True)
        cat_breakdown = analysis["match_details"]["skills_by_category"]
        if cat_breakdown:
            for cat_name, info in cat_breakdown.items():
                with st.expander(f"📁 {cat_name} ({len(info['matched'])} matched, {len(info['missing'])} missing)"):
                    sc_col1, sc_col2 = st.columns(2)
                    with sc_col1:
                        st.markdown("**Matched:**")
                        if info["matched"]:
                            st.markdown(" ".join([f"`{s}`" for s in info["matched"]]))
                        else:
                            st.write("*None*")
                    with sc_col2:
                        st.markdown("**Missing:**")
                        if info["missing"]:
                            st.markdown(" ".join([f"`{s}`" for s in info["missing"]]))
                        else:
                            st.write("*None*")
        else:
            st.info("No skill categories matching the job requirements could be classified.")

    # --- Tab 2: Detailed Feedback (Strengths, Weaknesses, Suggestions) ---
    with tab_detailed:
        st.markdown("### Qualitative Assessment")
        
        d_col1, d_col2 = st.columns([1, 1])
        
        with d_col1:
            st.markdown("#### 💪 Key Strengths")
            for s in analysis["llm_feedback"].get("strengths", []):
                st.markdown(f'<div class="feedback-item">✅ {s}</div>', unsafe_allow_html=True)
                
        with d_col2:
            st.markdown("#### 🔍 Areas for Development")
            for w in analysis["llm_feedback"].get("weaknesses", []):
                st.markdown(f'<div class="feedback-item">⚠️ {w}</div>', unsafe_allow_html=True)
                
        st.markdown("---")
        st.markdown("#### 💡 Specific Suggestions for Resume Improvement")
        for sug in analysis["llm_feedback"].get("suggestions", []):
            st.markdown(f"- **Improvement:** {sug}")
            
    # --- Tab 3: Recommended Projects ---
    with tab_projects:
        st.markdown("### Actionable Skill-Bridging Projects")
        st.markdown("Implement these sample projects to demonstrate the missing skills required for this job description.")
        
        for idx, project in enumerate(analysis["llm_feedback"].get("recommended_projects", [])):
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin: 0 0 10px 0; color: #0284C7;">{idx+1}. {project.get('title', 'Recommended Project')}</h4>
                <p style="line-height: 1.6;">{project.get('description', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Technologies to Use:**")
            tech_html = "".join([f'<span class="tag tag-section">{t}</span>' for t in project.get("tech_stack", [])])
            st.markdown(f"<div>{tech_html}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    # --- Tab 4: Extracted Profile Details ---
    with tab_extraction:
        st.markdown("Heuristics and text sections detected from the uploaded resume file:")
        
        ex_col1, ex_col2 = st.columns([1, 1])
        
        with ex_col1:
            st.markdown("#### 📏 Metric Extraction")
            det_details = analysis["match_details"]
            st.write(f"- **Candidate Education Detected:** {det_details['candidate_education']}")
            st.write(f"- **Required Education in Job Description:** {det_details['required_education']}")
            st.write(f"- **Candidate Experience Detected:** {det_details['candidate_experience']} years")
            st.write(f"- **Required Experience in Job Description:** {det_details['required_experience']} years")
            
        with ex_col2:
            st.markdown("#### 📑 Detected Resume Sections")
            sections = det_details["detected_sections"]
            if sections:
                tags_html = "".join([f'<span class="tag tag-section">{sect}</span>' for sect in sections])
                st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
            else:
                st.write("*No major sections (Education, Experience, Projects, Skills) were explicitly detected by name.*")

# ----------------- HISTORY VIEW -----------------
def render_history_page():
    st.markdown('<h1 class="app-title">📜 Analysis History</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Review, delete, and view PDF reports of past resume evaluations.</p>', unsafe_allow_html=True)
    
    # Check if a specific past analysis is selected to display
    if st.session_state.active_analysis:
        render_analysis_result(st.session_state.active_analysis)
        return
        
    history = database.get_user_history(st.session_state.user["id"])
    
    if not history:
        st.info("You haven't run any resume analyses yet! Click 'New Resume Analysis' in the sidebar to start.")
        return
        
    # Search Filter
    search_query = st.text_input("🔍 Search History", placeholder="Search by job title or resume filename")
    
    # Process history list with filter
    filtered_history = []
    for item in history:
        if search_query:
            q = search_query.lower()
            if q not in item["job_title"].lower() and q not in item["resume_name"].lower():
                continue
        filtered_history.append(item)
        
    if not filtered_history:
        st.warning("No matches found for your search query.")
        return

    # List past reviews in structured rows
    for item in filtered_history:
        score = item["ats_score"]
        # Set dynamic colors based on score
        if score >= 75:
            score_color = "green"
            bg_badge = "#DEF7EC"
            fg_badge = "#03543F"
        elif score >= 50:
            score_color = "orange"
            bg_badge = "#FEF08A"
            fg_badge = "#854D0E"
        else:
            score_color = "red"
            bg_badge = "#FEE2E2"
            fg_badge = "#991B1B"
            
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.markdown(f"#### Target Role: **{item['job_title']}**")
                st.markdown(f"<span style='color: #64748B; font-size: 0.85rem;'>File: {item['resume_name']} | Date: {item['created_at']}</span>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div style="text-align: center; margin-top: 10px;">
                    <span style="background-color: {bg_badge}; color: {fg_badge}; font-weight:800; font-size:1.1rem; padding:8px 16px; border-radius:8px;">
                        {score}% Score
                    </span>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                # View details button
                if st.button("👁️ View Details", key=f"view_{item['id']}", use_container_width=True):
                    # Load analysis detail
                    st.session_state.active_analysis = item["analysis_results"]
                    st.rerun()
            with col4:
                # Delete button
                if st.button("🗑️ Delete Record", key=f"del_{item['id']}", use_container_width=True):
                    success = database.delete_history_item(st.session_state.user["id"], item["id"])
                    if success:
                        st.success("Record deleted.")
                        st.rerun()
                    else:
                        st.error("Failed to delete record.")
            st.markdown("---")

# ----------------- SETTINGS VIEW -----------------
def render_settings_page():
    st.markdown('<h1 class="app-title">⚙️ App Settings</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Manage your account profile and security settings.</p>', unsafe_allow_html=True)
    
    # Change Account Password section (Full width)
    st.markdown("### 🛡️ Change Account Password")
    st.write("Provide your old password and define a secure new password for authorization.")
    
    with st.form("change_pwd_form"):
        old_pwd = st.text_input("Current Password", type="password", placeholder="Enter current password")
        new_pwd = st.text_input("New Password", type="password", placeholder="At least 6 characters")
        new_pwd_confirm = st.text_input("Confirm New Password", type="password", placeholder="Re-enter new password")
        submit = st.form_submit_button("Update Password", use_container_width=True)
        
        if submit:
            if new_pwd != new_pwd_confirm:
                st.error("Passwords do not match.")
            else:
                success, msg = auth.change_user_password(
                    user_id=st.session_state.user["id"],
                    username=st.session_state.user["username"],
                    old_password=old_pwd,
                    new_password=new_pwd
                )
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

# ----------------- APP ORCHESTRATOR -----------------
if __name__ == "__main__":
    # --- Always Render Instant Zero-Delay Theme Toggle in Sidebar ---
    with st.sidebar:
        st.markdown("### 🌓 Application Theme")
        components.html("""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }
        body { background: transparent; overflow: hidden; }
        .toggle-box {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 14px;
            border-radius: 10px;
            border: 1.5px solid #CBD5E1;
            background-color: #FFFFFF;
            cursor: pointer;
            user-select: none;
            height: 44px;
        }
        .toggle-label {
            font-weight: 700;
            font-size: 0.92rem;
            color: #0F172A;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .switch-track {
            position: relative;
            width: 44px;
            height: 22px;
            border-radius: 22px;
            background-color: #CBD5E1;
            cursor: pointer;
        }
        .switch-knob {
            position: absolute;
            top: 3px;
            left: 3px;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background-color: #FFFFFF;
        }
        </style>
        </head>
        <body>
        <div id="toggleBox" class="toggle-box">
            <span id="labelSpan" class="toggle-label">
                <span id="themeIcon">☀️</span>
                <span id="themeText">Light Mode</span>
            </span>
            <div class="switch-track" id="switchTrack">
                <div class="switch-knob" id="switchKnob"></div>
            </div>
        </div>

        <script>
        (function() {
            var box = document.getElementById('toggleBox');
            var labelSpan = document.getElementById('labelSpan');
            var icon = document.getElementById('themeIcon');
            var text = document.getElementById('themeText');
            var track = document.getElementById('switchTrack');
            var knob = document.getElementById('switchKnob');

            function applyTheme(isDark) {
                var theme = isDark ? 'dark' : 'light';
                try {
                    var pDoc = window.parent.document;
                    pDoc.documentElement.setAttribute('data-theme', theme);
                    pDoc.body.setAttribute('data-theme', theme);
                    var app = pDoc.querySelector('.stApp');
                    if (app) app.setAttribute('data-theme', theme);
                    var sidebar = pDoc.querySelector('section[data-testid="stSidebar"]');
                    if (sidebar) sidebar.setAttribute('data-theme', theme);
                    window.parent.localStorage.setItem('app_theme_preference', theme);
                } catch(e) {}

                if (isDark) {
                    box.style.backgroundColor = '#1E293B';
                    box.style.borderColor = '#334155';
                    labelSpan.style.color = '#F1F5F9';
                    icon.innerText = '🌙';
                    text.innerText = 'Dark Mode';
                    track.style.backgroundColor = '#0284C7';
                    knob.style.left = '25px';
                } else {
                    box.style.backgroundColor = '#FFFFFF';
                    box.style.borderColor = '#CBD5E1';
                    labelSpan.style.color = '#0F172A';
                    icon.innerText = '☀️';
                    text.innerText = 'Light Mode';
                    track.style.backgroundColor = '#CBD5E1';
                    knob.style.left = '3px';
                }
            }

            var isDark = false;
            try {
                var saved = window.parent.localStorage.getItem('app_theme_preference');
                if (saved === 'dark') isDark = true;
            } catch(e) {}

            applyTheme(isDark);

            box.addEventListener('click', function() {
                isDark = !isDark;
                applyTheme(isDark);
            });
        })();
        </script>
        </body>
        </html>
        """, height=52)
        st.markdown("---")

    if st.session_state.logged_in:
        render_main_app()
    else:
        render_login_register()
