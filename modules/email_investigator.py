import streamlit as st
import dns.resolver
import hashlib
import requests
import subprocess
import sys
import re
from urllib.parse import quote


def render():
    """Main render function for the email investigator module."""
    st.header("ð§ Email Investigator")
    st.write("Investigate email addresses and discover emails from usernames â no API keys required.")

    # Two modes
    mode = st.radio(
        "Investigation mode:",
        ["Investigate a known email", "Find emails by username (Mailcat)"],
        horizontal=True
    )

    if mode == "Investigate a known email":
        _render_email_investigation()
    else:
        _render_mailcat_search()


# âââââââââââââââââââââââââââââââââââââââââââââ
# MODE 1: Investigate a known email
# âââââââââââââââââââââââââââââââââââââââââââââ

def _render_email_investigation():
    """Original email investigation UI."""
    email = st.text_input(
        "Enter email address to investigate:",
        placeholder="example@domain.com"
    )

    if not email or "@" not in email:
        st.info("Enter a valid email address to begin investigation.")
        return

    email_lower = email.lower().strip()
    domain = email_lower.split("@")[1]

    # Email Verification Section
    with st.expander("Email Verification", expanded=True):
        st.subheader("MX Record Verification")
        mx_records = _check_mx_records(domain)
        if mx_records:
            st.success(f"Domain has {len(mx_records)} valid mail server(s)")
            for priority, mx_host in mx_records:
                st.write(f"- Priority {priority}: {mx_host}")
        else:
            st.warning("No MX records found for this domain")

    # Social Detection Section
    with st.expander("Social Platform Detection"):
        st.subheader("Check Linked Social Accounts")
        social_results = _check_social_platforms(email_lower)

        if social_results["gravatar"]:
            st.success("Gravatar Account Found")
            st.write(f"[View Gravatar Profile](https://gravatar.com/{social_results['gravatar_hash']})")
        else:
            st.write("No Gravatar account found")

        if social_results["github"]:
            st.success("GitHub Account(s) Found")
            for user in social_results["github"]:
                st.write(f"- [{user['login']}]({user['html_url']})")
        else:
            st.write("No GitHub accounts found with this email")

    # DNS Lookups Section
    with st.expander("DNS Records for Domain"):
        st.subheader(f"DNS Information for {domain}")

        st.write("**MX Records (Mail Servers):**")
        mx_records = _check_mx_records(domain)
        if mx_records:
            for priority, host in mx_records:
                st.write(f"- {host} (Priority: {priority})")
        else:
            st.write("No MX records found")

        st.write("**TXT Records (SPF, DKIM, DMARC):**")
        txt_records = _get_txt_records(domain)
        if txt_records:
            for record in txt_records:
                st.write(f"- {record}")
        else:
            st.write("No TXT records found")

        st.write("**A Records:**")
        a_records = _get_a_records(domain)
        if a_records:
            for record in a_records:
                st.write(f"- {record}")
        else:
            st.write("No A records found")

        st.write("**NS Records (Name Servers):**")
        ns_records = _get_ns_records(domain)
        if ns_records:
            for record in ns_records:
                st.write(f"- {record}")
        else:
            st.write("No NS records found")

    # Related Emails Section
    with st.expander("Email Variations"):
        st.subheader("Generated Email Variations to Investigate")
        variations = _generate_email_variations(email_lower)

        if variations:
            st.write("Common variations of this email:")
            for variation in variations:
                st.write(f"- `{variation}`")
        else:
            st.write("Could not generate variations for this email format")

    # Pastebin Search Section
    with st.expander("Paste Site Searches"):
        st.subheader("Search Email on Paste Sites")
        st.write("Click the links below to search for this email on common paste sites:")

        dork_links = _generate_dork_links(email_lower)
        for site_name, dork_url in dork_links:
            st.markdown(f"[Search {site_name}]({dork_url})", unsafe_allow_html=False)


# âââââââââââââââââââââââââââââââââââââââââââââ
# MODE 2: Find emails by username (Mailcat)
# âââââââââââââââââââââââââââââââââââââââââââââ

def _render_mailcat_search():
    """Find existing email addresses for a username using mailcat."""
    st.write(
        "Powered by [Mailcat](https://github.com/sharsil/mailcat) â "
        "checks 37+ email providers (170+ domains) to find which email "
        "addresses exist for a given username. Uses SMTP, API, and "
        "recovery page checks. **Does not notify the account holder.**"
    )

    username = st.text_input(
        "Enter username / nickname:",
        placeholder="e.g., johndoe"
    )

    with st.expander("Options"):
        col1, col2 = st.columns(2)
        with col1:
            use_tor = st.checkbox("Use Tor (recommended for anonymity)", value=False)
        with col2:
            proxy = st.text_input("HTTP Proxy (optional):", placeholder="http://1.2.3.4:8080")

    if st.button("ð Search Email Providers", type="primary"):
        if not username:
            st.error("Please enter a username.")
            return

        if not re.match(r'^[\w.\-]{1,64}$', username):
            st.error("Username must be 1-64 characters: letters, numbers, underscores, hyphens, periods.")
            return

        with st.spinner(f"Checking email providers for **{username}**..."):
            results, error = _run_mailcat(username, use_tor=use_tor, proxy=proxy)

        if error:
            st.error(f"Error: {error}")
            return

        if not results:
            st.warning(f"No email accounts found for username **{username}**.")
            return

        st.success(f"Found **{len(results)}** email address(es) for **{username}**")

        for email_addr in results:
            provider = email_addr.split("@")[1] if "@" in email_addr else "Unknown"
            st.markdown(f"- `{email_addr}` ({provider})")

        # Quick action: investigate any found email
        st.subheader("Quick Actions")
        st.write("Switch to **Investigate a known email** mode above and paste any of these addresses to dig deeper.")


def _run_mailcat(username, use_tor=False, proxy=None):
    """Run mailcat as a subprocess and parse output."""
    cmd = [sys.executable, "-m", "mailcat", username]

    if use_tor:
        cmd.append("--tor")
    if proxy:
        cmd.extend(["--proxy", proxy])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return None, "Mailcat timed out after 2 minutes."
    except FileNotFoundError:
        return None, "Mailcat is not installed. Run: pip install mailcat"

    # Parse output â mailcat prints found emails to stdout
    output = result.stdout.strip()
    if not output:
        # Check stderr for errors
        if result.stderr:
            # Filter out progress/info lines
            err_lines = [l for l in result.stderr.strip().split("\n")
                         if "error" in l.lower() or "exception" in l.lower()]
            if err_lines:
                return None, "\n".join(err_lines)
        return [], None

    # Extract email addresses from output
    emails = []
    email_pattern = re.compile(r'[\w.\-+]+@[\w.\-]+\.\w+')
    for line in output.split("\n"):
        line = line.strip()
        found = email_pattern.findall(line)
        emails.extend(found)

    # Deduplicate while preserving order
    seen = set()
    unique_emails = []
    for e in emails:
        if e.lower() not in seen:
            seen.add(e.lower())
            unique_emails.append(e)

    return unique_emails, None


# âââââââââââââââââââââââââââââââââââââââââââââ
# Helper functions (unchanged from original)
# âââââââââââââââââââââââââââââââââââââââââââââ

def _check_mx_records(domain: str) -> list:
    """Check MX records for a domain."""
    try:
        mx_records = dns.resolver.resolve(domain, "MX")
        results = []
        for mx in mx_records:
            results.append((mx.preference, str(mx.exchange).rstrip(".")))
        return sorted(results, key=lambda x: x[0])
    except Exception:
        return []


def _get_txt_records(domain: str) -> list:
    """Get TXT records for a domain."""
    try:
        txt_records = dns.resolver.resolve(domain, "TXT")
        return [str(txt) for txt in txt_records]
    except Exception:
        return []


def _get_a_records(domain: str) -> list:
    """Get A records for a domain."""
    try:
        a_records = dns.resolver.resolve(domain, "A")
        return [str(a) for a in a_records]
    except Exception:
        return []


def _get_ns_records(domain: str) -> list:
    """Get NS records for a domain."""
    try:
        ns_records = dns.resolver.resolve(domain, "NS")
        return [str(ns).rstrip(".") for ns in ns_records]
    except Exception:
        return []


def _check_social_platforms(email: str) -> dict:
    """Check if email is linked to social platforms."""
    results = {
        "gravatar": False,
        "gravatar_hash": None,
        "github": []
    }

    # Check Gravatar
    email_hash = hashlib.md5(email.encode()).hexdigest()
    results["gravatar_hash"] = email_hash
    try:
        gravatar_url = f"https://gravatar.com/avatar/{email_hash}?d=404"
        response = requests.head(gravatar_url, timeout=5)
        if response.status_code == 200:
            results["gravatar"] = True
    except Exception:
        pass

    # Check GitHub
    try:
        github_url = f"https://api.github.com/search/users?q={quote(email)}"
        response = requests.get(github_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("items"):
                results["github"] = data["items"]
    except Exception:
        pass

    return results


def _generate_email_variations(email: str) -> list:
    """Generate common email variations."""
    try:
        local, domain = email.split("@")
        variations = set()

        if "." in local:
            parts = local.split(".")
            if len(parts) == 2:
                first, last = parts
                variations.add(f"{first}{last}@{domain}")
                variations.add(f"{first}_{last}@{domain}")
                variations.add(f"{first[0]}{last}@{domain}")
                variations.add(f"{last}{first[0]}@{domain}")
                variations.add(f"{last}{first}@{domain}")
                variations.add(f"{first[0]}.{last}@{domain}")
                variations.add(f"{first}.{last[0]}@{domain}")

        elif "_" in local:
            parts = local.split("_")
            if len(parts) == 2:
                first, last = parts
                variations.add(f"{first}.{last}@{domain}")
                variations.add(f"{first}{last}@{domain}")
                variations.add(f"{first[0]}{last}@{domain}")
                variations.add(f"{last}{first[0]}@{domain}")
                variations.add(f"{last}{first}@{domain}")

        variations.discard(email)
        return sorted(list(variations))
    except Exception:
        return []


def _generate_dork_links(email: str) -> list:
    """Generate Google dork links for paste site searches."""
    encoded_email = quote(email)
    return [
        ("Pastebin", f"https://www.google.com/search?q=site:pastebin.com+%22{encoded_email}%22"),
        ("Ghostbin", f"https://www.google.com/search?q=site:ghostbin.co+%22{encoded_email}%22"),
        ("Hastebin", f"https://www.google.com/search?q=site:hastebin.com+%22{encoded_email}%22"),
        ("Paste.ee", f"https://www.google.com/search?q=site:paste.ee+%22{encoded_email}%22"),
        ("All Paste Sites", f"https://www.google.com/search?q=%22{encoded_email}%22+site:pastebin.com+OR+site:ghostbin.co+OR+site:hastebin.com"),
    ]
