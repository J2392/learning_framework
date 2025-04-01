"""
Generator for Seven Hat Thinking analysis
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger('generators')

def generate_seven_hat_analysis(analysis: Dict[str, Any]) -> List[str]:
    """Generate analysis using de Bono's Seven Thinking Hats method"""
    logger.info("Generating Seven Hat Thinking analysis")
    
    # Default analysis if no input is available
    if not analysis:
        return ["No Seven Hat analysis available"]
    
    hat_analysis = []
    
    # White Hat (Facts and Information)
    hat_analysis.append("WHITE HAT (Facts and Information):")
    white_hat = _generate_white_hat(analysis)
    hat_analysis.extend(white_hat)
    
    # Red Hat (Feelings and Emotions)
    hat_analysis.append("RED HAT (Feelings and Emotions):")
    red_hat = _generate_red_hat(analysis)
    hat_analysis.extend(red_hat)
    
    # Black Hat (Critical Judgment)
    hat_analysis.append("BLACK HAT (Critical Judgment):")
    black_hat = _generate_black_hat(analysis)
    hat_analysis.extend(black_hat)
    
    # Yellow Hat (Positive Aspects)
    hat_analysis.append("YELLOW HAT (Positive Aspects):")
    yellow_hat = _generate_yellow_hat(analysis)
    hat_analysis.extend(yellow_hat)
    
    # Green Hat (Creativity and Alternatives)
    hat_analysis.append("GREEN HAT (Creativity and Alternatives):")
    green_hat = _generate_green_hat(analysis)
    hat_analysis.extend(green_hat)
    
    # Blue Hat (Process and Overview)
    hat_analysis.append("BLUE HAT (Process and Overview):")
    blue_hat = _generate_blue_hat(analysis)
    hat_analysis.extend(blue_hat)
    
    return hat_analysis

def _generate_white_hat(analysis: Dict[str, Any]) -> List[str]:
    """Generate White Hat (facts and information) analysis"""
    white_hat = []
    
    if 'facts' in analysis and analysis['facts']:
        for fact in analysis['facts']:
            white_hat.append(f"• {fact}")
    else:
        white_hat.append("• The text presents several key facts and data points")
        white_hat.append("• The information appears to be structured around main concepts")
        white_hat.append("• Multiple sources or references may be cited to support claims")
    
    return white_hat

def _generate_red_hat(analysis: Dict[str, Any]) -> List[str]:
    """Generate Red Hat (feelings and emotions) analysis"""
    red_hat = []
    
    if 'sentiment' in analysis:
        sentiment = analysis['sentiment']
        red_hat.append(f"• The overall tone of the text appears to be {sentiment}")
    
    red_hat.append("• The material may evoke curiosity and intellectual engagement")
    red_hat.append("• Some concepts might cause confusion if not clearly explained")
    red_hat.append("• The presentation style could affect emotional response to the content")
    
    return red_hat

def _generate_black_hat(analysis: Dict[str, Any]) -> List[str]:
    """Generate Black Hat (critical judgment) analysis"""
    black_hat = []
    
    black_hat.append("• Some claims may lack sufficient supporting evidence")
    black_hat.append("• Alternative perspectives might not be adequately addressed")
    black_hat.append("• The scope of application could be limited by unstated constraints")
    black_hat.append("• Potential risks or downsides should be more thoroughly examined")
    
    return black_hat

def _generate_yellow_hat(analysis: Dict[str, Any]) -> List[str]:
    """Generate Yellow Hat (positive aspects) analysis"""
    yellow_hat = []
    
    yellow_hat.append("• The concepts presented offer valuable insights into the subject")
    yellow_hat.append("• The approach could lead to effective problem-solving applications")
    yellow_hat.append("• Understanding these ideas may provide competitive advantages")
    yellow_hat.append("• Long-term benefits include deeper understanding of the domain")
    
    return yellow_hat

def _generate_green_hat(analysis: Dict[str, Any]) -> List[str]:
    """Generate Green Hat (creativity and alternatives) analysis"""
    green_hat = []
    
    green_hat.append("• Consider applying these concepts in entirely different domains")
    green_hat.append("• What if the fundamental assumptions were reversed?")
    green_hat.append("• Combining these ideas with emerging technologies could create new opportunities")
    green_hat.append("• Alternative methodologies might yield complementary insights")
    
    return green_hat

def _generate_blue_hat(analysis: Dict[str, Any]) -> List[str]:
    """Generate Blue Hat (process and overview) analysis"""
    blue_hat = []
    
    blue_hat.append("• This analysis has examined the content from multiple perspectives")
    blue_hat.append("• The key insights emerge from considering both critical and positive aspects")
    blue_hat.append("• Further exploration should focus on practical applications and testing")
    blue_hat.append("• The next steps involve synthesizing these viewpoints into actionable insights")
    
    return blue_hat