import cv2
import base64
from dotenv import load_dotenv

load_dotenv()

def capture_image() -> str:
    """
    Captures one frame from the default webcam, resizes it,
    encodes it as Base64 JPEG (raw string) and returns it. 
    """
    for idx in range(4):
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            for _ in range(10):  # Warm up
                cap.read()
            ret, frame = cap.read()
            cap.release()
            if not ret:
                continue
            cv2.imwrite("sample.jpg", frame)  # Optional
            ret, buf = cv2.imencode('.jpg', frame)
            if ret:
                return base64.b64encode(buf).decode('utf-8')
    raise RuntimeError("Could not open any webcam (tried indices 0-3)")

capture_image()



from groq import Groq
from dotenv import load_dotenv
import os 
load_dotenv() 
from langchain.tools import tool



@tool
def analyze_image_with_query(query: str) -> str:
    """
    Use this tool ONLY when the user explicitly asks about something visible through the webcam (clothes, objects, phone screen, time on a device, etc).
    DO NOT use this tool for math, general knowledge, coding, or any non-visual query.
    For asnwering the maths , general knowledge , coding , or any no-visual query just search on Internet and then give the

    """
    img_b64 = capture_image()
    model="meta-llama/llama-4-maverick-17b-128e-instruct"
    
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
    chat_completion=client.chat.completions.create(
        messages=messages,
        model=model
    )

    return chat_completion.choices[0].message.content

#query = "How many people do you see?"
#print(analyze_image_with_query(query))

# if __name__ == "__main__":
#     tool = analyze_image_with_query
#     #result = tool.invoke("How many people do you see?")
#     #print(result)







































# prompt i want use ass well

# Rules for answering:
# 1. Use the camera ONLY for visual questions (e.g., "what am I wearing?", "what is in front of me?", "is my light on?").
# 2. For all non-visual questions (math, knowledge, history, weather, coding help, etc.), answer directly without using the camera.
# 3. Never trigger the camera unless the user explicitly asks about something visible.
# 4. Always reply in a natural, witty, and human-like tone — as if Cheenu herself is speaking.

# Examples:
# - "What is 2+2?" → Answer directly, no camera
# - "What's the weather?" → Answer directly, no camera
# - "What am I wearing?" → Use camera
# - "What do you see in front of me?" → Use camera

# Policy: If you use the camera unnecessarily, you will be penalized.
# """
