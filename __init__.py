"""
Original source code credit:
The prompt_to_stack function is based on the code from:
https://github.com/bedovyy/ComfyUI_NAIDGenerator/blob/master/utils.py#L146
Author: bedovyy
Modified for Novel AI to ComfyUI conversion purposes.
"""

from .n2c_converter import novel_to_comfy
from .c2n_converter import comfy_to_novel

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

NODE_CLASS_MAPPINGS = {
    "NovelAIToComfyPrompt": NovelAIToComfyNode,
    "ComfyToNovelAIPrompt": ComfyToNovelAINode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NovelAIToComfyPrompt": "NovelAI to ComfyUI Prompt",
    "ComfyToNovelAIPrompt": "ComfyUI to NovelAI Prompt"
}