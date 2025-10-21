# Imagenation 🎨

[![PyPI version](https://badge.fury.io/py/imagenation.svg)](https://pypi.org/project/imagenation/)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Generate AI Images in Batches with Google's Imagen. Transform text prompts and optional image inputs into stunning visuals, effortlessly.

![Banner](https://raw.githubusercontent.com/pmsosa/imagenation/main/banner.png)

## Features

- **Text-to-Image**: Generate images from text descriptions
- **Text+Image-to-Image**: Modify existing images with text prompts  
- **CLI Interface**: Direct command-line usage
- **Batch Processing**: Process multiple images from CSV/JSON files
- **Library Support**: Import and use in your Python projects
- **Rate Limiting**: Built-in rate limiting with configurable delays to prevent API quota issues

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API key** in `.env`:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

3. **Generate an image**:
   ```bash
   ./start.sh -it "A beautiful sunset over mountains" -o sunset.png
   ```

## Usage

### Command Line

```bash
# Text to image (with default rate limiting)
./start.sh -it "A majestic dragon in a fantasy landscape" -o dragon.png

# Text + image to image  
./start.sh -it "Add a rainbow to this landscape" -ii photo.jpg -o rainbow_photo.png

# Batch processing from CSV
./start.sh --csv batch_data.csv

# Batch processing from JSON
./start.sh --json batch_data.json

# Custom rate limiting for paid tier (faster processing)
./start.sh -it "Beautiful landscape" -o output.png --delay 0.2

# Conservative rate limiting for batch processing
./start.sh --csv large_batch.csv --delay 15.0
```

### Rate Limiting

The tool includes built-in rate limiting to prevent hitting Google API quotas:

- **Default delay**: 12 seconds between requests (5 requests/minute for free tier)
- **Custom delay**: Use `--delay` parameter to adjust timing
- **Automatic handling**: Built-in wait times and error handling for rate limit errors

#### Rate Limiting Recommendations

| Tier | Delay | Requests/Minute | Use Case |
|------|-------|-----------------|----------|
| Free | 12s (default) | 5 | Personal use, occasional generation |
| Paid | 0.2s | 300 | High-volume processing, development |
| Batch | 15s+ | 4 | Large batch processing, quota conservation |

#### Rate Limiting Examples

```bash
# Free tier (default 12s delay)
./start.sh -it "sunset" -o output.png

# Paid tier (faster processing)
./start.sh -it "sunset" -o output.png --delay 0.2

# Batch processing with conservative delay
./start.sh --csv batch.csv --delay 15.0

# Library usage with custom rate limiting
from imagenation import ImagenationGenerator
gen = ImagenationGenerator(rate_limit_delay=0.2)  # 300 RPM
```

### Python Library

```python
from imagenation import ImagenationGenerator

# Initialize generator with custom rate limiting
gen = ImagenationGenerator(rate_limit_delay=0.2)  # 300 RPM for paid tier

# Generate text-to-image
gen.generate_text_to_image("A serene lake at sunset", "lake.png")

# Generate text+image-to-image
gen.generate_text_image_to_image(
    "Make this photo look vintage", 
    "input.jpg", 
    "vintage_output.jpg"
)
```

### Alternative Usage

```bash
# Using Python module directly
python -m imagenation -it "Beautiful landscape" -o output.png

# Using original script (backward compatibility)
python imagenation.py -it "Beautiful landscape" -o output.png
```

## File Formats

### CSV Format
```csv
input_text,input_image_path,output_image_name
"A beautiful sunset","","sunset.png"
"Add a rainbow","landscape.jpg","rainbow_landscape.png"
```

### JSON Format
```json
[
  {
    "input_text": "A beautiful sunset",
    "input_image_path": "",
    "output_image_name": "sunset.png"
  },
  {
    "input_text": "Add a rainbow", 
    "input_image_path": "landscape.jpg",
    "output_image_name": "rainbow_landscape.png"
  }
]
```

## Requirements

- Python 3.7+
- Google API key with Gemini access
- Dependencies: `google-genai`, `pillow`, `python-dotenv`

## Project Structure

```
imagenation/
├── imagenation/           # Main package
│   ├── __init__.py       # Package exports
│   ├── generator.py      # Core generation logic with rate limiting
│   ├── cli.py           # Command-line interface
│   └── __main__.py      # Module entry point
├── imagenation.py        # Backward compatibility script
├── start.sh             # Setup and run script
├── requirements.txt     # Dependencies
├── .env                # API key configuration
└── README.md           # This file
```

## Rate Limiting Details

The tool automatically handles rate limiting to prevent API quota issues:

- **Built-in delays**: Automatic wait times between requests
- **Error handling**: Graceful handling of 429 rate limit errors
- **Configurable**: Adjust timing via `--delay` parameter or constructor
- **Batch processing**: Essential for processing large numbers of images without hitting daily limits

When rate limits are exceeded, the tool provides clear feedback and suggestions for adjusting the delay parameter.


---
_🌊 Made with Good Vibes by Pedro, Claude, and Gemini 🌊_