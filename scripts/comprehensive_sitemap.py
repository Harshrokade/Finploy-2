import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading
import collections # For deque

class ComprehensiveFinploySitemap:
    def __init__(self, base_url="https://www.finploy.com"):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.discovered_urls = set()
        self.lock = threading.Lock()

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Set to keep track of URLs that have been added to the queue or processed
        self.processed_or_queued_urls = set()

    def generate_comprehensive_urls(self):
        """Generate comprehensive URL list based on real Finploy structure"""
        urls = {self.base_url}

        # Real Finploy departments from the provided images
        departments = [
            'sales-loans',
            'sales-casa-deposits-mfs',
            'sales-corporate-institutional',
            'sales-life-insurance',
            'sales-general-insurance',
            'collections',
            'credit-department',
            'technology-digital',
            'hr-training',
            'legal-compliance-risk',
            'operations-loans-underwrtg-disb-mis',
            'operations-central-support',
            'operations-banking',
            'investment-banking-pe-vc',
            'broking-trading-asset-wealth-mgt',
            'treasury-forex',
            'trading-commod-crypto-others',
            'others-emerging',
            'marketing',
            'finance-accounts-taxation'
        ]

        # Extended list of Indian cities (50+ cities to reach 800+ URLs)
        cities = [
            # Tier 1 cities
            'mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'kolkata', 'pune',
            # Tier 2 cities
            'ahmedabad', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore', 'thane',
            'bhopal', 'visakhapatnam', 'patna', 'vadodara', 'ghaziabad', 'ludhiana',
            'agra', 'nashik', 'faridabad', 'meerut', 'rajkot', 'varanasi', 'srinagar',
            'aurangabad', 'dhanbad', 'amritsar', 'allahabad', 'ranchi', 'howrah',
            'coimbatore', 'jabalpur', 'gwalior', 'vijayawada', 'jodhpur', 'madurai',
            'raipur', 'kota', 'guwahati', 'chandigarh', 'solapur', 'hubli-dharwad',
            'bareilly', 'moradabad', 'mysore', 'gurgaon', 'aligarh', 'jalandhar',
            'tiruchirappalli', 'bhubaneswar', 'salem', 'warangal', 'thiruvananthapuram',
            'bhiwandi', 'saharanpur', 'gorakhpur', 'guntur', 'bikaner', 'amravati',
            'noida', 'jamshedpur', 'bhilai', 'cuttack', 'firozabad', 'kochi', 'nellore'
        ]

        print(f"🏢 Using {len(departments)} real Finploy departments")
        print(f"🏙️ Using {len(cities)} Indian cities")

        # 1. Department + City combinations (20 depts × 60 cities = 1200 URLs)
        for dept in departments:
            for city in cities:
                urls.add(f"{self.base_url}/{dept}-jobs-in-{city}")

        # 2. Location-based job URLs
        for city in cities:
            urls.add(f"{self.base_url}/jobs-in-{city}")
            urls.add(f"{self.base_url}/careers-in-{city}")

        # 3. Department-only URLs
        for dept in departments:
            urls.add(f"{self.base_url}/{dept}-jobs")
            urls.add(f"{self.base_url}/jobs/{dept}")
            urls.add(f"{self.base_url}/careers/{dept}")

        # 4. Experience level combinations
        experience_levels = ['fresher', 'experienced', 'senior', 'manager', 'executive', 'entry-level']
        for exp in experience_levels:
            for city in cities[:15]:  # Top 15 cities
                urls.add(f"{self.base_url}/{exp}-jobs-in-{city}")

        # 5. Salary-based URLs
        salary_types = ['high-salary', 'competitive-salary', 'attractive-package']
        for salary in salary_types:
            for city in cities[:10]:
                urls.add(f"{self.base_url}/{salary}-jobs-in-{city}")

        # 6. Company and static pages
        static_pages = [
            '/jobs', '/careers', '/companies', '/employers', '/job-seekers',
            '/about', '/contact', '/services', '/solutions', '/products',
            '/blog', '/news', '/resources', '/help', '/support', '/faq',
            '/privacy-policy', '/terms-conditions', '/sitemap', '/login', '/register'
        ]

        for page in static_pages:
            urls.add(f"{self.base_url}{page}")

        # 7. Pagination URLs (common patterns)
        for page_num in range(2, 11):  # Pages 2-10
            urls.add(f"{self.base_url}/jobs?page={page_num}")
            urls.add(f"{self.base_url}/careers?page={page_num}")

        print(f"📊 Generated {len(urls)} potential URLs")
        return urls

    def fetch_and_extract_links(self, url):
        """
        Fetches a URL, extracts internal links, and returns the URL if accessible.
        Returns (accessible_url, list_of_new_internal_links) or (None, []).
        """
        try:
            response = self.session.get(url, timeout=5) # Increased timeout slightly
            # Check for successful response and HTML content type
            if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                soup = BeautifulSoup(response.text, 'html.parser')
                internal_links = []
                for link in soup.find_all('a', href=True):
                    absolute_url = urljoin(url, link['href'])
                    parsed_absolute_url = urlparse(absolute_url)

                    # Ensure it's the same domain and not already processed/queued
                    if parsed_absolute_url.netloc == self.domain and \
                       absolute_url not in self.processed_or_queued_urls:
                        # Filter out common non-content links like mailto, tel, #anchors
                        if not absolute_url.startswith(('mailto:', 'tel:', '#')):
                            internal_links.append(absolute_url)
                return url, internal_links
            else:
                return None, []
        except requests.exceptions.RequestException:
            # Handle connection errors, timeouts, etc.
            return None, []

    def crawl_and_validate(self, initial_urls, max_urls_to_discover=1000, max_workers=10, crawl_delay=0.1):
        """
        Crawls initial URLs and discovers more accessible URLs by following internal links.
        """
        self.discovered_urls.clear() # Reset for new crawl
        self.processed_or_queued_urls.clear() # Reset for new crawl

        queue = collections.deque()
        for url in initial_urls:
            if url not in self.processed_or_queued_urls:
                queue.append(url)
                self.processed_or_queued_urls.add(url)

        print(f"🔍 Starting crawl with {len(initial_urls)} initial URLs...")
        processed_count = 0
        accessible_count = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            while queue and accessible_count < max_urls_to_discover:
                # Submit a batch of tasks to keep workers busy
                batch_size = min(len(queue), max_workers * 2)
                for _ in range(batch_size):
                    if queue:
                        url_to_process = queue.popleft()
                        future = executor.submit(self.fetch_and_extract_links, url_to_process)
                        futures[future] = url_to_process

                if not futures: # No more URLs to process or waiting for futures
                    break

                # Process results as they complete
                # Convert to list to avoid RuntimeError: dictionary changed size during iteration
                for future in as_completed(list(futures.keys())):
                    url_processed = futures.pop(future)
                    processed_count += 1
                    accessible_url, new_links = future.result()

                    if accessible_url:
                        with self.lock:
                            self.discovered_urls.add(accessible_url)
                            accessible_count = len(self.discovered_urls)
                        for link in new_links:
                            if link not in self.processed_or_queued_urls:
                                queue.append(link)
                                self.processed_or_queued_urls.add(link)

                    # Implement a small delay to be polite to the server
                    time.sleep(crawl_delay)

                print(f"Progress: {accessible_count} accessible URLs found, {processed_count} URLs processed, {len(queue)} URLs in queue.")

        print(f"✅ Crawl finished. Found {accessible_count} accessible URLs.")
        return self.discovered_urls


    def create_comprehensive_sitemap(self, filename="comprehensive_sitemap.xml"):
        """Create comprehensive sitemap targeting 800+ URLs"""
        print("🚀 Starting Comprehensive Finploy Sitemap Generation...")
        start_time = time.time()

        # Generate all possible URLs as initial seeds
        initial_generated_urls = self.generate_comprehensive_urls()

        # Crawl and validate to find accessible URLs
        # Target 1000 accessible URLs, can be adjusted based on site size
        accessible_urls = self.crawl_and_validate(initial_generated_urls, max_urls_to_discover=1000)

        # Ensure we have 800+ URLs (if not, the crawl might need more aggressive settings or the site doesn't have that many)
        if len(accessible_urls) < 800:
            print(f"⚠️ Only {len(accessible_urls)} accessible URLs found. Consider increasing max_urls_to_discover or adjusting crawl_delay if needed.")

        # Create XML sitemap
        urlset = ET.Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

        # Sort URLs by priority
        # Prioritize base URL, then URLs containing 'jobs' or 'careers', then department-specific, then others
        sorted_urls = sorted(list(accessible_urls), key=lambda x: (
            0 if x == self.base_url else
            1 if '/jobs' in x or '/careers' in x else
            2 if any(dept in x for dept in ['sales', 'marketing', 'operations', 'technology', 'finance']) else
            3
        ))

        for url in sorted_urls:
            url_elem = ET.SubElement(urlset, "url")

            loc_elem = ET.SubElement(url_elem, "loc")
            loc_elem.text = url

            lastmod_elem = ET.SubElement(url_elem, "lastmod")
            lastmod_elem.text = datetime.now().strftime("%Y-%m-%d")

            # Smart priority and changefreq assignment
            if url == self.base_url:
                priority = "1.0"
                changefreq = "daily"
            elif any(dept in url for dept in ['sales', 'marketing', 'operations', 'technology', 'finance']):
                priority = "0.9"
                changefreq = "daily"
            elif 'jobs' in url or 'careers' in url:
                priority = "0.8"
                changefreq = "daily"
            else:
                priority = "0.6"
                changefreq = "weekly"

            changefreq_elem = ET.SubElement(url_elem, "changefreq")
            changefreq_elem.text = changefreq

            priority_elem = ET.SubElement(url_elem, "priority")
            priority_elem.text = priority

        # Write sitemap
        tree = ET.ElementTree(urlset)
        ET.indent(tree, space="  ", level=0)
        tree.write(filename, encoding="utf-8", xml_declaration=True)

        end_time = time.time()

        print(f"\n✅ COMPREHENSIVE SITEMAP COMPLETED!")
        print(f"⏱️ Time taken: {end_time - start_time:.2f} seconds")
        print(f"📁 Sitemap saved as: {filename}")
        print(f"🔗 Total URLs: {len(sorted_urls)}")
        print(f"🎯 Target achieved: {'✅ YES' if len(sorted_urls) >= 800 else '❌ NO'}")

        return filename, len(sorted_urls)

# Main execution
if __name__ == "__main__":
    generator = ComprehensiveFinploySitemap("https://www.finploy.com")
    sitemap_file, url_count = generator.create_comprehensive_sitemap()

    # Also generate for UK site
    print(f"\n🇬🇧 Generating UK sitemap...")
    generator_uk = ComprehensiveFinploySitemap("https://finploy.co.uk")
    sitemap_file_uk, url_count_uk = generator_uk.create_comprehensive_sitemap("comprehensive_sitemap_uk.xml")

    print(f"\n🎉 FINAL RESULTS:")
    print(f"📊 finploy.com: {url_count} URLs")
    print(f"📊 finploy.co.uk: {url_count_uk} URLs")
    print(f"🎯 Total URLs: {url_count + url_count_uk}")
    print(f"✅ Assignment requirement (800+ URLs): {'ACHIEVED' if url_count >= 800 else 'PARTIAL'}")
