"""
Generator for Bloom's Taxonomy questions
"""
import logging
import random

logger = logging.getLogger(__name__)

def generate_blooms_questions(analysis_data):
    """Generate questions based on Bloom's Taxonomy"""
    try:
        text = analysis_data.get('text', '')
        if not text:
            logger.warning("No text provided for Bloom's Taxonomy questions generation")
            return []
            
        # Get key concepts and other analysis data
        key_concepts = analysis_data.get('key_concepts', [])
        entities = analysis_data.get('entities', [])
        themes = analysis_data.get('themes', [])
        
        # Question templates for each level of Bloom's Taxonomy
        blooms_templates = {
            "Remember": [
                "Define {} in your own words.",
                "Identify the key features of {}.",
                "List the main components of {}.",
                "What does {} mean in this context?",
                "Recall the purpose of {}."
            ],
            "Understand": [
                "Explain the concept of {} in your own words.",
                "Summarize how {} works.",
                "Interpret the significance of {}.",
                "Describe the relationship between {} and {}.",
                "Clarify why {} is important."
            ],
            "Apply": [
                "How would you use {} to solve a real problem?",
                "Demonstrate how {} could be implemented in a new situation.",
                "Apply the concept of {} to {}.",
                "How might {} be used in your own context?",
                "What examples illustrate the principle of {}?"
            ],
            "Analyze": [
                "What are the different components of {}?",
                "Compare and contrast {} and {}.",
                "Analyze the strengths and limitations of {}.",
                "What evidence supports claims about {}?",
                "How does {} relate to broader issues of {}?"
            ],
            "Evaluate": [
                "Evaluate the effectiveness of {}.",
                "Critique the approach to {}.",
                "What are the most persuasive arguments for or against {}?",
                "Judge the validity of claims about {}.",
                "What criteria would you use to assess {}?"
            ],
            "Create": [
                "Design a new approach to {}.",
                "Propose an alternative to {}.",
                "How would you improve {}?",
                "Generate a solution that addresses the limitations of {}.",
                "Create a plan that incorporates {}."
            ]
        }
        
        # Generate one question for each Bloom's level
        questions = []
        
        # Get concepts to use in questions
        concepts = key_concepts + themes
        if not concepts and entities:
            concepts = entities
        if not concepts:
            concepts = ["the main topic", "this concept", "the central idea", "this approach"]
            
        # Generate questions for each level
        for level, templates in blooms_templates.items():
            template = random.choice(templates)
            
            # Format template based on number of placeholders
            if template.count("{}") == 1:
                concept = random.choice(concepts) if concepts else "this concept"
                question = f"{level}: {template.format(concept)}"
            elif template.count("{}") == 2 and len(concepts) >= 2:
                # Use two different concepts
                concept1 = concepts[0]
                concept2 = concepts[1]
                question = f"{level}: {template.format(concept1, concept2)}"
            else:
                # Fallback for templates with multiple placeholders but not enough concepts
                concept = random.choice(concepts) if concepts else "this concept"
                context = "the broader field" if not entities else random.choice(entities)
                question = f"{level}: {template.format(concept, context)}"
                
            questions.append(question)
            
        return questions
            
    except Exception as e:
        logger.error(f"Error generating Bloom's Taxonomy questions: {str(e)}")
        return []