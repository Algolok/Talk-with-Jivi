from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS) for frontend access

# Configure Gemini API
genai.configure(api_key="AIzaSyDJbITw7tQYUR8FZyQ7OxIp8R9fpTPl1Pw")

model = genai.GenerativeModel(
    "gemini-pro",
    safety_settings=[
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "LOW"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "MEDIUM"},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "MEDIUM"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "MEDIUM"},
    ]
)

# System Prompt to Control AI Behavior
SYSTEM_PROMPT = (
    "You are Jivi, a helpful and intelligent AI assistant. "
    "For casual questions, provide short, natural responses. "
    "For complex questions, provide structured, detailed answers using steps or bullet points. "
    "For recommendations, list them in an organized format. "
    "Keep your tone friendly and engaging."
)

def generate_response(question):
    """
    Streams response chunk by chunk and handles safety filter errors.
    """
    try:
        # Generate AI response
        response = model.generate_content(SYSTEM_PROMPT + "\nUser: " + question, stream=True)

        for chunk in response:
            if hasattr(chunk, "text") and chunk.text:
                yield f"{chunk.text}\n\n"

        # Check if response was blocked by safety filters
        if response.candidates and response.candidates[0].safety_ratings:
            for rating in response.candidates[0].safety_ratings:
                if rating.category == "HARM_CATEGORY_SEXUALLY_EXPLICIT" and rating.probability == "HIGH":
                    yield f"data: Sorry, I can't answer that question. Try rephrasing it!\n\n"
                    return

    except Exception as e:
        yield f"Error: {str(e)}\n\n"

@app.route("/chat", methods=["POST"])
def chat():
    """
    Handles user queries and streams the response.
    """
    data = request.json
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    return Response(generate_response(user_input), mimetype="text/event-stream")

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, threaded=True)
