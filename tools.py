# import cv2
# import base64
# from dotenv import load_dotenv



# load_dotenv()

# def capture_image() -> str:
#     """
#     Captures one frame from the default webcam, resizes it,
#     encodes it as Base64 JPEG (raw string) and returns it. 
#     """
#     for idx in range(4):
#         cap = cv2.VideoCapture(idx)
#         if cap.isOpened():
#             for _ in range(10):  # Warm up
#                 cap.read()
#             ret, frame = cap.read()
#             cap.release()
#             if not ret:
#                 continue
#             cv2.imwrite("sample.jpg", frame)  # Optional
#             ret, buf = cv2.imencode('.jpg', frame)
#             if ret:
#                 return base64.b64encode(buf).decode('utf-8')
#     raise RuntimeError("Could not open any webcam (tried indices 0-3)")

# capture_image()

# # import base64
# # import cv2
# # import time
# # from app import last_frame, frame_lock  # reuse the global webcam frame

# # def capture_images(num_frames: int = 5, delay: float = 0.1) -> list[str]:
# #     from app import last_frame, frame_lock
# #     """
# #     Capture multiple frames (default: 5) from the live webcam feed
# #     and return them as a list of Base64 JPEG strings.
    
# #     :param num_frames: Number of frames to capture.
# #     :param delay: Delay between frames in seconds.
# #     """
# #     images = []

# #     for _ in range(num_frames):
# #         with frame_lock:
# #             frame = last_frame.copy() if last_frame is not None else None

# #         if frame is None:
# #             raise RuntimeError("No webcam frame available yet. Start the camera first.")

# #         ret, buf = cv2.imencode('.jpg', frame)
# #         if not ret:
# #             raise RuntimeError("Failed to encode frame as JPEG.")

# #         images.append(base64.b64encode(buf).decode('utf-8'))
# #         time.sleep(delay)  # small pause between frames

# #     return images



# from groq import Groq
# from dotenv import load_dotenv
# import os 
# load_dotenv() 
# from langchain.tools import tool



# @tool
# def analyze_image_with_query(query: str) -> str:
#     """
#     Use this tool ONLY when the user explicitly asks about something visible through the webcam (clothes, objects, phone screen, time on a device, etc).
#     DO NOT use this tool for math, general knowledge, coding, or any non-visual query.
#     For asnwering the maths , general knowledge , coding , or any no-visual query just search on Internet and then give the

#     """
#     img_b64 = capture_images()
#     model="meta-llama/llama-4-maverick-17b-128e-instruct"
    
#     if not query or not img_b64:
#         return "Error: both 'query' and 'image' fields required."

#     client = Groq(api_key=os.getenv("GROQ_API_KEY"))
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text", 
#                     "text": query
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:image/jpeg;base64,{img_b64}",
#                     },
#                 },
#             ],
#         }]
#     chat_completion=client.chat.completions.create(
#         messages=messages,
#         model=model
#     )

#     return chat_completion.choices[0].message.content

# #query = "How many people do you see?"
# #print(analyze_image_with_query(query))

# # if __name__ == "__main__":
# #     tool = analyze_image_with_query
# #     #result = tool.invoke("How many people do you see?")
# #     #print(result)







































# # prompt i want use ass well

# # Rules for answering:
# # 1. Use the camera ONLY for visual questions (e.g., "what am I wearing?", "what is in front of me?", "is my light on?").
# # 2. For all non-visual questions (math, knowledge, history, weather, coding help, etc.), answer directly without using the camera.
# # 3. Never trigger the camera unless the user explicitly asks about something visible.
# # 4. Always reply in a natural, witty, and human-like tone — as if Cheenu herself is speaking.

# # Examples:
# # - "What is 2+2?" → Answer directly, no camera
# # - "What's the weather?" → Answer directly, no camera
# # - "What am I wearing?" → Use camera
# # - "What do you see in front of me?" → Use camera

# # Policy: If you use the camera unnecessarily, you will be penalized.
# # """


# tools.py
# tools.py

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