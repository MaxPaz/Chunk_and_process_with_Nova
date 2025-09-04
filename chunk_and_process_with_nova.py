"""
Splits the tall screenshot into 1,024 × 8,000 chunks (Nova Vision max),
estimates token cost, and (optionally) calls Amazon Nova Pro/Lite on each tile.
"""
from PIL import Image, ImageDraw, ImageFont
import math, json, base64, os
import boto3
# import boto3   # ← Uncomment when you’re ready to call Bedrock

SOURCE_FILE      = "demo_image.png"
MAX_CHUNK_HEIGHT = 16_000                 # Nova Vision hard limit per side

MODELS = {
    "nova-pro": "us.amazon.nova-pro-v1:0",
    "nova-premier": "us.amazon.nova-premier-v1:0"
}

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# Create 1024x50000 demo image
if not os.path.exists(SOURCE_FILE):
    print("🎨 Creating 1024x50000 demo image...")
    img = Image.new("RGB", (1024, 50000), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    
    colors = [(255, 179, 186), (255, 223, 186), (255, 255, 186), (186, 255, 201), (186, 225, 255)]
    lorem_texts = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur ultricies, nunc et tincidunt scelerisque.",
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud.",
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est.",
        "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti."
    ]
    
    for i in range(50):
        top = i * 1000
        draw.rectangle([0, top, 1024, top + 1000], fill=colors[i % len(colors)])
        
        # Section title
        draw.text((20, top + 20), f"📰 Section {i+1}", fill="black", font=font)
        
        # Body text
        draw.text((20, top + 60), lorem_texts[i % len(lorem_texts)], fill="black", font=font)
        
        # URL
        draw.text((20, top + 140), f"https://example.com/section/{i+1}", fill="blue", font=font)
        
        # Additional elements
        draw.rectangle([20, top + 180, 200, top + 220], outline="gray", fill="lightgray")
        draw.text((25, top + 190), "Button", fill="black", font=font)
        
        draw.rectangle([220, top + 180, 400, top + 220], outline="green", fill="lightgreen")
        draw.text((225, top + 190), "Call to Action", fill="black", font=font)
    
    img.save(SOURCE_FILE)
    print(f"✅ Created {SOURCE_FILE}")

img = Image.open(SOURCE_FILE)
width, height = img.size
num_chunks    = math.ceil(height / MAX_CHUNK_HEIGHT)

print(f"📄  {SOURCE_FILE}: {width}×{height}")
print(f"🔪  Splitting into {num_chunks} chunks (≤{MAX_CHUNK_HEIGHT}px high)\n")

total_tokens = 0
pro_input_tokens = 0
pro_output_tokens = 0
premier_input_tokens = 0
premier_output_tokens = 0

for i in range(num_chunks):
    top    = i * MAX_CHUNK_HEIGHT
    bottom = min(top + MAX_CHUNK_HEIGHT, height)
    h      = bottom - top

    tile = img.crop((0, top, width, bottom))
    fname = f"chunk_{i+1}.png"
    tile.save(fname)
    print(f"✅  Saved {fname:13}  {width}×{h}")

    # Token estimate (Nova Vision: ~1.3 tokens per 1000 pixels)
    pixels = width * h
    tokens = int(pixels * 1.3 / 1000)
    total_tokens += tokens
    print(f"   ↳ token estimate: {tokens}")

    # Process with both Nova models
    with open(fname, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    payload = {
        "messages": [{
            "role": "user",
            "content": [{
                "image": {"format": "png", "source": {"bytes": image_data}}
            }, {
                "text": "Describe this image section."
            }]
        }],
        "inferenceConfig": {"maxTokens": 100}
    }
    
    for model_name, model_id in MODELS.items():
        try:
            resp = bedrock.invoke_model(modelId=model_id, body=json.dumps(payload))
            result = json.loads(resp["body"].read())
            input_tokens = result.get("usage", {}).get("inputTokens", 0)
            output_tokens = result.get("usage", {}).get("outputTokens", 0)
            response_text = result["output"]["message"]["content"][0]["text"][:80]
            
            if "pro" in model_name:
                pro_input_tokens += input_tokens
                pro_output_tokens += output_tokens
            else:
                premier_input_tokens += input_tokens
                premier_output_tokens += output_tokens
                
            print(f"   ↳ {model_name}: {input_tokens} in + {output_tokens} out tokens")
            print(f"     Response: {response_text}...")
        except Exception as e:
            print(f"   ↳ {model_name} failed: {e}")

print("\n💰 ACTUAL COST COMPARISON:")
print(f"   Estimated input tokens: {total_tokens:,}")
print(f"\n   Nova Pro actual usage:")
print(f"     Input: {pro_input_tokens:,} tokens")
print(f"     Output: {pro_output_tokens:,} tokens")
print(f"     Cost: ${(pro_input_tokens/1000)*0.0008 + (pro_output_tokens/1000)*0.0032:.4f}")
print(f"\n   Nova Premier actual usage:")
print(f"     Input: {premier_input_tokens:,} tokens")
print(f"     Output: {premier_output_tokens:,} tokens")
print(f"     Cost: ${(premier_input_tokens/1000)*0.003 + (premier_output_tokens/1000)*0.012:.4f}")
print("\n   (Pricing: Pro $0.0008/$0.0032, Premier $0.003/$0.012 per 1K tokens)") 