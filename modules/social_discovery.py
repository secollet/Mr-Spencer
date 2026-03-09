import streamlit as st
from urllib.parse import quote


def render():
    st.header("Social Media Profile Finder")
    st.write("Search for social media profiles across major platforms.")

    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Enter full name", placeholder="John Doe")
    with col2:
        email = st.text_input("Enter email (optional)", placeholder="john@example.com")

    if st.button("Search Profiles", key="social_search_btn"):
        if full_name or email:
            search_profiles(full_name, email)
        else:
            st.error("Please enter a name or email address")


def search_profiles(full_name, email):
    platforms = {
        "LinkedIn": "site:linkedin.com",
        "Twitter/X": "site:twitter.com",
        "Facebook": "site:facebook.com",
        "Instagram": "site:instagram.com",
        "TikTok": "site:tiktok.com",
        "YouTube": "site:youtube.com",
        "Reddit": "site:reddit.com",
        "GitHub": "site:github.com",
        "Pinterest": "site:pinterest.com",
        "Medium": "site:medium.com",
    }

    st.subheader("Search Results")

    if full_name:
        st.write(f"**Searching for:** {full_name}")
        st.write("---")
        for platform, domain in platforms.items():
            query = f'"{full_name}" {domain}'
            google_url = f"https://www.google.com/search?q={quote(query)}"
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"🔗 {platform}")
            with col2:
                st.markdown(f"[Search]({google_url})")

    if email:
        st.write(f"**Email searches:** {email}")
        st.write("---")
        for platform, domain in platforms.items():
            query = f'"{email}" {domain}'
            google_url = f"https://www.google.com/search?q={quote(query)}"
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"📧 {platform}")
            with col2:
                st.markdown(f"[Search]({google_url})")

    st.info("💡 Click the search links to see results.")
    with st.expander("📌 Advanced Search Tips"):
        st.write("- Use exact name matches for more precise results\n- Try name variations\n- Add company name to narrow results")
