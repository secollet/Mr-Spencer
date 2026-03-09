import streamlit as st
import requests
from datetime import datetime


def render():
    st.header("Wayback Machine Archive Checker")
    st.write("Search for archived snapshots of a URL using the Internet Archive's Wayback Machine.")
    col1, col2 = st.columns([3, 1])
    with col1:
        url = st.text_input("Enter URL to check", placeholder="https://example.com")
    with col2:
        search_button = st.button("Check Archives", key="wayback_btn")
    if search_button and url:
        check_wayback_archives(url)
    elif search_button and not url:
        st.error("Please enter a URL")


def check_wayback_archives(url):
    st.subheader("Archive Results")
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    st.write(f"**URL:** {url}")
    st.write("---")
    try:
        with st.spinner("Searching Wayback Machine..."):
            cdx_api_url = "https://web.archive.org/cdx/search/cdx"
            params = {'url': url, 'output': 'json', 'limit': 50}
            response = requests.get(cdx_api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if len(data) <= 1:
                st.warning("No archived snapshots found for this URL.")
                return
            snapshots = data[1:]
            if not snapshots:
                st.warning("No archived snapshots found for this URL.")
                return
            snapshot_list = []
            for snapshot in snapshots:
                if len(snapshot) >= 2:
                    timestamp = snapshot[1]
                    snapshot_list.append({'timestamp': timestamp, 'datetime': parse_timestamp(timestamp)})
            if snapshot_list:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Snapshots", len(snapshot_list))
                with col2:
                    st.metric("Earliest Capture", snapshot_list[0]['datetime'].strftime("%Y-%m-%d"))
                with col3:
                    st.metric("Latest Capture", snapshot_list[-1]['datetime'].strftime("%Y-%m-%d"))
                st.write("---")
                st.subheader(f"📅 {len(snapshot_list)} Snapshots Found")
                for i, snapshot in enumerate(reversed(snapshot_list)):
                    timestamp = snapshot['timestamp']
                    dt = snapshot['datetime']
                    archive_url = f"https://web.archive.org/web/{timestamp}/{url}"
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.write(f"**{dt.strftime('%Y-%m-%d %H:%M:%S')}**")
                    with col2:
                        st.write(f"ID: {timestamp}")
                    with col3:
                        st.markdown(f"[View Archive]({archive_url})")
            else:
                st.warning("Could not parse archive data.")
    except requests.exceptions.Timeout:
        st.error("Request timed out. The Wayback Machine may be experiencing high traffic.")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to Wayback Machine: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    with st.expander("ℹ️ About the Wayback Machine", expanded=False):
        st.write("The Wayback Machine is an internet archive that has captured billions of web pages. Use it to view historical versions of websites, check when content was added/removed, and find cached versions of deleted pages.")


def parse_timestamp(timestamp_str):
    try:
        return datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
    except ValueError:
        return datetime.now()
