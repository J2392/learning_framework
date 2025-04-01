// static/js/app.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    
    // Debug: Check DOM elements
    console.log('DOM elements check:');
    console.log('- results-container:', document.getElementById('results-container'));
    console.log('- concepts-display:', document.getElementById('concepts-display'));
    console.log('- json-display:', document.getElementById('json-display'));
    
    // Method selection handling
    const allMethodsCheckbox = document.getElementById('method-all');
    const methodCheckboxes = document.querySelectorAll('input[type="checkbox"]:not(#method-all)');
    
    // When "All Methods" is checked/unchecked
    if (allMethodsCheckbox) {
        allMethodsCheckbox.addEventListener('change', function() {
            methodCheckboxes.forEach(checkbox => {
                checkbox.checked = false;
                checkbox.disabled = this.checked;
            });
        });
    }
    
    // When individual methods are checked/unchecked
    methodCheckboxes.forEach(checkbox => {
        if (allMethodsCheckbox) {
            checkbox.disabled = allMethodsCheckbox.checked;
        }
        
        checkbox.addEventListener('change', function() {
            if (!allMethodsCheckbox) return;
            
            const anyMethodChecked = Array.from(methodCheckboxes).some(cb => cb.checked);
            if (anyMethodChecked) {
                allMethodsCheckbox.checked = false;
            }
        });
    });
    
    // Clear button handler
    document.getElementById('clear-btn')?.addEventListener('click', function() {
        document.getElementById('input-text').value = '';
        document.getElementById('results-container').style.display = 'none';
    });
    
    // Analyze button click handler
    document.getElementById('analyze-btn').addEventListener('click', function() {
        console.log('Analyze button clicked');
        const text = document.getElementById('input-text').value;
        if (!text) {
            alert('Please enter text to analyze');
            return;
        }
        
        // Get selected methods
        const methods = [];
        
        if (allMethodsCheckbox && allMethodsCheckbox.checked) {
            methods.push('all');
        } else {
            methodCheckboxes.forEach(checkbox => {
                if (checkbox.checked) {
                    methods.push(checkbox.value);
                }
            });
            
            if (methods.length === 0) {
                alert('Please select at least one thinking method');
                return;
            }
        }
        
        // Get AI enhancement option
        const useAI = document.getElementById('use-ai')?.checked || false;
        
        // Show loading, hide results
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }
        
        const resultsContainer = document.getElementById('results-container');
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
        
        // Record start time for tracking processing time
        const startTime = Date.now();
        
        // Disable analyze button
        this.disabled = true;
        this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Analyzing...';
        
        console.log('Sending data:', {text: text, methods: methods, use_ai: useAI});
        
        // Call API
        fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                methods: methods,
                use_ai: useAI
            })
        })
        .then(response => {
            console.log('Response received:', response);
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Analysis failed');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Data received:', data);
            
            // Calculate and display processing time
            const processingTime = Date.now() - startTime;
            const timeValue = document.getElementById('time-value');
            if (timeValue) {
                timeValue.textContent = processingTime;
                document.getElementById('processing-time').style.display = 'block';
            }
            
            // Reset button
            document.getElementById('analyze-btn').disabled = false;
            document.getElementById('analyze-btn').innerHTML = 'Analyze';
            
            // Hide loading
            if (loadingElement) {
                loadingElement.style.display = 'none';
            }
            
            if (data.error) {
                alert(data.error);
                return;
            }
            
            // Display results
            displayResults(data);
            
            // Show results container - CRITICAL FIX
            if (resultsContainer) {
                console.log('Setting results container display to block');
                resultsContainer.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('analyze-btn').disabled = false;
            document.getElementById('analyze-btn').innerHTML = 'Analyze';
            if (loadingElement) {
                loadingElement.style.display = 'none';
            }
            alert('An error occurred while analyzing text: ' + error.message);
        });
    });
    
    // Function to display results
    function displayResults(data) {
        console.log('Displaying results - data:', data);
        
        // Display concepts in visual tab
        const conceptsDisplay = document.getElementById('concepts-display');
        if (conceptsDisplay) {
            conceptsDisplay.innerHTML = '';
            if (data.concepts && data.concepts.length > 0) {
                data.concepts.forEach(concept => {
                    const badge = document.createElement('div');
                    badge.className = 'concept-badge';
                    badge.textContent = concept;
                    conceptsDisplay.appendChild(badge);
                });
            } else {
                conceptsDisplay.innerHTML = '<p>No key concepts identified</p>';
            }
            console.log('Concepts displayed');
        } else {
            console.warn('concepts-display element not found');
        }
        
        // Display context 
        const contextDisplay = document.getElementById('context-display');
        if (contextDisplay) {
            contextDisplay.textContent = data.context || 'Unknown context';
            console.log('Context displayed:', data.context);
        } else {
            console.warn('context-display element not found');
        }
        
        // Display complexity
        const complexityDisplay = document.getElementById('complexity-display');
        if (complexityDisplay && data.complexity) {
            complexityDisplay.innerHTML = `
                <p><strong>Total words:</strong> ${data.complexity.total_words || 'N/A'}</p>
                <p><strong>Unique words:</strong> ${data.complexity.unique_words || 'N/A'}</p>
                <p><strong>Average sentence length:</strong> ${data.complexity.avg_sentence_length ? data.complexity.avg_sentence_length.toFixed(1) : 'N/A'} words</p>
            `;
            console.log('Complexity displayed');
        } else if (complexityDisplay) {
            complexityDisplay.innerHTML = '<p>No complexity data available</p>';
        }
        
        // Display JSON Data
        const jsonDisplay = document.getElementById('json-display');
        if (jsonDisplay) {
            try {
                jsonDisplay.innerHTML = syntaxHighlight(JSON.stringify(data, null, 2));
                console.log('JSON data displayed');
            } catch (e) {
                console.error('Error displaying JSON:', e);
                jsonDisplay.innerHTML = '<p>Error displaying JSON data</p>';
            }
        }
        
        // Display Socratic Questions
        const socraticDisplay = document.getElementById('socratic-display');
        if (socraticDisplay) {
            socraticDisplay.innerHTML = '';
            
            // First check if we have direct socratic_questions in the root
            if (data.socratic_questions) {
                displaySocraticQuestions(data.socratic_questions, socraticDisplay);
            }
            // Then check if it's under methods.socratic
            else if (data.methods && data.methods.socratic) {
                displaySocraticQuestions(data.methods.socratic, socraticDisplay);
            }
            // Finally, try the normal generator output format - check if data has expected question types
            else if (data.conceptual || data.exploratory || data.analytical) {
                displaySocraticQuestions(data, socraticDisplay);
            }
            // If nothing matches, display empty message
            else {
                socraticDisplay.innerHTML = '<p>No Socratic questions available</p>';
            }
        }
        
        // Display Multi-level Explanations
        const multilevelDisplay = document.getElementById('multilevel-display');
        if (multilevelDisplay) {
            multilevelDisplay.innerHTML = '';
            
            // Check possible data structures
            if (data.multi_level_explanations) {
                displayMultiLevelExplanations(data.multi_level_explanations, multilevelDisplay);
            }
            else if (data.methods && data.methods.multi_level) {
                displayMultiLevelExplanations(data.methods.multi_level, multilevelDisplay);
            }
            else if (data.child || data.high_school || data.academic) {
                displayMultiLevelExplanations(data, multilevelDisplay);
            }
            else {
                multilevelDisplay.innerHTML = '<p>No multi-level explanations available</p>';
            }
        }
        
        // Display Practice Questions
        const practiceDisplay = document.getElementById('practice-display');
        if (practiceDisplay) {
            practiceDisplay.innerHTML = '';
            
            // Check possible data structures
            if (data.practice_questions) {
                displayPracticeQuestions(data.practice_questions, practiceDisplay);
            }
            else if (data.methods && data.methods.practice) {
                displayPracticeQuestions(data.methods.practice, practiceDisplay);
            }
            else if (data.beginner || data.intermediate || data.advanced) {
                displayPracticeQuestions(data, practiceDisplay);
            }
            else {
                practiceDisplay.innerHTML = '<p>No practice questions available</p>';
            }
        }

        // Add similar handling for other thinking methods (if their display elements exist)
        console.log('All results displayed successfully');
    }
    
    // Function to display Socratic questions
function displaySocraticQuestions(questions, container) {
    console.log("Displaying Socratic questions:", questions);
    
    // If no questions, error object, or empty object, show message
    if (!questions || questions.error || Object.keys(questions).length === 0) {
        if (questions && questions.error) {
            container.innerHTML = `<p class="text-danger">Error: ${questions.error}</p>`;
            if (questions.details) {
                container.innerHTML += `<p><small class="text-muted">${questions.details}</small></p>`;
            }
        } else {
            container.innerHTML = '<p>No Socratic questions available</p>';
        }
        return;
    }
    
    try {
        // Clear previous content
        container.innerHTML = '';
        
        // Handle different data structures
        if (typeof questions === 'object' && !Array.isArray(questions)) {
            // If the result has keys like "conceptual", "exploratory", etc.
            const questionTypes = [
                "conceptual", "exploratory", "analytical", 
                "evaluative", "hypothetical", "reflective"
            ];
            
            // Check if result has any of the expected question types
            const hasQuestionTypes = questionTypes.some(type => 
                Array.isArray(questions[type]) && questions[type].length > 0
            );
            
            if (hasQuestionTypes) {
                // Process each question type
                questionTypes.forEach(type => {
                    if (Array.isArray(questions[type]) && questions[type].length > 0) {
                        const typeHeading = document.createElement('h5');
                        typeHeading.textContent = type.charAt(0).toUpperCase() + type.slice(1) + ' Questions';
                        container.appendChild(typeHeading);
                        
                        const questionsList = document.createElement('ul');
                        questionsList.className = 'list-group mb-3';
                        
                        questions[type].forEach(question => {
                            const listItem = document.createElement('li');
                            listItem.className = 'list-group-item';
                            listItem.textContent = typeof question === 'string' ? question : 
                                (question.question ? question.question : JSON.stringify(question));
                            questionsList.appendChild(listItem);
                        });
                        
                        container.appendChild(questionsList);
                    }
                });
                return;
            }
        }
        
        // If we get here, the data structure wasn't what we expected
        container.innerHTML = '<p>Unable to display Socratic questions (unsupported data structure)</p>';
    } catch (e) {
        console.error('Error displaying Socratic questions:', e);
        container.innerHTML = `<p class="text-danger">Error displaying Socratic questions: ${e.message}</p>`;
    }
}

// Function to display Multi-level explanations
function displayMultiLevelExplanations(explanations, container) {
    console.log("Displaying Multi-level explanations:", explanations);
    
    // If no explanations, error object, or empty object, show message
    if (!explanations || explanations.error || Object.keys(explanations).length === 0) {
        if (explanations && explanations.error) {
            container.innerHTML = `<p class="text-danger">Error: ${explanations.error}</p>`;
            if (explanations.details) {
                container.innerHTML += `<p><small class="text-muted">${explanations.details}</small></p>`;
            }
        } else {
            container.innerHTML = '<p>No multi-level explanations available</p>';
        }
        return;
    }
    
    try {
        // Clear previous content
        container.innerHTML = '';
        
        // Handle different data structures
        if (typeof explanations === 'object' && !Array.isArray(explanations)) {
            // If the result has keys like "child", "high_school", "academic"
            const levels = ["child", "high_school", "academic"];
            
            // Check if result has any of the expected levels
            const hasLevels = levels.some(level => 
                Array.isArray(explanations[level]) && explanations[level].length > 0
            );
            
            if (hasLevels) {
                // Process each level
                levels.forEach(level => {
                    if (Array.isArray(explanations[level]) && explanations[level].length > 0) {
                        const levelHeading = document.createElement('h5');
                        levelHeading.textContent = formatLevelName(level) + ' Level Explanations';
                        container.appendChild(levelHeading);
                        
                        const explanationsList = document.createElement('ul');
                        explanationsList.className = 'list-group mb-3';
                        
                        explanations[level].forEach(explanation => {
                            const listItem = document.createElement('li');
                            listItem.className = 'list-group-item';
                            listItem.textContent = typeof explanation === 'string' ? explanation : JSON.stringify(explanation);
                            explanationsList.appendChild(listItem);
                        });
                        
                        container.appendChild(explanationsList);
                    }
                });
                return;
            }
        }
        
        // If we get here, the data structure wasn't what we expected
        container.innerHTML = '<p>Unable to display multi-level explanations (unsupported data structure)</p>';
    } catch (e) {
        console.error('Error displaying Multi-level explanations:', e);
        container.innerHTML = `<p class="text-danger">Error displaying Multi-level explanations: ${e.message}</p>`;
    }
}

// Function to display Practice questions
function displayPracticeQuestions(questions, container) {
    console.log("Displaying Practice questions:", questions);
    
    // If no questions, error object, or empty object, show message
    if (!questions || questions.error || Object.keys(questions).length === 0) {
        if (questions && questions.error) {
            container.innerHTML = `<p class="text-danger">Error: ${questions.error}</p>`;
            if (questions.details) {
                container.innerHTML += `<p><small class="text-muted">${questions.details}</small></p>`;
            }
        } else {
            container.innerHTML = '<p>No practice questions available</p>';
        }
        return;
    }
    
    try {
        // Clear previous content
        container.innerHTML = '';
        
        // Handle different data structures
        if (typeof questions === 'object' && !Array.isArray(questions)) {
            // If the result has keys like "beginner", "intermediate", "advanced"
            const levels = ["beginner", "intermediate", "advanced"];
            
            // Check if result has any of the expected levels
            const hasLevels = levels.some(level => 
                Array.isArray(questions[level]) && questions[level].length > 0
            );
            
            if (hasLevels) {
                // Process each level
                levels.forEach(level => {
                    if (Array.isArray(questions[level]) && questions[level].length > 0) {
                        const levelHeading = document.createElement('h5');
                        levelHeading.textContent = level.charAt(0).toUpperCase() + level.slice(1) + ' Level Questions';
                        container.appendChild(levelHeading);
                        
                        const questionsList = document.createElement('ul');
                        questionsList.className = 'list-group mb-3';
                        
                        questions[level].forEach(question => {
                            const listItem = document.createElement('li');
                            listItem.className = 'list-group-item';
                            listItem.textContent = typeof question === 'string' ? question : JSON.stringify(question);
                            questionsList.appendChild(listItem);
                        });
                        
                        container.appendChild(questionsList);
                    }
                });
                return;
            }
        }
        
        // If we get here, the data structure wasn't what we expected
        container.innerHTML = '<p>Unable to display practice questions (unsupported data structure)</p>';
    } catch (e) {
        console.error('Error displaying Practice questions:', e);
        container.innerHTML = `<p class="text-danger">Error displaying Practice questions: ${e.message}</p>`;
    }
}
    // Helper function to format level names
    function formatLevelName(level) {
        if (level === 'child') return 'Child';
        if (level === 'high_school') return 'High School';
        if (level === 'academic') return 'Academic';
        return level.charAt(0).toUpperCase() + level.slice(1);
    }
    
    // Function to syntax highlight JSON
    function syntaxHighlight(json) {
        if (typeof json != 'string') {
            json = JSON.stringify(json, undefined, 2);
        }
        json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
            let cls = 'number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'key';
                } else {
                    cls = 'string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean';
            } else if (/null/.test(match)) {
                cls = 'null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        });
    }

    // Log loading completion
    console.log('App.js initialization complete');
});