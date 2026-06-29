import os
import shutil
from pathlib import Path
import customtkinter as ctk
from customtkinter import filedialog
from tkinter.colorchooser import askcolor
# Set the global theme to Dark
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# The Master Map for the Organizer
EXTENSION_MAP = {
    "Images": ['.jpg', '.jpeg', '.png', '.gif', '.svg'],
    "Documents": ['.pdf', '.docx', '.txt', '.xlsx', '.csv'],
    "Code": ['.py', '.c', '.cpp', '.java', '.css', '.html', '.js'],
    "Archives": ['.zip', '.tar', '.gz', '.rar'],
    "Audio": ['.mp3', '.wav', '.flac']
}

class FileUtilityApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup & Translucency ---
        self.title("File Management Utility")
        self.geometry("700x650")
        
        

        # --- Application State ---
        self.target_dir = ""
        self.pending_moves = []
        self.history_log = []
        self.merge_files_list = []

        # --- UI Layout ---
        self.setup_settings_bar()

        # Main Tabview
        self.tabview = ctk.CTkTabview(self, width=650, height=350)
        self.tabview.pack(padx=20, pady=10)
        self.tabview.add("Organizer Mode")
        self.tabview.add("Merger Mode")

        self.setup_organizer_tab()
        self.setup_merger_tab()
        self.setup_history_panel()

    def setup_settings_bar(self):
        # Create a transparent frame at the very top of the app
        self.settings_frame = ctk.CTkFrame(self, height=40, fg_color="transparent")
        self.settings_frame.pack(padx=20, pady=(10, 0), fill="x")

        # 1. The Light/Dark Mode Toggle
        self.mode_switch = ctk.CTkSwitch(
            self.settings_frame, 
            text="Dark Mode", 
            command=self.toggle_mode
        )
        self.mode_switch.pack(side="left", padx=10)
        self.mode_switch.select() # Default to dark mode

        # 2. The Interactive Color Picker Button
        self.btn_color_picker = ctk.CTkButton(
            self.settings_frame, 
            text="🎨 Pick Theme Color", 
            command=self.choose_color,
            fg_color="gray25", hover_color="gray15"
        )
        self.btn_color_picker.pack(side="left", padx=40)
    def setup_organizer_tab(self):
        tab = self.tabview.tab("Organizer Mode")
        
        self.lbl_dir = ctk.CTkLabel(tab, text="No directory selected.", text_color="gray")
        self.lbl_dir.pack(pady=5)
        
        self.btn_browse = ctk.CTkButton(tab, text="Select Directory to Scan", command=self.select_directory)
        self.btn_browse.pack(pady=5)

        self.txt_dry_run = ctk.CTkTextbox(tab, width=600, height=150)
        self.txt_dry_run.pack(pady=10)
        self.txt_dry_run.insert("0.0", "Workspace is empty. Select a directory to begin.")

        # Action Buttons
        self.btn_dry_run = ctk.CTkButton(tab, text="Run Dry Run", command=self.run_dry_run, state="disabled")
        self.btn_dry_run.pack(side="left", padx=50, pady=10)

        self.btn_confirm = ctk.CTkButton(tab, text="Confirm Actions", command=self.confirm_actions, fg_color="green", hover_color="darkgreen", state="disabled")
        self.btn_confirm.pack(side="right", padx=50, pady=10)

    def setup_merger_tab(self):
        tab = self.tabview.tab("Merger Mode")

        self.lbl_merge_files = ctk.CTkLabel(tab, text="No files selected.", text_color="gray")
        self.lbl_merge_files.pack(pady=10)

        self.btn_select_files = ctk.CTkButton(tab, text="Select Files to Merge (Text/Code/CSV)", command=self.select_merge_files)
        self.btn_select_files.pack(pady=5)

        self.entry_merge_name = ctk.CTkEntry(tab, placeholder_text="Output filename (e.g. merged.txt)", width=300)
        self.entry_merge_name.pack(pady=20)

        self.btn_merge = ctk.CTkButton(tab, text="Merge Selected Files", command=self.merge_files, state="disabled")
        self.btn_merge.pack(pady=10)

    def setup_history_panel(self):
        # History Frame at the bottom
        history_frame = ctk.CTkFrame(self, width=650, height=180)
        history_frame.pack(padx=20, pady=10, fill="both", expand=True)

        lbl_hist = ctk.CTkLabel(history_frame, text="Action History Log", font=("Arial", 14, "bold"))
        lbl_hist.pack(anchor="w", padx=10, pady=5)

        self.txt_history = ctk.CTkTextbox(history_frame, width=500, height=100)
        self.txt_history.pack(side="left", padx=10, pady=5, fill="both", expand=True)

        self.btn_undo = ctk.CTkButton(history_frame, text="Undo Last Action", command=self.undo_last_action, fg_color="darkred", hover_color="red")
        self.btn_undo.pack(side="right", padx=10, pady=5)

    # --- Settings Logic ---

    def toggle_mode(self):
        """Switches the entire app between dark and light mode."""
        if self.mode_switch.get() == 1:
            ctk.set_appearance_mode("dark")
            self.attributes('-alpha', 0.90) 
        else:
            ctk.set_appearance_mode("light")
            self.attributes('-alpha', 0.95) 

    def choose_color(self):
        """Opens a color wheel dialog and updates the app theme."""
        # askcolor() opens the wheel and returns a tuple: ((R, G, B), '#HexCode')
        color = askcolor(title="Choose Theme Color")
        
        # color[1] holds the hex code. It returns None if the user clicks "Cancel"
        new_color = color[1] 
        
        if new_color:
            try:
                # Update main buttons
                self.btn_browse.configure(fg_color=new_color)
                self.btn_dry_run.configure(fg_color=new_color)
                self.btn_select_files.configure(fg_color=new_color)
                self.btn_merge.configure(fg_color=new_color)
                
                # Update tabview active color
                self.tabview.configure(segmented_button_selected_color=new_color)
                
                self.log_to_ui(f"[Settings] Theme color updated to {new_color}")
            except Exception as e:
                self.log_to_ui(f"[Error] Could not apply color: {e}")

    # --- Organizer Logic ---

    def select_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.target_dir = Path(folder)
            self.lbl_dir.configure(text=f"Selected: {self.target_dir}")
            self.btn_dry_run.configure(state="normal")
            self.txt_dry_run.delete("0.0", "end")
            self.txt_dry_run.insert("0.0", f"Directory mapped: {self.target_dir.name}. Ready for Dry Run.")

    def run_dry_run(self):
        if not self.target_dir: return

        self.pending_moves.clear()
        self.txt_dry_run.delete("0.0", "end")
        
        # Build reverse map
        ext_to_folder = {ext: folder for folder, exts in EXTENSION_MAP.items() for ext in exts}
        
        summary = {key: 0 for key in EXTENSION_MAP.keys()}

        for item in self.target_dir.iterdir():
            if item.is_file():
                folder_name = ext_to_folder.get(item.suffix.lower())
                if folder_name:
                    dest = self.target_dir / folder_name / item.name
                    self.pending_moves.append((str(item), str(dest)))
                    summary[folder_name] += 1

        if self.pending_moves:
            log_text = "DRY RUN SUMMARY:\n\n"
            for folder, count in summary.items():
                if count > 0:
                    log_text += f"- Moving {count} files to {folder}\n"
            log_text += "\nReady to confirm actions."
            self.txt_dry_run.insert("0.0", log_text)
            self.btn_confirm.configure(state="normal")
        else:
            self.txt_dry_run.insert("0.0", "No matching files found to organize.")

    def confirm_actions(self):
        if not self.pending_moves: return

        completed_moves = []
        for src, dest in self.pending_moves:
            Path(dest).parent.mkdir(exist_ok=True)
            if not Path(dest).exists():
                shutil.move(src, dest)
                completed_moves.append({"src": src, "dest": dest})

        # Update History State
        action_record = {"type": "organize", "moves": completed_moves}
        self.history_log.append(action_record)
        self.log_to_ui(f"[Organize] Moved {len(completed_moves)} files successfully.")

        # Reset Organizer State
        self.pending_moves.clear()
        self.btn_confirm.configure(state="disabled")
        self.txt_dry_run.delete("0.0", "end")
        self.txt_dry_run.insert("0.0", "Actions confirmed and executed.")

    # --- Merger Logic ---

    def select_merge_files(self):
        files = filedialog.askopenfilenames(title="Select files to merge")
        if files:
            self.merge_files_list = files
            self.lbl_merge_files.configure(text=f"{len(files)} files selected.")
            self.btn_merge.configure(state="normal")

    def merge_files(self):
        if not self.merge_files_list: return
        output_name = self.entry_merge_name.get().strip() or "merged_output.txt"
        
        target_dir = Path(self.merge_files_list[0]).parent
        output_path = target_dir / output_name

        try:
            with open(output_path, 'w', encoding='utf-8') as outfile:
                for file_path in self.merge_files_list:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(f"\n--- Data from {Path(file_path).name} ---\n")
                        outfile.write(infile.read() + "\n")
            
            self.history_log.append({"type": "merge", "output": str(output_path)})
            self.log_to_ui(f"[Merge] Created {output_name} successfully.")
            
            # Reset Merger state
            self.merge_files_list.clear()
            self.lbl_merge_files.configure(text="No files selected.")
            self.entry_merge_name.delete(0, "end")
            self.btn_merge.configure(state="disabled")

        except Exception as e:
            self.log_to_ui(f"[Error] Failed to merge: {e}")

    # --- Global Undo Logic ---

    def undo_last_action(self):
        if not self.history_log:
            self.log_to_ui("No actions to undo.")
            return

        last_action = self.history_log.pop()

        if last_action["type"] == "organize":
            restored = 0
            for move in last_action["moves"]:
                if Path(move["dest"]).exists():
                    shutil.move(move["dest"], move["src"])
                    restored += 1
            self.log_to_ui(f"[Undo] Restored {restored} files to original locations.")

        elif last_action["type"] == "merge":
            output_file = Path(last_action["output"])
            if output_file.exists():
                output_file.unlink()
                self.log_to_ui(f"[Undo] Deleted merged file: {output_file.name}")

    def log_to_ui(self, message):
        self.txt_history.insert("end", message + "\n")
        self.txt_history.see("end")

if __name__ == "__main__":
    app = FileUtilityApp()
    app.mainloop()