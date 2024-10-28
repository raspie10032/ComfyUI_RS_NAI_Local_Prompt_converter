import re

def identify_character_tags(text):
    """캐릭터 태그 패턴을 식별하고 임시 토큰으로 변환"""
    result = text
    
    # 패턴들 정의
    patterns = [
        # 일반 패턴
        # 1. name (title) - 기본형
        (r'\b\w+\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_1'),
        # 2. name (title) (option1) - 옵션 1개
        (r'\b\w+\s+\([^()]+\)\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_2'),
        # 3. name (title) (option1) (option2) - 옵션 2개
        (r'\b\w+\s+\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_3'),
        # 4. name (title) (option1) (option2) (option3) - 옵션 3개
        (r'\b\w+\s+\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)', 'CHAR_TAG_4'),
        
        # 언더스코어 패턴
        # 5. name_(title) - 언더스코어 기본형
        (r'\b\w+_\([^()]+\)(?!\s*\()', 'CHAR_TAG_5'),
        # 6. name_(title) (option1) - 언더스코어 옵션 1개
        (r'\b\w+_\([^()]+\)\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_6'),
        # 7. name_(title) (option1) (option2) - 언더스코어 옵션 2개
        (r'\b\w+_\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)(?!\s*\()', 'CHAR_TAG_7'),
        # 8. name_(title) (option1) (option2) (option3) - 언더스코어 옵션 3개
        (r'\b\w+_\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)\s+\([^()]+\)', 'CHAR_TAG_8'),

        # 이스케이프 패턴
        # 9. name \(title\) - 이스케이프 기본형
        (r'\b\w+\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_1'),
        # 10. name \(title\) \(option1\) - 이스케이프 옵션 1개
        (r'\b\w+\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_2'),
        # 11. name \(title\) \(option1\) \(option2\) - 이스케이프 옵션 2개
        (r'\b\w+\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_3'),
        # 12. name \(title\) \(option1\) \(option2\) \(option3\) - 이스케이프 옵션 3개
        (r'\b\w+\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)', 'ESC_CHAR_TAG_4'),

        # 언더스코어 이스케이프 패턴
        # 13. name_\(title\) - 언더스코어 이스케이프 기본형
        (r'\b\w+_\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_5'),
        # 14. name_\(title\) \(option1\) - 언더스코어 이스케이프 옵션 1개
        (r'\b\w+_\\\([^()]+\\\)\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_6'),
        # 15. name_\(title\) \(option1\) \(option2\) - 언더스코어 이스케이프 옵션 2개
        (r'\b\w+_\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)(?!\s*\\\()', 'ESC_CHAR_TAG_7'),
        # 16. name_\(title\) \(option1\) \(option2\) \(option3\) - 언더스코어 이스케이프 옵션 3개
        (r'\b\w+_\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)\s+\\\([^()]+\\\)', 'ESC_CHAR_TAG_8')
    ]
    
    # 패턴 매칭 결과와 토큰을 저장할 딕셔너리
    tokens = {}
    token_count = 0
    
    # 각 패턴에 대해 매칭 검사 및 토큰 변환
    for pattern, token_base in patterns:
        matches = list(re.finditer(pattern, result))
        for match in matches:
            matched_text = match.group(0)
            token = f"{token_base}_{token_count}"
            # 이스케이프된 괄호를 일반 괄호로 변환하여 저장
            if token_base.startswith('ESC_'):
                stored_text = matched_text.replace('\\(', '(').replace('\\)', ')')
            else:
                stored_text = matched_text
            tokens[token] = stored_text
            result = result.replace(matched_text, token)
            token_count += 1
            print(f"Found {token_base}: {matched_text} -> {token}")
    
    return result, tokens

def prompt_to_stack(sentence):
    """
    프롬프트를 파싱하여 중첩 구조와 가중치를 가진 스택으로 변환
    """
    result = []
    current_str = ""
    # 스택의 각 항목은 { "weight": 가중치값, "data": 내용물 리스트 } 형식
    stack = [{"weight": 1.0, "data": result}]
    
    for i, c in enumerate(sentence):
        if c in '()':
            if c == '(':
                # 현재까지의 문자열 처리
                if current_str.strip(): 
                    stack[-1]["data"].append(current_str.strip())
                # 새로운 그룹 시작
                stack[-1]["data"].append({"weight": 1.0, "data": []})
                stack.append(stack[-1]["data"][-1])
            elif c == ')':
                # 닫는 괄호를 만났을 때 가중치 처리
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
    스택 구조를 처리하여 최종 가중치를 계산
    """
    if isinstance(stack_item, str):
        return f"({stack_item}:{parent_weight:.2f})"
    
    current_weight = stack_item["weight"] * parent_weight
    processed_items = []
    
    for item in stack_item["data"]:
        if isinstance(item, str):
            # 쉼표로 구분된 항목들 처리
            subitems = [subitem.strip() for subitem in item.split(',')]
            for subitem in subitems:
                if subitem:  # 빈 문자열이 아닌 경우만 처리
                    if ':' in subitem:  # 이미 가중치가 있는 경우
                        tag, weight = subitem.split(':')
                        processed_items.append(f"({tag.strip()}:{float(weight) * current_weight:.2f})")
                    else:  # 가중치가 없는 경우
                        processed_items.append(f"({subitem}:{current_weight:.2f})")
        else:
            # 중첩된 구조 재귀적 처리
            result = process_stack_with_weights(item, current_weight)
            if result:
                processed_items.extend(result.split(', '))
    
    return ', '.join(processed_items)

def process_weighted_tags(text):
    """
    ComfyUI 형식의 가중치 태그를 처리하는 함수
    """
    print("Starting process_weighted_tags with text:", text)
    
    # 스택 구조로 변환
    stack = prompt_to_stack(text)
    
    # 가중치 계산 및 결과 생성
    result = process_stack_with_weights({"weight": 1.0, "data": stack})
    
    print("Final result from process_weighted_tags:", result)
    return result

def convert_to_novelai(tag, weight):
    """
    단일 태그와 가중치를 Novel AI 형식으로 변환
    weight > 1: 중괄호 사용
    weight < 1: 대괄호 사용
    """
    print("Converting to NovelAI format:", tag, "with weight:", weight)
    if abs(weight - 1.0) < 0.001:
        return tag
        
    if weight > 1:
        count = round((weight - 1.0) / 0.05)
        result = '{' * count + tag + '}' * count
    else:
        count = round((1.0 - weight) / 0.05)
        result = '[' * count + tag + ']' * count
    
    print("Conversion result:", result)
    return result

def comfy_to_novel(prompt):
    if not isinstance(prompt, str):
        return "Error: Input must be a string"

    try:
        print("Starting conversion with prompt:", prompt)
        
        # 1. 캐릭터 태그 패턴 식별 및 임시 토큰으로 변환
        prompt, char_tokens = identify_character_tags(prompt)
        print("After character tag identification:", prompt)
        
        # 2. "artist:" 를 임시로 "artist_"로 변환
        prompt = prompt.replace("artist:", "artist_")
        print("After artist replacement:", prompt)
        
        # 3. 가중치 태그 처리
        prompt = process_weighted_tags(prompt)
        print("After weight processing:", prompt)
        
        # 4. 처리된 가중치 태그들을 Novel AI 형식으로 변환
        pattern = r'\(([^:]+):(\d+(?:\.\d+)?)\)'
        prompt = re.sub(pattern,
                       lambda m: convert_to_novelai(m.group(1), float(m.group(2))),
                       prompt)
        print("After NovelAI conversion:", prompt)

        # 5. 캐릭터 태그 토큰을 원래 텍스트로 복원
        for token, original in char_tokens.items():
            prompt = prompt.replace(token, original)
        print("After character tag restoration:", prompt)
        
        # 6. "artist_"를 "artist:"로 복원
        prompt = prompt.replace("artist_", "artist:")
        print("Final result:", prompt)

        # 7. 언더스코어를 공백으로 치환
        prompt = prompt.replace('_', ' ')
        print("Final result:", prompt)
        
        return prompt
    except Exception as e:
        print("Error occurred:", str(e))
        return f"Error: {str(e)}"