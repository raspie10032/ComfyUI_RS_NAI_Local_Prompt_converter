import re
import base64
import math

class ComfyUIToNovelAIV4Converter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "comfyui_prompt": ("STRING", {"multiline": True, "default": "qw, a, (b c:1.05), d, e\\(f: g h\\), black bikini top, denim shorts, shorts under bikini bottom, (i j:1.2)"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("novelai_prompt",)
    FUNCTION = "convert_prompt"
    CATEGORY = "prompt"

    def convert_prompt(self, comfyui_prompt):
        processed_prompt = comfyui_prompt.replace(r"\\(", "(").replace(r"\\)", ")")
        novelai_parts = []

        elements = re.split(r'(?<!\\)([,()])', processed_prompt)
        processed_elements = [el.strip() for el in elements if el.strip()]

        i = 0
        while i < len(processed_elements):
            element = processed_elements[i]
            if element == '(':
                i += 1
                content = ""
                balance = 1
                while i < len(processed_elements):
                    sub_element = processed_elements[i]
                    if sub_element == '(':
                        balance += 1
                    elif sub_element == ')':
                        balance -= 1
                        if balance == 0:
                            i += 1
                            break
                    content += sub_element
                    i += 1

                if content:
                    match_weight = re.search(r':([\d.]+)\s*$', content)
                    weight = 1.1
                    tags_str = content
                    if match_weight:
                        try:
                            weight = float(match_weight.group(1))
                            tags_str = content[:match_weight.start()].strip()
                            if not (0 <= weight <= 2):
                                print(f"Warning: 가중치 '{weight}'가 0~2 범위를 벗어납니다. 기본값 1.1 사용: {tags_str}")
                                weight = 1.1
                        except ValueError:
                            print(f"Warning: 잘못된 형식의 가중치 '{match_weight.group(1)}'. 기본값 1.1 사용: {tags_str}")

                    if tags_str:
                        novelai_parts.append(f"{weight}::{tags_str}::")

            elif element == ',':
                novelai_parts.append(',')
                i += 1
            else:
                if element:
                    novelai_parts.append(element)
                i += 1

        final_prompt = "".join(novelai_parts).replace("\\", "") # 최종 변환 후 백슬래시 제거
        final_prompt_with_spaces = ""
        for part in final_prompt.split(','):
            final_prompt_with_spaces += part.strip() + ', '
        final_prompt_with_spaces = final_prompt_with_spaces.rstrip(', ') # 마지막 콤마와 공백 제거

        return (final_prompt_with_spaces,)

class NovelAIV4ToComfyUIConverter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "novelai_prompt": ("STRING", {"multiline": True, "default": "qw, a, 1.05::b c::, d, e(f: g h), black bikini top, denim shorts, shorts under bikini bottom, 1.2::i j::"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("comfyui_prompt",)
    FUNCTION = "convert_prompt"
    CATEGORY = "prompt"

    def convert_prompt(self, novelai_prompt):
        processed_prompt = novelai_prompt.replace("(", r"\(").replace(")", r"\)")
        processed_prompt = processed_prompt.replace(r"\(", "__escopen__").replace(r"\)", "__escclose__")

        def encode_tags(tags_string):
            # Base64 인코딩 유지 - 패딩 제거하지 않음
            return base64.b64encode(tags_string.encode('utf-8')).decode('utf-8')

        def decode_tags(encoded_string):
            try:
                # Base64 디코딩
                return base64.b64decode(encoded_string).decode('utf-8')
            except:
                return encoded_string

        def replace_with_encoded(match):
            weight = match.group(1)
            tags_str = match.group(2)
            encoded_tags = encode_tags(tags_str)
            return f"{weight}::__TEMP_ENCODED__({encoded_tags})__TEMP_ENCODED_END__"

        processed_prompt = re.sub(r"([\d.]+)::([^:]+?)::", replace_with_encoded, processed_prompt)

        comfyui_parts = []
        for part in processed_prompt.split(','):
            part = part.strip()
            if "__TEMP_ENCODED__" in part:
                match = re.match(r"([\d.]+)::(__TEMP_ENCODED__\((.+?)\)__TEMP_ENCODED_END__)", part)
                if match:
                    weight = match.group(1)
                    encoded_tags = match.group(3)
                    comfyui_parts.append(f"(__TEMP_ENCODED__({encoded_tags}):{weight})")
                else:
                    comfyui_parts.append(part)
            else:
                comfyui_parts.append(part)

        comfyui_prompt = ", ".join(comfyui_parts)

        def replace_encoded_with_decoded(match):
            encoded_tags = match.group(1)
            weight = match.group(2)
            decoded_tags = decode_tags(encoded_tags).replace("__escopen__", "(").replace("__escclose__", ")")
            return f"({decoded_tags}:{weight})"

        comfyui_prompt = re.sub(r"__TEMP_ENCODED__\((.+?)\):([\d.]+)", replace_encoded_with_decoded, comfyui_prompt)

        comfyui_prompt = comfyui_prompt.replace("__escopen__", r"\(").replace("__escclose__", r"\)")
        comfyui_prompt = comfyui_prompt.replace("((", "(").replace("))", ")")
        comfyui_prompt = re.sub(r",(?!\s)", ", ", comfyui_prompt)

        return (comfyui_prompt,)

class NovelAIV4ToOldNAIConverter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "novelai_v4_prompt": ("STRING", {"multiline": True, "default": "1.05::tag1::, 0.9::tag3::, 1.2::tag4::, 1.1::misty, golden hour::"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("novelai_old_prompt",)
    FUNCTION = "convert_prompt"
    CATEGORY = "prompt"

    def convert_prompt(self, novelai_v4_prompt):
        def find_closest_power(weight, base):
            """로그 함수를 사용하여 가중치에 가장 가까운 지수 값 찾기"""
            if weight <= 0 or base <= 0 or base == 1:
                return 0
            exponent = math.log(weight) / math.log(base)
            return round(exponent)
            
        # 정규식 패턴 정의 - 가중치::태그:: 형식 찾기
        # 이 패턴은 콤마를 포함한 어떤 내용이든 :: 사이에 있는 것을 하나의 태그 단위로 처리
        pattern = r'([\d.]+)::([^:]+?)::'
        
        # 가중치::태그:: 형식 찾기
        tags_with_weights = re.finditer(pattern, novelai_v4_prompt)
        
        # 처리된 부분 기록
        processed_spans = []
        old_nai_parts = []
        
        # 가중치가 있는 태그들 먼저 처리
        for match in tags_with_weights:
            weight_str = match.group(1)
            tags = match.group(2).strip()
            start, end = match.span()
            processed_spans.append((start, end))
            
            try:
                weight = float(weight_str)
                
                if weight > 1:
                    # 증가 가중치 - 중괄호 사용
                    n_105 = find_closest_power(weight, 1.05)
                    if n_105 > 0:
                        old_nai_parts.append((start, "{" * n_105 + tags + "}" * n_105))
                    else:
                        old_nai_parts.append((start, tags))
                elif weight < 1:
                    # 감소 가중치 - 대괄호 사용
                    n_095 = find_closest_power(weight, 0.95)
                    if n_095 < 0:
                        old_nai_parts.append((start, "[" * abs(n_095) + tags + "]" * abs(n_095)))
                    else:
                        old_nai_parts.append((start, tags))
                else:
                    # 가중치 1.0 - 그대로 유지
                    old_nai_parts.append((start, tags))
            except ValueError:
                # 가중치 변환 실패 시 원본 유지
                old_nai_parts.append((start, match.group(0)))
        
        # 처리되지 않은 부분 찾기
        last_end = 0
        for start, end in sorted(processed_spans):
            if start > last_end:
                # 처리되지 않은 부분 추가
                remaining = novelai_v4_prompt[last_end:start].strip()
                if remaining:
                    # 콤마로 구분하여 추가
                    for part in remaining.split(','):
                        if part.strip():
                            old_nai_parts.append((last_end, part.strip()))
            last_end = end
        
        # 마지막 처리되지 않은 부분 추가
        if last_end < len(novelai_v4_prompt):
            remaining = novelai_v4_prompt[last_end:].strip()
            if remaining:
                # 콤마로 구분하여 추가
                for part in remaining.split(','):
                    if part.strip():
                        old_nai_parts.append((last_end, part.strip()))
        
        # 위치 순서대로 정렬
        old_nai_parts.sort()
        
        # 최종 결과 조합 (위치 정보 제거)
        final_prompt = ", ".join(part[1] for part in old_nai_parts)
        return (final_prompt,)

class OldNAIToNovelAIV4Converter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "novelai_old_prompt": ("STRING", {"multiline": True, "default": "{tag1}, [tag2], {{tag3}}, [[tag4]], tag5, {{{important tag}}}, {{misty, golden hour}}"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("novelai_v4_prompt",)
    FUNCTION = "convert_prompt"
    CATEGORY = "prompt"

    def convert_prompt(self, novelai_old_prompt):
        # 정규식 패턴 정의 - 중괄호나 대괄호로 감싸진 패턴
        # 괄호 안에 콤마가 있는 경우도 하나의 태그로 처리
        pattern = r'([{\[]+)([^}\]]+?)([}\]]+)'
        
        # 패턴 매칭 결과와 위치 저장
        matches = list(re.finditer(pattern, novelai_old_prompt))
        processed_spans = []
        
        # 변환 결과 저장
        result_parts = []
        
        for match in matches:
            prefix = match.group(1)  # 여는 괄호들
            content = match.group(2).strip()  # 괄호 안 내용
            suffix = match.group(3)  # 닫는 괄호들
            start, end = match.span()
            
            processed_spans.append((start, end))
            
            # 괄호 균형 검사
            if prefix.count('{') == suffix.count('}') and prefix.count('[') == suffix.count(']'):
                # 괄호 종류와 개수에 따른 가중치 계산
                curly_count = prefix.count('{')
                square_count = prefix.count('[')
                
                weight = 1.0
                if curly_count > 0 and square_count == 0:
                    # 중괄호는 가중치 증가 (1.05^n)
                    weight = 1.05 ** curly_count
                elif square_count > 0 and curly_count == 0:
                    # 대괄호는 가중치 감소 (0.95^n)
                    weight = 0.95 ** square_count
                
                if weight != 1.0:
                    # 소수점 두 자리까지만 표시 (불필요한 0 제거)
                    weight_str = f"{weight:.2f}".rstrip('0').rstrip('.')
                    result_parts.append((start, f"{weight_str}::{content}::"))
                else:
                    result_parts.append((start, content))
            else:
                # 괄호 불균형 시 원본 유지
                result_parts.append((start, match.group(0)))
        
        # 처리되지 않은 부분 처리
        last_end = 0
        for start, end in sorted(processed_spans):
            if start > last_end:
                # 처리되지 않은 텍스트 분석
                unprocessed = novelai_old_prompt[last_end:start].strip()
                if unprocessed:
                    # 콤마로 구분된 각 부분 처리
                    for part in re.split(r',', unprocessed):
                        part = part.strip()
                        if part:
                            result_parts.append((last_end, part))
            last_end = end
        
        # 마지막 처리되지 않은 부분
        if last_end < len(novelai_old_prompt):
            unprocessed = novelai_old_prompt[last_end:].strip()
            if unprocessed:
                # 콤마로 구분된 각 부분 처리
                for part in re.split(r',', unprocessed):
                    part = part.strip()
                    if part:
                        result_parts.append((last_end, part))
        
        # 위치 순서대로 정렬
        result_parts.sort()
        
        # 최종 변환된 프롬프트 조합
        if result_parts:
            # 모든 부분을 하나의 문자열로 결합
            final_prompt = ", ".join(part[1] for part in result_parts)
        else:
            # 변환할 것이 없으면 원본 유지
            final_prompt = novelai_old_prompt.strip()
            
        return (final_prompt,)

NODE_CLASS_MAPPINGS = {
    "ComfyUIToNovelAIV4": ComfyUIToNovelAIV4Converter,
    "NovelAIV4ToComfyUI": NovelAIV4ToComfyUIConverter,
    "NovelAIV4ToOldNAI": NovelAIV4ToOldNAIConverter,
    "OldNAIToNovelAIV4": OldNAIToNovelAIV4Converter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyUIToNovelAIV4": "Convert ComfyUI to Novel AI V4",
    "NovelAIV4ToComfyUI": "Convert Novel AI V4 to ComfyUI",
    "NovelAIV4ToOldNAI": "Convert Novel AI V4 to Old NAI",
    "OldNAIToNovelAIV4": "Convert Old NAI to Novel AI V4",
}