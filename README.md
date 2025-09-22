## AI Assistant–Dora

My new AI assistant that can interact with you through webcam and audio in real time. You can ask her anything — she listens, thinks, browse the internet and responds like a real conversational agent.



## 🌟 Features

* **🎙️ Voice-Activated:** Fully conversational using Groq's blazing-fast Whisper API for speech-to-text.
* **🧠 Intelligent Agent:** Powered by **Google's Gemini 2.0 Flash** and a **LangChain ReAct Agent**. Dora doesn't just respond; she *reasons*, plans, and chooses the correct tool for your question.
* **👁️ Real-Time Computer Vision:** Dora can "see"! Ask "What am I holding?" or "What color is my shirt?" and the agent will use your webcam and a model GROQ or  (Hugging Face) to answer.
* **🌐 Live Web Search:** Connected to the internet with **DuckDuckGo**. Dora can answer questions about current events, solve math problems, or look up general knowledge.
* **🔊 Natural Voice Output:** Responds with a natural voice using ElevenLabs and  Google Text-to-Speech (gTTS).
* **🖥️ Interactive UI:** Built with **Gradio**, the interface includes a live webcam feed and a persistent chat history, all running locally.

## ⚙️ Architecture: How it Works

This project uses a decoupled architecture to allow the Gradio UI and the AI Agent to work together seamlessly.

1.  **Gradio UI (`app.py`):** Runs a background thread to continuously capture frames from your webcam. This keeps the UI feed smooth and live.
2.  **Webcam Manager (`webcam_manager.py`):** A simple shared-state module that holds the *very latest frame* from the webcam in memory.
3.  **AI Agent (`ai_agent.py`):** This is the brain. It's a LangChain ReAct agent powered by Gemini. When you ask a question, the agent decides what to do:
    * **Is it visual?** -> The agent calls the **`analyze_image_with_query` tool**. This tool instantly reads the latest frame from the `webcam_manager`, sends it to the Hugging Face model for analysis, and returns the answer.
    * **Is it knowledge?** -> The agent calls the **`General_Knowledge_and_Math_Search` tool** (powered by DuckDuckGo) to get a live web result.
    * **Is it chat?** -> Gemini answers directly.

This allows the UI to show a smooth video feed while the AI can "grab" a frame for analysis at any moment without freezing the stream.

## 🛠️ Technology Stack

* **Python 3.10+**
* **AI Framework:** LangChain (ReAct Agent)
* **Reasoning LLM:** Google Gemini or Hugging Face Model
* **UI:** Gradio
* **Tools:**
    * **Vision Model:** meta-llama/llama-4-maverick-17b-128e-instruct (Hugging Face)
    * **Search:** DuckDuckGo (`DuckDuckGoSearchRun`)
    * **STT (Speech-to-Text):** Groq (Whisper)
    * **TTS (Text-to-Speech):** gTTS
* **Computer Vision:** OpenCV
* **Environment:** `uv` & Virtual Environment



## 🚀 Setup & Installation

Follow these steps to get Dora running on your local machine.

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/Dora_AI_Assistant.git](https://github.com/your-username/Dora_AI_Assistant.git)
cd Dora_AI_Assistant

# Create a virtual environment
python -m venv .venv
# Activate it (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
# (or macOS/Linux)
# source .venv/bin/activate

# Then install dependencies from requirement.txt
uv pip install -r requirements.txt

# Then Create Your Environment File (.env file )

GROQ_API_KEY=""
LANGCHAIN_TRACING_V2=false
GOOGLE_API_KEY=""
ELEVENLABS_API_KEY="" 


# Now How to Run 
1. Make sure your virtual environment is activated.
Run the application with command = uv run app.py
2. Open your web browser and go to the local URL shown in your terminal (usually http://127.0.0.1:7886)
3.Click "Start Camera".
4.Click "Start Conversation" and start talking!

or you can do this aslo 

Clone the repo and run:
uv sync

That’s it. This command:

Creates a virtual environment (if one doesn't exist)

Installs all dependencies from uv.lock

Sets up everything exactly as expected
