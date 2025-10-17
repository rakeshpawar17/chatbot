import google.generativeai as genai

# --- IMPORTANT ---
# Paste the same API key you used in your app.py file.
API_KEY = "AIzaSyDkmiG3eUUNl_I37XJSkkw7hjSXTaVEcg8"

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"Error configuring API key: {e}")
    exit()

print("Finding models that support 'generateContent'...\n")

# List all available models
for model in genai.list_models():
  # Check if the 'generateContent' method is supported by the model
  if 'generateContent' in model.supported_generation_methods:
    print(f"Model name: {model.name}")
    print("-" * 20)