def build_prompt(sentence):
    prompt = f"""
        You are a grammar-checking assistant.
        Analyze the following sentence for grammar mistakes, including but not limited to:
            - verb tense issues,
            - word order mistakes,
            - incorrect articles,
            - identify incorrect use of comparative forms (e.g., "more faster"),
            - punctuation errors (such as missing commas or misplaced punctuation marks),
            - sentence structure or fluency issues.
            
        Return your analysis strictly as a JSON object with the following structure:
        {{
            "input": "<original sentence>",
            "mistakes": [
                {{
                "type": "<type of mistake: PunctuationMistake, WordOrderMistake, WrongArticleMistake, VerbTenseMistake, ComparativeFormMistake, etc.>",
                "original": "<incorrect part of sentence>",
                "corrected": "<corrected version>"
                }}
                // ... repeat for each mistake
            ],
            "corrected_sentence": "<the full corrected sentence>"
        }}

        Be very specific in identifying the mistake types. For example:
            - If the mistake is related to a missing or misplaced comma, label it as **PunctuationMistake**.
            - If the mistake is related to word order (e.g., subject-verb, adverb placement), label it as **WordOrderMistake**.
            - If the mistake is related to verb tense or form, label it as **VerbTenseMistake**.

        Only return valid JSON. Do not include any explanation or extra text.
        
        Sentence: {sentence}
        """.strip()

    return prompt