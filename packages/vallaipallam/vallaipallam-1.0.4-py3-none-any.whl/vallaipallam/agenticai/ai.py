import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import csv, os, uuid
from datetime import datetime
import re 
import vallaipallam.agenticai.main 

# --- CONFIGURATION ---
HISTORY_FILE = "chat_history.csv"
AGENT_NAME = "Agent Vallai (v1.0)" # New Agent Name/Version
BG_DARK = "#1e1e1e"     
BG_MEDIUM = "#2d2d2d"   
BG_LIGHT_USER = "#3a3a3a" # Light shade for user input/chat bubble
FG_WHITE = "white"
ACCENT_USER = "#00afff" 
ACCENT_AGENT = "#ffcc00" 
ACCENT_CODE = "#94e45c" 
FONT_MAIN = "Segoe UI"
FONT_CODE = "Consolas"

# Ensure CSV exists
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["session_id", "timestamp", "role", "message"])

# --- Main App ---
class AgentVallaiApp:
    """The main application window using pure Tkinter and ttk."""
    
    def __init__(self, root, workingdir, apikey):
        # --- Application Variables ---
        self.root = root
        self.working_dir = workingdir
        self.apikey = apikey
        self.session_id = str(uuid.uuid4())
        self.current_chat = []          
        self.gemini_chat_history = []   
        
        # --- Window Setup ---
        self.root.title("🍌 AGENT VALLAI - Code Interpreter")
        self.root.geometry("1200x800")
        self.root.configure(bg=BG_DARK)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "logo.png")
            icon_img = tk.PhotoImage(file=icon_path)
            root.iconphoto(False, icon_img)
        except Exception as e:
            print("⚠️ Could not set icon:", e)
        # --- Apply Modern ttk Theme ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure general button style
        self.style.configure("TButton", 
                        font=(FONT_MAIN, 11, "bold"), 
                        padding=6,
                        background=BG_MEDIUM, 
                        foreground=FG_WHITE,
                        bordercolor=BG_DARK)
        self.style.map("TButton", 
                  background=[('active', BG_DARK)], 
                  foreground=[('active', ACCENT_USER)])

        # --- Create Widgets ---
        self._create_sidebar()
        self._create_main_frame()
        self._create_status_bar()
        self.load_chat_sessions()
        
        # Initial welcome message
        self.display_message(
            "🍌 AGENT VALLAI", 
            f"Welcome, Agent is active in directory: {self.working_dir}\nAsk your query."
        )

    # ==================================
    # === UI STRUCTURE METHODS (Tkinter) ===
    # ==================================
    
    def _create_sidebar(self):
        """Creates the left sidebar for chat history and controls."""
        self.sidebar_frame = tk.Frame(self.root, bg=BG_MEDIUM, width=250)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_propagate(False) 
        
        # Sidebar Title
        tk.Label(
            self.sidebar_frame, text="Chat History", font=(FONT_MAIN, 18, "bold"),
            bg=BG_MEDIUM, fg=FG_WHITE
        ).pack(pady=(20, 10))

        # New Chat Button (using custom style defined below)
        ttk.Button(
            self.sidebar_frame, text="✨ New Chat", command=self.new_chat, 
            style="Accent.TButton" 
        ).pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Custom Accent Button Style
        self.style.configure("Accent.TButton", 
                        background=ACCENT_AGENT, 
                        foreground=BG_DARK,
                        bordercolor=ACCENT_AGENT)
        self.style.map("Accent.TButton", background=[('active', "#e6b800")])
        
        # Chat History List Frame
        self.chat_list_frame = tk.Frame(self.sidebar_frame, bg=BG_MEDIUM)
        self.chat_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
    def _create_main_frame(self):
        """Creates the main area for agent header, chat display, and input."""
        self.main_frame = tk.Frame(self.root, bg=BG_DARK)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1) # Chat display gets weight
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # 1. Agent Header (New Feature)
        agent_header = tk.Label(
            self.main_frame, text=AGENT_NAME, font=(FONT_MAIN, 18, "bold"),
            bg=BG_DARK, fg=ACCENT_AGENT, anchor="w", padx=10
        )
        agent_header.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # 2. Chat Display 
        self.chat_display = scrolledtext.ScrolledText(
            self.main_frame, wrap=tk.WORD, font=(FONT_MAIN, 14),
            bg=BG_DARK, fg=FG_WHITE, insertbackground=FG_WHITE,
            relief="flat", padx=10, pady=10
        )
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))
        self.chat_display.config(state=tk.DISABLED)

        # 3. Input Area Frame
        self.input_frame = tk.Frame(self.main_frame, bg=BG_DARK)
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # User Input Entry (Styled with a custom border/background)
        # Using a Canvas to draw a rounded rectangle for the modern border effect
        input_canvas = tk.Canvas(self.input_frame, bg=BG_DARK, highlightthickness=0)
        input_canvas.grid(row=0, column=0, sticky="ew")
        input_canvas.grid_columnconfigure(0, weight=1)
        
        # Create a light gray curved box for the input background (like a message bubble)
        # We need to manually draw the rounded rectangle inside the canvas for the effect
        def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, color):
            canvas.delete("input_box")
            points = [x1+radius, y1, x2-radius, y1, x2, y1+radius, x2, y2-radius, x2-radius, y2, x1+radius, y2, x1, y2-radius, x1, y1+radius]
            canvas.create_polygon(points, fill=color, smooth=True, tags="input_box")

        def resize_input_canvas(event):
            draw_rounded_rect(input_canvas, 2, 2, input_canvas.winfo_width()-2, input_canvas.winfo_height()-2, 10, BG_LIGHT_USER)
            
        input_canvas.bind("<Configure>", resize_input_canvas)

        self.user_input = tk.Entry(
            input_canvas, font=(FONT_MAIN, 13),
            bg=BG_LIGHT_USER, fg=FG_WHITE, insertbackground=FG_WHITE,
            relief="flat", bd=0, highlightthickness=0
        )
        # Place the entry widget inside the canvas to sit over the drawn background
        self.user_input.place(relx=0.01, rely=0.5, relwidth=0.98, relheight=0.9, anchor="w")
        self.user_input.bind("<Return>", self.send_message)
        
        # Set canvas height for visual spacing
        input_canvas.config(height=40)

        # Send Button
        ttk.Button(
            self.input_frame, text="➤ Send", command=self.send_message, width=10
        ).grid(row=0, column=1, padx=(10, 0))
        
        # Clear Button
        ttk.Button(
            self.input_frame, text="🗑 Clear", command=self.clear_chat, width=10,
            style="Clear.TButton"
        ).grid(row=0, column=2, padx=(10, 0))
        
        # Custom Clear Button Style
        self.style.configure("Clear.TButton", background="#cc0000", foreground=FG_WHITE)
        self.style.map("Clear.TButton", background=[('active', "#a30000")])


    def _create_status_bar(self):
        """Creates a status bar at the bottom."""
        self.status_bar = tk.Label(
            self.root, text=f"Status: Ready | Working Directory: {self.working_dir}",
            anchor="w", font=(FONT_MAIN, 10), bg=BG_MEDIUM, fg="#999999", padx=10
        )
        self.status_bar.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 5))


    # ==================================
    # === CHAT LOGIC METHODS (Backend) ===
    # ==================================

    def get_ai_response(self, user_input):
        """Calls the AGENT VALLAI backend (agenticai.main)."""
        return vallaipallam.agenticai.main.main(
            user_input,
            self.working_dir,
            self.apikey,
            self.gemini_chat_history
        )

    def send_message(self, event=None):
        """Handles sending the user message and receiving the AI response."""
        user_text = self.user_input.get().strip()
        if not user_text: return "break"
        
        # 1. Display User Message
        self.display_message("🧑 You", user_text, user=True)
        
        try:
            # 2. Get AI Response (blocking call)
            ai_text = self.get_ai_response(user_text)
        except Exception as e:
            ai_text = f"An error occurred: {e}. Check your API key or module installation."
            
        # 3. Display AI Response
        self.display_message("🍌 AGENT VALLAI", ai_text)
        
        # 4. Update History 
        self.current_chat.append(("🧑 You", user_text))
        self.current_chat.append(("🍌 AGENT VALLAI", ai_text))
        
        # 5. Clear Input and Save
        self.user_input.delete(0, tk.END)
        self.save_chat_to_csv()
        return "break"

    def display_message(self, sender, text, user=False):
        """
        Inserts message into the chat display with tags for formatting and highlighting.
        """
        self.chat_display.config(state=tk.NORMAL)
        
        # Insert Sender Label
        label_tag = "user_label" if user else "agent_label"
        self.chat_display.insert(tk.END, f"\n{sender}:\n", label_tag)
        
        # Split text by markdown code blocks (```...```)
        parts = re.split(r'(```[\s\S]*?```)', text)
        for part in parts:
            if part.startswith("```"):
                clean_code = part.strip().strip('`').lstrip('python').strip()
                self.chat_display.insert(tk.END, clean_code + "\n", "code_block")
            else:
                self.chat_display.insert(tk.END, f"  {part}\n", "text_block")
        
        # --- Configure Tags for Premium Look ---
        self.chat_display.tag_config("user_label", 
                                     foreground=ACCENT_USER, 
                                     font=(FONT_MAIN, 13, "bold"))
        self.chat_display.tag_config("agent_label", 
                                     foreground=ACCENT_AGENT, 
                                     font=(FONT_MAIN, 13, "bold"))
        self.chat_display.tag_config("code_block", 
                                     background=BG_MEDIUM, 
                                     foreground=ACCENT_CODE, 
                                     font=(FONT_CODE, 12), 
                                     lmargin1=20, lmargin2=20, rmargin=20, spacing1=5)
        self.chat_display.tag_config("text_block", 
                                     font=(FONT_MAIN, 13), 
                                     lmargin1=20, lmargin2=20, rmargin=20)
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END) 


    def clear_chat(self):
        """Clears the visual display and resets history."""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.current_chat = []
        self.gemini_chat_history = []
        self.display_message("🍌 AGENT VALLAI", "Chat cleared. Starting fresh.")

    # ==================================
    # === SESSION MANAGEMENT METHODS ===
    # ==================================

    def new_chat(self):
        """Starts a new session, saves the old one, and reloads the session list."""
        if self.current_chat:
            self.save_chat_to_csv()
        
        self.session_id = str(uuid.uuid4())
        self.current_chat = []
        self.gemini_chat_history = []
        self.clear_chat()
        self.load_chat_sessions()
        self.display_message("🍌 AGENT VALLAI", "New chat started. Ask your query!")

    def load_chat_sessions(self):
        """Loads session IDs from the CSV and populates the sidebar with buttons/labels."""
        for widget in self.chat_list_frame.winfo_children():
            widget.destroy()
        
        sessions = {}
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sid = row["session_id"]
                    if sid not in sessions:
                        sessions[sid] = row["message"][:40].replace('\n', ' ') + "..." 
        except Exception:
             pass 

        for i, (sid, snippet) in enumerate(sessions.items()):
            label = tk.Label(
                self.chat_list_frame, 
                text=snippet, 
                anchor="w", 
                padx=5, 
                pady=5, 
                bg=BG_MEDIUM, 
                fg="#cccccc", 
                wraplength=200,
                cursor="hand2"
            )
            label.pack(fill=tk.X, pady=(2, 0))
            # Bind click event
            label.bind("<Button-1>", lambda e, s=sid: self.load_chat_history(s))
            label.bind("<Enter>", lambda e, l=label: l.config(bg="#3a3a3a"))
            label.bind("<Leave>", lambda e, l=label: l.config(bg=BG_MEDIUM))


    def load_chat_history(self, session_id):
        """Clears current chat and loads history from the selected session ID."""
        self.session_id = session_id
        self.clear_chat()
        self.current_chat = []
        
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["session_id"] == session_id:
                        is_user = row["role"] == "🧑 You"
                        self.display_message(row["role"], row["message"], user=is_user)
                        self.current_chat.append((row["role"], row["message"]))
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load chat history: {e}")

    def save_chat_to_csv(self):
        """Appends the latest chat turn to the CSV file."""
        if len(self.current_chat) >= 2:
            latest_turn = self.current_chat[-2:]
            with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for role, msg in latest_turn:
                    writer.writerow([self.session_id, datetime.now(), role, msg])

# --- Main Execution Block ---
def main(workingdir, apikey):
    """Entry point for the UI."""
    root = tk.Tk()
    app = AgentVallaiApp(root, workingdir, apikey)
    root.mainloop()

