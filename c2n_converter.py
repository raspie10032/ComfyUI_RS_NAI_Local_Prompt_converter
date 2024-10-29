import re

def identify_character_tags(text):
    """Identify character tag patterns and convert them to temporary tokens"""
    result = text
    
    # Define patterns
    patterns = [
        # Basic patterns
        # 1. name (title) - basic form
        (r'\b\w+\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_1'),
        # 2. name (title) (option1) - 1 option
        (r'\b\w+\s+\([^()]+\)\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_2'),
        # 3. name (title) (option1) (option2) - 2 options
        (r'\b\w+\s+\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_3'),
        # 4. name (title) (option1) (option2) (option3) - 3 options
        (r'\b\w+\s+\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)', 'CHAR_TAG_4'),
        
        # Underscore patterns
        # 5. name_(title) - underscore basic form
        (r'\b\w+_\([^()]+\)(?!\s*\()', 'CHAR_TAG_5'),
        # 6. name_(title) (option1) - underscore with 1 option
        (r'\b\w+_\([^()]+\)\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_6'),
        # 7. name_(title) (option1) (option2) - underscore with 2 options
        (r'\b\w+_\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_7'),
        # 8. name_(title) (option1) (option2) (option3) - underscore with 3 options
        (r'\b\w+_\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)', 'CHAR_TAG_8'),

        # Escape patterns
        # 9. name \(title\) - escaped basic form
        (r'\b\w+\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_1'),
        # 10. name \(title\) \(option1\) - escaped with 1 option
        (r'\b\w+\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_2'),
        # 11. name \(title\) \(option1\) \(option2\) - escaped with 2 options
        (r'\b\w+\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_3'),
        # 12. name \(title\) \(option1\) \(option2\) \(option3\) - escaped with 3 options
        (r'\b\w+\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)', 'ESC_CHAR_TAG_4'),

        # Underscore escape patterns
        # 13. name_\(title\) - underscore escaped basic form
        (r'\b\w+_\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_5'),
        # 14. name_\(title\) \(option1\) - underscore escaped with 1 option
        (r'\b\w+_\\\([^()]+\\\)\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_6'),
        # 15. name_\(title\) \(option1\) \(option2\) - underscore escaped with 2 options
        (r'\b\w+_\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_7'),
        # 16. name_\(title\) \(option1\) \(option2\) \(option3\) - underscore escaped with 3 options
        (r'\b\w+_\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)', 'ESC_CHAR_TAG_8')
    ]
    
    # Dictionary to store pattern matching results and tokens
    tokens = {}
    token_count = 0
    
    # Check pattern matches and convert to tokens
    for pattern, token_base in patterns:
        matches = list(re.finditer(pattern, result))
        for match in matches:
            matched_text = match.group(0)
            token = f"{token_base}_{token_count}"
            # Convert escaped parentheses to regular ones when storing
            if token_base.startswith('ESC_'):
                stored_text = matched_text.replace('\\(', '(').replace('\\)', ')')
            else:
                stored_text = matched_text
            tokens[token] = stored_text
            result = result.replace(matched_text, token)
            token_count += 1
            # print(f"Found {token_base}: {matched_text} -> {token}")
    
    return result, tokens

def prompt_to_stack(sentence):
    """
    Parse prompt and convert to nested structure with weights
    """
    result = []
    current_str = ""
    # Stack items format: { "weight": weight_value, "data": content_list }
    stack = [{"weight": 1.0, "data": result}]
    
    for i, c in enumerate(sentence):
        if c in '()':
            if c == '(':
                # Process current string
                if current_str.strip(): 
                    stack[-1]["data"].append(current_str.strip())
                # Start new group
                stack[-1]["data"].append({"weight": 1.0, "data": []})
                stack.append(stack[-1]["data"][-1])
            elif c == ')':
                # Process weight when closing parenthesis
                searched = re.search(r"^(.*):([0-9\.]+)$", current_str.strip())
                current_str, weight = searched.groups() if searched else (current_str.strip(), 1.1)
                if current_str.strip(): 
                    stack[-1]["data"].append(current_str.strip())
                stack[-1]["weight"] = float(weight)
                if stack[-1]["data"] != result:
                    stack.pop()
                else:
                    print("Error in parsing:", sentence)
                    print(f"Column {i:>3}:", " " * i + "^")
            current_str = ""
        else:
            current_str += c
            
    if current_str.strip():
        stack[-1]["data"].append(current_str.strip())
    
    return result

def process_stack_with_weights(stack_item, parent_weight=1.0):
    """
    Process stack structure and calculate final weights
    """
    if isinstance(stack_item, str):
        return f"({stack_item}:{parent_weight:.2f})"
    
    current_weight = stack_item["weight"] * parent_weight
    processed_items = []
    
    for item in stack_item["data"]:
        if isinstance(item, str):
            # Process comma-separated items
            subitems = [subitem.strip() for subitem in item.split(',')]
            for subitem in subitems:
                if subitem:  # Process only non-empty strings
                    if ':' in subitem:  # If weight already exists
                        tag, weight = subitem.split(':')
                        processed_items.append(f"({tag.strip()}:{float(weight) * current_weight:.2f})")
                    else:  # If no weight
                        processed_items.append(f"({subitem}:{current_weight:.2f})")
        else:
            # Process nested structure recursively
            result = process_stack_with_weights(item, current_weight)
            if result:
                processed_items.extend(result.split(', '))
    
    return ', '.join(processed_items)

def process_weighted_tags(text):
    """
    Process weighted tags in ComfyUI format
    """
    # print("Starting process_weighted_tags with text:", text)
    
    # Convert to stack structure
    stack = prompt_to_stack(text)
    
    # Calculate weights and generate result
    result = process_stack_with_weights({"weight": 1.0, "data": stack})
    
    # print("Final result from process_weighted_tags:", result)
    return result

def convert_to_novelai(tag, weight):
    """
    Convert single tag and weight to Novel AI format
    weight > 1: use curly braces
    weight < 1: use square brackets
    """
    # print("Converting to NovelAI format:", tag, "with weight:", weight)
    if abs(weight - 1.0) < 0.001:
        return tag
        
    if weight > 1:
        count = round((weight - 1.0) / 0.05)
        result = '{' * count + tag + '}' * count
    else:
        count = round((1.0 - weight) / 0.05)
        result = '[' * count + tag + ']' * count
    
    # print("Conversion result:", result)
    return result

def comfy_to_novel(prompt):
    if not isinstance(prompt, str):
        return "Error: Input must be a string"

    try:
        # print("Starting conversion with prompt:", prompt)
        
        # 1. Identify character tag patterns and convert to temporary tokens
        prompt, char_tokens = identify_character_tags(prompt)
        # print("After character tag identification:", prompt)
        
        # 2. Temporarily convert "artist:" to "artist_"
        prompt = prompt.replace("artist:", "artist_")
        # print("After artist replacement:", prompt)
        
        # 3. Process weight tags
        prompt = process_weighted_tags(prompt)
        # print("After weight processing:", prompt)
        
        # 4. Convert processed weight tags to Novel AI format
        pattern = r'\(([^:]+):(\d+(?:\.\d+)?)\)'
        prompt = re.sub(pattern,
                       lambda m: convert_to_novelai(m.group(1), float(m.group(2))),
                       prompt)
        # print("After NovelAI conversion:", prompt)

        # 5. Restore character tag tokens to original text
        for token, original in char_tokens.items():
            prompt = prompt.replace(token, original)
        # print("After character tag restoration:", prompt)
        
        # 6. Restore "artist_" to "artist:"
        prompt = prompt.replace("artist_", "artist:")
        # print("Final result:", prompt)

        # 7. Replace underscores with spaces
        prompt = prompt.replace('_', ' ')
        # print("Final result:", prompt)
        
        return prompt
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return f"Error: {str(e)}"