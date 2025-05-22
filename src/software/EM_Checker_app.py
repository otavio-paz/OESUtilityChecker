import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD #Drag and drop support
import pandas as pd
import os


class DropZone(tk.Label):
    def __init__(self, master, label, report_text, filetype_key, file_store, on_files_ready):
        # Initialize the label widget with styling
        super().__init__(master, text=label, bg="#2E2E2E", fg="white", borderwidth=1, relief="solid", pady=12)
        # Enable drag-and-drop of files
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.on_drop)
       
        # Store parameters
        self.report_text = report_text
        self.filetype_key = filetype_key
        self.file_store = file_store
        self.on_files_ready = on_files_ready

         # Add a 'Browse' button for manual file selection
        self.browse_button = tk.Button(self, text="Browse", bg="#1E1E1E", fg="white", command=self.on_browse)
        self.browse_button.pack(side=tk.BOTTOM, pady=5)

    def on_file_received(self, filename):
        """
        This function handle a file once dropped or selected. 
        It validates that the path exists, updates UI and triggers validation if both files are present.

        Input: filename (str) - the path of the file

        Output: None
        """
        # Check if the file exists
        if not os.path.isfile(filename):
            self.report_text.insert(tk.END, f"Invalid file: {filename}\n")
            return
        # Store filename under corresponding key
        self.file_store[self.filetype_key] = filename
        self.config(text=f"{self.filetype_key} file loaded: {os.path.basename(filename)}") # Update label to show loaded file
        # Log to report
        self.report_text.insert(tk.END, f"{self.filetype_key} file loaded: {filename}\n")
        
        # If both EM and bill files are loaded, trigger validation callback
        if self.file_store.get("em_file") and self.file_store.get("bill_file"):
            self.on_files_ready(self.file_store["em_file"], self.file_store["bill_file"], self.report_text)

    def on_drop(self, event):
        """
        This function is an event handler for drag-and-drop. Strips braces from filename and processes it.
        """
        filename = event.data.strip('{}')  # Handle filenames with spaces
        self.on_file_received(filename)

    def on_browse(self):
        """
        THis function is an handler for the Browse button. Opens file dialog and processes selected file.
        """
        filename = filedialog.askopenfilename()
        if filename:
            self.on_file_received(filename)


def validate_files(em_file, bill_file, report_text):
    """
    This function validates that entries in the bill spreadsheet match corresponding entries in the Energy Manager (EM) export.
    Logs validation progress and results to report_text widget.
    """
    report_text.insert(tk.END, "\n=== Running Validation ===\n")

    try:
        # Read in the data
        df_bill = pd.read_excel(bill_file, dtype={'ACCT#': str})
        df_em = pd.read_csv(em_file, dtype={'Account Number': str})

        # Standardize column names (strip whitespace)
        df_bill.columns = df_bill.columns.str.strip()
        df_em.columns = df_em.columns.str.strip()

        # Mapping of bill columns -> (EM Line Item Type Name, EM column to compare)
        utilities = {
            # usage columns
            'H20-CFT':         ('Water-Usage (CF)',      'Line Item Usage'),
            'KWH':             ('Electric-Usage (KWH)',  'Line Item Usage'),
            # cost columns
            'WATER$ 7304':     ('Water-Usage (CF)',      'Line Item Cost'),
            'SEWER$ 7305':     ('Sewer-Usage (CF)',      'Line Item Cost'),
            'TRASH$ 7207':     ('Trash (City Charges)',  'Line Item Cost'),
            'ELECTRIC$ 7303':  ('Electric-Usage (KWH)',  'Line Item Cost'),
            'DEMAND':          ('Demand',                'Line Item Cost'),
        }
        
        errors = [] # to collect error messages
        results = {} # to collect per-account pass/fail

        # Iterate through each account in the bill (assumed unique, at least for bill)
        for idx, bill_row in df_bill.iterrows():
            acct = bill_row['ACCT#']

            # Skip if account number is NaN or "* CPO * ACCT#"
            if pd.isna(acct) or acct.strip() == "* CPO * ACCT#":
                continue
            
            # Filter EM rows for this account
            acct_errors = []
            em_acct = df_em[df_em['Account Number'] == acct]
            if em_acct.empty:
                acct_errors.append(f"Account {acct}: not found in Energy Manager file.")
                results[acct] = False
                errors.extend(acct_errors)
                continue
            
            # Check each utility column
            for bill_col, (em_type, em_col) in utilities.items():
                bill_val = bill_row.get(bill_col, None)
                 # Handle missing bill data: assume that they wont be data in EM
                if pd.isna(bill_val) or bill_val == ' ' or bill_val == '':
                    continue
                
                # Filter EM rows further by Line Item Type Name
                em_rows = em_acct[em_acct['Line Item Type Name'].str.strip() == em_type]
                if em_rows.empty and bill_val != 0:
                    acct_errors.append(f"Account {acct}, '{bill_col}': EM missing rows with type '{em_type}'.")
                    continue
                
                # Gather all EM values for this utility
                em_vals = []
                for raw in em_rows[em_col]:
                    try:
                        em_vals.append(float(raw))
                    except (TypeError, ValueError):
                        em_vals.append(str(raw).strip())

                # Convert the bill value for comparison
                try:
                    bill_num = float(bill_val)
                    compare_as_number = True
                except (TypeError, ValueError):
                    bill_num = str(bill_val).strip()
                    compare_as_number = False

                # Check if any EM value matches the bill value exactly
                match_found = any(
                    (bill_num == v if compare_as_number else bill_num == str(v).strip())
                    for v in em_vals
                )

                if not match_found and bill_num != 0:
                    acct_errors.append(f"Account {acct}, '{bill_col}': bill={bill_num} not in EM values {em_vals}")
            
            # Record result for this account
            if acct_errors:
                results[acct] = False
                errors.extend(acct_errors)
            else:
                results[acct] = True
        
         # Output summary and details
        report_text.insert(tk.END, "\n=== VALIDATION SUMMARY ===\n")
        for acct, ok in results.items():
            status = "OK" if ok else "ERROR"

            # Attempt to get the address for this account
            address = df_bill[df_bill['ACCT#'] == acct].iloc[0, 1] if not df_bill[df_bill['ACCT#'] == acct].empty else "Address not found"
            report_text.insert(tk.END, f"Account {acct} | Address: {address} | Status: {status}\n")
        report_text.insert(tk.END, "\n=== DETAILS ===\n")
        if errors:
            for e in errors:
                report_text.insert(tk.END, f" - {e}\n")
        else:
            report_text.insert(tk.END, "All accounts validated successfully!\n")

    except Exception as e:
        # Log any unexpected errors
        report_text.insert(tk.END, f"Error while processing files: {str(e)}\n")


def save_report(report_text):
    """
    This function prompts user to save the current report to a text file.
    """
    
    filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if filename:
        with open(filename, "w") as file:
            file.write(report_text.get("1.0", tk.END))


# GUI Setup
root = TkinterDnD.Tk()
root.title("EM Checker")
root.config(bg="#1E1E1E")

# Center window on screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = screen_width // 2
center_y = screen_height // 2
root.geometry(f"{screen_width}x{screen_height}+{center_x - screen_width // 2}+{center_y - screen_height // 2}")

# Layout frames for drop zones and report
frame_left = tk.Frame(root, bg="#1E1E1E")
frame_left.place(relx=0, rely=0, relwidth=0.5, relheight=1)
frame_right = tk.Frame(root, bg="#1E1E1E")
frame_right.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

# Widgets for report and save button
frame_drop_zones = tk.Frame(frame_left, bg="#1E1E1E")
frame_drop_zones.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

report_label = tk.Label(frame_right, text="Report content", bg="#1E1E1E", fg="white")
report_label.pack(side=tk.TOP, pady=10, fill=tk.X)

report_text = tk.Text(frame_right, bg="#2E2E2E", fg="white")
report_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

download_button = tk.Button(frame_right, text="Download Report", bg="#2E2E2E", fg="white",
                            command=lambda: save_report(report_text))
download_button.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

file_store = {}

# Drop zones
drop_zone_1 = DropZone(frame_drop_zones, "Energy Manager (bill Export.csv)", report_text, "em_file", file_store, validate_files)
drop_zone_1.pack(fill=tk.BOTH, expand=True)

drop_zone_2 = DropZone(frame_drop_zones, "Bill Spreadsheet", report_text, "bill_file", file_store, validate_files)
drop_zone_2.pack(fill=tk.BOTH, expand=True)

# Start application loop
root.mainloop()