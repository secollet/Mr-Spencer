import streamlit as st
import subprocess
import json
import time
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse
from io import BytesIO
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows


def initialize_session_state():
    """Initialize session state for dynamic lists."""
    if 'aliases' not in st.session_state:
        st.session_state.aliases = ['']
    if 'handles' not in st.session_state:
        st.session_state.handles = ['']
    if 'excluded_accounts' not in st.session_state:
        st.session_state.excluded_accounts = ['']


def add_list_item(list_key):
    """Add another item to a dynamic list."""
    st.session_state[list_key].append('')


def render_dynamic_list(label, session_key, placeholder=""):
    """Render a dynamic list input with 'Add Another' button."""
    st.write(f"**{label}**")

    items = []
    cols = st.columns([1, 0.15])

    with cols[0]:
        for i, item in enumerate(st.session_state[session_key]):
            st.session_state[session_key][i] = st.text_input(
                f"{label} {i+1}",
                value=item,
                placeholder=placeholder,
                label_visibility="collapsed",
                key=f"{session_key}_{i}"
            )

    with cols[1]:
        if st.button("Add", key=f"btn_{session_key}", use_container_width=True):
            add_list_item(session_key)
            st.rerun()

    return [item.strip() for item in st.session_state[session_key] if item.strip()]


def check_yt_dlp_installed():
    """Check if yt-dlp is installed."""
    try:
        subprocess.run(['yt-dlp', '--version'],
                      capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def enrich_metadata_with_yt_dlp(video_url):
    """Enrich video metadata using yt-dlp."""
    try:
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--no-download',
            '--socket-timeout', '10',
            video_url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                return {
                    'upload_date': data.get('upload_date', ''),
                    'description': data.get('description', ''),
                    'uploader': data.get('uploader', ''),
                    'channel_url': data.get('channel_url', ''),
                }
            except json.JSONDecodeError:
                return {}

        return {}

    except Exception:
        return {}


def build_search_queries(target_name, aliases, handles, selected_platforms):
    """Build Google search queries for each platform and name variant."""
    platforms = {
        'YouTube': {'site_domain': 'youtube.com'},
        'Vimeo': {'site_domain': 'vimeo.com'},
        'Rumble': {'site_domain': 'rumble.com'},
        'Dailymotion': {'site_domain': 'dailymotion.com'},
        'Archive.org': {'site_domain': 'archive.org'},
        'Twitter/X': {'site_domain': 'twitter.com'},
        'Instagram': {'site_domain': 'instagram.com'},
        'TikTok': {'site_domain': 'tiktok.com'},
        'Facebook': {'site_domain': 'facebook.com'},
    }

    search_tasks = []

    # Build search tasks
    for platform_name, site_domain in platforms.items():
        if platform_name not in selected_platforms:
            continue

        # Search by name
        search_tasks.append((platform_name, site_domain['site_domain'], target_name, target_name))

        # Search by each alias
        for alias in aliases:
            if alias.strip():
                search_tasks.append((platform_name, site_domain['site_domain'], alias.strip(), alias))

        # Search by each handle
        for handle in handles:
            if handle.strip():
                search_tasks.append((platform_name, site_domain['site_domain'], handle.strip(), handle))

    return search_tasks


def search_google_for_videos(query, site_domain, session):
    """Search Google for video URLs on a specific platform domain."""
    google_query = f"{query} site:{site_domain} video"
    search_url = f"https://www.google.com/search?q={quote_plus(google_query)}"

    try:
        response = session.get(search_url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract video URLs
        results = []
        for link in soup.find_all('a', href=True):
            href = link['href']

            if site_domain in href:
                if '/url?q=' in href:
                    clean_url = href.split('/url?q=')[1].split('&')[0]
                else:
                    clean_url = href

                if 'google.com' in clean_url:
                    continue

                title = link.get_text() or 'Unknown'

                results.append({
                    'Link': clean_url,
                    'Source Platform': '',
                    'Date Published': 'Unknown',
                    'Video Title': title,
                    'Description': '',
                    'Uploader/Channel Name': '',
                    'Channel URL': '',
                    'Tagged Handles Found': query if query.startswith('@') else ''
                })

        time.sleep(2)  # Rate limiting
        return results

    except requests.RequestException as e:
        st.warning(f"Error searching {site_domain} for {query}: {str(e)}")
        return []
    except Exception as e:
        st.warning(f"Unexpected error searching {site_domain}: {str(e)}")
        return []


def search_youtube(target_name, aliases, handles, excluded_accounts, progress_bar):
    """Search for content on YouTube via Google scraping."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    results = []

    # Build search queries for YouTube
    search_names = [target_name] + [a for a in aliases if a.strip()]
    search_names += [h for h in handles if h.strip()]

    total_queries = len(search_names)

    for idx, name in enumerate(search_names):
        progress_percent = int((idx / max(total_queries, 1)) * 20)
        progress_bar.progress(min(progress_percent, 20))

        query_results = search_google_for_videos(name, 'youtube.com', session)
        for r in query_results:
            r['Source Platform'] = 'YouTube'
            r['Tagged Handles Found'] = name if name.startswith('@') else ''
        results.extend(query_results)

        time.sleep(1)

    # Enrich with yt-dlp metadata
    for result in results:
        metadata = enrich_metadata_with_yt_dlp(result['Link'])
        if metadata:
            if metadata.get('upload_date'):
                date_str = metadata['upload_date']
                try:
                    result['Date Published'] = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                except (IndexError, ValueError):
                    pass
            if metadata.get('description'):
                result['Description'] = metadata['description'][:200]
            if metadata.get('uploader'):
                result['Uploader/Channel Name'] = metadata['uploader']
            if metadata.get('channel_url'):
                result['Channel URL'] = metadata['channel_url']

    return results


def search_google_videos(target_name, aliases, handles, selected_platforms, progress_bar, progress_offset):
    """Search Google for videos on selected platforms (non-YouTube)."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    # Build tasks for non-YouTube platforms
    search_tasks = build_search_queries(target_name, aliases, handles, selected_platforms)
    search_tasks = [(p, s, q, n) for p, s, q, n in search_tasks if p != 'YouTube']

    total_tasks = len(search_tasks)
    results = []

    for task_idx, (platform, site_domain, query, query_type) in enumerate(search_tasks):
        progress_percent = progress_offset + int((task_idx / max(total_tasks, 1)) * 25)
        progress_bar.progress(min(progress_percent, 50))

        query_results = search_google_for_videos(query, site_domain, session)

        for r in query_results:
            r['Source Platform'] = platform

        results.extend(query_results)

        time.sleep(1)

    # Try to enrich with yt-dlp where supported
    for result in results:
        metadata = enrich_metadata_with_yt_dlp(result['Link'])
        if metadata:
            if metadata.get('upload_date'):
                date_str = metadata['upload_date']
                try:
                    result['Date Published'] = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                except (IndexError, ValueError):
                    pass
            if metadata.get('description'):
                result['Description'] = metadata['description'][:200]
            if metadata.get('uploader'):
                result['Uploader/Channel Name'] = metadata['uploader']
            if metadata.get('channel_url'):
                result['Channel URL'] = metadata['channel_url']

    return results


def search_social_tagged_content(target_name, handles, progress_bar, progress_offset):
    """Search for social media tagged content featuring the target."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    platforms = {
        'Twitter/X': 'twitter.com',
        'Instagram': 'instagram.com',
        'TikTok': 'tiktok.com',
        'Facebook': 'facebook.com',
    }

    search_tasks = []

    for platform_name, site_domain in platforms.items():
        # Search by handle
        for handle in handles:
            if handle.strip():
                search_tasks.append((platform_name, site_domain, handle.strip(), handle))

        # Search by name
        search_tasks.append((platform_name, site_domain, target_name, target_name))

    total_tasks = len(search_tasks)
    results = []

    for task_idx, (platform, site_domain, query, query_type) in enumerate(search_tasks):
        progress_percent = progress_offset + int((task_idx / max(total_tasks, 1)) * 30)
        progress_bar.progress(min(progress_percent, 85))

        try:
            # Build Google query
            google_query = f"{query} site:{site_domain} video"
            search_url = f"https://www.google.com/search?q={quote_plus(google_query)}"

            response = session.get(search_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            for link in soup.find_all('a', href=True):
                href = link['href']

                if site_domain in href:
                    if '/url?q=' in href:
                        clean_url = href.split('/url?q=')[1].split('&')[0]
                    else:
                        clean_url = href

                    if 'google.com' in clean_url:
                        continue

                    title = link.get_text() or 'Unknown'

                    results.append({
                        'Link': clean_url,
                        'Source Platform': platform,
                        'Date Published': 'Unknown',
                        'Video Title': title,
                        'Description': '',
                        'Uploader/Channel Name': '',
                        'Channel URL': '',
                        'Tagged Handles Found': query if query.startswith('@') else ''
                    })

            time.sleep(2)  # Rate limiting

        except requests.RequestException as e:
            st.warning(f"Error searching {platform} for {query}: {str(e)}")
        except Exception as e:
            st.warning(f"Unexpected error searching {platform}: {str(e)}")

    return results


def deduplicate_results(results):
    """Remove duplicate URLs from results."""
    seen_urls = set()
    unique = []

    for result in results:
        url = result.get('Link', '')
        if url not in seen_urls:
            seen_urls.add(url)
            unique.append(result)

    return unique


def apply_exclude_filter(results, exclude_urls):
    """Filter out results matching excluded account URLs."""
    if not exclude_urls:
        return results

    filtered = []

    for result in results:
        link = result.get('Link', '')
        should_exclude = False

        for exclude in exclude_urls:
            if exclude.strip() and exclude.strip() in link:
                should_exclude = True
                break

        if not should_exclude:
            filtered.append(result)

    return filtered


def export_to_excel(df):
    """Export dataframe to Excel bytes."""
    output = BytesIO()

    # Use pandas to write to Excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Video Finder Results')

        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Video Finder Results']

        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass

            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    output.seek(0)
    return output


def run_video_finder():
    """Main video finder function."""
    st.header("Video Finder - OSINT Investigation")
    st.write("Search for videos featuring a target individual across multiple platforms.")

    # Initialize session state
    initialize_session_state()

    # UI Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        target_name = st.text_input(
            "Target Name",
            placeholder="Enter the target individual's name",
            key="target_name_input"
        )

    st.divider()

    # Aliases section
    aliases = render_dynamic_list("Aliases", "aliases", placeholder="Alternative names/spellings")

    st.divider()

    # Social Media Handles
    handles = render_dynamic_list(
        "Social Media Handles",
        "handles",
        placeholder="@username format"
    )

    st.divider()

    # Excluded Accounts
    excluded_accounts = render_dynamic_list(
        "Target's Own Accounts to Exclude",
        "excluded_accounts",
        placeholder="Channel/profile URL to filter OUT"
    )

    st.divider()

    # Optional Keywords
    keywords = st.text_input(
        "Optional Keywords",
        placeholder="e.g., conference, interview, speech (optional)"
    )

    st.divider()

    # Platform selection
    st.write("**Select Platforms to Search**")
    platform_cols = st.columns(3)

    platforms_options = [
        'YouTube', 'Vimeo', 'Rumble', 'Dailymotion', 'Archive.org',
        'Twitter/X', 'Instagram', 'TikTok', 'Facebook'
    ]

    selected_platforms = []
    for idx, platform in enumerate(platforms_options):
        col_idx = idx % 3
        with platform_cols[col_idx]:
            if st.checkbox(platform, value=True, key=f"platform_{platform}"):
                selected_platforms.append(platform)

    st.divider()

    # Search button
    search_button = st.button("\U0001f50d Search Videos", type="primary", use_container_width=True)

    if search_button:
        # Validation
        if not target_name.strip():
            st.error("Please enter a target name.")
            return

        # Check yt-dlp installation
        if not check_yt_dlp_installed():
            st.error(
                "yt-dlp is not installed. Please install it with: `pip install yt-dlp`"
            )
            return

        # Create progress bar and status areas
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        results_placeholder = st.empty()

        all_results = []

        try:
            # Phase 1: YouTube search
            status_placeholder.info("Phase 1/4: Searching YouTube...")
            youtube_results = search_youtube(
                target_name,
                aliases,
                handles,
                excluded_accounts,
                progress_bar
            )
            all_results.extend(youtube_results)
            st.write(f"Found {len(youtube_results)} YouTube videos")

            # Phase 2: Google scraping for video platforms
            status_placeholder.info("Phase 2/4: Searching video platforms (Vimeo, Rumble, etc.)...")
            video_platform_results = search_google_videos(
                target_name,
                aliases,
                handles,
                selected_platforms,
                progress_bar,
                25
            )
            all_results.extend(video_platform_results)
            st.write(f"Found {len(video_platform_results)} videos on other platforms")

            # Phase 3: Social media tagged content
            status_placeholder.info("Phase 3/4: Searching social media tagged content...")
            social_results = search_social_tagged_content(
                target_name,
                handles,
                progress_bar,
                50
            )
            all_results.extend(social_results)
            st.write(f"Found {len(social_results)} social media videos")

            # Phase 4: Deduplication and filtering
            status_placeholder.info("Phase 4/4: Processing and deduplicating results...")
            progress_bar.progress(90)

            all_results = deduplicate_results(all_results)
            st.write(f"After deduplication: {len(all_results)} unique videos")

            all_results = apply_exclude_filter(all_results, excluded_accounts)
            st.write(f"After filtering excluded accounts: {len(all_results)} videos")

            progress_bar.progress(100)
            status_placeholder.success(f"Search complete! Found {len(all_results)} videos.")

            # Display results
            if all_results:
                df = pd.DataFrame(all_results)

                # Remove Channel URL column from display (internal use only)
                display_df = df[['Link', 'Source Platform', 'Date Published',
                                 'Video Title', 'Description', 'Uploader/Channel Name',
                                 'Tagged Handles Found']]

                st.subheader("Search Results")
                st.dataframe(display_df, use_container_width=True, hide_index=True)

                # Export button
                excel_bytes = export_to_excel(display_df)
                st.download_button(
                    label="\U0001f4e5 Download as Excel (.xlsx)",
                    data=excel_bytes,
                    file_name="video_finder_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Statistics
                st.subheader("Search Statistics")
                stats_col1, stats_col2, stats_col3 = st.columns(3)

                with stats_col1:
                    st.metric("Total Videos Found", len(all_results))

                with stats_col2:
                    platform_counts = display_df['Source Platform'].value_counts()
                    st.metric("Platforms with Results", len(platform_counts))

                with stats_col3:
                    st.metric("With Known Upload Dates",
                             len(display_df[display_df['Date Published'] != 'Unknown']))

            else:
                st.warning("No videos found matching your search criteria.")

        except Exception as e:
            status_placeholder.error(f"An error occurred during search: {str(e)}")
            st.exception(e)


render = run_video_finder

if __name__ == "__main__":
    run_video_finder()
