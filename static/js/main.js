document.getElementById('analyze-form')?.addEventListener('submit', function(e) {
    const submitButton = this.querySelector('button[type="submit"]');
    const resultsContainer = document.querySelector('.results-container');
    const originalText = submitButton.textContent;
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.textContent = 'Analyzing...';
    
    // Add loading animation
    resultsContainer.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>Analyzing your text...</p>
        </div>
    `;
    
    // Form submission continues normally
});