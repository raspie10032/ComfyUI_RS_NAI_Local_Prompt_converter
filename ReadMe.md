# ComfyUI Prompt Converter

Version 2.0.0

A custom node extension for ComfyUI that enables conversion between different prompt formats: NovelAI V4, ComfyUI, and old NovelAI.

## Major Changes in v2.0.0

This version represents a complete rewrite of the extension with improved functionality:
- Removed image metadata extraction features
- Focused entirely on prompt conversion capabilities
- Added support for NovelAI V4 format
- More reliable conversion between different formats
- Fixed issues with base64 encoding/decoding

## Features

### Prompt Format Conversion

This extension provides conversion between multiple prompt formats:

#### ComfyUI → NovelAI V4
- Converts ComfyUI's weight format to NovelAI V4 format
  - `(tag:1.05)` → `1.05::tag::`
  - `(multiple tags:1.1)` → `1.1::multiple tags::`

#### NovelAI V4 → ComfyUI
- Converts NovelAI V4 format to ComfyUI's weight format
  - `1.05::tag::` → `(tag:1.05)`
  - `1.1::multiple tags::` → `(multiple tags:1.1)`

#### NovelAI V4 → Old NovelAI
- Converts NovelAI V4 format to old NovelAI's bracket notation
  - `1.05::tag::` → `{tag}`
  - `1.1::tag::` → `{{tag}}`
  - `0.95::tag::` → `[tag]`
  - `0.9::tag::` → `[[tag]]`
- Uses logarithmic function to determine the appropriate number of brackets based on the weight value

#### Old NovelAI → NovelAI V4
- Converts old NovelAI's bracket notation to NovelAI V4 format
  - `{tag}` → `1.05::tag::`
  - `{{tag}}` → `1.1::tag::`
  - `[tag]` → `0.95::tag::`
  - `[[tag]]` → `0.9::tag::`
- Uses logarithmic function to calculate precise weight values based on number of brackets

### Special Handling
- Proper handling of escaped parentheses
- Maintains proper tag spacing and formatting
- Improved handling of complex prompts with nested structures

### Limitations
- Direct conversion between ComfyUI and Old NovelAI formats is not supported
- To convert between ComfyUI and Old NovelAI, use NovelAI V4 as an intermediate format
- **Mixed prompt formats are not supported** - Each converter expects input in a single, consistent format
- The converters cannot process strings containing a mix of ComfyUI, Old NovelAI, and NovelAI V4 formats
- Each prompt must be fully converted to a specific format before using another converter

## Installation

1. Clone this repository into your ComfyUI's custom nodes directory:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/raspie10032/ComfyUI_RS_NAI_Local_Prompt_converter
```

2. Restart ComfyUI

## Usage

After installation, four new nodes will be available in the prompt category:
- **Convert ComfyUI to Novel AI V4**
- **Convert Novel AI V4 to ComfyUI**
- **Convert Novel AI V4 to Old NAI**
- **Convert Old NAI to Novel AI V4**

Simply connect your prompt to the appropriate conversion node to transform between formats.

### Important Note About Backward Compatibility

**Version 2.0.0 is NOT backward compatible with version 1.x**

- Existing workflows using v1.x nodes will need to be rebuilt using the new v2.0.0 nodes
- The node names and functionality have changed completely
- If you were using version 1.x for extracting metadata from NovelAI-generated images, please note that this functionality has been completely removed in version 2.0.0

## Notes

- This extension focuses solely on prompt format conversion
- The previous image metadata extraction functionality has been removed
- The extension is now more reliable and handles complex cases better
- To convert between ComfyUI and Old NovelAI formats, you'll need to use two conversion steps with NovelAI V4 as an intermediate format

## Development

Created by Claude and Google Gemini, maintained by raspie10032. The code was rewritten from scratch in v2.0.0 to improve reliability and add support for new formats.

## Code References

This project incorporates code and techniques from the following sources:

### ComfyUI NAIDGenerator
- Repository: https://github.com/bedovyy/ComfyUI_NAIDGenerator
- Author: bedovyy
- Used for: Prompt conversion functionality and base implementation

Special thanks to the authors and contributors of these projects for their valuable work and making their code available to the community.

## License

This project is available under the MIT License.