"""
Command-line interface for Imagenation
"""

import argparse
import csv
import json
import sys

from .generator import ImagenationGenerator


def process_single_generation(args):
    """Process single image generation from command line arguments"""
    generator = ImagenationGenerator(rate_limit_delay=args.delay)
    
    if args.input_image:
        success = generator.generate_text_image_to_image(
            args.input_text, args.input_image, args.output
        )
    else:
        success = generator.generate_text_to_image(args.input_text, args.output)
    
    return success


def process_csv_file(csv_path: str, rate_limit_delay: float = 12.0):
    """Process CSV file with columns: input_text, input_image_path, output_image_name"""
    generator = ImagenationGenerator(rate_limit_delay=rate_limit_delay)
    
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_num, row in enumerate(reader, start=1):
                input_text = row.get('input_text', '').strip()
                input_image_path = row.get('input_image_path', '').strip()
                output_image_name = row.get('output_image_name', '').strip()
                
                if not input_text or not output_image_name:
                    print(f"Row {row_num}: Missing required fields")
                    continue
                
                print(f"Processing row {row_num}: {output_image_name}")
                
                if input_image_path:
                    success = generator.generate_text_image_to_image(
                        input_text, input_image_path, output_image_name
                    )
                else:
                    success = generator.generate_text_to_image(input_text, output_image_name)
                
                if not success:
                    print(f"Failed to generate image for row {row_num}")
    
    except FileNotFoundError:
        print(f"CSV file not found: {csv_path}")
    except Exception as e:
        print(f"Error processing CSV file: {e}")


def process_json_file(json_path: str, rate_limit_delay: float = 12.0):
    """Process JSON file with entries containing: input_text, input_image_path, output_image_name"""
    generator = ImagenationGenerator(rate_limit_delay=rate_limit_delay)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
        
        if not isinstance(data, list):
            print("JSON file must contain an array of objects")
            return
        
        for idx, item in enumerate(data):
            input_text = item.get('input_text', '').strip()
            input_image_path = item.get('input_image_path', '').strip()
            output_image_name = item.get('output_image_name', '').strip()
            
            if not input_text or not output_image_name:
                print(f"Item {idx + 1}: Missing required fields")
                continue
            
            print(f"Processing item {idx + 1}: {output_image_name}")
            
            if input_image_path:
                success = generator.generate_text_image_to_image(
                    input_text, input_image_path, output_image_name
                )
            else:
                success = generator.generate_text_to_image(input_text, output_image_name)
            
            if not success:
                print(f"Failed to generate image for item {idx + 1}")
    
    except FileNotFoundError:
        print(f"JSON file not found: {json_path}")
    except json.JSONDecodeError:
        print(f"Invalid JSON format in file: {json_path}")
    except Exception as e:
        print(f"Error processing JSON file: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Imagenation - AI Image Generation Tool using Google's Imagen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Text to image
  imagenation -it "A beautiful sunset over mountains" -o sunset.png
  
  # Text + image to image
  imagenation -it "Add a rainbow to this landscape" -ii photo.jpg -o rainbow_photo.png
  
  # Process CSV file
  imagenation --csv data.csv
  
  # Process JSON file
  imagenation --json data.json
        """
    )
    
    # Single generation arguments
    parser.add_argument('-it', '--input-text', type=str, help='Input text prompt')
    parser.add_argument('-ii', '--input-image', type=str, help='Input image path (optional)')
    parser.add_argument('-o', '--output', type=str, help='Output image path')
    
    # Batch processing arguments
    parser.add_argument('--csv', type=str, help='CSV file path for batch processing')
    parser.add_argument('--json', type=str, help='JSON file path for batch processing')
    
    # Rate limiting arguments
    parser.add_argument('--delay', type=float, default=12.0, 
                       help='Delay between API requests in seconds (default: 12.0 for free tier)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.csv:
        process_csv_file(args.csv, args.delay)
    elif args.json:
        process_json_file(args.json, args.delay)
    elif args.input_text and args.output:
        success = process_single_generation(args)
        if not success:
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()