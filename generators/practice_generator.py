"""
Generator for practice questions
"""
import logging
import random

logger = logging.getLogger(__name__)

def generate_practice_questions(analysis_data):
    """Generate practice questions based on analyzed text"""
    try:
        text = analysis_data.get('text', '')
        if not text:
            logger.warning("No text provided for practice questions generation")
            return []
            
        # Get key concepts and other analysis data
        key_concepts = analysis_data.get('key_concepts', [])
        entities = analysis_data.get('entities', [])
        themes = analysis_data.get('themes', [])
        
        # Lists of question templates
        recall_templates = [
            "Identify and explain the concept of {}.",
            "Define {} in your own words.",
            "List the main characteristics of {}.",
            "Describe the process of {} mentioned in the text.",
            "What are the key points about {} presented in the text?"
        ]
        
        application_templates = [
            "How would you apply the concept of {} in a real-world situation?",
            "Give an example of how {} might be used in {}.",
            "Explain how {} relates to your personal experience.",
            "How could the principles of {} be implemented in a different context?",
            "Design a scenario where {} would be particularly important."
        ]
        
        analysis_templates = [
            "Compare and contrast {} and {}.",
            "What are the strengths and weaknesses of {}?",
            "Analyze the relationship between {} and {}.",
            "What evidence supports the claims about {}?",
            "What are potential criticisms of the approach to {}?"
        ]
        
        # Generate diverse practice questions
        questions = []
        
        # Recall questions
        if key_concepts:
            for concept in key_concepts[:2]:
                template = random.choice(recall_templates)
                questions.append(template.format(concept))
                
        # Application questions
        if key_concepts and entities:
            concept = random.choice(key_concepts)
            context = random.choice(entities) if entities else "a different field"
            template = random.choice(application_templates)
            if "{}" in template:
                if template.count("{}") == 1:
                    questions.append(template.format(concept))
                else:
                    questions.append(template.format(concept, context))
                
        # Analysis questions
        if len(key_concepts) >= 2:
            template = random.choice(analysis_templates)
            if template.count("{}") == 1:
                questions.append(template.format(key_concepts[0]))
            else:
                questions.append(template.format(key_concepts[0], key_concepts[1]))
                
        # Add general practice questions if we don't have enough
        if len(questions) < 5:
            general_questions = [
                "Summarize the main ideas presented in this text.",
                "What do you think is the most important point made? Explain your reasoning.",
                "Identify a real-world example that illustrates the key concepts.",
                "How does this information connect to what you already know about the topic?",
                "What questions do you still have after reading this text?",
                "How might this information be useful in your work or studies?"
            ]
            # Add randomly selected general questions
            num_to_add = min(5 - len(questions), len(general_questions))
            questions.extend(random.sample(general_questions, num_to_add))
            
        return questions
            
    except Exception as e:
        logger.error(f"Error generating practice questions: {str(e)}")
        return []