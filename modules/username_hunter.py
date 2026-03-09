import streamlit as st
import requests
import json
import re
import pandas as pd
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


# User-Agent to mimic a real browser
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def _load_sites():
    """Load sites.json from the project root."""
    sites_path = os.path.join(os.path.dirname(__file__), "..", "sites.json")
    try:
        with open(sites_path, "r") as f:
            sites = json.load(f)
        # Filter out sites with broken URL templates (e.g., double {})
        valid = []
        for site in sites:
            url_template = site.get("url", "")
            if "{}" in url_template and url_template.count("{}") == 1:
                valid.append(site)
        return valid
    except Exception as e:
        st.error(f"Failed to load sites.json: {e}")
        return []


def _check_site(site, username, timeout=10):
    """Check if a username exists on a given site by HTTP status code."""
    url = site["url"].replace("{}", username)
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        # Consider 200 as found; some sites return 200 for everything,
        # but this is the best we can do without per-site logic
        if resp.status_code == 200:
            return {
                "site": site["name"],
                "url": url,
                "status": "Found",
                "http_code": resp.status_code,
            }
        else:
            return {
                "site": site["name"],
                "url": url,
                "status": "Not Found",
                "http_code": resp.status_code,
            }
    except requests.exceptions.Timeout:
        return {
            "site": site["name"],
            "url": url,
            "status": "Timeout",
            "http_code": None,
        }
    except requests.exceptions.ConnectionError:
        return {
            "site": site["name"],
            "url": url,
            "status": "Connection Error",
            "http_code": None,
        }
    except Exception:
        return {
            "site": site["name"],
            "url": url,
            "status": "Error",
            "http_code": None,
        }


def render():
    """Render the Username Hunter UI."""
    st.header("ð Username Hunter")
    st.write(
        "Search **{}+ sites** for a username by checking profile URLs directly."
    )

    sites = _load_sites()
    if not sites:
        st.error("No sites loaded. Ensure sites.json exists in the project root.")
        return

    # Update the header with actual count
    st.write(f"Loaded **{len(sites)}** sites to check.")

    # Username input
    username = st.text_input("Enter username to search:", placeholder="e.g., john_doe")

    # Options
    col1, col2 = st.columns(2)
    with col1:
        timeout = st.slider("Per-site timeout (seconds)", 3, 15, 8)
    with col2:
        max_workers = st.slider("Concurrent checks", 5, 30, 15)

    show_all = st.checkbox("Show all results (including Not Found)", value=False)

    if st.button("ð Hunt Username", type="primary"):
        if not username:
            st.error("Please enter a username.")
            return

        # Validate username
        if not re.match(r'^[\w.\-]{1,100}$', username):
            st.error("Username must be 1-100 characters: letters, numbers, underscores, hyphens, periods.")
            return

        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.info(f"Checking {len(sites)} sites for **{username}**...")

        results = []
        completed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_check_site, site, username, timeout): site
                for site in sites
            }

            for future in as_completed(futures):
                completed += 1
                progress_bar.progress(completed / len(sites))
                result = future.result()
                if result:
                    results.append(result)

        progress_bar.progress(1.0)

        # Separate found vs not found
        found = [r for r in results if r["status"] == "Found"]
        not_found = [r for r in results if r["status"] != "Found"]

        status_text.success(f"Done! Found **{len(found)}** account(s) for **{username}** across {len(sites)} sites.")

        if found:
            st.subheader(f"â Found ({len(found)})")
            df_found = pd.DataFrame(found)
            # Make URLs clickable
            display_df = df_found[["site", "url", "status"]].copy()
            display_df["url"] = display_df["url"].apply(
                lambda x: f'<a href="{x}" target="_blank">{x}</a>' if x else ""
            )
            display_df.columns = ["Site", "URL", "Status"]
            st.markdown(
                display_df.to_html(escape=False, index=False),
                unsafe_allow_html=True,
            )

            # Export
            export_df = pd.DataFrame(found)
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="ð¥ Export Found to CSV",
                data=csv,
                file_name=f"username_hunt_{username}_{int(time.time())}.csv",
                mime="text/csv",
            )

        if show_all and not_found:
            st.subheader(f"â Not Found / Errors ({len(not_found)})")
            df_nf = pd.DataFrame(not_found)
            display_nf = df_nf[["site", "url", "status"]].copy()
            display_nf.columns = ["Site", "URL", "Status"]
            st.dataframe(display_nf, use_container_width=True, hide_index=True)
