#!/usr/bin/env python3

import requests
import sys
from urllib.parse import urljoin, urlparse
import re

def normalize_url(url):
    """
    Ensure the URL has a scheme. Defaults to https if missing.
    """
    parsed = urlparse(url)
    if not parsed.scheme:
        url = 'https://' + url
        parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    # Remove any trailing slash for consistency
    return parsed.scheme + "://" + parsed.netloc.rstrip('/') + '/'

def fetch_robots_txt(base_url):
    """
    Fetch the robots.txt content from the base URL.
    """
    robots_url = urljoin(base_url, 'robots.txt')
    try:
        response = requests.get(robots_url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"robots.txt not found at {robots_url} (status code: {response.status_code})")
            return None
    except requests.RequestException as e:
        print(f"Error fetching robots.txt: {e}")
        return None

def parse_sitemaps_from_robots(robots_txt):
    """
    Parse Sitemap directives from robots.txt.
    """
    sitemaps = []
    sitemap_pattern = re.compile(r'^\s*Sitemap:\s*(\S+)', re.IGNORECASE)
    for line in robots_txt.splitlines():
        match = sitemap_pattern.match(line)
        if match:
            sitemap_url = match.group(1).strip()
            sitemaps.append(sitemap_url)
    return sitemaps

def check_url(url):
    """
    Check if the URL exists (status code 200).
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException:
        return False

def find_standard_sitemaps(base_url):
    """
    Attempt to find sitemaps by checking standard locations.
    """
    standard_paths = [
        'sitemap.xml',
        'sitemap_index.xml',
        'sitemap1.xml',
        'sitemap2.xml',
        'sitemap.xml.gz',
        'sitemap_index.xml.gz',
        'sitemap',
        'sitemap_index',
        'sitemap1',
        'sitemap2',
    ]
    found_sitemaps = []
    for path in standard_paths:
        sitemap_url = urljoin(base_url, path)
        if check_url(sitemap_url):
            found_sitemaps.append(sitemap_url)
    return found_sitemaps

def main():
    # Get the website URL from command-line arguments or prompt the user
    if len(sys.argv) < 2:
        website = input("Enter the website URL (e.g., https://example.com): ").strip()
    else:
        website = sys.argv[1].strip()
    
    try:
        base_url = normalize_url(website)
    except ValueError as e:
        print(e)
        sys.exit(1)
    
    print(f"\nSearching for sitemaps on {base_url}...\n")
    
    sitemaps = set()
    
    # Fetch and parse robots.txt
    robots_txt = fetch_robots_txt(base_url)
    if robots_txt:
        robots_sitemaps = parse_sitemaps_from_robots(robots_txt)
        if robots_sitemaps:
            print(f"Found {len(robots_sitemaps)} sitemap(s) in robots.txt:")
            for sitemap in robots_sitemaps:
                print(f" - {sitemap}")
                sitemaps.add(sitemap)
        else:
            print("No Sitemap directives found in robots.txt.")
    else:
        print("robots.txt could not be retrieved.")
    
    print("")  

    standard_sitemaps = find_standard_sitemaps(base_url)
    if standard_sitemaps:
        print(f"Found {len(standard_sitemaps)} sitemap(s) at standard locations:")
        for sitemap in standard_sitemaps:
            print(f" - {sitemap}")
            sitemaps.add(sitemap)
    else:
        print("No sitemaps found at standard locations.")
    
    # Final report
    if not sitemaps:
        print("\nNo sitemaps found.")
    else:
        print("\nAll found sitemaps:")
        for sitemap in sorted(sitemaps):
            print(sitemap)

if __name__ == "__main__":
    main()
