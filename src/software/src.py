import customtkinter as ctk
from tkinter import filedialog

class DropZone(ctk.CTkLabel):
    def __init__(self, master, text=""):
        super().__init__(master, text=text)
        self.configure(fg_color="#333", text_color="black", corner_radius=10)  # Removed border_width
        self.filename = None
        self.bind("<ButtonPress-1>", self.open_explorer)
        self.bind("<Enter>", self.enter_zone)
        self.bind("<Leave>", self.leave_zone)

    def open_explorer(self, event):
        self.filename = filedialog.askopenfilename()
        if self.filename:
            self.configure(text=self.filename.split("/")[-1])

    def enter_zone(self, event):
        self.configure(fg_color="#555")

    def leave_zone(self, event):
        self.configure(fg_color="#333")

class FileDropApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EM Checker")

        # Configure grid layout for the main application
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create frames with grid layout
        self.left_frame = ctk.CTkFrame(self, fg_color="#222")
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.right_frame = ctk.CTkFrame(self, fg_color="#222")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # Configure frames to expand vertically
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)

        # Create widgets in the left frame
        self.top_label = ctk.CTkLabel(self.left_frame, text="Drag and drop files here", text_color="gray", font=("Arial", 12), fg_color="#222")
        self.top_label.pack(pady=10)

        self.drop_zones = []
        for i in range(2):
            zone = DropZone(self.left_frame, f"Drop Zone {i + 1}")
            zone.pack(fill=ctk.BOTH, pady=20, expand=True)
            self.drop_zones.append(zone)

        # Create widgets in the right frame
        self.report_label = ctk.CTkLabel(self.right_frame, text="Report\n[Placeholder for report content]", text_color="gray", justify="left")
        self.report_label.pack(fill=ctk.BOTH, expand=True)

        self.download_button = ctk.CTkButton(self.right_frame, text="Download Report", text_color="black", fg_color="#333")
        self.download_button.pack(pady=10)

    def update_info(self):
        report_text = "Report content...\n"
        if all(zone.filename for zone in self.drop_zones):
            report_text += f"Files Dropped:\n  - {self.drop_zones[0].filename}\n  - {self.drop_zones[1].filename}"
        self.report_label.configure(text=report_text)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Change to "light" if you want light mode
    app = FileDropApp()
    app.after(100, app.update_info)
    app.mainloop()
