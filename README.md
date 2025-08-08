# Finploy Sitemap Generator & Validator

A comprehensive Flask web application for generating and validating XML sitemaps for Finploy websites. This tool automatically discovers URLs, creates comprehensive sitemaps targeting 800+ URLs, and validates all URLs for accessibility.

## 🚀 Features

- **Automated URL Discovery**: Generates comprehensive URLs based on real Finploy structure
- **Multi-site Support**: Supports both finploy.com and finploy.co.uk domains
- **Smart URL Generation**: Creates 800+ URLs using department + city combinations
- **Real-time Validation**: Validates all URLs for accessibility and redirects
- **Detailed Reports**: Generates JSON validation reports with comprehensive analytics
- **Responsive Web Interface**: Clean, modern Bootstrap-based UI
- **Downloadable Results**: Download generated sitemaps and validation reports

## 📁 Project Structure

```
Finloy/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── scripts/
│   ├── comprehensive_sitemap.py    # URL generation and sitemap creation
│   └── sitemap_validator.py        # URL validation logic
├── templates/
│   ├── base.html                   # Base template
│   ├── index.html                  # Main dashboard
│   ├── developer_info.html         # Developer documentation
│   ├── full_validation_results.html  # Detailed validation results
│   └── base.html                   # Base template
├── static/
│   ├── style.css                   # Custom styles
│   ├── script.js                   # Frontend JavaScript
│   └── REPORT.pdf                  # Project documentation
├── comprehensive_sitemap.xml       # Generated sitemap
├── validation_report_*.json        # Validation reports
└── README.md                       # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project
```bash
# Clone or download the project files
# Ensure all files are in the correct directory structure
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation
```bash
python -c "import flask; print('Flask installed successfully')"
```

## 🚀 Running the Project

### Method 1: Local Development Server

1. **Start the Flask application:**
```bash
python app.py
```

2. **Access the web interface:**
- Open your browser to: `http://localhost:5000`
- You'll see the Finploy Sitemap Generator Dashboard

### Method 2: Using the Scripts Directly

#### Generate Sitemap
```bash
# Generate comprehensive sitemap
python scripts/comprehensive_sitemap.py
```

#### Validate Sitemap
```bash
# Validate existing sitemap
python scripts/sitemap_validator.py
```

## 🎯 Using the Web Interface

### 1. Generate Sitemap
1. Enter your website URL (e.g., `https://www.finploy.com`)
2. Click "Generate Sitemap"
3. Wait for processing (typically 30-60 seconds)
4. Download the generated `comprehensive_sitemap.xml`

### 2. Validate Sitemap
1. Click "Validate Sitemap" 
2. The system will test all URLs for accessibility
3. View detailed results including:
   - Total URLs tested
   - Successful vs error URLs
   - Redirect information
   - Individual URL status

### 3. View Full Results
1. Click "Show All Validation Results" to see detailed per-URL validation
2. Download the JSON validation report

## 🔧 Configuration

### Environment Variables
Create a `.env` file (optional):
```bash
# Flask settings
FLASK_ENV=development
FLASK_DEBUG=True

# Sitemap settings
MAX_URLS=1000
MAX_WORKERS=20
CRAWL_DELAY=0.1
```

### Customizing URL Generation
Edit `scripts/comprehensive_sitemap.py`:
- Modify `departments` list for different business units
- Update `cities` list for different geographic coverage
- Adjust `generate_comprehensive_urls()` method for custom URL patterns

## 📊 Output Files

### Generated Files
- `comprehensive_sitemap.xml` - Main sitemap file
- `comprehensive_sitemap_uk.xml` - UK-specific sitemap
- `validation_report_*.json` - Detailed validation reports

### Report Structure
```json
{
  "sitemap_file": "comprehensive_sitemap.xml",
  "validation_date": "2024-01-15T10:30:00",
  "total_urls": 850,
  "summary": {
    "accessible": 820,
    "errors": 25,
    "redirects": 5
  },
  "results": {
    "https://www.finploy.com": {
      "status": 200,
      "accessible": true,
      "redirect": false
    }
  }
}
```

## 🐛 Troubleshooting

### Common Issues

#### "Sitemap file not found"
- Run the sitemap generator first: `python scripts/comprehensive_sitemap.py`

#### "Module not found" errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`

#### "Connection timeout" during validation
- Increase timeout in `sitemap_validator.py`
- Check internet connection
- Verify target website is accessible

#### "Permission denied" errors
- Run with appropriate permissions
- Check file system permissions

### Performance Optimization
- Increase `MAX_WORKERS` in validator for faster processing
- Adjust `CRAWL_DELAY` to balance speed vs server load
- Use SSD storage for better I/O performance

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/generate_sitemap_action` | POST | Generate sitemap |
| `/validate_sitemap_action` | POST | Validate sitemap |
| `/full_validation_results` | GET | Detailed validation results |
| `/download_sitemap/<filename>` | GET | Download sitemap XML |
| `/download_validation_report/<filename>` | GET | Download validation report |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is created for educational and demonstration purposes. Please ensure compliance with target website terms of service when using this tool.

## 📞 Support
- harshrokade95@gmail.com 

For issues or questions:
1. Check the troubleshooting section above
2. Review the validation reports for specific URL issues
3. Ensure target websites allow automated access

---

**Happy Sitemap Generation!** 🎉
