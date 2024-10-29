"""
Implementation of NovelAI Prompt Extractor Node with LSB-based metadata extraction
"""
import os
import json
import numpy as np
import torch
from PIL import Image
import folder_paths
import gzip
from typing import Union

def byteize(alpha):
    alpha = alpha.T.reshape((-1,))
    alpha = alpha[:(alpha.shape[0] // 8) * 8]
    alpha = np.bitwise_and(alpha, 1)
    alpha = alpha.reshape((-1, 8))
    alpha = np.packbits(alpha, axis=1)
    return alpha

class LSBExtractor:
    def __init__(self, data):
        self.data = byteize(data[..., -1])
        self.pos = 0

    def get_one_byte(self):
        byte = self.data[self.pos]
        self.pos += 1
        return byte

    def get_next_n_bytes(self, n):
        n_bytes = self.data[self.pos:self.pos + n]
        self.pos += n
        return bytearray(n_bytes)

    def read_32bit_integer(self):
        bytes_list = self.get_next_n_bytes(4)
        if len(bytes_list) == 4:
            integer_value = int.from_bytes(bytes_list, byteorder='big')
            return integer_value
        else:
            return None

def extract_image_metadata(image: Union[Image.Image, np.ndarray], get_fec: bool = False) -> dict:
    if isinstance(image, Image.Image):
        image = np.array(image.convert("RGBA"))
    if image.shape[-1] != 4 or len(image.shape) != 3:
        return None
    
    try:
        reader = LSBExtractor(image)
        magic = "stealth_pngcomp"
        read_magic = reader.get_next_n_bytes(len(magic)).decode("utf-8")
        if magic != read_magic:
            return None
        
        read_len = reader.read_32bit_integer() // 8
        json_data = reader.get_next_n_bytes(read_len)
        json_data = json.loads(gzip.decompress(json_data).decode("utf-8"))
        
        if "Comment" in json_data and isinstance(json_data["Comment"], str):
            json_data["Comment"] = json.loads(json_data["Comment"])
        
        return json_data
    except Exception:
        return None

class NAIPromptExtractorNode:
    FUNCTION = "extract_nai_metadata"
    CATEGORY = "prompt"
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

            # Open and process image
            with Image.open(image_path) as img:
                width, height = img.size
                img_rgb = img.convert('RGB')
                img_array = np.array(img_rgb).astype(np.float32) / 255.0
                image_tensor = torch.from_numpy(img_array)[None,]
                
                # Extract metadata using LSB method
                metadata = extract_image_metadata(img)
                
                if metadata:
                    raw_metadata = json.dumps(metadata, indent=2, ensure_ascii=False)
                    
                    # Extract values from Comment if present
                    if "Comment" in metadata:
                        comment_data = metadata["Comment"]
                        prompt = comment_data.get('prompt', 'N/A')
                        negative_prompt = comment_data.get('uc', 'N/A')
                        seed = str(comment_data.get('seed', 'N/A'))
                        steps = str(comment_data.get('steps', 'N/A'))
                        sampler = comment_data.get('sampler', 'N/A')
                        cfg_scale = str(comment_data.get('scale', 'N/A'))
            
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