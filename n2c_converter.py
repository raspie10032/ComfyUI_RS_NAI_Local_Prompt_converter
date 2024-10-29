import re

def round_to_step(number, step=0.05):
   """
   Round a number to the nearest step value
   """
   return round(number / step) * step

def parse_and_count_brackets(text, pos=0, outer_curly=0, outer_square=0):
   """
   Recursively parse brackets and calculate tag weights
   """
   result = []
   current_tag = ""
   curly_count = outer_curly
   square_count = outer_square
   tag_start_pos = pos
   
   while pos < len(text):
       char = text[pos]
       
       if char == '{':
           if pos == tag_start_pos or not current_tag:  # Start new tag
               curly_count += 1
           else:  # New nesting within current tag
               nested_result, new_pos = parse_and_count_brackets(text, pos, curly_count, square_count)
               result.extend(nested_result)
               pos = new_pos
               current_tag = ""
               tag_start_pos = pos + 1
               continue
       elif char == '[':
           if pos == tag_start_pos or not current_tag:  # Start new tag
               square_count += 1
           else:  # New nesting within current tag
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
                   weight = round_to_step(weight)  # Apply rounding here
                   result.append((current_tag.strip(), weight))
                   current_tag = ""
               curly_count -= 1
               if curly_count == outer_curly and outer_curly > 0:  # Return only for nested cases
                   return result, pos
       elif char == ']':
           if square_count > outer_square:
               if current_tag:
                   weight = (1.05 ** (curly_count - outer_curly)) * (0.95 ** (square_count - outer_square))
                   weight = round_to_step(weight)  # Apply rounding here
                   result.append((current_tag.strip(), weight))
                   current_tag = ""
               square_count -= 1
               if square_count == outer_square and outer_square > 0:  # Return only for nested cases
                   return result, pos
       elif char == ',':
           if current_tag:
               if curly_count > outer_curly or square_count > outer_square:
                   weight = (1.05 ** (curly_count - outer_curly)) * (0.95 ** (square_count - outer_square))
                   weight = round_to_step(weight)  # Apply rounding here
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
           weight = round_to_step(weight)  # Apply rounding here
           result.append((current_tag.strip(), weight))
       else:
           result.append((current_tag.strip(), 1.0))
   
   return result, pos

def novel_to_comfy(prompt):
   if not isinstance(prompt, str):
       return "Error: Input must be a string"

   try:
       # 1. Temporarily convert "artist:" to "artist_"
       prompt = prompt.replace("artist:", "artist_")
       
       # 2. Split tags and calculate weights
       tags, _ = parse_and_count_brackets(prompt)
       
       # 3. Convert to ComfyUI format
       result_tags = []
       for tag, weight in tags:
           if abs(weight - 1.0) < 0.001:  # Weight very close to 1
               result_tags.append(tag)
           else:
               result_tags.append(f"({tag}:{weight:.2f})")
       
       # 4. Create result string
       result = ", ".join(result_tags)
       
       # 5. Convert "artist_" back to "artist:"
       result = result.replace("artist_", "artist:")
       
       return result
       
   except Exception as e:
       return f"Error: {str(e)}"