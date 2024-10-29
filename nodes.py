"""
Implementation of NovelAI Prompt Extractor Node
"""
import os
import json
import numpy as np
import torch
from PIL import Image
import folder_paths
import logging

# Logging configuration
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     filename='nai_extractor.log'
# )
# logger = logging.getLogger('NAIExtractor')

class NAIPromptExtractorNode:
    FUNCTION = "extract_nai_metadata"
    CATEGORY = "prompt"  # changed to prompt category
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "INT", "INT", "IMAGE")
    RETURN_NAMES = ("prompt", "negative_prompt", "seed", "steps", "sampler", "cfg_scale", "raw_metadata", "width", "height", "image")
    
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        return {
            "required": {
                "original_file": (sorted(files), {"default": files[0] if len(files) > 0 else None}),
                "reload_files": ("BOOLEAN", {"default": False, "label_on": "Reload", "label_off": "No Reload"}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, original_file, reload_files=False):
        if reload_files:
            return float("NaN")
        return original_file

    @classmethod
    def VALIDATE_INPUTS(cls, original_file, reload_files=False):
        if not original_file:
            return "No file selected"
        return True

    def extract_nai_metadata(self, original_file, reload_files=False):
        try:
            # logger.info(f"Processing started - Original file: {original_file}")
            
            input_dir = folder_paths.get_input_directory()
            image_path = os.path.join(input_dir, original_file)
            
            if not os.path.exists(image_path):
                print(f"File not found: {image_path}")
                return ("File not found",) * 7 + (0, 0, None)

            # Set default values
            prompt = "No NAI metadata"
            negative_prompt = "No NAI metadata"
            seed = "No NAI metadata"
            steps = "No NAI metadata"
            sampler = "No NAI metadata"
            cfg_scale = "No NAI metadata"
            raw_metadata = "No NAI metadata"
            width = 0
            height = 0
            image_tensor = None

            # Open image
            with Image.open(image_path) as img:
                # logger.info(f"Image loaded: {image_path}")
                # logger.info(f"Image info: {list(img.info.keys())}")
                
                # Get image size
                width, height = img.size
                # logger.info(f"Image size: {width}x{height}")
                
                # Convert image to tensor
                img_rgb = img.convert('RGB')
                img_array = np.array(img_rgb).astype(np.float32) / 255.0
                image_tensor = torch.from_numpy(img_array)[None,]
                
                # Extract Novel AI metadata
                if 'Comment' in img.info:
                    # logger.info("Novel AI metadata found")
                    try:
                        comment_data = img.info['Comment']
                        # logger.info(f"Raw Comment data: {repr(comment_data)}")
                        
                        # Parse string or bytes to JSON
                        if isinstance(comment_data, bytes):
                            metadata = json.loads(comment_data.decode('utf-8'))
                        else:
                            metadata = json.loads(comment_data)
                            
                        raw_metadata = json.dumps(metadata, indent=2, ensure_ascii=False)
                        # logger.info(f"Parsed metadata: {raw_metadata[:200]}...")
                        
                        prompt = metadata.get('prompt', 'N/A')
                        negative_prompt = metadata.get('uc', 'N/A')
                        seed = str(metadata.get('seed', 'N/A'))
                        steps = str(metadata.get('steps', 'N/A'))
                        sampler = metadata.get('sampler', 'N/A')
                        cfg_scale = str(metadata.get('scale', 'N/A'))
                        
                        # logger.info("NAI metadata parsing successful")
                    except Exception as e:
                        print(f"NAI parsing error: {str(e)}")
            
            # logger.info(f"""Extracted results:
            # Prompt: {prompt[:200]}...
            # Negative prompt: {negative_prompt[:200]}...
            # Seed: {seed}
            # Steps: {steps}
            # Sampler: {sampler}
            # CFG: {cfg_scale}
            # Size: {width}x{height}
            # Image tensor: {image_tensor.shape if image_tensor is not None else 'None'}
            # """)
            
            return (
                prompt,
                negative_prompt,
                seed,
                steps,
                sampler,
                cfg_scale,
                raw_metadata,
                width,
                height,
                image_tensor
            )
                
        except Exception as e:
            error_msg = f"Error occurred: {str(e)}"
            print(error_msg)
            return (error_msg,) * 7 + (0, 0, None)

# Register node in ComfyUI
NODE_CLASS_MAPPINGS = {
    "NAIPromptExtractor": NAIPromptExtractorNode
}

# Set node display name
NODE_DISPLAY_NAME_MAPPINGS = {
    "NAIPromptExtractor": "NAI Prompt Extractor 🔍"
}