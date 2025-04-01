"""
Generators package
"""

# Import các generators từ wrapped_generators
from .wrapped_generators import generate_socratic_questions, generate_multilevels, generate_practice_questions

# Thêm các generators khác nếu có
try:
    from .blooms_generator import generate_blooms_questions
except ImportError:
    def generate_blooms_questions(*args, **kwargs): 
        return ["Bloom's generator not available"]

try:
    from .key_terms_generator import generate_key_terms
except ImportError:
    def generate_key_terms(*args, **kwargs): 
        return ["Key terms generator not available"]
        
try:
    from .analogies_generator import generate_analogies
except ImportError:
    def generate_analogies(*args, **kwargs): 
        return ["Analogies generator not available"]
        
try:
    from .summary_generator import generate_summary
except ImportError:
    def generate_summary(*args, **kwargs): 
        return ["Summary generator not available"]

# Định nghĩa AVAILABLE_GENERATORS với các generators
AVAILABLE_GENERATORS = {
    "socratic": generate_socratic_questions,
    "multilevel": generate_multilevels,
    "practice": generate_practice_questions,
    "blooms": generate_blooms_questions,
    "key_terms": generate_key_terms,
    "analogies": generate_analogies,
    "summary": generate_summary
}

__all__ = ['AVAILABLE_GENERATORS']