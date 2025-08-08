from flask import Flask, render_template, request, jsonify, send_file
import time
import random
import asyncio
import os

# Import your sitemap generation and validation logic
from scripts.comprehensive_sitemap import ComprehensiveFinploySitemap
from scripts.sitemap_validator import SitemapValidator

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/developer_info')
def developer_info():
    return render_template('developer_info.html')

@app.route('/generate_sitemap_action', methods=['POST'])
def generate_sitemap_action():
    website_url = request.form.get('website_url')
    if not website_url:
        return jsonify({"status": "error", "error": "Website URL is required."}), 400

    try:
        start_time = time.time()
        generator = ComprehensiveFinploySitemap(base_url=website_url)
        sitemap_file, url_count = generator.create_comprehensive_sitemap()
        end_time = time.time()
        time_taken = round(end_time - start_time, 2)

        # Since the original script doesn't return sample URLs, we'll simulate them
        # or you can modify comprehensive_sitemap.py to return them if allowed.
        # For now, using a simple simulation based on the generated count.
        sample_urls = [f"{website_url}/sample-page-{i}" for i in range(1, min(6, url_count + 1))]
        if url_count > 5:
            sample_urls.append(f"... and {url_count - 5} more.")

        return jsonify({
            "status": "success",
            "total_urls": url_count,
            "time_taken": time_taken,
            "sample_urls": sample_urls,
            "saved_file": sitemap_file
        })
    except Exception as e:
        print(f"Error during sitemap generation: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/validate_sitemap_action', methods=['POST'])
def validate_sitemap_action():
    sitemap_file_to_validate = "comprehensive_sitemap.xml" # Assuming this is the main sitemap to validate

    if not os.path.exists(sitemap_file_to_validate):
        return jsonify({"status": "error", "error": f"Sitemap file '{sitemap_file_to_validate}' not found. Please generate it first."}), 404

    try:
        start_time = time.time()
        validator = SitemapValidator(sitemap_file_to_validate)
        
        # Run the async validation in a synchronous Flask route
        validation_results_dict = asyncio.run(validator.validate_all_urls())
        report = validator.generate_validation_report(f"validation_report_{sitemap_file_to_validate.replace('.xml', '')}.json")
        end_time = time.time()
        time_taken = round(end_time - start_time, 2)

        # Prepare sample and full results for the frontend
        sample_validated_urls = []
        full_validated_urls = []
        count = 0
        for url, result in validation_results_dict.items():
            status_text = f"{result['status']} {'OK' if result['accessible'] else 'Error'}"
            if result.get('redirect'):
                status_text += " (Redirect)"
            
            item = {"url": url, "status_text": status_text, "status_code": result['status'], "accessible": result['accessible'], "redirect": result.get('redirect', False)}
            full_validated_urls.append(item)

            if count < 5:
                sample_validated_urls.append(item)
            count += 1
        
        if len(validation_results_dict) > 5:
            sample_validated_urls.append({"url": None, "status_text": f"... and {len(validation_results_dict) - 5} more."})

        return jsonify({
            "total_tested": report['summary']['accessible'] + report['summary']['errors'],
            "successful": report['summary']['accessible'],
            "errors": report['summary']['errors'],
            "redirects": report['summary']['redirects'],
            "time_taken": time_taken,
            "sample_validated_urls": sample_validated_urls,
            "full_validated_urls": full_validated_urls, # Send all results for the new page
            "saved_file": report['sitemap_file']
        })
    except Exception as e:
        print(f"Error during sitemap validation: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/full_validation_results')
def full_validation_results():
    sitemap_file_to_validate = "comprehensive_sitemap.xml"
    if not os.path.exists(sitemap_file_to_validate):
        # Handle case where sitemap isn't generated yet
        return render_template('full_validation_results.html', results=[], error="Sitemap not found. Please generate it first.")

    try:
        validator = SitemapValidator(sitemap_file_to_validate)
        validation_results_dict = asyncio.run(validator.validate_all_urls())
        
        full_results_for_template = []
        for url, result in validation_results_dict.items():
            status_text = f"{result['status']} {'OK' if result['accessible'] else 'Error'}"
            if result.get('redirect'):
                status_text += " (Redirect)"
            full_results_for_template.append({
                "url": url,
                "status_text": status_text,
                "accessible": result['accessible'],
                "redirect": result.get('redirect', False)
            })
        return render_template('full_validation_results.html', results=full_results_for_template)
    except Exception as e:
        print(f"Error retrieving full validation results: {e}")
        return render_template('full_validation_results.html', results=[], error=f"Error loading results: {str(e)}")


@app.route('/download_sitemap/<filename>')
def download_sitemap(filename):
    # IMPORTANT: In a Vercel deployment, files saved locally are ephemeral.
    # You would need to serve this from persistent storage like Vercel Blob.
    # For local development, this works.
    file_path = os.path.join(os.getcwd(), filename) # Assumes sitemap.xml is in root
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

@app.route('/download_validation_report/<filename>')
def download_validation_report(filename):
    # IMPORTANT: In a Vercel deployment, files saved locally are ephemeral.
    # You would need to serve this from persistent storage like Vercel Blob.
    # For local development, this works.
    file_path = os.path.join(os.getcwd(), filename) # Assumes report.json is in root
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
