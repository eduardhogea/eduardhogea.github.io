from scholarly import scholarly
import os
import re

def sanitize_title(title):
    # Remove special characters and replace spaces with hyphens
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'\s+', '-', title)
    return title.lower()

def sanitize_text(text):
    # Ensure the text is properly encoded in UTF-8 and escape special YAML characters
    if isinstance(text, str):
        text = text.encode('utf-8', errors='replace').decode('utf-8')
        # Escape special characters for YAML
        text = text.replace('\\', ' ')  # Replace backslashes with empty space
        text = text.replace('"', ' ')  # Escape double quotes
        text = text.replace(':', ' ')  # Escape colons
        text = text.replace('\n', ' ')  # Replace newlines with spaces
    return text

def generate_bibtex(publication):
    author = publication['bib']['author']
    title = publication['bib']['title']
    venue = publication['bib'].get('venue', 'Unknown Venue')
    year = publication['bib'].get('pub_year', 'Unknown Year')
    
    bibtex = f"@article{{{author.replace(' ', '')}{year},\n"
    bibtex += f"  author = {{{author}}},\n"
    bibtex += f"  title = {{{title}}},\n"
    bibtex += f"  journal = {{{venue}}},\n"
    bibtex += f"  year = {{{year}}}\n"
    bibtex += "}"
    return bibtex

def generate_markdown(publication):
    title = sanitize_text(publication['bib']['title'])
    year = publication['bib'].get('pub_year', 'Unknown Year')
    venue = sanitize_text(publication['bib'].get('venue', 'Unknown Venue'))
    url = publication.get('eprint_url', '#')
    citation = generate_bibtex(publication)
    excerpt = sanitize_text(publication['bib'].get('abstract', 'No abstract available.'))

    return f"""---
title: "{title}"
collection: publications
permalink: /publication/{year}-{sanitize_title(title)}
excerpt: "{excerpt}"
date: {year}-01-01
venue: "{venue}"
slidesurl: "#"
thumbnail: "/images/thumbnail.jpg"  # Adjust the path to your actual thumbnail location
paperurl: "{url if url else '#'}"
citation: "{citation}"
---
"""

def main():
    search_query = scholarly.search_author('Eduard Hogea')
    author = next(search_query, None)

    if not author:
        print("Author not found.")
        return

    # Fill author details to retrieve publications
    author = scholarly.fill(author)
    print("Author filled:", author)

    # Check if the 'publications' key exists
    if 'publications' not in author:
        print("No publications found for this author.")
        return

    # Make sure the publications directory exists
    os.makedirs('_publications', exist_ok=True)

    for pub in author['publications']:
        pub_details = scholarly.fill(pub)
        title = pub_details['bib']['title']
        year = pub_details['bib'].get('pub_year', 'Unknown Year')
        sanitized_title = sanitize_title(title)
        file_name = f"{year}-{sanitized_title[:30]}.md"  # Limit filename length to 30 characters for simplicity
        file_path = os.path.join('_publications', file_name)
        
        # Check if the file already exists
        if not os.path.exists(file_path):
            markdown = generate_markdown(pub_details)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"Generated markdown for: {title}")
            print(f"Full path: {os.path.abspath(file_path)}")
        else:
            print(f"File already exists: {os.path.abspath(file_path)}")

if __name__ == "__main__":
    main()
