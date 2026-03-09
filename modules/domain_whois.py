import streamlit as st
import whois
import dns.resolver
from datetime import datetime


def render():
    st.header("Domain WHOIS Lookup")
    col1, col2 = st.columns([3, 1])
    with col1:
        domain = st.text_input("Enter domain name", placeholder="example.com")
    with col2:
        search_button = st.button("Lookup", key="whois_lookup_btn")
    if search_button and domain:
        lookup_domain(domain)
    elif search_button and not domain:
        st.error("Please enter a domain name")


def lookup_domain(domain):
    domain = domain.strip().lower()
    if domain.startswith("http://"):
        domain = domain.replace("http://", "")
    if domain.startswith("https://"):
        domain = domain.replace("https://", "")
    if domain.startswith("www."):
        domain = domain.replace("www.", "")
    domain = domain.split("/")[0]

    st.subheader("WHOIS Information")
    try:
        whois_data = whois.whois(domain)
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Registrar:**", whois_data.registrar or "N/A")
            st.write("**Registrant Name:**", whois_data.name or "N/A")
            st.write("**Registrant Email:**", whois_data.email or "N/A")
            st.write("**Registrant Phone:**", whois_data.phone or "N/A")
        with col2:
            creation_date = whois_data.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            st.write("**Creation Date:**", creation_date or "N/A")
            expiry_date = whois_data.expiration_date
            if isinstance(expiry_date, list):
                expiry_date = expiry_date[0]
            st.write("**Expiry Date:**", expiry_date or "N/A")
            updated_date = whois_data.updated_date
            if isinstance(updated_date, list):
                updated_date = updated_date[0]
            st.write("**Last Updated:**", updated_date or "N/A")
        st.write("**Nameservers:**")
        nameservers = whois_data.nameservers
        if nameservers:
            if isinstance(nameservers, list):
                for ns in nameservers:
                    st.write(f"  • {ns}")
            else:
                st.write(f"  • {nameservers}")
        else:
            st.write("  N/A")
        if whois_data.org:
            st.write("**Organization:**", whois_data.org)
    except Exception as e:
        st.error(f"WHOIS lookup failed: {str(e)}")

    st.subheader("DNS Records")
    dns_records = {'A': [], 'MX': [], 'NS': [], 'TXT': []}
    for record_type in dns_records.keys():
        try:
            answers = dns.resolver.resolve(domain, record_type)
            for rdata in answers:
                dns_records[record_type].append(str(rdata))
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, Exception):
            pass
    for record_type, records in dns_records.items():
        st.write(f"**{record_type} Records:**")
        if records:
            for record in records:
                st.write(f"  • {record}")
        else:
            st.write("  No records found")
