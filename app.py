
import os
import gradio as gr

# Imports from your other files
from Speech_to_text import record_audio, transcribe_with_groq
from ai_agent import ask_agent
from text_to_speech import text_to_speech_with_gtts, text_to_speech_with_elevenlabs

import cv2
import threading
import time

# Import the new shared manager
import webcam_manager

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
audio_filepath = "audio_question.mp3"
conversation_running = False

def process_audio_and_chat( chat_history = []):
    global conversation_running
    conversation_running = True
    
    # Check if camera is running
    if not is_running:
        # FIX: Use the imported function 'text_to_speech_with_gtts'
        text_to_speech_with_gtts("Please start the camera first so I can see.")
        chat_history.append(["(System)", "Please start the camera first so I can see."])
        return chat_history

    while conversation_running:
        try:
            record_audio(file_path=audio_filepath)
            user_input = transcribe_with_groq(audio_filepath)

            if not user_input or not user_input.strip():
                continue

           #Stop condition
            if "goodbye" in user_input.lower():
                chat_history.append([user_input, "👋 Goodbye! Conversation ended."])
                yield chat_history
                break

            response = ask_agent(user_query=user_input)

            # This creates the file. You may need to add code to play it.
            text_to_speech_with_gtts(input_text=response, output_filepath="final.mp3")

            chat_history.append([user_input, response])
            yield chat_history

        except Exception as e:
            print(f"Error in continuous recording: {e}")
            break

def stop_conversation():
    global conversation_running
    conversation_running = False
    return [["🛑 Conversation stopped by user.", ""]]

# ---- Webcam code ----

camera = None
is_running = False

def initialize_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return camera is not None and camera.isOpened()

def webcam_loop():
    """Background loop to continuously capture frames"""
    global camera, is_running
    while is_running and camera is not None:
        ret, frame = camera.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # FIX: Use webcam_manager to store the frame
            with webcam_manager.frame_lock:
                webcam_manager.last_frame = frame_rgb
        time.sleep(0.03) # ~30 FPS

def start_webcam():
    """Start the webcam feed"""
    global is_running
    if not initialize_camera():
        print("Error: Could not initialize camera.")
        return None
    is_running = True
    threading.Thread(target=webcam_loop, daemon=True).start()
    
    # Wait for the first frame to appear
    for _ in range(10): 
        with webcam_manager.frame_lock:
            if webcam_manager.last_frame is not None:
                return webcam_manager.last_frame
        time.sleep(0.1)
    return None # Return None if no frame appeared

def stop_webcam():
    """Stop the webcam feed"""
    global is_running, camera
    is_running = False
    if camera is not None:
        camera.release()
        camera = None
    # FIX: Clear the frame in webcam_manager
    with webcam_manager.frame_lock:
        webcam_manager.last_frame = None
    return None

def get_webcam_frame():
    """Get the most recent webcam frame"""
    # FIX: Read the frame from webcam_manager
    with webcam_manager.frame_lock:
        return webcam_manager.last_frame


# ---- Setup UI (No changes) ----
with gr.Blocks() as demo:
    gr.Markdown("<h1 style='color: orange; text-align: center;  font-size: 4em;'> 👧🏼 Dora – Your Personal AI Assistant</h1>")

    with gr.Row():
        # Left column - Webcam
        with gr.Column(scale=1):
            gr.Markdown("## Webcam Feed")
            
            with gr.Row():
                start_btn = gr.Button("Start Camera", variant="primary")
                stop_btn = gr.Button("Stop Camera", variant="secondary")
            
            webcam_output = gr.Image(
                label="Live Feed",
                streaming=True,
                show_label=False,
                width=640,
                height=480
            )
            
            # Faster refresh rate for smoother video
            webcam_timer = gr.Timer(0.033) # ~30 FPS
        
        # Right column - Chat
        with gr.Column(scale=1):
            gr.Markdown("## Chat Interface")
            
            chatbot = gr.Chatbot(
                label="Conversation",
                height=400,
                show_label=False
            )
            
            with gr.Row():
                start_convo_btn = gr.Button("▶️ Start Conversation", variant="primary")
                stop_convo_btn = gr.Button("⏹ Stop Conversation", variant="stop")
                clear_btn = gr.Button("🧹 Clear Chat", variant="secondary")
    
    # Event handlers
    start_btn.click(
        fn=start_webcam,
        outputs=webcam_output
    )
    
    stop_btn.click(
        fn=stop_webcam,
        outputs=webcam_output
    )
    
    webcam_timer.tick(
        fn=get_webcam_frame,
        outputs=webcam_output,
        show_progress=False # Hide progress indicator
    )
    
    start_convo_btn.click(
        fn=process_audio_and_chat,
        inputs=[],
        outputs=chatbot
    )

    stop_convo_btn.click(
        fn=stop_conversation,
        inputs=[],
        outputs=chatbot
    )

    clear_btn.click(
        fn=lambda: [],
        outputs=chatbot
    )

## Launch the app
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        share=False,
        debug=True
    )