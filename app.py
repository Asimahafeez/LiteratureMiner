import streamlit as st
import requests
from xml.etree import ElementTree as ET

def fetch_pubmed_articles(query, max_results=5):
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json"
    }
    search_resp = requests.get(search_url, params=search_params)
    id_list = search_resp.json().get("esearchresult", {}).get("idlist", [])

    articles = []
    if id_list:
        ids = ",".join(id_list)
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ids,
            "retmode": "xml"
        }
        fetch_resp = requests.get(fetch_url, params=fetch_params)
        root = ET.fromstring(fetch_resp.text)

        for article in root.findall(".//PubmedArticle"):
            art = {}
            medline = article.find(".//MedlineCitation")
            if medline is not None:
                article_title = medline.find(".//ArticleTitle")
                art['title'] = article_title.text if article_title is not None else "No title"
                authors_list = []
                authors = medline.findall(".//Author")
                for author in authors:
                    last = author.find("LastName")
                    first = author.find("ForeName")
                    if last is not None and first is not None:
                        authors_list.append(f"{first.text} {last.text}")
                art['authors'] = ", ".join(authors_list) if authors_list else "No authors"
                date = medline.find(".//DateCompleted")
                if date is not None:
                    year = date.find("Year").text if date.find("Year") is not None else "N/A"
                    month = date.find("Month").text if date.find("Month") is not None else "N/A"
                    day = date.find("Day").text if date.find("Day") is not None else "N/A"
                    art['date'] = f"{year}-{month}-{day}"
                else:
                    art['date'] = "N/A"
                abstract_text = ""
                abstract = medline.find(".//Abstract")
                if abstract is not None:
                    for elem in abstract.findall("AbstractText"):
                        if elem.text:
                            abstract_text += elem.text + " "
                art['abstract'] = abstract_text.strip() if abstract_text else "No abstract available"
                articles.append(art)
    return articles

st.title("Fast & Lightweight Bioinformatics PubMed Miner")
st.write("Type a keyword to fetch PubMed articles without heavy AI models.")

query = st.text_input("Enter keyword", "bioinformatics")
max_results = st.slider("Number of articles", 1, 10, 5)

if st.button("Fetch Articles"):
    if not query.strip():
        st.error("Please enter a valid keyword!")
    else:
        articles = fetch_pubmed_articles(query, max_results)
        if articles:
            st.success(f"Found {len(articles)} articles:")
            for i, art in enumerate(articles, 1):
                st.subheader(f"Article {i}: {art['title']}")
                st.write(f"**Authors:** {art['authors']}")
                st.write(f"**Date:** {art['date']}")
                st.write(f"**Abstract:** {art['abstract']}")
                st.markdown("---")
        else:
            st.error("No articles found for this keyword.")
