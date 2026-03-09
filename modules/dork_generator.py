import streamlit as st
from urllib.parse import quote


def render():
    st.header("Google Dork Query Generator")
    st.write("Generate targeted Google search queries to find sensitive information about a target.")

    col1, col2 = st.columns([3, 1])
    with col1:
        target = st.text_input("Enter target name or domain", placeholder="example.com or Company Name")
    with col2:
        generate_button = st.button("Generate Dorks", key="dork_gen_btn")

    st.subheader("Select Categories")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        social_media = st.checkbox("Social Media")
        documents = st.checkbox("Documents")
    with col2:
        login_pages = st.checkbox("Login Pages")
        sensitive_files = st.checkbox("Sensitive Files")
    with col3:
        email_discovery = st.checkbox("Email Discovery")
        phone_numbers = st.checkbox("Phone Numbers")
    with col4:
        exposed_db = st.checkbox("Exposed Databases")
        cached_pages = st.checkbox("Cached Pages")

    if generate_button and target:
        generate_dorks(target, social_media, documents, login_pages, sensitive_files, email_discovery, phone_numbers, exposed_db, cached_pages)
    elif generate_button and not target:
        st.error("Please enter a target name or domain")


def generate_dorks(target, social_media, documents, login_pages, sensitive_files, email_discovery, phone_numbers, exposed_db, cached_pages):
    dorks = {}
    if social_media:
        dorks["Social Media"] = [f'"{target}" site:linkedin.com', f'"{target}" site:twitter.com', f'"{target}" site:facebook.com', f'"{target}" site:instagram.com', f'"{target}" site:reddit.com']
    if documents:
        dorks["Documents"] = [f'"{target}" filetype:pdf', f'"{target}" filetype:docx', f'"{target}" filetype:xlsx', f'"{target}" filetype:pptx', f'"{target}" site:scribd.com']
    if login_pages:
        dorks["Login Pages"] = [f'inurl:login site:{target}', f'inurl:admin site:{target}', f'inurl:signin site:{target}', f'inurl:authenticate site:{target}', f'"login" site:{target}']
    if sensitive_files:
        dorks["Sensitive Files"] = [f'site:{target} inurl:backup', f'site:{target} inurl:config', f'site:{target} filetype:sql', f'site:{target} filetype:bak', f'site:{target} inurl:database']
    if email_discovery:
        dorks["Email Discovery"] = [f'"{target}" "@{target}" email', f'"{target}" "contact us"', f'site:{target} "@{target}"', f'"{target}" filetype:vcf', f'"{target}" employee email']
    if phone_numbers:
        dorks["Phone Numbers"] = [f'"{target}" "phone"', f'"{target}" "+1"', f'"{target}" filetype:vcf', f'site:{target} "tel:"', f'"{target}" contact inurl:about']
    if exposed_db:
        dorks["Exposed Databases"] = [f'"{target}" inurl:phpmyadmin', f'"{target}" "database" filetype:sql', f'site:{target} ".sql"', f'"{target}" exposed database', f'site:pastebin.com "{target}"']
    if cached_pages:
        dorks["Cached Pages"] = [f'cache:{target}', f'cache:www.{target}', f'"{target}" cache:']

    if dorks:
        st.subheader("Generated Google Dork Queries")
        st.write(f"Target: **{target}**")
        st.write("---")
        for category, queries in dorks.items():
            with st.expander(f"📌 {category} ({len(queries)} queries)"):
                for query in queries:
                    encoded_query = quote(query)
                    google_url = f"https://www.google.com/search?q={encoded_query}"
                    st.markdown(f"[🔍 {query}]({google_url})")
                    st.write(f"```\n{query}\n```")
        st.info("📝 Click any link above to perform the Google search.")
    else:
        st.warning("Please select at least one category to generate dorks.")
