import streamlit as st

st.set_page_config(
    page_title="Mr. Spencer — OSINT Tool",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark detective theme
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #E8E8E8;
        text-align: center;
        margin-bottom: 0;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #888;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stRadio > label {
        font-size: 1.05rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("# 🕵️ Mr. Spencer")
    st.markdown("*Open Source Intelligence Tool*")
    st.markdown("---")

    tool = st.radio(
        "Select Tool",
        [
            "🔍 Username Hunter",
            "🧬 Profile Analyzer",
            "📧 Email Investigator",
            "🌐 Domain WHOIS",
            "🎯 Google Dork Generator",
            "👥 Social Discovery",
            "🖼️ Reverse Image Search",
            "📜 Wayback Machine",
            "🎬 Video Finder",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption("Mr. Spencer v1.0")

# Main content area
st.markdown('<p class="main-title">🕵️ Mr. Spencer</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Open Source Intelligence Investigation Tool</p>', unsafe_allow_html=True)

# Route to the selected tool
if tool == "🔍 Username Hunter":
    from modules.username_hunter import render
    render()
elif tool == "🧬 Profile Analyzer":
    from modules.profile_analyzer import render
    render()
elif tool == "📧 Email Investigator":
    from modules.email_investigator import render
    render()
elif tool == "🌐 Domain WHOIS":
    from modules.domain_whois import render
    render()
elif tool == "🎯 Google Dork Generator":
    from modules.dork_generator import render
    render()
elif tool == "👥 Social Discovery":
    from modules.social_discovery import render
    render()
elif tool == "🖼️ Reverse Image Search":
    from modules.reverse_image import render
    render()
elif tool == "📜 Wayback Machine":
    from modules.wayback_machine import render
    render()
elif tool == "🎬 Video Finder":
    from modules.video_finder import render
    render()
