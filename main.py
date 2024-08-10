import os
from flask import Flask, request, jsonify
import google.generativeai as genai

# Configure the Google Generative AI SDK
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

app = Flask(__name__)

def upload_to_gemini(file_path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(file_path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

# Model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

@app.route('/api/process', methods=['POST'])
def process_image_and_prompt():
    if 'image' not in request.files or 'prompt' not in request.form:
        return jsonify({"error": "Image and prompt are required."}), 400

    image = request.files['image']
    prompt = request.form['prompt']

    # Création du répertoire si nécessaire
    save_dir = "/mnt/data/"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Save the image to the specified directory
    image_path = os.path.join(save_dir, image.filename)
    image.save(image_path)

    # Upload the image to Gemini
    file_uri = upload_to_gemini(image_path, mime_type=image.mimetype)

    # Create the chat session with the image and prompt
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    file_uri,
                    prompt,
                ],
            },
        ]
    )

    response = chat_session.send_message(prompt)

    return jsonify({"response": response.text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
