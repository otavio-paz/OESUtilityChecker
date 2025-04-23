import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD


class DropZone(tk.Label):
    def __init__(self, master, text="", report_text=None):
        super().__init__(master, text=text, bg="#2E2E2E", fg="white", borderwidth=1, relief="solid", pady=10)
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.on_drop)
        self.report_text = report_text  # Reference to the report text widget

        # Browse button
        self.browse_button = tk.Button(self, text="Browse", bg="#1E1E1E", fg="white", command=self.on_browse)
        self.browse_button.pack(side=tk.BOTTOM, pady=5)

    def on_drop(self, event):
        # Simulate some processing of the dropped files
        file_names = event.data  # Concatenate file names into one string
        self.config(text=f"Processing: {file_names}")
        # Replace with your actual file processing logic here
        self.report_text.insert(tk.END, f"Dropped: {file_names}\n")  # Update report text

    def on_browse(self):
        # Opens a file dialog to select a file
        filename = filedialog.askopenfilename()
        if filename:
            self.config(text=f"Selected: {filename}")
            # Handle the selected file (replace with your logic)
            self.report_text.insert(tk.END, f"Selected: {filename}\n")  # Update report text


def save_report(report_text):
    filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if filename:
        with open(filename, "w") as file:
            file.write(report_text.get("1.0", tk.END))


root = TkinterDnD.Tk()
root.title("EM Checker")

# Set background color
root.config(bg="#1E1E1E")

# Calculate the center of the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = screen_width // 2
center_y = screen_height // 2

# Set dimensions for left and right sides
left_width = screen_width // 2
right_width = screen_width - left_width

# Set geometry for the window
root.geometry(f"{screen_width}x{screen_height}+{center_x - left_width // 2}+{center_y - screen_height // 2}")

# Frame for left side (input)
frame_left = tk.Frame(root, bg="#1E1E1E")
frame_left.place(relx=0, rely=0, relwidth=0.5, relheight=1)

# Frame for right side (report)
frame_right = tk.Frame(root, bg="#1E1E1E")
frame_right.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

# Frame for drop zones on the left side
frame_drop_zones = tk.Frame(frame_left, bg="#1E1E1E")
frame_drop_zones.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Report section on the right side
report_label = tk.Label(frame_right, text="Report content", bg="#1E1E1E", fg="white")
report_label.pack(side=tk.TOP, pady=10, fill=tk.X)

report_text = tk.Text(frame_right, bg="#2E2E2E", fg="white")
report_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

download_button = tk.Button(frame_right, text="Download Report", bg="#2E2E2E", fg="white",
                            command=lambda: save_report(report_text))
download_button.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

# Drop zone 1
drop_zone_1 = DropZone(frame_drop_zones, text="Energy Manager File", report_text=report_text)
drop_zone_1.pack(fill=tk.BOTH, expand=True)

# Drop zone 2
drop_zone_2 = DropZone(frame_drop_zones, text="Bill Excel (monthly)", report_text=report_text)
drop_zone_2.pack(fill=tk.BOTH, expand=True)

root.mainloop()
