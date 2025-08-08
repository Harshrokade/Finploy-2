import xml.etree.ElementTree as ET
import requests
from urllib.parse import urlparse
import asyncio
import aiohttp
from datetime import datetime
import json
import os

class SitemapValidator:
    def __init__(self, sitemap_file):
        self.sitemap_file = sitemap_file
        self.urls = []
        self.validation_results = {}
        
    def parse_sitemap(self):
        """Parse the XML sitemap and extract URLs"""
        try:
            tree = ET.parse(self.sitemap_file)
            root = tree.getroot()
            
            # Handle namespace
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            for url_elem in root.findall('.//ns:url', namespace):
                loc_elem = url_elem.find('ns:loc', namespace)
                if loc_elem is not None:
                    self.urls.append(loc_elem.text)
            
            print(f"Parsed {len(self.urls)} URLs from sitemap")
            return self.urls
        except Exception as e:
            print(f"Error parsing sitemap: {e}")
            return []
    
    async def validate_url(self, session, url, semaphore):
        """Validate a single URL"""
        async with semaphore:
            try:
                async with session.head(url, timeout=10) as response:
                    return {
                        'url': url,
                        'status': response.status,
                        'accessible': response.status < 400,
                        'redirect': response.status in [301, 302, 303, 307, 308]
                    }
            except Exception as e:
                return {
                    'url': url,
                    'status': None,
                    'accessible': False,
                    'error': str(e)
                }
    
    async def validate_all_urls(self, max_concurrent=20):
        """Validate all URLs in the sitemap"""
        if not self.urls:
            self.parse_sitemap()
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async with aiohttp.ClientSession() as session:
            tasks = [self.validate_url(session, url, semaphore) for url in self.urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            accessible_count = 0
            error_count = 0
            redirect_count = 0
            
            for result in results:
                if isinstance(result, dict):
                    url = result['url']
                    self.validation_results[url] = result
                    
                    if result['accessible']:
                        accessible_count += 1
                    else:
                        error_count += 1
                    
                    if result.get('redirect', False):
                        redirect_count += 1
            
            print(f"\nValidation Results:")
            print(f"Total URLs: {len(self.urls)}")
            print(f"Accessible: {accessible_count}")
            print(f"Errors: {error_count}")
            print(f"Redirects: {redirect_count}")
            
            return self.validation_results
    
    def generate_validation_report(self, output_file="validation_report.json"):
        """Generate a detailed validation report"""
        report = {
            'sitemap_file': self.sitemap_file,
            'validation_date': datetime.now().isoformat(),
            'total_urls': len(self.urls),
            'results': self.validation_results,
            'summary': {
                'accessible': sum(1 for r in self.validation_results.values() if r.get('accessible', False)),
                'errors': sum(1 for r in self.validation_results.values() if not r.get('accessible', True)),
                'redirects': sum(1 for r in self.validation_results.values() if r.get('redirect', False))
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Validation report saved to {output_file}")
        return report

def check_sitemap_files():
    """Check if comprehensive sitemap files exist"""
    files_to_check = [
        "comprehensive_sitemap.xml",
        "comprehensive_sitemap_uk.xml"
    ]
    
    missing_files = []
    for file in files_to_check:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing sitemap files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n💡 Please run comprehensive_sitemap.py first to generate sitemaps!")
        return False
    
    print("✅ Found all required sitemap files")
    return True

# Usage - Updated to work with comprehensive sitemap generator output
async def validate_comprehensive_sitemaps():
    """Validate both comprehensive sitemaps automatically"""
    
    print("🔍 Starting Sitemap Validation...")
    print("=" * 50)
    
    # Validate main sitemap
    print("\n📊 Validating comprehensive_sitemap.xml...")
    validator = SitemapValidator("comprehensive_sitemap.xml")
    await validator.validate_all_urls()
    main_report = validator.generate_validation_report("validation_report_main.json")
    
    # Validate UK sitemap  
    print("\n🇬🇧 Validating comprehensive_sitemap_uk.xml...")
    validator_uk = SitemapValidator("comprehensive_sitemap_uk.xml")
    await validator_uk.validate_all_urls()
    uk_report = validator_uk.generate_validation_report("validation_report_uk.json")
    
    # Combined summary
    total_urls = main_report['total_urls'] + uk_report['total_urls']
    total_accessible = main_report['summary']['accessible'] + uk_report['summary']['accessible']
    total_errors = main_report['summary']['errors'] + uk_report['summary']['errors']
    
    print(f"\n🎉 VALIDATION SUMMARY:")
    print(f"📊 Total URLs Tested: {total_urls}")
    print(f"✅ Accessible URLs: {total_accessible} ({(total_accessible/total_urls)*100:.1f}%)")
    print(f"❌ Error URLs: {total_errors} ({(total_errors/total_urls)*100:.1f}%)")
    print(f"📁 Reports saved: validation_report_main.json, validation_report_uk.json")

if __name__ == "__main__":
    if check_sitemap_files():
        asyncio.run(validate_comprehensive_sitemaps())
    else:
        print("\n🚀 Run this command first:")
        print("   python scripts/comprehensive_sitemap.py")
        print("\n📝 Then run validation:")
        print("   python scripts/sitemap_validator.py")
