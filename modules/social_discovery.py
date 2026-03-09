import streamlit as st
import requests
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote


# User-Agent to mimic a real browser
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Platforms with direct profile URL patterns
PLATFORMS = [
    {"name": "GitHub", "url": "https://github.com/{}", "icon": "ð»"},
    {"name": "Twitter/X", "url": "https://x.com/{}", "icon": "ð¦"},
    {"name": "Instagram", "url": "https://www.instagram.com/{}", "icon": "ð¸"},
    {"name": "TikTok", "url": "https://www.tiktok.com/@{}", "icon": "ðµ"},
    {"name": "YouTube", "url": "https://www.youtube.com/@{}", "icon": "ð¬"},
    {"name": "Reddit", "url": "https://www.reddit.com/user/{}", "icon": "ð¤"},
    {"name": "LinkedIn", "url": "https://www.linkedin.com/in/{}", "icon": "ð¼"},
    {"name": "Pinterest", "url": "https://www.pinterest.com/{}/", "icon": "ð"},
    {"name": "Twitch", "url": "https://www.twitch.tv/{}", "icon": "ð®"},
    {"name": "Snapchat", "url": "https://www.snapchat.com/add/{}", "icon": "ð»"},
    {"name": "Medium", "url": "https://medium.com/@{}", "icon": "ð"},
    {"name": "Dev.to", "url": "https://dev.to/{}", "icon": "ð©âð»"},
    {"name": "Behance", "url": "https://www.behance.net/{}", "icon": "ð¨"},
    {"name": "Dribbble", "url": "https://dribbble.com/{}", "icon": "ð"},
    {"name": "SoundCloud", "url": "https://soundcloud.com/{}", "icon": "ðµ"},
    {"name": "Spotify", "url": "https://open.spotify.com/user/{}", "icon": "ð§"},
    {"name": "Flickr", "url": "https://www.flickr.com/photos/{}", "icon": "ð·"},
    {"name": "Vimeo", "url": "https://vimeo.com/{}", "icon": "ð¥"},
    {"name": "Steam", "url": "https://steamcommunity.com/id/{}/", "icon": "ð®"},
    {"name": "Patreon", "url": "https://www.patreon.com/{}", "icon": "ð°"},
    {"name": "Substack", "url": "https://substack.com/@{}", "icon": "ð°"},
    {"name": "Linktree", "url": "https://linktr.ee/{}", "icon": "ð"},
    {"name": "Keybase", "url": "https://keybase.io/{}", "icon": "ð"},
    {"name": "About.me", "url": "https://about.me/{}", "icon": "ð¤"},
    {"name": "Gravatar", "url": "https://gravatar.com/{}", "icon": "ð"},
    {"name": "GitLab", "url": "https://gitlab.com/{}", "icon": "ð¦"},
    {"name": "HackerNews", "url": "https://news.ycombinator.com/user?id={}", "icon": "ð°"},
    {"name": "Product Hunt", "url": "https://www.producthunt.com/@{}", "icon": "ð"},
    {"name": "Quora", "url": "https://www.quora.com/profile/{}", "icon": "â"},
    {"name": "Tumblr", "url": "https://{}.tumblr.com/", "icon": "ð"},
    {"name": "Mastodon", "url": "https://mastodon.social/@{}", "icon": "ð¦£"},
    {"name": "Bluesky", "url": "https://bsky.app/profile/{}", "icon": "ð¦"},
    {"name": "Ko-fi", "url": "https://ko-fi.com/{}", "icon": "â"},
    {"name": "Buy Me A Coffee", "url": "https://www.buymeacoffee.com/{}", "icon": "â"},
    {"name": "Cash App", "url": "https://cash.app/${}", "icon": "ðµ"},
    {"name": "Letterboxd", "url": "https://letterboxd.com/{}", "icon": "ð¬"},
    {"name": "Goodreads", "url": "https://www.goodreads.com/user/show/{}", "icon": "ð"},
    {"name": "Last.fm", "url": "https://www.last.fm/user/{}", "icon": "ð¶"},
    {"name": "MyAnimeList", "url": "https://myanimelist.net/profile/{}", "icon": "ð"},
    {"name": "Duolingo", "url": "https://www.duolingo.com/profile/{}", "icon": "ð¦"},
]


def _check_profile(platform, username, timeout=8):
    """Check if a profile exists on a platform."""
    url = platform["url"].replace("{}", username)
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        if resp.status_code == 200:
            return {
                "platform": platform["name"],
                "icon": platform["icon"],
                "url": url,
                "status": "Found",
            }
        return None
    except Exception:
        return None


def render():
    """Render the Social Discovery UI."""
    st.header("ð¥ Social Discovery")
    st.write(
        "Find social media accounts by checking profile URLs directly across 40+ platforms. "
        "Enter a username to discover which platforms have an account with that name."
    )

    # Input
    username = st.text_input(
        "Enter username to search:",
        placeholder="e.g., johndoe"
    )

    col1, col2 = st.columns(2)
    with col1:
        timeout = st.slider("Per-site timeout (seconds)", 3, 15, 8)
    with col2:
        max_workers = st.slider("Concurrent checks", 5, 25, 15)

    search_button = st.button("ð Find Social Profiles", type="primary")

    if search_button:
        if not username:
            st.error("Please enter a username.")
            return

        username = username.strip().lstrip("@")

        if not re.match(r'^[\w.\-]{1,100}$', username):
            st.error("Username must be 1-100 characters: letters, numbers, underscores, hyphens, periods.")
            return

        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.info(f"Checking {len(PLATFORMS)} platforms for **{username}**...")

        found_profiles = []
        completed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_check_profile, platform, username, timeout): platform
                for platform in PLATFORMS
            }

            for future in as_completed(futures):
                completed += 1
                progress_bar.progress(completed / len(PLATFORMS))
                result = future.result()
                if result:
                    found_profiles.append(result)

        progress_bar.progress(1.0)

        if found_profiles:
            status_text.success(
                f"Found **{len(found_profiles)}** profile(s) for **{username}** "
                f"across {len(PLATFORMS)} platforms."
            )

            st.subheader("Found Profiles")

            for profile in sorted(found_profiles, key=lambda x: x["platform"]):
                st.markdown(
                    f"{profile['icon']} **{profile['platform']}** â "
                    f"[{profile['url']}]({profile['url']})"
                )

        else:
            status_text.warning(f"No profiles found for **{username}** across {len(PLATFORMS)} platforms.")

        # Also offer Google search as fallback
        st.subheader("Additional Searches")
        st.write("Try these Google searches for more results:")
        google_queries = [
            (f'"{username}" social media profile', "General search"),
            (f'"{username}" site:linkedin.com', "LinkedIn"),
            (f'"{username}" site:facebook.com', "Facebook"),
        ]
        for query, label in google_queries:
            encoded = quote(query)
            st.markdown(f"ð [{label}](https://www.google.com/search?q={encoded})")
