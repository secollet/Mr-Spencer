import streamlit as st
from urllib.parse import quote


def render():
    """Render the Reverse image search link generator."""
    st.header("Reverse Image Search")

    st.write("Generate reverse image search links to find the source or usage of an image.")

    # Input
    col1, col2 = st.columns([3, 1])
    with col1:
        image_url = st.text_input(
            "Enter image URL",
            placeholder="https://example.com/image.jpg"
        )
    with col2:
        search_button = st.button("Generate Links", key="reverse_image_btn")

    if search_button and image_url:
        generate_reverse_search_links(image_url)
    elif search_button and not image_url:
        st.error("Please enter an image URL")


def generate_reverse_search_links(image_url):
    """Generate reverse image search links for major search engines."""

    st.subheader("Reverse Search Links")

    image_url = image_url.strip()
    if not image_url.startswith(('http://', 'https://')):
        st.error("Please enter a valid URL starting with http:// or https://")
        return

    search_engines = {
        "Google Images": {
            "url": f"https://www.google.com/searchbyimage?image_url={quote(image_url)}",
            "icon": "🔍",
            "description": "Google's reverse image search - finds similar images and source websites"
        },
        "TinEye": {
            "url": f"https://www.tineye.com/search?url={quote(image_url)}",
            "icon": "👁️",
            "description": "TinEye specializes in finding image sources and usage history"
        },
        "Yandex Images": {
            "url": f"https://www.yandex.com/images/search?rpt=imageview&url={quote(image_url)}",
            "icon": "🎨",
            "description": "Yandex reverse search - good for finding images not in Google"
        },
        "Bing Visual Search": {
            "url": f"https://www.bing.com/images/search?view=detailv2&iss=sbiupload&FORM=SBIR&sbisrc=ImgDropper&q=imgurl:{quote(image_url)}",
            "icon": "🔷",
            "description": "Microsoft Bing's reverse image search"
        }
    }

    st.write(f"**Image URL:** {image_url}")
    st.write("---")

    for service, details in search_engines.items():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**{details['icon']} {service}**")
            st.write(f"*{details['description']}*")
        with col2:
            st.markdown(f"[🔗 Search]({details['url']})", unsafe_allow_html=False)
        st.write("---")

    with st.expander("📖 How to Use Each Service", expanded=False):
        st.write("""
        **Google Images:** Most comprehensive reverse search. Shows visually similar images and websites using the image.

        **TinEye:** Tracks image history and modifications. Excellent for finding original sources.

        **Yandex Images:** Often finds images not indexed by Google. Particularly effective for international content.

        **Bing Visual Search:** Microsoft's visual search platform with AI technology.
        """)

    with st.expander("💡 Tips for Reverse Image Search", expanded=False):
        st.write("""
        - Use multiple services for comprehensive results
        - Crop distinctive parts of images for better matches
        - Try different search engines as results vary
        - Check image metadata for EXIF information
        - Use reverse search to verify if images are authentic
        """)
