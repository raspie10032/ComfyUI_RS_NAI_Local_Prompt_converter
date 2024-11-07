import re

def identify_character_tags(text):
    """Identify character tag patterns and convert to temporary tokens"""
    result = text
    
    # Define patterns
    patterns = [
        # Basic patterns
        (r'\b\w+\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_1'),
        (r'\b\w+\s+\([^()]+\)\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_2'),
        (r'\b\w+\s+\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_3'),
        (r'\b\w+\s+\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)', 'CHAR_TAG_4'),
        
        # Underscore patterns
        (r'\b\w+_\([^()]+\)(?!\s*\()', 'CHAR_TAG_5'),
        (r'\b\w+_\([^()]+\)\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_6'),
        (r'\b\w+_\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_7'),
        (r'\b\w+_\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)', 'CHAR_TAG_8'),

        # Escape patterns
        (r'\b\w+\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_1'),
        (r'\b\w+\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_2'),
        (r'\b\w+\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_3'),
        (r'\b\w+\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)', 'ESC_CHAR_TAG_4'),

        # Underscore escape patterns
        (r'\b\w+_\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_5'),
        (r'\b\w+_\\\([^()]+\\\)\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_6'),
        (r'\b\w+_\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_7'),
        (r'\b\w+_\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)', 'ESC_CHAR_TAG_8')
    ]
    
    tokens = {}
    token_count = 0
    
    for pattern, token_base in patterns:
        matches = list(re.finditer(pattern, result))
        for match in matches:
            matched_text = match.group(0)
            token = f"{token_base}_{token_count}"
            if token_base.startswith('ESC_'):
                stored_text = matched_text.replace('\\(', '(').replace('\\)', ')')
            else:
                stored_text = matched_text
            tokens[token] = stored_text
            result = result.replace(matched_text, token)
            token_count += 1
    
    return result, tokens

def handle_special_tokens(text):
    """Handle special tokens like emojis and known tags"""
    result = text
    special_tokens = {}
    token_count = 0
    
    # Known tags that use colon
    known_tags = ['artist:', 'camera:', 'quality:', 'style:', 'subject:']
    
    # Common emoji patterns - 순서가 중요합니다! 더 구체적인 패턴을 먼저 처리
    emoji_patterns = [
        # 숫자를 포함하는 이모티콘 - 가장 먼저 처리
        r':3\b',              # :3 (단어 경계 확인)
        r':8[DPOo\-]',       # :8D, :8P, :8O, :8o, :8-
        
        # 복합 이모티콘
        r':-[DPOo\)\(]',     # :-D, :-P, :-O, :-o, :-), :-(
        r':[;][-]?[DPOo\)\(]', # ;D, ;-D, ;), ;-) 등
        
        # 기본 이모티콘
        r':[DPOoXxVv]',      # :D, :P, :O, :o, :X, :x, :V, :v
        r':[)(<>\]\[\{\}]',   # :), :(, :>, :<, :], :[, :}, :{
        r':[\'\"]',           # :', :"
        
        # 한글 이모티콘
        r':ㅅ',              # :ㅅ
        r':ㅇ',              # :ㅇ
        r':ㅎ',              # :ㅎ
    ]
    
    # Combine all emoji patterns
    combined_emoji_pattern = '|'.join(f'({pattern})' for pattern in emoji_patterns)
    
    # First, handle emojis (순서 변경: 이모지를 먼저 처리)
    emoji_matches = list(re.finditer(combined_emoji_pattern, result))
    for match in emoji_matches:
        matched_text = match.group(0)
        token = f"EMOJI_TAG_{token_count}"
        special_tokens[token] = matched_text
        result = result.replace(matched_text, token)
        token_count += 1
    
    # Then, handle known tags
    for tag in known_tags:
        if tag in result:
            token = f"KNOWN_TAG_{token_count}"
            special_tokens[token] = tag
            result = result.replace(tag, f"{token}_")
            token_count += 1
    
    return result, special_tokens

def prompt_to_stack(sentence):
    """Parse prompt and convert to nested structure with weights"""
    result = []
    current_str = ""
    stack = [{"weight": 1.0, "data": result}]
    
    for i, c in enumerate(sentence):
        if c in '()':
            if c == '(':
                if current_str.strip(): 
                    stack[-1]["data"].append(current_str.strip())
                stack[-1]["data"].append({"weight": 1.0, "data": []})
                stack.append(stack[-1]["data"][-1])
            elif c == ')':
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
    """Process stack structure and calculate final weights"""
    if isinstance(stack_item, str):
        return f"({stack_item}:{parent_weight:.2f})"
    
    current_weight = stack_item["weight"] * parent_weight
    processed_items = []
    
    for item in stack_item["data"]:
        if isinstance(item, str):
            subitems = [subitem.strip() for subitem in item.split(',')]
            for subitem in subitems:
                if subitem:
                    if ':' in subitem:
                        tag, weight = subitem.split(':')
                        processed_items.append(f"({tag.strip()}:{float(weight) * current_weight:.2f})")
                    else:
                        processed_items.append(f"({subitem}:{current_weight:.2f})")
        else:
            result = process_stack_with_weights(item, current_weight)
            if result:
                processed_items.extend(result.split(', '))
    
    return ', '.join(processed_items)

def convert_to_novelai(tag, weight):
    """Convert single tag and weight to Novel AI format"""
    if abs(weight - 1.0) < 0.001:
        return tag
        
    if weight > 1:
        count = round((weight - 1.0) / 0.05)
        result = '{' * count + tag + '}' * count
    else:
        count = round((1.0 - weight) / 0.05)
        result = '[' * count + tag + ']' * count
    
    return result

def comfy_to_novel(prompt):
    """Main function to convert ComfyUI prompts to NovelAI format"""
    if not isinstance(prompt, str):
        return "Error: Input must be a string"

    try:
        # Debug helper
        debug_steps = []
        debug_steps.append(("Input", prompt))
        
        # 1. Handle special tokens first (emojis and known tags)
        prompt, special_tokens = handle_special_tokens(prompt)
        debug_steps.append(("After special tokens", prompt))
        
        # 2. Identify character tag patterns
        prompt, char_tokens = identify_character_tags(prompt)
        debug_steps.append(("After character tags", prompt))
        
        # 3. Process weight tags
        if '(' in prompt:
            stack = prompt_to_stack(prompt)
            prompt = process_stack_with_weights({"weight": 1.0, "data": stack})
        debug_steps.append(("After weight processing", prompt))
        
        # 4. Convert processed weight tags to Novel AI format
        if '(' in prompt:
            pattern = r'\(([^:]+):(\d+(?:\.\d+)?)\)'
            prompt = re.sub(pattern,
                           lambda m: convert_to_novelai(m.group(1), float(m.group(2))),
                           prompt)
        debug_steps.append(("After NovelAI conversion", prompt))
        
        # 5. Restore character tag tokens
        for token, original in char_tokens.items():
            prompt = prompt.replace(token, original)
        debug_steps.append(("After character tag restoration", prompt))
        
        # 6. Restore special tokens (emojis and known tags)
        for token, original in special_tokens.items():
            if token.startswith('EMOJI_TAG_'):
                prompt = prompt.replace(token, original)
            else:
                prompt = prompt.replace(f"{token}_", original)
        debug_steps.append(("After special token restoration", prompt))
        
        # 7. Replace remaining underscores with spaces
        prompt = prompt.replace('_', ' ')
        debug_steps.append(("Final result", prompt))
        
        return prompt
        
    except Exception as e:
        return f"Error: {str(e)}"