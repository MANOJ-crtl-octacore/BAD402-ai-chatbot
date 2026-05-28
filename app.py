from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from dotenv import load_dotenv
import markdown
import os

# ============================================
# Load Environment Variables
# ============================================

load_dotenv()

# ============================================
# Flask App
# ============================================

app = Flask(__name__)

app.secret_key = "cybermentor_super_secret_key"

# ============================================
# Gemini API Configuration
# ============================================

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

# ============================================
# Gemini Generation Settings
# ============================================

generation_config = {

    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,

}

# ============================================
# Gemini Model
# ============================================

model = genai.GenerativeModel(

    model_name="gemini-2.5-flash",

    generation_config=generation_config

)

# ============================================
# Cybersecurity System Prompt
# ============================================

SYSTEM_PROMPT = """
You are CyberMentor AI.

You are an advanced cybersecurity mentor and ethical hacking expert.

Your behavior:
- Talk naturally like a real human mentor.
- Be intelligent, friendly, and professional.
- Give practical real-world cybersecurity explanations.
- Explain concepts step-by-step.
- Use markdown formatting.
- Keep conversations engaging.
- Avoid robotic responses.
- Ask follow-up questions when appropriate.
- Adapt to beginner or advanced users automatically.

Your expertise:
- Ethical Hacking
- Penetration Testing
- Kali Linux
- Linux
- Networking
- Cybersecurity Fundamentals
- Bug Bounty
- Python for Cybersecurity
- Web Application Security
- OWASP Top 10
- Malware Analysis
- SOC Analyst
- Digital Forensics
- Red Teaming
- Blue Teaming
- CTFs
- Career Guidance

Important Rules:
- Never assist illegal hacking.
- Refuse malicious requests.
- Encourage legal and ethical cybersecurity learning.
- Reply in the SAME language as the user.
- Provide examples whenever useful.
- If code is required, provide clean working code.
"""

# ============================================
# Home Route
# ============================================

@app.route('/')
def home():

    if 'chat_history' not in session:

        session['chat_history'] = []

    return render_template('index.html')

# ============================================
# Chat Route
# ============================================

@app.route('/chat', methods=['POST'])
def chat():

    try:

        data = request.get_json()

        user_message = data.get('message')

        if not user_message:

            return jsonify({
                "reply": "Please enter a message."
            })

        # ============================================
        # Load Previous Memory
        # ============================================

        chat_history = session.get('chat_history', [])

        # ============================================
        # Convert Memory into Text
        # ============================================

        history_text = ""

        for chat in chat_history:

            history_text += f"""

User: {chat['user']}

Assistant: {chat['assistant']}

"""

        # ============================================
        # Final Prompt
        # ============================================

        full_prompt = f"""

{SYSTEM_PROMPT}

Conversation History:

{history_text}

Current User Message:

{user_message}

Assistant:

"""

        # ============================================
        # Generate AI Response
        # ============================================

        response = model.generate_content(full_prompt)

        bot_reply = response.text

        # ============================================
        # Save Memory
        # ============================================

        chat_history.append({

            "user": user_message,

            "assistant": bot_reply

        })

        # Keep only latest chats

        chat_history = chat_history[-15:]

        session['chat_history'] = chat_history

        # ============================================
        # Convert Markdown to HTML
        # ============================================

        bot_reply_html = markdown.markdown(

            bot_reply,

            extensions=['fenced_code']

        )

        # ============================================
        # Return Response
        # ============================================

        return jsonify({

            "reply": bot_reply_html

        })

    except Exception as e:

        print(e)

        return jsonify({

            "reply": f"⚠️ Error: {str(e)}"

        })

# ============================================
# Clear Chat
# ============================================

@app.route('/clear', methods=['POST'])
def clear_chat():

    session.pop('chat_history', None)

    return jsonify({

        "status": "success"

    })

# ============================================
# Run Flask App
# ============================================

if __name__ == '__main__':

    app.run(

        debug=True,

        host='0.0.0.0',

        port=5000

    )