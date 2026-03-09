import streamlit as st
import asyncio
import subprocess
import json
import re
import pandas as pd
import time
import os
import sys


def _run_maigret(username, timeout=15, top_sites=500, use_all=False):
    """Run maigret as a subprocess and parse JSON output."""
    # Build a temp output path
    out_dir = os.path.join(os.path.dirname(__file__), "..", ".maigret_output")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{username}_{int(time.time())}")

    cmd = [
        sys.executable, "-m", "maigret",
        username,
        "--timeout", str(timeout),
        "--json", "ndjson",
        "--no-progressbar",
        "-o", out_file,
    ]

    if use_all:
        cmd.append("--use-all-sites")
    else:
        cmd.extend(["--top-sites", str(top_sites)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 min hard cap
        )
    except subprocess.TimeoutExpired:
        return None, "Maigret timed out after 5 minutes."
    except FileNotFoundError:
        return None, (
            "Maigret is not installed. Run: pip install maigret"
        )

    # Parse the ndjson output file
    ndjson_path = out_file + ".ndjson"
    if not os.path.exists(ndjson_path):
        # Try the regular json path
        json_path = out_file + ".json"
        if os.path.exists(json_path):
            try:
                with open(json_path, "r") as f:
                    data = json.load(f)
                os.remove(json_path)
                return data, None
            except Exception as e:
                return None, f"Error reading output: {e}"
        return None, f"No output file found. Stderr: {result.stderr[:500] if result.stderr else 'none'}"

    records = []
    try:
        with open(ndjson_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        os.remove(ndjson_path)
    except Exception as e:
        return None, f"Error parsing output: {e}"

    return records, None


def _parse_maigret_results(records):
    """Parse maigret output records into a clean list of dicts."""
    results = []
    if not records:
        return results

    # Handle both list-of-dicts (ndjson) and dict-of-dicts formats
    if isinstance(records, dict):
        items = records.values() if isinstance(list(records.values())[0], dict) else [records]
    elif isinstance(records, list):
        items = records
    else:
        return results

    for item in items:
        if not isinstance(item, dict):
            continue

        status = item.get("status", "")
        # Only include claimed/found accounts
        if status and "Claimed" not in str(status) and "Found" not in str(status):
            continue

        site_name = item.get("siteName", item.get("site_name", item.get("name", "Unknown")))
        url = item.get("url_user", item.get("url", ""))
        tags = item.get("tags", [])
        if isinstance(tags, list):
            tags = ", ".join(tags)

        results.append({
            "site": site_name,
            "url": url,
            "status": "Found",
            "tags": tags,
        })

    return results


def render():
    """Render the Username Hunter powered by Maigret."""
    st.header("ð Username Hunter")
    st.write("Search **3,000+ sites** for a username using [Maigret](https://github.com/soxoj/maigret) â "
             "an advanced OSINT username search engine with profile data extraction.")

    # Username input
    username = st.text_input("Enter username to search:", placeholder="e.g., john_doe")

    # Options
    col1, col2 = st.columns(2)
    with col1:
        timeout = st.slider("Per-site timeout (seconds)", 5, 30, 15)
    with col2:
        scope = st.radio("Search scope", ["Top 500 sites", "All 3,000+ sites"], horizontal=True)

    use_all = scope == "All 3,000+ sites"
    top_sites = 500

    if st.button("ð Hunt Username", type="primary"):
        if not username:
            st.error("Please enter a username.")
            return

        # Validate username (basic)
        if not re.match(r'^[\w.\-]{1,100}$', username):
            st.error("Username must be 1-100 characters: letters, numbers, underscores, hyphens, periods.")
            return

        with st.spinner(f"Searching {'all 3,000+' if use_all else 'top 500'} sites for **{username}**... This may take a few minutes."):
            records, error = _run_maigret(username, timeout=timeout, top_sites=top_sites, use_all=use_all)

        if error:
            st.error(f"Error: {error}")
            return

        results = _parse_maigret_results(records)

        if not results:
            st.warning(f"No accounts found for **{username}**.")
            return

        # Display results
        st.success(f"Found **{len(results)}** account(s) for **{username}**")

        df = pd.DataFrame(results)

        # Summary
        st.subheader("Results")

        # Make URLs clickable
        display_df = df.copy()
        display_df["url"] = display_df["url"].apply(
            lambda x: f'<a href="{x}" target="_blank">{x}</a>' if x else ""
        )
        display_df.columns = ["Site", "URL", "Status", "Tags"]

        st.markdown(
            display_df.to_html(escape=False, index=False),
            unsafe_allow_html=True
        )

        # Export
        csv = df.to_csv(index=False)
        st.download_button(
            label="ð¥ Export to CSV",
            data=csv,
            file_name=f"username_hunt_{username}_{int(time.time())}.csv",
            mime="text/csv"
        )

        # Tag filter
        if "tags" in df.columns:
            all_tags = set()
            for t in df["tags"]:
                if t:
                    for tag in str(t).split(", "):
                        if tag.strip():
                            all_tags.add(tag.strip())
            if all_tags:
                st.subheader("Filter by Tag")
                selected_tag = st.selectbox("Filter results by site category:", ["All"] + sorted(all_tags))
                if selected_tag != "All":
                    filtered = df[df["tags"].str.contains(selected_tag, na=False)]
                    st.write(f"**{len(filtered)}** result(s) tagged **{selected_tag}**:")
                    filt_display = filtered.copy()
                    filt_display["url"] = filt_display["url"].apply(
                        lambda x: f'<a href="{x}" target="_blank">{x}</a>' if x else ""
                    )
                    filt_display.columns = ["Site", "URL", "Status", "Tags"]
                    st.markdown(
                        filt_display.to_html(escape=False, index=False),
                        unsafe_allow_html=True
                    )
