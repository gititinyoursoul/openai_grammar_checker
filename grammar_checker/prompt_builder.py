from grammar_checker.logger import get_logger
from grammar_checker.config import PROMPT_TEMPLATE

logger = get_logger(__name__)

def build_prompt(sentence, prompt_template_path=PROMPT_TEMPLATE):
    # load prompt
    try:
        with open(prompt_template_path, "r", encoding="utf-8") as file:
            template = file.read().strip()
        logger.info(f"Loaded prompt template from {prompt_template_path}")
    except FileNotFoundError:
        logger.error(f"Prompt template file not found: {prompt_template_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading prompt template: {e}")
        raise        
    
    # build prompt
    if not sentence:
        logger.error("Empty sentence provided for prompt building")
        raise ValueError("Sentence cannot be empty") 
    prompt = template.replace("{sentence}", sentence)
    logger.info(f"Prompt built successfully for sentence: {sentence}")    
    
    return prompt