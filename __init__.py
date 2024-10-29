"""
ComfyUI_RS_NAI_Local_Prompt_converter

Features:
1. NovelAI and ComfyUI prompt conversion
2. NovelAI metadata extraction
"""

# Import converter nodes
from .n2c_converter import novel_to_comfy
from .c2n_converter import comfy_to_novel

# Import metadata extractor node
from .nodes import NODE_CLASS_MAPPINGS as METADATA_NODES
from .nodes import NODE_DISPLAY_NAME_MAPPINGS as METADATA_DISPLAY_NAMES

class NovelAIToComfyNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "convert"
    CATEGORY = "prompt"
    TITLE = "NovelAI to ComfyUI Prompt"

    def convert(self, prompt):
        return (novel_to_comfy(prompt),)

class ComfyToNovelAINode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "convert"
    CATEGORY = "prompt"
    TITLE = "ComfyUI to NovelAI Prompt"

    def convert(self, prompt):
        return (comfy_to_novel(prompt),)

# Converter nodes mapping
CONVERTER_NODE_CLASS_MAPPINGS = {
    "NovelAIToComfyPrompt": NovelAIToComfyNode,
    "ComfyToNovelAIPrompt": ComfyToNovelAINode
}

CONVERTER_NODE_DISPLAY_NAME_MAPPINGS = {
    "NovelAIToComfyPrompt": "NovelAI to ComfyUI Prompt",
    "ComfyToNovelAIPrompt": "ComfyUI to NovelAI Prompt"
}

# Merge all mappings
NODE_CLASS_MAPPINGS = {
    **METADATA_NODES,  # This includes the MetadataExtractor node from nodes.py
    **CONVERTER_NODE_CLASS_MAPPINGS
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **METADATA_DISPLAY_NAMES,  # This includes the display name from nodes.py
    **CONVERTER_NODE_DISPLAY_NAME_MAPPINGS
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

WEB_DIRECTORY = "./js"