import re

def round_to_step(number, step=0.05):
    """
    주어진 숫자를 step 단위로 반올림하는 함수
    """
    return round(number / step) * step

def parse_and_count_brackets(text, pos=0, outer_curly=0, outer_square=0):
    """
    재귀적으로 괄호를 파싱하고 태그와 가중치를 계산하는 함수
    """
    result = []
    current_tag = ""
    curly_count = outer_curly
    square_count = outer_square
    tag_start_pos = pos
    
    while pos < len(text):
        char = text[pos]
        
        if char == '{':
            if pos == tag_start_pos or not current_tag:  # 새로운 태그 시작
                curly_count += 1
            else:  # 현재 태그 내부의 새로운 중첩
                nested_result, new_pos = parse_and_count_brackets(text, pos, curly_count, square_count)
                result.extend(nested_result)
                pos = new_pos
                current_tag = ""
                tag_start_pos = pos + 1
                continue
        elif char == '[':
            if pos == tag_start_pos or not current_tag:  # 새로운 태그 시작
                square_count += 1
            else:  # 현재 태그 내부의 새로운 중첩
                nested_result, new_pos = parse_and_count_brackets(text, pos, curly_count, square_count)
                result.extend(nested_result)
                pos = new_pos
                current_tag = ""
                tag_start_pos = pos + 1
                continue
        elif char == '}':
            if curly_count > outer_curly:
                if current_tag:
                    weight = (1.05 ** (curly_count - outer_curly)) * (0.95 ** (square_count - outer_square))
                    weight = round_to_step(weight)  # 여기서도 반올림 적용
                    result.append((current_tag.strip(), weight))
                    current_tag = ""
                curly_count -= 1
                if curly_count == outer_curly and outer_curly > 0:  # 중첩된 경우에만 반환
                    return result, pos
        elif char == ']':
            if square_count > outer_square:
                if current_tag:
                    weight = (1.05 ** (curly_count - outer_curly)) * (0.95 ** (square_count - outer_square))
                    weight = round_to_step(weight)  # 여기서도 반올림 적용
                    result.append((current_tag.strip(), weight))
                    current_tag = ""
                square_count -= 1
                if square_count == outer_square and outer_square > 0:  # 중첩된 경우에만 반환
                    return result, pos
        elif char == ',':
            if current_tag:
                if curly_count > outer_curly or square_count > outer_square:
                    weight = (1.05 ** (curly_count - outer_curly)) * (0.95 ** (square_count - outer_square))
                    weight = round_to_step(weight)  # 여기서도 반올림 적용
                    result.append((current_tag.strip(), weight))
                else:
                    result.append((current_tag.strip(), 1.0))
                current_tag = ""
                tag_start_pos = pos + 1
        else:
            current_tag += char
        pos += 1
    
    if current_tag:
        if curly_count > outer_curly or square_count > outer_square:
            weight = (1.05 ** (curly_count - outer_curly)) * (0.95 ** (square_count - outer_square))
            weight = round_to_step(weight)  # 여기서도 반올림 적용
            result.append((current_tag.strip(), weight))
        else:
            result.append((current_tag.strip(), 1.0))
    
    return result, pos

def novel_to_comfy(prompt):
    if not isinstance(prompt, str):
        return "Error: Input must be a string"

    try:
        # 1. "artist:" 를 임시로 "artist_"로 변환
        prompt = prompt.replace("artist:", "artist_")
        
        # 2. 태그 분리 및 가중치 계산
        tags, _ = parse_and_count_brackets(prompt)
        
        # 3. ComfyUI 형식으로 변환
        result_tags = []
        for tag, weight in tags:
            if abs(weight - 1.0) < 0.001:  # 가중치가 1에 매우 가까운 경우
                result_tags.append(tag)
            else:
                result_tags.append(f"({tag}:{weight:.2f})")
        
        # 4. 결과 문자열 생성
        result = ", ".join(result_tags)
        
        # 5. 마지막으로 "artist_"를 "artist:"로 다시 변환
        result = result.replace("artist_", "artist:")
        
        return result
        
    except Exception as e:
        return f"Error: {str(e)}"