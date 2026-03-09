import streamlit as st
from urllib.parse import quote


def _is_domain(target: str) -> bool:
    """Check if the target looks like a domain name."""
    # Simple heuristic: contains a dot and no spaces
    return "." in target and " " not in target.strip()


def render():
    """Render the Google Dork query generator."""
    st.header("ð¯ Google Dork Generator")

    st.write("Generate targeted Google search queries to find information about a person or domain.")

    # Input
    col1, col2 = st.columns([3, 1])
    with col1:
        target = st.text_input(
            "Enter target name or domain",
            placeholder="John Doe or example.com"
        )
    with col2:
        generate_button = st.button("Generate Dorks", key="dork_gen_btn", type="primary")

    is_domain = _is_domain(target) if target else False

    if target:
        st.caption(f"Detected target type: **{'Domain' if is_domain else 'Person/Name'}**")

    # Categories
    st.subheader("Select Categories")

    if is_domain:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            social_media = st.checkbox("Social Media Mentions")
            documents = st.checkbox("Documents")
        with col2:
            login_pages = st.checkbox("Login Pages")
            sensitive_files = st.checkbox("Sensitive Files")
        with col3:
            email_discovery = st.checkbox("Email Discovery")
            phone_numbers = st.checkbox("Phone Numbers")
        with col4:
            exposed_db = st.checkbox("Exposed Data")
            cached_pages = st.checkbox("Cached Pages")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            social_media = st.checkbox("Social Media Profiles")
            documents = st.checkbox("Documents & Files")
        with col2:
            email_discovery = st.checkbox("Email Discovery")
            phone_numbers = st.checkbox("Phone Numbers")
        with col3:
            news_mentions = st.checkbox("News & Media")
            public_records = st.checkbox("Public Records")

        # These don't apply to person searches
        login_pages = False
        sensitive_files = False
        exposed_db = False
        cached_pages = False

    if generate_button and target:
        if is_domain:
            _generate_domain_dorks(
                target, social_media, documents, login_pages,
                sensitive_files, email_discovery, phone_numbers,
                exposed_db, cached_pages
            )
        else:
            _generate_person_dorks(
                target, social_media, documents, email_discovery,
                phone_numbers, news_mentions, public_records
            )
    elif generate_button and not target:
        st.error("Please enter a target name or domain")


def _generate_person_dorks(target, social_media, documents, email_discovery,
                           phone_numbers, news_mentions, public_records):
    """Generate dorks for a person/name search."""
    dorks = {}

    if social_media:
        dorks["Social Media Profiles"] = [
            f'"{target}" site:linkedin.com',
            f'"{target}" site:twitter.com OR site:x.com',
            f'"{target}" site:facebook.com',
            f'"{target}" site:instagram.com',
            f'"{target}" site:reddit.com',
            f'"{target}" site:tiktok.com',
            f'"{target}" site:youtube.com',
            f'"{target}" site:github.com',
        ]

    if documents:
        dorks["Documents & Files"] = [
            f'"{target}" filetype:pdf',
            f'"{target}" filetype:docx',
            f'"{target}" filetype:xlsx',
            f'"{target}" filetype:pptx',
            f'"{target}" site:scribd.com',
            f'"{target}" site:slideshare.net',
            f'"{target}" site:issuu.com',
            f'"{target}" filetype:csv',
        ]

    if email_discovery:
        dorks["Email Discovery"] = [
            f'"{target}" email',
            f'"{target}" "@gmail.com" OR "@yahoo.com" OR "@outlook.com"',
            f'"{target}" "contact" email',
            f'"{target}" filetype:vcf',
            f'"{target}" site:hunter.io OR site:rocketreach.co',
        ]

    if phone_numbers:
        dorks["Phone Numbers"] = [
            f'"{target}" phone',
            f'"{target}" "phone" OR "tel" OR "cell" OR "mobile"',
            f'"{target}" "+1" OR "(555)" OR "(xxx)"',
            f'"{target}" "contact us" phone',
        ]

    if news_mentions:
        dorks["News & Media"] = [
            f'"{target}" site:reuters.com OR site:apnews.com',
            f'"{target}" site:bbc.com OR site:cnn.com',
            f'"{target}" site:nytimes.com OR site:washingtonpost.com',
            f'"{target}" inurl:news OR inurl:article',
            f'"{target}" "press release"',
            f'"{target}" "interview" OR "quoted"',
        ]

    if public_records:
        dorks["Public Records"] = [
            f'"{target}" site:whitepages.com OR site:spokeo.com',
            f'"{target}" site:beenverified.com OR site:truepeoplesearch.com',
            f'"{target}" site:courtlistener.com OR site:unicourt.com',
            f'"{target}" "public record" OR "court record"',
            f'"{target}" site:opencorporates.com',
            f'"{target}" site:sec.gov',
        ]

    _display_dorks(dorks, target)


def _generate_domain_dorks(target, social_media, documents, login_pages,
                           sensitive_files, email_discovery, phone_numbers,
                           exposed_db, cached_pages):
    """Generate dorks for a domain search."""
    dorks = {}

    if social_media:
        dorks["Social Media Mentions"] = [
            f'"{target}" site:linkedin.com',
            f'"{target}" site:twitter.com OR site:x.com',
            f'"{target}" site:facebook.com',
            f'"{target}" site:reddit.com',
            f'"{target}" site:youtube.com',
        ]

    if documents:
        dorks["Documents"] = [
            f'site:{target} filetype:pdf',
            f'site:{target} filetype:docx',
            f'site:{target} filetype:xlsx',
            f'site:{target} filetype:pptx',
            f'"{target}" filetype:pdf',
        ]

    if login_pages:
        dorks["Login Pages"] = [
            f'site:{target} inurl:login',
            f'site:{target} inurl:admin',
            f'site:{target} inurl:signin',
            f'site:{target} intitle:"login" OR intitle:"sign in"',
            f'site:{target} inurl:portal',
        ]

    if sensitive_files:
        dorks["Sensitive Files"] = [
            f'site:{target} filetype:sql',
            f'site:{target} filetype:bak',
            f'site:{target} filetype:log',
            f'site:{target} filetype:env',
            f'site:{target} filetype:conf OR filetype:cfg',
            f'site:{target} inurl:backup',
            f'site:{target} inurl:config',
        ]

    if email_discovery:
        dorks["Email Discovery"] = [
            f'"@{target}" email',
            f'site:{target} "email" OR "contact"',
            f'"@{target}" filetype:vcf',
            f'"{target}" employee email directory',
        ]

    if phone_numbers:
        dorks["Phone Numbers"] = [
            f'site:{target} "phone" OR "tel:"',
            f'"{target}" phone directory',
            f'site:{target} "contact us"',
        ]

    if exposed_db:
        dorks["Exposed Data"] = [
            f'site:{target} inurl:phpmyadmin',
            f'site:{target} "database" filetype:sql',
            f'site:{target} intitle:"index of"',
            f'site:{target} "error" "sql"',
            f'site:pastebin.com "{target}"',
            f'site:github.com "{target}" password OR token OR secret',
        ]

    if cached_pages:
        dorks["Cached Pages"] = [
            f'cache:{target}',
            f'cache:www.{target}',
        ]

    _display_dorks(dorks, target)


def _display_dorks(dorks, target):
    """Display generated dork queries with clickable links."""
    if dorks:
        st.subheader("Generated Google Dork Queries")
        st.write(f"Target: **{target}**")
        st.write("---")

        for category, queries in dorks.items():
            with st.expander(f"ð {category} ({len(queries)} queries)", expanded=True):
                for query in queries:
                    # Create clickable Google search link
                    encoded_query = quote(query)
                    google_url = f"https://www.google.com/search?q={encoded_query}"

                    st.markdown(
                        f"[ð {query}]({google_url})",
                        unsafe_allow_html=False
                    )
                    st.code(query, language=None)

        st.info(
            "ð Click any link above to perform the Google search. "
            "Use these results ethically and responsibly."
        )
    else:
        st.warning("Please select at least one category to generate dorks.")
