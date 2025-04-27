from grammar_checker.logger import get_logger

logger = get_logger(__name__)

def build_prompt(sentence: str, prompt_template_path):
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
    
    truncted_sentence = sentence[:20] + "..." if len(sentence) > 20 else sentence
    logger.info(f"Building prompt using template '{prompt_template_path}' with sentence: '{truncted_sentence}'")  
    
    return prompt