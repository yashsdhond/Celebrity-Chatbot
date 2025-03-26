from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import random

# Configure Gemini API
genai.configure(api_key="AIzaSyDfiMTGcE54t49AC3PcI2gEN4PbR_TVzHc")

app = Flask(__name__)

# Load scraped Wikipedia data
with open("ms_dhoni_wikipedia.txt", "r", encoding="utf-8") as file:
    scraped_data = file.read()

# Store conversation history
chat_history = []

def get_response(user_input):
    global chat_history  

    chat_history.append(f"Text: {scraped_data}")

    # Keep only the last 5 exchanges for memory
    if len(chat_history) > 5:
        chat_history = chat_history[-5:]

    # Format history for the prompt
    history_text = "\n".join(chat_history)

    # Randomized greetings & farewells
    greetings = ["Hello bhai! Kaise ho?", "Arey! Hi", "Hey! What's on your mind today?"]
    farewells = ["Thik hai bhai, milte hain!", "Okay, bas nikalta hoon!", "Milte hain agle match ke baad!"]
    unknown_responses = ["Sorry bhai, yeh toh mujhe bhi nahi pata.", "Iske baare mein mujhe zyada maloom nahi."]

    # Handle greetings
    if user_input.lower() in ["hi", "hello", "hey"]:
        bot_reply = random.choice(greetings)
    elif user_input.lower() in ["bye", "exit", "goodbye"]:
        bot_reply = random.choice(farewells)
    else:
        # Generate response using Gemini API
        response = genai.GenerativeModel("gemini-1.5-flash").generate_content(
            f"""
            Previous conversation:
            {history_text}

            Act as a chatbot representing MS Dhoni and respond in his natural dialect, tone, and style of speaking.
            Use his real-life phrases and maintain context from previous conversations.

            ### Important Rules:
            1. **Strict Information Control**: 
              - If the answer is found in the **scraped data** or **previous conversation**, then answer.
              - If not, respond you cannot answer the specific question or query
              - **Never generate** information beyond what is provided.

            2. **Follow User Commands**:  
              - If the user asks to **respond in a specific language**, follow their instruction.  
              - Example: If the user says "Talk in English," respond only in English.

            3. **Conversation Handling**:  
              - If the question is related to **previous conversation**, use that context to answer.  
              - If unrelated, check the scraped data first before responding.
              - If question or query is not clear reply what do you exactly want to ask?

            4. **MS Dhoni’s Tone & Style**:   
              - Keep responses **short, practical, and to the point.** 
          

            ### Answer the Current Question Only If Information Exists:
            Current Question: {user_input}
            """
        )
        bot_reply = response.text

    # Append bot response to history
    # Append user query to history
    chat_history.append(f"User: {user_input}")
    chat_history.append(f"MS Dhoni: {bot_reply}")

    return bot_reply

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    bot_reply = get_response(user_input)
    return jsonify({"response": bot_reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)