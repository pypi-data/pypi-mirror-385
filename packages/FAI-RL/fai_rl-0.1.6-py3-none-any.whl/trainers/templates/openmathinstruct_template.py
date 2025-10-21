"""OpenMathInstruct dataset formatting template."""

SYSTEM_PROMPT = """
Respond in the following format:

<reasoning>
...
</reasoning>
<answer>
...
</answer>
"""

XML_COT_FORMAT = """\
<reasoning>
{reasoning}
</reasoning>
<answer>
{answer}
</answer>
"""


class OpenMathInstructTemplate:
    """Template for formatting OpenMathInstruct math dataset examples."""
    
    @staticmethod
    def format_for_training(example, prompt_col="question", answer_col="answer"):
        """
        Format a OpenMathInstruct example for training.
        
        Args:
            example: Dataset example containing question and answer
            prompt_col: Column name for the question/prompt
            answer_col: Column name for the answer
            
        Returns:
            dict: Formatted example with 'prompt' and 'answer' keys
        """
        prompt = example[prompt_col]
        answer = example[answer_col]
        
        training_prompt = [
            {'role': 'system', 'content': SYSTEM_PROMPT}, 
            {'role': 'user', 'content': 'What is the largest single-digit prime number?'},
            {'role': 'assistant', 'content': XML_COT_FORMAT.format(
                reasoning="9 is divisible by 3 and 8 is divisible by 2, but 7 is prime.",
                answer="7"
            )},
            {'role': 'user', 'content': prompt}
        ]
        return {'prompt': training_prompt, 'answer': answer}
    
    @staticmethod
    def format_prompt_only(example, prompt_col="question", answer_col="answer"):
        """
        Format an OpenMathInstruct example for PPO training (prompt only).
        
        Args:
            example: Dataset example containing question
            prompt_col: Column name for the question/prompt  
            answer_col: Column name for the answer (for ground truth extraction)
            
        Returns:
            str: Formatted prompt for generation
        """
        prompt = example[prompt_col]
        
        # Create the conversation for PPO training
        training_prompt = [
            {'role': 'system', 'content': SYSTEM_PROMPT}, 
            {'role': 'user', 'content': 'What is the largest single-digit prime number?'},
            {'role': 'assistant', 'content': XML_COT_FORMAT.format(
                reasoning="9 is divisible by 3 and 8 is divisible by 2, but 7 is prime.",
                answer="7"
            )},
            {'role': 'user', 'content': prompt}
        ]
        
        # For PPO, we typically need the conversation formatted as a string
        # This is a simple format - you may need to adjust based on your tokenizer
        formatted_prompt = ""
        for turn in training_prompt:
            if turn['role'] == 'system':
                formatted_prompt += f"System: {turn['content']}\n\n"
            elif turn['role'] == 'user':
                formatted_prompt += f"User: {turn['content']}\n\n"
            elif turn['role'] == 'assistant':
                formatted_prompt += f"Assistant: {turn['content']}\n\n"
        
        formatted_prompt += "Assistant:"  # Prompt for generation
        
        return formatted_prompt.strip()
    