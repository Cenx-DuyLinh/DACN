import cv2
import tkinter as tk
from PIL import Image, ImageTk
import time 
def update_frame():
    ret, frame = cap.read()
    if ret:
        # Convert frame to RGB format
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize the frame to fit in the Tkinter window
        frame_resized = cv2.resize(frame_rgb, (640, 480))
        
        # Convert the resized frame to an ImageTk object
        img = Image.fromarray(frame_resized)
        start = time.time()
        imgtk = ImageTk.PhotoImage(image=img)
        end = time.time()
        # Clear the existing image from the Canvas
        canvas.delete("all")
        
        # Create a new image item on the Canvas
        canvas.image = imgtk
        canvas.create_image(0, 0, anchor=tk.NW, image=canvas.image)
        print(f"tk time {end - start}")
        
        # Schedule the update_frame function to be called again after a delay
        canvas.after(1, update_frame)

# Create a Tkinter window
window = tk.Tk()
window.title("Webcam Capture")

# Create a Canvas to display the video feed
canvas = tk.Canvas(window, width=640, height=480)
canvas.pack()

# Open the webcam
cap = cv2.VideoCapture(0)

# Call the update_frame function to start capturing and displaying the video
update_frame()

# Start the Tkinter event loop
window.mainloop()

# Release the webcam and close the OpenCV window after exiting Tkinter
cap.release()
cv2.destroyAllWindows()