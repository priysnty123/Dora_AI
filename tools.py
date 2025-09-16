
import cv2
import base64
from dotenv import load_dotenv
from groq import Groq
import os 
from langchain.tools import tool
import time  # Import time for a delay
import numpy as np # Import numpy to help save the image

# Import from our new shared file
import webcam_manager

load_dotenv() 

def capture_frame_from_stream() -> str:
    """
    Captures one frame from the LIVE webcam stream (managed by app.py),
    encodes it as Base64 JPEG (raw string) and returns it.
    """
    with webcam_manager.frame_lock:
        frame = webcam_manager.last_frame.copy() if webcam_manager.last_frame is not None else None

    if frame is None:
        raise RuntimeError("No webcam frame available. Is the camera started in the UI?")

    # The frame from app.py is already RGB, but cv2.imencode expects BGR
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    ret, buf = cv2.imencode('.jpg', frame_bgr)
    if not ret:
        raise RuntimeError("Failed to encode frame as JPEG.")
        
    return base64.b64encode(buf).decode('utf-8')


@tool
def analyze_image_with_query(query: str) -> str:
    """
    Use this tool ONLY when the user explicitly asks about something visible through the webcam (clothes, objects, phone screen, time on a device, etc).
    DO NOT use this tool for math, general knowledge, coding, or any non-visual query.
    """
    
    try:
        # ADD A SMALL DELAY: This gives your camera 0.5 seconds to focus
        time.sleep(0.5) 
        
        # Call our function that reads the live stream
        img_b64 = capture_frame_from_stream()

        # --- START DEBUGGING ---
        # This will save the image the AI is seeing as 'debug_image.jpg'
        try:
            img_data = base64.b64decode(img_b64)
            np_arr = np.frombuffer(img_data, np.uint8)
            img_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            debug_filename = "debug_image.jpg"
            cv2.imwrite(debug_filename, img_bgr)
            print(f"--- Debug image saved to {debug_filename} ---")
        except Exception as e:
            print(f"Could not save debug image: {e}")
        # --- END DEBUGGING ---

    except RuntimeError as e:
        return str(e) # Return the error (e.g., "camera not started")
        
    # FIX: Use a vision-capable model.
    model = "meta-llama/llama-4-maverick-17b-128e-instruct" 
    
    if not query or not img_b64:
        return "Error: both 'query' and 'image' fields required."

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": query
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_b64}",
                    },
                },
            ],
        }]
    
    try:
        chat_completion=client.chat.completions.create(
            messages=messages,
            model=model,
            max_tokens=1024 # Give it more room to answer
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error during Groq API call: {e}")
        return f"Sorry, I had an error analyzing the image: {e}"
    
    
    # tool for the general search 

from langchain_community.tools import DuckDuckGoSearchRun

# Initialize the DuckDuckGo search tool.

ddg_tool = DuckDuckGoSearchRun(name="General_Knowledge_and_Math_Search")