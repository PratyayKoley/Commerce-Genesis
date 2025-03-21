import base64
import io

import google.generativeai as genai
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Set up Gemini API
genai.configure(api_key="AIzaSyBWDDYP8BVH3689jdIJ08jL_Y-RAQsq3No")

# Function to generate response using Gemini API
def get_gemini_response(text):
    model = genai.GenerativeModel("gemini-1.5-flash-8b")
    response = model.generate_content(text)
    return response.text

# Route for text-based chat
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    print(data)
    user_input = data.get("text")
    print(user_input)
    
    if not user_input:
        return jsonify({"error": "No text input provided"}), 400

    response_text = get_gemini_response(user_input)
    print(response_text)
    return jsonify({"response": response_text})


@app.route("/eco", methods=["POST"])
def eco():
    data = request.json
    print(data)
    product_title = data.get("product_title")
    print(product_title)

    prompt = f"must Provide a list of eco-friendly alternatives  and the harmfulness of the following product: {product_title}. Also, suggest what can be done to make it better in one line. provide in plane text format"
    
    if not product_title:
        return jsonify({"error": "No text input provided"}), 400

    response_text = get_gemini_response(prompt)
    print(response_text)
    return jsonify({"suggestions": response_text})

@app.route('/image', methods=['POST'])
def process_image():
    print("Received image processing request...")

    try:
        # Check if file is in the request
        if 'file' not in request.files:
            print("Error: No file part in the request")
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['file']
        
        if file.filename == '':
            print("Error: No selected file")
            return jsonify({'error': 'No selected file'}), 400

        print(f"File received: {file.filename}")

        # Read the image file
        print("Reading the image file...")
        image = Image.open(file.stream)

        # Convert the image to Base64
        print("Converting image to Base64...")
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        print("Base64 conversion completed.")

        # Initialize the Gemini model
        print("Initializing Gemini model...")
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")

        # Prepare the prompt
        prompt = "What is the category of the product in this image? Only give the name of the product nothing else"
        print("Prompt prepared.")

        # Send the image and prompt to Gemini
        print("Sending image and prompt to Gemini model...")
        response = model.generate_content([{'mime_type': 'image/jpeg', 'data': img_str}, prompt])

        print("Received response from Gemini.")

        # Return the response from Gemini
        return jsonify({'product_name': response.text})

    except Exception as e:
        print(f"Error during processing: {e}")
        return jsonify({'error': str(e)}), 500

if __name__== "__main__":
    app.run(debug=True)
