document.addEventListener('DOMContentLoaded', function() {
    // Elements for Generate Sitemap
    const generateSitemapForm = document.getElementById('generateSitemapForm');
    const generateSitemapBtn = document.getElementById('generateSitemapBtn');
    const generateLoader = document.getElementById('generateLoader');
    const generateResults = document.getElementById('generateResults');
    const generateStatus = document.getElementById('generateStatus');
    const generateErrorMessage = document.getElementById('generateErrorMessage');
    const totalUrls = document.getElementById('totalUrls');
    const generateTimeTaken = document.getElementById('generateTimeTaken');
    const sampleGeneratedUrls = document.getElementById('sampleGeneratedUrls');
    const generatedFileName = document.getElementById('generatedFileName');
    const downloadSitemapBtn = document.getElementById('downloadSitemapBtn');

    // Elements for Validate Sitemap
    const validateSitemapForm = document.getElementById('validateSitemapForm');
    const validateSitemapBtn = document.getElementById('validateSitemapBtn');
    const validateLoader = document.getElementById('validateLoader');
    const validateResults = document.getElementById('validateResults');
    const totalTestedUrls = document.getElementById('totalTestedUrls');
    const successfulUrls = document.getElementById('successfulUrls');
    const errorUrls = document.getElementById('errorUrls');
    const redirectUrls = document.getElementById('redirectUrls');
    const validateTimeTaken = document.getElementById('validateTimeTaken');
    const sampleValidatedUrls = document.getElementById('sampleValidatedUrls');
    const validatedFileName = document.getElementById('validatedFileName');
    const showAllValidationBtn = document.getElementById('showAllValidationBtn');
    const downloadValidationReportBtn = document.getElementById('downloadValidationReportBtn');

    let generationChartInstance = null;
    let validationChartInstance = null;

    // Function to render Generation Chart
    function renderGenerationChart(total, time) {
        const ctx = document.getElementById('generationChart').getContext('2d');
        if (generationChartInstance) {
            generationChartInstance.destroy();
        }
        generationChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Total URLs', 'Time Taken (s)'],
                datasets: [{
                    label: 'Sitemap Generation Metrics',
                    data: [total, time],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)'
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Sitemap Generation Overview'
                    }
                }
            }
        });
    }

    // Function to render Validation Chart
    function renderValidationChart(successful, errors, redirects) {
        const ctx = document.getElementById('validationChart').getContext('2d');
        if (validationChartInstance) {
            validationChartInstance.destroy();
        }
        validationChartInstance = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Successful', 'Errors', 'Redirects'],
                datasets: [{
                    label: 'Validation Status',
                    data: [successful, errors, redirects],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.6)', // Green for successful
                        'rgba(220, 53, 69, 0.6)',  // Red for errors
                        'rgba(255, 193, 7, 0.6)'   // Yellow for redirects
                    ],
                    borderColor: [
                        'rgba(40, 167, 69, 1)',
                        'rgba(220, 53, 69, 1)',
                        'rgba(255, 193, 7, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Sitemap Validation Breakdown'
                    }
                }
            }
        });
    }


    // Handle Generate Sitemap form submission
    generateSitemapForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        generateSitemapBtn.disabled = true;
        generateLoader.style.display = 'inline-block';
        generateResults.style.display = 'none';
        generateErrorMessage.style.display = 'none';
        downloadSitemapBtn.style.display = 'none'; // Hide download button initially

        const formData = new FormData(generateSitemapForm);

        try {
            const response = await fetch('/generate_sitemap_action', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.status === 'success') {
                if (generateStatus) generateStatus.textContent = 'Success';
                if (generateStatus) generateStatus.className = 'badge badge-success badge-pill';
                if (totalUrls) totalUrls.textContent = data.total_urls;
                if (generateTimeTaken) generateTimeTaken.textContent = data.time_taken;
                if (generatedFileName) generatedFileName.textContent = data.saved_file;

                if (sampleGeneratedUrls) sampleGeneratedUrls.innerHTML = '';
                data.sample_urls.forEach(url => {
                    const li = document.createElement('li');
                    li.textContent = url;
                    if (sampleGeneratedUrls) sampleGeneratedUrls.appendChild(li);
                });
                
                if (downloadSitemapBtn) {
                    downloadSitemapBtn.href = `/download_sitemap/${data.saved_file}`;
                    downloadSitemapBtn.style.display = 'inline-block'; // Show download button
                }

                renderGenerationChart(data.total_urls, data.time_taken);

            } else {
                if (generateStatus) generateStatus.textContent = 'Error';
                if (generateStatus) generateStatus.className = 'badge badge-danger badge-pill';
                if (generateErrorMessage) generateErrorMessage.textContent = data.error || 'An unknown error occurred during sitemap generation.';
                if (generateErrorMessage) generateErrorMessage.style.display = 'block';
                // Clear other fields on error
                if (totalUrls) totalUrls.textContent = '';
                if (generateTimeTaken) generateTimeTaken.textContent = '';
                if (generatedFileName) generatedFileName.textContent = '';
                if (sampleGeneratedUrls) sampleGeneratedUrls.innerHTML = '';
            }
            if (generateResults) generateResults.style.display = 'block';

        } catch (error) {
            console.error('Error generating sitemap:', error);
            if (generateStatus) generateStatus.textContent = 'Error';
            if (generateStatus) generateStatus.className = 'badge badge-danger badge-pill';
            if (generateErrorMessage) generateErrorMessage.textContent = 'Network error or server issue. Please try again.';
            if (generateErrorMessage) generateErrorMessage.style.display = 'block';
            if (generateResults) generateResults.style.display = 'block';
        } finally {
            if (generateSitemapBtn) generateSitemapBtn.disabled = false;
            if (generateLoader) generateLoader.style.display = 'none';
        }
    });

    // Handle Validate Sitemap form submission
    validateSitemapForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        if (validateSitemapBtn) validateSitemapBtn.disabled = true;
        if (validateLoader) validateLoader.style.display = 'inline-block';
        if (validateResults) validateResults.style.display = 'none';
        if (showAllValidationBtn) showAllValidationBtn.style.display = 'none'; // Hide button initially
        if (downloadValidationReportBtn) downloadValidationReportBtn.style.display = 'none'; // Hide button initially

        try {
            const response = await fetch('/validate_sitemap_action', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.status === 'error') {
                alert(`Validation Error: ${data.error}`);
                if (validateResults) validateResults.style.display = 'none';
            } else {
                if (totalTestedUrls) totalTestedUrls.textContent = data.total_tested;
                if (successfulUrls) successfulUrls.textContent = data.successful;
                if (errorUrls) errorUrls.textContent = data.errors;
                if (redirectUrls) redirectUrls.textContent = data.redirects;
                if (validateTimeTaken) validateTimeTaken.textContent = data.time_taken;
                if (validatedFileName) validatedFileName.textContent = data.saved_file;

                if (sampleValidatedUrls) sampleValidatedUrls.innerHTML = '';
                data.sample_validated_urls.forEach(item => {
                    const li = document.createElement('li');
                    if (item.url) { // Check if it's a real URL or the "more" message
                        const a = document.createElement('a');
                        a.href = item.url;
                        a.target = "_blank"; // Open in new tab
                        a.textContent = `${item.url} - ${item.status_text}`;
                        li.appendChild(a);
                    } else {
                        li.textContent = item.status_text; // For the "... and X more" message
                    }
                    if (sampleValidatedUrls) sampleValidatedUrls.appendChild(li);
                });

                if (showAllValidationBtn) showAllValidationBtn.style.display = 'inline-block'; // Show "Show All" button
                if (downloadValidationReportBtn) {
                    downloadValidationReportBtn.href = `/download_validation_report/${data.saved_file}`;
                    downloadValidationReportBtn.style.display = 'inline-block'; // Show download button
                }

                renderValidationChart(data.successful, data.errors, data.redirects);
                
                if (validateResults) validateResults.style.display = 'block';
            }

        } catch (error) {
            console.error('Error validating sitemap:', error);
            alert('Failed to validate sitemap. Please check console for details.');
            // Ensure results section is hidden or displayed with an error message in case of fetch error
            if (validateResults) validateResults.style.display = 'block'; // Show to allow user to see console error
            // Potentially add a dedicated error message display here if not already handled.
        } finally {
            if (validateSitemapBtn) validateSitemapBtn.disabled = false;
            if (validateLoader) validateLoader.style.display = 'none';
        }
    });
});
