document.getElementById('analyze-form')?.addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent normal form submission
    
    const submitButton = this.querySelector('button[type="submit"]');
    const resultsContainer = document.querySelector('.results-container');
    const originalText = submitButton.textContent;
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.textContent = 'Analyzing...';
    
    // Add loading animation
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>Analyzing your text...</p>
            </div>
        `;
    }
    
    // Get form data
    const formData = new FormData(this);
    const text = formData.get('text');
    
    // Get selected methods
    const methodCheckboxes = document.querySelectorAll('input[name="methods"]:checked');
    const methods = Array.from(methodCheckboxes).map(cb => cb.value);
    
    // Check if AI should be used
    const useAI = document.querySelector('input[name="use_ai"]')?.checked ?? true;
    
    // Create request payload
    const payload = {
        text: text,
        methods: methods,
        use_ai: useAI
    };
    
    // Send AJAX request
    fetch('/api/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Network response error: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error('Error from server:', data.error);
            alert(`Error: ${data.error}`);
            submitButton.disabled = false;
            submitButton.textContent = originalText;
            return;
        }
        
        // Redirect to results page with the data ID
        window.location.href = `/analyze?id=${data.id || 'latest'}`;
    })
    .catch(error => {
        console.error('Error during analysis:', error);
        alert('Error analyzing text. Please try again.');
        
        // Reset form state
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    });
});