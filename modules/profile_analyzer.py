import streamlit as st
import requests
import json

# User-Agent to mimic a real browser
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def _fetch_page(url, cookies=None):
    """Fetch a URL and return its HTML text."""
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=15, cookies=cookies, allow_redirects=True)
        resp.raise_for_status()
        return resp.text, None
    except requests.exceptions.RequestException as e:
        return None, str(e)


def _extract_profile(html_text):
    """Extract profile data using socid_extractor."""
    try:
        from socid_extractor import extract
    except ImportError:
        return None, "socid_extractor is not installed. Run: pip install socid-extractor"

    try:
        data = extract(html_text)
        return data, None
    except Exception as e:
        return None, f"Extraction error: {e}"


def _categorize_fields(data):
    """Organize extracted fields into logical categories."""
    categories = {
        "Identity": [],
        "Contact": [],
        "Social Links": [],
        "Statistics": [],
        "Location": [],
        "Bio & About": [],
        "Other": [],
    }

    identity_keys = {"fullname", "name", "username", "nickname", "first_name", "last_name",
                     "display_name", "real_name", "id", "uid", "user_id", "gender", "age",
                     "birth_date", "birthday"}
    contact_keys = {"email", "phone", "website", "homepage"}
    link_keys = {"links", "url", "profile_url", "social_links"}
    stat_keys = {"followers", "following", "subscribers", "posts", "likes",
                 "views", "comments", "reputation", "karma", "rating", "score",
                 "friends", "connections"}
    location_keys = {"location", "city", "country", "state", "region", "timezone"}
    bio_keys = {"bio", "about", "description", "tagline", "headline", "summary",
                "status", "occupation", "company", "job_title", "education"}

    for key, value in data.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        k = key.lower()
        if any(ik in k for ik in identity_keys):
            categories["Identity"].append((key, value))
        elif any(ck in k for ck in contact_keys):
            categories["Contact"].append((key, value))
        elif any(lk in k for lk in link_keys):
            categories["Social Links"].append((key, value))
        elif any(sk in k for sk in stat_keys):
            categories["Statistics"].append((key, value))
        elif any(lok in k for lok in location_keys):
            categories["Location"].append((key, value))
        elif any(bk in k for bk in bio_keys):
            categories["Bio & About"].append((key, value))
        else:
            categories["Other"].append((key, value))

    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def render():
    """Render the Profile Analyzer UI."""
    st.header("ð§¬ Profile Analyzer")
    st.write(
        "Extract structured personal data from social media profile pages using "
        "[socid-extractor](https://github.com/soxoj/socid-extractor). "
        "Supports 100+ platforms including GitHub, Reddit, Medium, TikTok, Instagram, "
        "Facebook, VK, Flickr, Tumblr, and more."
    )

    # Input mode
    mode = st.radio("Input mode:", ["Profile URL", "Raw HTML"], horizontal=True)

    html_text = None
    source_label = ""

    if mode == "Profile URL":
        url = st.text_input(
            "Enter a social media profile URL:",
            placeholder="https://github.com/username"
        )

        # Optional cookies for platforms that need them
        with st.expander("Advanced: Cookies (optional)"):
            st.caption(
                "Some platforms (Google, Yandex) require cookies to avoid CAPTCHAs. "
                "Paste cookie string as `name=value; name2=value2`"
            )
            cookie_str = st.text_area("Cookie string:", height=60)

        if st.button("ð Analyze Profile", type="primary"):
            if not url:
                st.error("Please enter a profile URL.")
                return

            cookies = {}
            if cookie_str:
                for pair in cookie_str.split(";"):
                    pair = pair.strip()
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        cookies[k.strip()] = v.strip()

            with st.spinner(f"Fetching and analyzing {url}..."):
                html_text, err = _fetch_page(url, cookies=cookies or None)
                if err:
                    st.error(f"Failed to fetch URL: {err}")
                    return
                source_label = url

    elif mode == "Raw HTML":
        html_input = st.text_area(
            "Paste HTML source of a profile page:",
            height=200,
            placeholder="<html>...</html>"
        )

        if st.button("ð Analyze HTML", type="primary"):
            if not html_input or len(html_input.strip()) < 50:
                st.error("Please paste valid HTML content (at least 50 characters).")
                return
            html_text = html_input
            source_label = "Pasted HTML"

    # Process if we have HTML
    if html_text:
        with st.spinner("Extracting profile data..."):
            data, err = _extract_profile(html_text)

        if err:
            st.error(err)
            return

        if not data:
            st.warning(
                "No profile data could be extracted. This may mean the page isn't a recognized "
                "profile format, or the platform requires authentication/cookies."
            )
            return

        # Show results
        st.success(f"Extracted **{len(data)}** field(s) from {source_label}")

        # Categorized display
        categories = _categorize_fields(data)

        for cat_name, fields in categories.items():
            with st.expander(f"**{cat_name}** ({len(fields)} fields)", expanded=True):
                for key, value in fields:
                    # Handle lists of links
                    if isinstance(value, list):
                        st.write(f"**{key}:**")
                        for item in value:
                            if isinstance(item, str) and item.startswith("http"):
                                st.markdown(f"  - [{item}]({item})")
                            else:
                                st.write(f"  - {item}")
                    elif isinstance(value, str) and value.startswith("http"):
                        st.markdown(f"**{key}:** [{value}]({value})")
                    else:
                        st.write(f"**{key}:** {value}")

        # Raw JSON export
        st.subheader("Raw Data")
        with st.expander("View raw extracted JSON"):
            # Convert any non-serializable values
            clean = {}
            for k, v in data.items():
                if v is not None:
                    clean[k] = v
            st.json(clean)

        # Download as JSON
        json_str = json.dumps(data, indent=2, default=str, ensure_ascii=False)
        st.download_button(
            label="ð¥ Download as JSON",
            data=json_str,
            file_name=f"profile_data_{int(__import__('time').time())}.json",
            mime="application/json"
        )
