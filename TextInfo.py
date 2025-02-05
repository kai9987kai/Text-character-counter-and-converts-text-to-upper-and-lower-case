import socket
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import threading
import os
import json
import time
import pyperclip  # For clipboard functionality

class TextAnalyzerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Text Analyzer")
        self.master.minsize(600, 500)
        self.master.attributes("-topmost", True)
        try:
            self.master.iconbitmap('favicon.ico')
        except Exception:
            pass

        # Set default theme and initialize status variable early
        self.current_theme = "light"
        self.status_var = tk.StringVar(value="Ready")

        # Setup ttk style for modern look
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.set_theme(self.current_theme)

        # Main container frame (auto-adjusting)
        self.container = ttk.Frame(master, padding=10)
        self.container.grid(row=0, column=0, sticky="nsew")
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        self.create_top_section()
        self.create_input_section()
        self.create_output_section()
        self.create_history_and_favorites_section()
        self.create_bottom_section()
        self.create_status_bar()
        self.create_menu()

        # Schedule auto-refresh (if implemented later)
        self.auto_refresh_enabled = tk.BooleanVar(value=False)
        self.refresh_interval = 10000  # milliseconds
        self.master.after(self.refresh_interval, self.check_auto_refresh)

    def set_theme(self, theme):
        if theme == "light":
            bg = "#F5F5F5"
            fg = "#000000"
            status_bg = "#DDDDDD"
        else:
            bg = "#333333"
            fg = "#F5F5F5"
            status_bg = "#555555"
        self.master.configure(background=bg)
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg, font=("Helvetica", 12))
        self.style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), background=bg, foreground=fg)
        self.style.configure("TButton", font=("Helvetica", 12))
        self.style.configure("TEntry", font=("Helvetica", 12, "bold"))
        # Update status variable if already created
        if hasattr(self, 'status_var'):
            self.status_var.set(f"{theme.title()} theme enabled")

    def create_top_section(self):
        top_frame = ttk.Frame(self.container)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_frame.columnconfigure(1, weight=1)

        # Emoji logo as a modern logo
        self.logo_label = ttk.Label(top_frame, text="💬", font=("Helvetica", 48))
        self.logo_label.grid(row=0, column=0, padx=5)

        # Title label
        self.title_label = ttk.Label(top_frame, text="Text Analyzer", style="Header.TLabel")
        self.title_label.grid(row=0, column=1, sticky="w", padx=5)

        # Theme toggle button
        self.theme_btn = ttk.Button(top_frame, text="Toggle Theme", command=self.toggle_theme)
        self.theme_btn.grid(row=0, column=2, padx=5)

    def create_input_section(self):
        input_frame = ttk.Frame(self.container)
        input_frame.grid(row=1, column=0, sticky="ew", pady=5)
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Enter Text:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.text_entry = ttk.Entry(input_frame)
        self.text_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.clear_input_btn = ttk.Button(input_frame, text="Clear Input", command=lambda: self.text_entry.delete(0, tk.END))
        self.clear_input_btn.grid(row=0, column=2, padx=5, pady=5)

        # Process button
        self.process_btn = ttk.Button(input_frame, text="Process Text", command=self.threaded_process)
        self.process_btn.grid(row=1, column=0, columnspan=3, pady=10)

        # Progress bar for processing indication
        self.progress = ttk.Progressbar(input_frame, orient="horizontal", mode="indeterminate")
        self.progress.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

    def create_output_section(self):
        # Notebook for Conversion and Analysis results
        self.notebook = ttk.Notebook(self.container)
        self.notebook.grid(row=2, column=0, sticky="nsew", pady=5)
        
        # Conversions tab
        self.conv_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.conv_frame, text="Conversions")
        self.conv_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.conv_frame, text="Original:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.orig_label = ttk.Label(self.conv_frame, text="")
        self.orig_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.conv_frame, text="Lower Case:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.lower_label = ttk.Label(self.conv_frame, text="")
        self.lower_label.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.conv_frame, text="Upper Case:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.upper_label = ttk.Label(self.conv_frame, text="")
        self.upper_label.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.conv_frame, text="Title Case:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.titlecase_label = ttk.Label(self.conv_frame, text="")
        self.titlecase_label.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.conv_frame, text="Reversed Text:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.reversed_label = ttk.Label(self.conv_frame, text="")
        self.reversed_label.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        self.copy_conv_btn = ttk.Button(self.conv_frame, text="Copy Conversions", command=self.copy_conversions)
        self.copy_conv_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Analysis tab
        self.analysis_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.analysis_frame, text="Analysis")
        self.analysis_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.analysis_frame, text="Letter Count:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.letter_count_label = ttk.Label(self.analysis_frame, text="")
        self.letter_count_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.analysis_frame, text="Word Count:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.word_count_label = ttk.Label(self.analysis_frame, text="")
        self.word_count_label.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.analysis_frame, text="Sentence Count:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.sentence_count_label = ttk.Label(self.analysis_frame, text="")
        self.sentence_count_label.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.analysis_frame, text="Vowel Count:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.vowel_count_label = ttk.Label(self.analysis_frame, text="")
        self.vowel_count_label.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.analysis_frame, text="Consonant Count:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.consonant_count_label = ttk.Label(self.analysis_frame, text="")
        self.consonant_count_label.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        self.clear_output_btn = ttk.Button(self.container, text="Clear Output", command=self.clear_output)
        self.clear_output_btn.grid(row=3, column=0, pady=10)

    def create_history_and_favorites_section(self):
        mid_frame = ttk.Frame(self.container)
        mid_frame.grid(row=4, column=0, sticky="nsew", pady=5)
        mid_frame.columnconfigure(0, weight=1)
        mid_frame.columnconfigure(1, weight=1)
        
        # History
        self.history_frame = ttk.Labelframe(mid_frame, text="Search History", padding=5)
        self.history_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.history_frame.columnconfigure(0, weight=1)
        self.history_listbox = tk.Listbox(self.history_frame, font=("Helvetica", 12))
        self.history_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.history_scroll = ttk.Scrollbar(self.history_frame, orient="vertical", command=self.history_listbox.yview)
        self.history_scroll.grid(row=0, column=1, sticky="ns", padx=5, pady=5)
        self.history_listbox.config(yscrollcommand=self.history_scroll.set)
        self.history_listbox.bind("<Double-Button-1>", self.on_history_double_click)
        self.load_history()
        self.clear_history_btn = ttk.Button(self.history_frame, text="Clear History", command=self.clear_history)
        self.clear_history_btn.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Favorites
        self.fav_frame = ttk.Labelframe(mid_frame, text="Favorites", padding=5)
        self.fav_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.fav_frame.columnconfigure(0, weight=1)
        self.fav_listbox = tk.Listbox(self.fav_frame, font=("Helvetica", 12))
        self.fav_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.fav_scroll = ttk.Scrollbar(self.fav_frame, orient="vertical", command=self.fav_listbox.yview)
        self.fav_scroll.grid(row=0, column=1, sticky="ns", padx=5, pady=5)
        self.fav_listbox.config(yscrollcommand=self.fav_scroll.set)
        self.fav_listbox.bind("<Double-Button-1>", self.on_fav_double_click)
        self.load_favorites()
        self.add_fav_btn = ttk.Button(self.fav_frame, text="Add to Favorites", command=self.add_favorite)
        self.add_fav_btn.grid(row=1, column=0, columnspan=2, pady=5)
        self.clear_fav_btn = ttk.Button(self.fav_frame, text="Clear Favorites", command=self.clear_favorites)
        self.clear_fav_btn.grid(row=2, column=0, columnspan=2, pady=5)

    def create_bottom_section(self):
        bottom_frame = ttk.Frame(self.container)
        bottom_frame.grid(row=5, column=0, sticky="ew", pady=10)
        bottom_frame.columnconfigure(0, weight=1)
        self.adv_options_btn = ttk.Button(bottom_frame, text="Advanced Options", command=self.open_advanced_options)
        self.adv_options_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    def create_status_bar(self):
        self.status_bar = ttk.Label(self.master, textvariable=self.status_var, relief="sunken", anchor="w", font=("Helvetica", 10))
        self.status_bar.grid(row=6, column=0, sticky="ew")

    def create_menu(self):
        self.menu = tk.Menu(self.master)
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="About", command=self.show_about)
        file_menu.add_command(label="Exit", command=self.master.destroy)
        self.menu.add_cascade(label="File", menu=file_menu)
        help_menu = tk.Menu(self.menu, tearoff=0)
        help_menu.add_command(label="Contact", command=lambda: messagebox.showinfo("Contact", "Email: your_email@example.com"))
        self.menu.add_cascade(label="Help", menu=help_menu)
        self.master.config(menu=self.menu)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.set_theme(self.current_theme)

    def threaded_process(self):
        threading.Thread(target=self.process_text, daemon=True).start()

    def process_text(self):
        self.set_status("Processing text...")
        self.progress.start(10)
        phrase = self.text_entry.get()
        if not phrase:
            messagebox.showerror("Input Error", "Please enter some text.")
            self.progress.stop()
            self.set_status("Ready")
            return
        # Conversions
        self.orig_label.config(text=phrase)
        self.lower_label.config(text=phrase.lower())
        self.upper_label.config(text=phrase.upper())
        self.titlecase_label.config(text=phrase.title())
        self.reversed_label.config(text=phrase[::-1])
        # Analysis
        self.letter_count_label.config(text=str(len(phrase)))
        words = phrase.split()
        self.word_count_label.config(text=str(len(words)))
        sentences = [s for s in phrase.replace("!",".").replace("?",".").split(".") if s.strip()]
        self.sentence_count_label.config(text=str(len(sentences)))
        vowels = sum(1 for char in phrase.lower() if char in "aeiou")
        self.vowel_count_label.config(text=str(vowels))
        consonants = sum(1 for char in phrase.lower() if char.isalpha() and char not in "aeiou")
        self.consonant_count_label.config(text=str(consonants))
        self.add_history(phrase)
        self.progress.stop()
        self.set_status("Text processed successfully")

    def copy_conversions(self):
        text = (f"Original: {self.orig_label.cget('text')}\n"
                f"Lower Case: {self.lower_label.cget('text')}\n"
                f"Upper Case: {self.upper_label.cget('text')}\n"
                f"Title Case: {self.titlecase_label.cget('text')}\n"
                f"Reversed: {self.reversed_label.cget('text')}\n")
        pyperclip.copy(text)
        self.set_status("Conversion data copied to clipboard")

    def clear_output(self):
        self.orig_label.config(text="")
        self.lower_label.config(text="")
        self.upper_label.config(text="")
        self.titlecase_label.config(text="")
        self.reversed_label.config(text="")
        self.letter_count_label.config(text="")
        self.word_count_label.config(text="")
        self.sentence_count_label.config(text="")
        self.vowel_count_label.config(text="")
        self.consonant_count_label.config(text="")
        self.set_status("Output cleared")

    def show_about(self):
        about_text = (
            "Text Analyzer v2.0\nDeveloped by Kai Piper\n\n"
            "Advanced text conversion and analysis tool.\n"
            "Features include: case conversion, letter/word/sentence/vowel/consonant counts,\n"
            "reverse text, favorites management, and more."
        )
        messagebox.showinfo("About", about_text)

    def set_status(self, text):
        self.status_var.set(text)

    # History functions
    def get_history(self):
        if os.path.exists("history.txt"):
            try:
                with open("history.txt", "r") as f:
                    return f.read().splitlines()
            except Exception:
                return []
        return []

    def save_history(self, history):
        try:
            with open("history.txt", "w") as f:
                f.write("\n".join(history))
        except Exception as e:
            print("Error saving history:", e)

    def add_history(self, query):
        history = self.get_history()
        if query not in history:
            history.insert(0, query)
            history = history[:10]
            self.save_history(history)
            self.load_history()

    def load_history(self):
        history = self.get_history()
        self.history_listbox.delete(0, tk.END)
        for item in history:
            self.history_listbox.insert(tk.END, item)

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear history?"):
            if os.path.exists("history.txt"):
                os.remove("history.txt")
            self.load_history()
            self.set_status("History cleared")

    def on_history_double_click(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            text = self.history_listbox.get(selection[0])
            self.text_entry.delete(0, tk.END)
            self.text_entry.insert(0, text)

    # Favorites functions
    def get_favorites(self):
        if os.path.exists("favorites.txt"):
            try:
                with open("favorites.txt", "r") as f:
                    return f.read().splitlines()
            except Exception:
                return []
        return []

    def save_favorites(self, favs):
        try:
            with open("favorites.txt", "w") as f:
                f.write("\n".join(favs))
        except Exception as e:
            print("Error saving favorites:", e)

    def add_favorite(self):
        text = self.text_entry.get().strip()
        if text:
            favs = self.get_favorites()
            if text not in favs:
                favs.insert(0, text)
                favs = favs[:10]
                self.save_favorites(favs)
                self.load_favorites()
                self.set_status("Added to favorites")
            else:
                self.set_status("Already in favorites")
        else:
            messagebox.showerror("Input Error", "Enter text to add as favorite.")

    def load_favorites(self):
        favs = self.get_favorites()
        self.fav_listbox.delete(0, tk.END)
        for fav in favs:
            self.fav_listbox.insert(tk.END, fav)

    def clear_favorites(self):
        if messagebox.askyesno("Clear Favorites", "Are you sure you want to clear favorites?"):
            if os.path.exists("favorites.txt"):
                os.remove("favorites.txt")
            self.load_favorites()
            self.set_status("Favorites cleared")

    def on_fav_double_click(self, event):
        selection = self.fav_listbox.curselection()
        if selection:
            fav = self.fav_listbox.get(selection[0])
            self.text_entry.delete(0, tk.END)
            self.text_entry.insert(0, fav)

    # Advanced Options dialog with Ping and Auto Refresh
    def open_advanced_options(self):
        adv_win = tk.Toplevel(self.master)
        adv_win.title("Advanced Options")
        adv_win.transient(self.master)
        adv_win.grab_set()
        adv_win.resizable(False, False)
        adv_win.geometry("")
        
        ttk.Label(adv_win, text="Advanced Options", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        # Ping Domain button
        ttk.Button(adv_win, text="Ping Domain", command=self.ping_domain).grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.ping_result = ttk.Label(adv_win, text="Ping: N/A", font=("Helvetica", 12))
        self.ping_result.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        # Auto Refresh option
        self.auto_refresh_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_win, text="Auto Refresh Analysis", variable=self.auto_refresh_enabled).grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        # Favorite Option
        ttk.Button(adv_win, text="Add Text to Favorites", command=self.add_favorite).grid(row=3, column=0, columnspan=2, padx=10, pady=5)
        ttk.Button(adv_win, text="Close", command=adv_win.destroy).grid(row=4, column=0, columnspan=2, pady=10)

    def ping_domain(self):
        text = self.text_entry.get().strip()
        if not text:
            messagebox.showerror("Input Error", "Enter text to ping (using first word as domain).")
            return
        try:
            domain = text.split()[0]
            start = time.time()
            socket.gethostbyname(domain)
            elapsed = (time.time() - start) * 1000
            self.ping_result.config(text=f"Ping: {int(elapsed)} ms")
            self.set_status("Ping successful")
        except Exception as e:
            messagebox.showerror("Ping Error", f"Error: {str(e)}")
            self.ping_result.config(text="Ping: Error")
    
    def check_auto_refresh(self):
        if self.auto_refresh_enabled.get():
            self.threaded_process()
        self.master.after(self.refresh_interval, self.check_auto_refresh)
    
    def threaded_process(self):
        threading.Thread(target=self.process_text, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = TextAnalyzerApp(root)
    root.mainloop()
