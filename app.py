import streamlit as st
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
    initial_sidebar_state="expanded"
)

# Initialize database
database.init_db()

# Premium Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Premium Title styling */
    .app-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1E293B, #0284C7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .app-subtitle {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 2rem;
    }
    
    /* Custom Card Design */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: 16px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
    }
    
    /* Tag Styling */
    .tag {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px;
    }
    .tag-matched {
        background-color: #DEF7EC;
        color: #03543F;
        border: 1px solid #BCF0DA;
    }
    .tag-missing {
        background-color: #FEF08A;
        color: #854D0E;
        border: 1px solid #FDE047;
    }
    .tag-section {
        background-color: #E0F2FE;
        color: #0369A1;
        border: 1px solid #BAE6FD;
    }
    
    /* Bullet list overrides */
    .feedback-item {
        padding: 8px 0;
        border-bottom: 1px solid #F1F5F9;
    }
    
    /* Login Box Container */
    .auth-container {
        max-width: 480px;
        margin: 80px auto;
        padding: 40px;
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
    }
    
    /* Score display circular badge */
    .score-circle {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 140px;
        height: 140px;
        border-radius: 50%;
        margin: 0 auto 15px auto;
        font-size: 2.2rem;
        font-weight: 800;
        box-shadow: inset 0 0 0 12px #F1F5F9;
    }
</style>
""", unsafe_allow_html=True)

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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "gemini_api_key" not in st.session_state:
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
    st.markdown('<h1 style="text-align: center; font-weight:800; margin-top: 50px;">🔍 AI Resume Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #64748B;">Upload resumes, evaluate ATS fit, get bridging projects suggestions, and download PDF reports.</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
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
                    # Persist session query params across refreshes
                    st.query_params["session_token"] = generate_session_token(user_data["username"])
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with tab2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.subheader("Create a new account")
        with st.form("register_form"):
            reg_username = st.text_input("Username", placeholder="3-20 characters, no spaces")
            reg_email = st.text_input("Email Address", placeholder="e.g. name@example.com")
            reg_password = st.text_input("Password", type="password", placeholder="At least 6 characters")
            submit = st.form_submit_button("Register Now", use_container_width=True)
            
            if submit:
                success, msg = auth.register_user(reg_username, reg_email, reg_password)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)

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
            
        # Retrieve key from session state or env
        gemini_key = st.session_state.gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        if not gemini_key.strip():
            st.error("⚠️ Gemini API Key is missing. Please add it to the `.env` file in your project directory (e.g. `GEMINI_API_KEY=your_key`) and restart/refresh the application.")
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
            <h4 style="margin-bottom: 20px; color: #1E293B;">ATS MATCH SCORE</h4>
            <div class="score-circle" style="box-shadow: inset 0 0 0 10px #F1F5F9, 0 0 0 4px {circle_color}; color: {text_color};">
                {score}%
            </div>
            <div style="font-weight: 800; font-size: 1.1rem; color: {text_color}; letter-spacing: 1px;">
                {fit_label}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_summary:
        st.markdown(f"""
        <div class="metric-card" style="height: 100%;">
            <h4 style="color: #1E293B; margin-top:0;">Evaluation Summary</h4>
            <p><b>Hiring Decision:</b> <span style="background-color: #E2E8F0; padding: 4px 8px; border-radius: 4px; font-weight:bold;">{analysis['llm_feedback']['hiring_recommendation']}</span></p>
            <p style="line-height: 1.6; color: #334155;">{analysis['llm_feedback']['hiring_explanation']}</p>
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
                <p style="color: #475569; line-height: 1.6;">{project.get('description', '')}</p>
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
    if st.session_state.logged_in:
        render_main_app()
    else:
        render_login_register()
