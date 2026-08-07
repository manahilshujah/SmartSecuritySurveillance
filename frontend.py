import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import subprocess
import sys
import cv2

from PIL import Image, ImageTk


# ==========================================
# PROJECT PATH SETTINGS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_NAME = os.path.join(
    BASE_DIR,
    "database",
    "surveillance.db"
)


def get_full_path(file_path):
    """
    Convert a database relative path into
    an absolute path inside the project.
    """

    if not file_path:
        return None

    if os.path.isabs(file_path):
        return file_path

    return os.path.join(BASE_DIR, file_path)


# ==========================================
# OPEN WEBCAM
# ==========================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Warning: Unable to access webcam.")


# ==========================================
# MAIN WINDOW
# ==========================================

root = tk.Tk()

root.title("Smart Security Surveillance System")

root.geometry("1200x700")

root.minsize(1000, 600)


# ==========================================
# MAIN TITLE
# ==========================================

title_label = tk.Label(
    root,
    text="Smart Security Surveillance System",
    font=("Arial", 22, "bold")
)

title_label.pack(
    pady=15
)


# ==========================================
# MAIN CONTENT AREA
# ==========================================

main_frame = tk.Frame(root)

main_frame.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=10
)


# ==========================================
# LIVE CAMERA FRAME
# ==========================================

camera_frame = tk.LabelFrame(
    main_frame,
    text="Live Camera",
    font=("Arial", 14, "bold"),
    padx=10,
    pady=10
)

camera_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=10
)


camera_label = tk.Label(
    camera_frame,
    text="Starting camera...",
    font=("Arial", 16),
    relief="sunken"
)

camera_label.pack(
    fill="both",
    expand=True
)


# ==========================================
# DETECTION HISTORY FRAME
# ==========================================

event_frame = tk.LabelFrame(
    main_frame,
    text="Detection History",
    font=("Arial", 14, "bold"),
    padx=10,
    pady=10
)

event_frame.pack(
    side="right",
    fill="both",
    expand=True,
    padx=10
)


# ==========================================
# TABLE
# ==========================================

columns = (
    "ID",
    "Date",
    "Time",
    "Event",
    "People",
    "Confidence",
    "Image",
    "Video"
)

event_table = ttk.Treeview(
    event_frame,
    columns=columns,
    show="headings"
)


# Table headings

for column in columns:

    event_table.heading(
        column,
        text=column
    )


# Column widths

event_table.column("ID", width=40)
event_table.column("Date", width=90)
event_table.column("Time", width=75)
event_table.column("Event", width=130)
event_table.column("People", width=60)
event_table.column("Confidence", width=80)
event_table.column("Image", width=180)
event_table.column("Video", width=180)


# ==========================================
# TABLE SCROLLBAR
# ==========================================

scrollbar = ttk.Scrollbar(
    event_frame,
    orient="vertical",
    command=event_table.yview
)

event_table.configure(
    yscrollcommand=scrollbar.set
)

event_table.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar.pack(
    side="right",
    fill="y"
)


# ==========================================
# LIVE CAMERA UPDATE
# ==========================================

def update_camera():

    success, frame = camera.read()

    if success:

        # Mirror effect
        frame = cv2.flip(frame, 1)

        # Convert OpenCV BGR format to RGB
        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # Convert frame to PIL image
        image = Image.fromarray(frame)

        # Resize to fit the camera panel
        image.thumbnail((550, 500))

        # Convert PIL image to Tkinter-compatible image
        photo = ImageTk.PhotoImage(image)

        # Display camera frame
        camera_label.config(
            image=photo,
            text=""
        )

        # Keep reference so image is not garbage collected
        camera_label.image = photo

    else:

        camera_label.config(
            text="Unable to access camera.",
            image=""
        )

    # Update camera every 30 milliseconds
    root.after(
        30,
        update_camera
    )


# ==========================================
# LOAD DATABASE RECORDS
# ==========================================

def load_events():

    # Remove old records from table

    for item in event_table.get_children():

        event_table.delete(item)


    # Check database exists

    if not os.path.exists(DATABASE_NAME):

        messagebox.showwarning(
            "Database Not Found",
            "The surveillance database does not exist yet."
        )

        return


    try:

        connection = sqlite3.connect(
            DATABASE_NAME
        )

        cursor = connection.cursor()


        cursor.execute("""
        SELECT
            id,
            date,
            time,
            event,
            people,
            confidence,
            image,
            video
        FROM detections
        ORDER BY id DESC
        """)


        records = cursor.fetchall()


        connection.close()


        # Add records to table

        for record in records:

            event_table.insert(
                "",
                "end",
                values=record
            )


    except sqlite3.Error as error:

        messagebox.showerror(
            "Database Error",
            f"Could not load database:\n{error}"
        )


# ==========================================
# REFRESH EVENTS
# ==========================================

def refresh_events():

    load_events()


# ==========================================
# OPEN IMAGE
# ==========================================

def view_image():

    selected = event_table.selection()


    if not selected:

        messagebox.showinfo(
            "Select Event",
            "Please select an event from the table first."
        )

        return


    values = event_table.item(
        selected[0],
        "values"
    )


    image_path = values[6]


    if not image_path:

        messagebox.showinfo(
            "No Image",
            "No image is associated with this event."
        )

        return


    image_path = get_full_path(image_path)


    if not os.path.exists(image_path):

        messagebox.showerror(
            "Image Not Found",
            f"Image could not be found:\n{image_path}"
        )

        return


    try:

        if sys.platform.startswith("win"):

            os.startfile(image_path)

        elif sys.platform == "darwin":

            subprocess.run(
                ["open", image_path]
            )

        else:

            subprocess.run(
                ["xdg-open", image_path]
            )


    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Could not open image:\n{error}"
        )


# ==========================================
# PLAY VIDEO
# ==========================================

def play_video():

    selected = event_table.selection()


    if not selected:

        messagebox.showinfo(
            "Select Event",
            "Please select an event from the table first."
        )

        return


    values = event_table.item(
        selected[0],
        "values"
    )


    video_path = values[7]


    if not video_path:

        messagebox.showinfo(
            "No Video",
            "No video is associated with this event."
        )

        return


    video_path = get_full_path(video_path)


    if not os.path.exists(video_path):

        messagebox.showerror(
            "Video Not Found",
            f"Video could not be found:\n{video_path}"
        )

        return


    try:

        if sys.platform.startswith("win"):

            os.startfile(video_path)

        elif sys.platform == "darwin":

            subprocess.run(
                ["open", video_path]
            )

        else:

            subprocess.run(
                ["xdg-open", video_path]
            )


    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Could not play video:\n{error}"
        )


# ==========================================
# EXIT APPLICATION
# ==========================================

def exit_application():

    # Release webcam
    camera.release()

    # Close application
    root.destroy()


# ==========================================
# BUTTON FRAME
# ==========================================

button_frame = tk.Frame(
    root
)

button_frame.pack(
    fill="x",
    pady=15
)


# ==========================================
# REFRESH BUTTON
# ==========================================

refresh_button = tk.Button(
    button_frame,
    text="Refresh Events",
    font=("Arial", 11),
    width=16,
    command=refresh_events
)

refresh_button.pack(
    side="left",
    padx=10
)


# ==========================================
# VIEW SCREENSHOT BUTTON
# ==========================================

image_button = tk.Button(
    button_frame,
    text="View Screenshot",
    font=("Arial", 11),
    width=16,
    command=view_image
)

image_button.pack(
    side="left",
    padx=10
)


# ==========================================
# PLAY VIDEO BUTTON
# ==========================================

video_button = tk.Button(
    button_frame,
    text="Play Video",
    font=("Arial", 11),
    width=16,
    command=play_video
)

video_button.pack(
    side="left",
    padx=10
)


# ==========================================
# EXIT BUTTON
# ==========================================

exit_button = tk.Button(
    button_frame,
    text="Exit",
    font=("Arial", 11),
    width=16,
    command=exit_application
)

exit_button.pack(
    side="right",
    padx=10
)


# ==========================================
# LOAD EXISTING EVENTS
# ==========================================

load_events()


# ==========================================
# START LIVE CAMERA
# ==========================================

update_camera()


# ==========================================
# START APPLICATION
# ==========================================

root.mainloop()