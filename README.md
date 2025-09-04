# Amazon Nova Vision Demo: Processing Large Images

Demo showing how to process large images (1024x50000px) with Amazon Nova models by chunking them into smaller pieces.

## Overview

This demo creates a tall webpage screenshot (50,000px height) and processes it with Amazon Nova Pro and Nova Premier models to compare:
- Token usage and costs
- Response quality 
- Processing capabilities

## Key Findings

- **Image Size Limit**: Nova models have a 16,000px height limit
- **Chunking Required**: Large images must be split into smaller chunks
- **Cost Comparison**: Nova Pro vs Premier pricing analysis included

## Files

- `chunk_and_process_with_nova.py` - Main demo script
- `requirements.txt` - Python dependencies

## Setup

1. **Install dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials**:
   ```bash
   aws configure
   # OR set environment variables:
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export AWS_DEFAULT_REGION=us-east-1
   ```

3. **Ensure Nova model access** in your AWS account (us-east-1 region)

## Usage

Run the main demo:
```bash
python chunk_and_process_with_nova.py
```

## Output

The script will:
1. Generate a 1024x50000px demo image
2. Split it into 16,000px chunks (4 chunks total)
3. Process each chunk with both Nova models
4. Show token usage and cost comparison

## Requirements

- Python 3.7+
- AWS account with Nova model access
- Pillow (image processing)
- boto3 (AWS SDK)

## Cost Estimation

Based on current AWS pricing (check for updates):
- **Nova Pro**: $0.0008 input / $0.0032 output per 1K tokens
- **Nova Premier**: $0.003 input / $0.012 output per 1K tokens

## Notes

- Images are processed in us-east-1 region
- Modify `MAX_CHUNK_HEIGHT` if needed (max 16,000px)
- Token estimates: ~1.3 tokens per 1000 pixels
