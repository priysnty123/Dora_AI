# webcam_manager.py
import threading

# These will be shared across app.py (which writes to them)
# and tools.py (which reads from them)
last_frame = None
frame_lock = threading.Lock()