"""
ConvAI Innovations - Main Application (Refactored)
Interactive LLM Training Academy with multi-language support and visualizations.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import io
import time
import subprocess
import tempfile
import atexit
import os
import webbrowser
from typing import Optional
import concurrent.futures

# Import our modular components
from .models import Language, CodeGenRequest
from .session_manager import SessionManager
from .ai_systems import LLMAIFeedbackSystem, EnhancedKokoroTTSSystem
from .visualizations import VisualizationManager
from .sandbox_manager import SandboxManager
from .ai_tutor_narrator import AITutorNarrator
from .conversation_storage import ConversationStorage, ConversationEntry, get_storage
from .ui_components import (
    ModernCodeEditor,
    CodeGenerationPanel,
    LanguageSelector,
    ModelDownloader
)


class SessionBasedLLMLearningDashboard:
    """Main application class - refactored and enhanced"""
    
    def __init__(self, root: tk.Tk, model_path: Optional[str], ai_system: Optional = None):
        self.root = root
        
        # Initialize core systems
        self.session_manager = SessionManager()
        self.ai_system = ai_system or LLMAIFeedbackSystem(model_path)
        self.tts_system = EnhancedKokoroTTSSystem()
        self.visualization_manager = VisualizationManager(None)  # Will be set later
        
        # Initialize sandbox environment
        self.sandbox = SandboxManager(cleanup_on_exit=True)
        self.sandbox_initialized = False
        
        # UI state
        self.is_loading = False
        self.current_language = Language.ENGLISH
        
        # Animation state
        self.animation_chars = ['|', '/', '-', '\\']
        self.animation_index = 0
        
        # Thread executor
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        
        # Package management
        self.installed_packages = set()

        # Persistent conversation storage
        self.conversation_storage = get_storage()
        self.current_session_id = self.session_manager.progress.current_session_id

        # Load previous session history
        self.conversation_history = self.conversation_storage.load_session_history(self.current_session_id)

        # Dictionary to store code for each session
        self.session_code = {}  # Will load from storage
        
        # Code generation state
        self.is_generating_code = False
        self.generation_stop_event = threading.Event()

        # AI Tutor Narrator (will be initialized after code editor is created)
        self.ai_tutor_narrator = None

        # Setup UI
        self._configure_styles()
        self._setup_window()
        self._create_main_interface()
        self._load_current_session()

        # Load saved code for current session
        self._load_session_code()

        # Show initial message
        self._show_initial_session_message()
        
        # Initialize sandbox in background
        self._initialize_sandbox()
        
        # Check AI system status
        if not self.ai_system.is_available:
            self.status_label.config(text="🚨 AI Mentor Offline. Check console for errors.")

    def _setup_window(self):
        """Setup main window"""
        self.root.title("🧠 ConvAI Innovations - Interactive LLM Training Academy")
        
        # Dynamic window sizing
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = min(1600, int(screen_width * 0.9))
        window_height = min(1000, int(screen_height * 0.9))
        
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.configure(bg='#1e1e1e')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Center window
        self.root.update_idletasks()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Window properties
        self.root.resizable(True, True)
        self.root.minsize(1400, 800)

    def _configure_styles(self):
        """Configure TTK styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define color scheme
        colors = {
            'bg': '#1e1e1e',
            'fg': '#f8f9fa',
            'accent': '#00aaff',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'secondary': '#6c757d'
        }
        
        # Button styles
        button_styles = {
            'TButton': {'background': '#3a3d41', 'foreground': 'white'},
            'Run.TButton': {'background': colors['success'], 'foreground': 'white'},
            'Clear.TButton': {'background': colors['danger'], 'foreground': 'white'},
            'Session.TButton': {'background': '#6f42c1', 'foreground': 'white'},
            'Next.TButton': {'background': colors['accent'], 'foreground': 'white'},
            'Generate.TButton': {'background': '#17a2b8', 'foreground': 'white'},
            'Edit.TButton': {'background': '#ffc107', 'foreground': 'black'}
        }
        
        for style_name, config in button_styles.items():
            style.configure(style_name, font=('Segoe UI', 10, 'bold'), 
                          padding=8, relief='flat', **config)
            style.map(style_name, background=[('active', self._darken_color(config['background']))])
        
        # Label styles
        style.configure('TLabel', background=colors['bg'], foreground=colors['fg'], 
                       font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), 
                       foreground=colors['accent'])
        style.configure('Session.TLabel', font=('Segoe UI', 12, 'bold'), 
                       foreground=colors['warning'])
        
        # Frame styles
        style.configure('TFrame', background=colors['bg'])
        style.configure('Left.TFrame', background='#252526')
        
        # Paned window
        style.configure('TPanedwindow', background=colors['bg'])
        style.configure('TPanedwindow.Sash', sashthickness=6, relief='flat', 
                       background='#3a3d41')

    def _darken_color(self, color):
        """Darken a color for hover effects"""
        color_map = {
            '#28a745': '#218838',
            '#dc3545': '#c82333', 
            '#00aaff': '#0056b3',
            '#6f42c1': '#5a32a3',
            '#17a2b8': '#138496',
            '#3a3d41': '#4a4d51',
            '#ffc107': '#e0a800'
        }
        return color_map.get(color, color)

    def _create_main_interface(self):
        """Create the main interface"""
        # Create main paned window
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel (sessions, reference, visualizations)
        left_panel = self._create_left_panel(main_pane)
        main_pane.add(left_panel, weight=1)
        
        # Right panel (code editor and output)
        right_pane = ttk.PanedWindow(main_pane, orient=tk.VERTICAL)
        self._create_right_panel(right_pane)
        main_pane.add(right_pane, weight=2)
        
        # Status bar
        self._create_status_bar()
        
        # Configure pane sizes
        self.root.after(100, lambda: self._configure_pane_sizes(main_pane))

    def _create_left_panel(self, parent):
        """Create enhanced left panel with tabs"""
        left_frame = ttk.Frame(parent, style='Left.TFrame')
        
        # Create notebook for tabs
        notebook = ttk.Notebook(left_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Session tab
        session_tab = self._create_session_tab(notebook)
        notebook.add(session_tab, text="📚 Sessions")
        
        # Visualization tab
        viz_tab = self._create_visualization_tab(notebook)
        notebook.add(viz_tab, text="📊 Visualizations")
        
        # AI Code Gen tab
        if self.ai_system.is_available:
            codegen_tab = self._create_codegen_tab(notebook)
            notebook.add(codegen_tab, text="🤖 AI Code")
        
        # Terminal tab
        terminal_tab = self._create_terminal_tab(notebook)
        notebook.add(terminal_tab, text="💻 Terminal")
        
        # Settings tab
        settings_tab = self._create_settings_tab(notebook)
        notebook.add(settings_tab, text="⚙️ Settings")
        
        return left_frame

    def _create_session_tab(self, parent):
        """Create session management tab with editable reference code"""
        session_frame = ttk.Frame(parent, style='Left.TFrame')
        
        # Header
        header_frame = ttk.Frame(session_frame, style='Left.TFrame')
        header_frame.pack(fill='x', padx=8, pady=8)

        ttk.Label(header_frame, text="🎯 Learning Sessions",
                 style='Header.TLabel', background='#252526').pack(anchor='w')
        
        # Current session info
        current_session = self.session_manager.get_session(
            self.session_manager.progress.current_session_id
        )
        session_title = current_session.title if current_session else "No Session"
        self.current_session_label = ttk.Label(
            header_frame, text=f"Current: {session_title}", 
            style='Session.TLabel', background='#252526'
        )
        self.current_session_label.pack(anchor='w', pady=(3, 0))
        
        # Session navigation
        nav_frame = ttk.Frame(session_frame, style='Left.TFrame')
        nav_frame.pack(fill='x', padx=8, pady=3)
        
        # Session dropdown
        session_names = [
            "🐍 Python Fundamentals", "🔢 PyTorch & NumPy", "🧠 Neural Networks",
            "⬅️ Backpropagation", "📚 Python Data Structures", "🔢 NumPy Fundamentals",
            "🔄 Data Preprocessing", "📈 Linear Regression", "🎯 Logistic Regression",
            "📊 Model Evaluation", "🛡️ Regularization", "📉 Loss & Optimizers",
            "🏗️ LLM Architecture", "🔤 Tokenization & BPE", "🎯 RoPE & Attention",
            "⚖️ RMS Normalization", "🔄 FFN & Activations", "🚂 Training LLMs",
            "🎯 Inference & Generation"
        ]
        
        self.session_var = tk.StringVar(value=session_names[0])
        session_dropdown = ttk.OptionMenu(
            nav_frame, self.session_var, session_names[0], *session_names, 
            command=self._on_session_change
        )
        session_dropdown.pack(side='left', fill='x', expand=True, padx=(0, 3))
        
        self.next_session_button = ttk.Button(
            nav_frame, text="Next →", command=self._next_session, 
            style='Next.TButton'
        )
        self.next_session_button.pack(side='right', padx=(3, 0))
        
        # Reference code section with edit controls
        ref_frame = ttk.Frame(session_frame, style='Left.TFrame')
        ref_frame.pack(fill='both', expand=True, padx=8, pady=3)
        
        # Reference code header with edit toggle
        ref_header_frame = ttk.Frame(ref_frame, style='Left.TFrame')
        ref_header_frame.pack(fill='x', pady=(0, 3))
        
        ttk.Label(ref_header_frame, text="📖 Reference Code", 
                 style='TLabel', background='#252526').pack(side='left')
        
        # Edit mode toggle
        self.edit_mode_var = tk.BooleanVar(value=True)
        self.edit_toggle_button = ttk.Button(
            ref_header_frame, text="✏️ Edit", command=self._toggle_edit_mode,
            style='Edit.TButton'
        )
        self.edit_toggle_button.pack(side='right', padx=(5, 0))
        
        # Editable reference text
        self.reference_text = scrolledtext.ScrolledText(
            ref_frame, wrap=tk.WORD, font=('Consolas', 9), 
            bg='#2d3748', fg='#e2e8f0', bd=1, relief='solid', 
            padx=8, pady=8, height=18, insertbackground='white'
        )
        self.reference_text.pack(fill='both', expand=True, pady=3)
        
        # Initially in read-only mode
        self.reference_text.config(state='disabled')
        
        # Action buttons for reference code
        ref_action_frame = ttk.Frame(ref_frame, style='Left.TFrame')
        ref_action_frame.pack(fill='x', pady=3)
        
        ttk.Button(ref_action_frame, text="💡 Hint", command=self._get_hint, 
                  style='Session.TButton').pack(side='left', fill='x', expand=True, padx=(0, 2))
        ttk.Button(ref_action_frame, text="📋 Copy", command=self._copy_reference, 
                  style='TButton').pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(ref_action_frame, text="🗑️ Clear", command=self._clear_reference, 
                  style='Clear.TButton').pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(ref_action_frame, text="🔄 Reset", command=self._reset_reference, 
                  style='TButton').pack(side='left', fill='x', expand=True, padx=(2, 0))
        
        # Action buttons
        action_frame = ttk.Frame(session_frame, style='Left.TFrame')
        action_frame.pack(fill='x', padx=8, pady=5)
        
        ttk.Button(action_frame, text="→ Copy to Editor", command=self._copy_ref_to_editor, 
                  style='Session.TButton').pack(side='left', fill='x', expand=True, padx=(0, 3))
        ttk.Button(action_frame, text="💾 Save Reference", command=self._save_reference_to_file, 
                  style='TButton').pack(side='left', fill='x', expand=True, padx=3)
        
        # Audio controls at bottom of session tab
        audio_controls_frame = ttk.Frame(session_frame, style='Left.TFrame')
        audio_controls_frame.pack(fill='x', padx=8, pady=(10, 5))
        
        # Audio status and controls
        self.audio_status_label = ttk.Label(
            audio_controls_frame, text="🔇 Audio: Ready", 
            style='TLabel', background='#252526', foreground='#28a745'
        )
        self.audio_status_label.pack(side='left', padx=(0, 10))
        
        # Stop audio button - prominently placed
        self.stop_audio_button = ttk.Button(
            audio_controls_frame, text="⏹️ Stop Audio", 
            command=self.tts_system.stop_speech,
            style='Clear.TButton'
        )
        self.stop_audio_button.pack(side='right')
        
        return session_frame

    def _toggle_edit_mode(self):
        """Toggle edit mode for reference code"""
        if self.edit_mode_var.get():
            # Switch to read-only mode
            self.reference_text.config(state='disabled')
            self.edit_toggle_button.config(text="✏️ Edit")
            self.edit_mode_var.set(False)
            self.status_label.config(text="📖 Reference code is now read-only")
        else:
            # Switch to edit mode
            self.reference_text.config(state='normal')
            self.edit_toggle_button.config(text="🔒 Lock")
            self.edit_mode_var.set(True)
            self.status_label.config(text="✏️ Reference code is now editable - paste your ChatGPT code here!")

    def _clear_reference(self):
        """Clear reference code area"""
        if self.edit_mode_var.get():
            self.reference_text.delete('1.0', 'end')
            self.status_label.config(text="🗑️ Reference code cleared")
        else:
            messagebox.showinfo("Edit Mode Required", "Enable edit mode first to clear the reference code")

    def _reset_reference(self):
        """Reset reference code to original session content"""
        current_session = self.session_manager.get_session(
            self.session_manager.progress.current_session_id
        )
        if current_session:
            # Temporarily enable editing
            original_state = self.reference_text.cget('state')
            self.reference_text.config(state='normal')
            
            # Reset content
            self.reference_text.delete('1.0', 'end')
            full_content = (
                current_session.description + "\n\n" + "="*60 + 
                "\nREFERENCE CODE TO TYPE:\n" + "="*60 + "\n\n" + 
                current_session.reference_code
            )
            self.reference_text.insert('1.0', full_content)
            
            # Restore original state
            self.reference_text.config(state=original_state)
            self.status_label.config(text="🔄 Reference code reset to original session content")

    def _copy_ref_to_editor(self):
        """Copy reference code to main editor"""
        content = self.reference_text.get('1.0', 'end-1c')
        if content.strip():
            # Extract just the code part (after the last separator)
            parts = content.split("="*60)
            if len(parts) >= 3:
                code_content = parts[-1].strip()
            else:
                code_content = content
            
            result = messagebox.askyesno(
                "Copy to Editor", 
                "This will replace all code in the main editor. Continue?"
            )
            if result:
                self.code_editor.set_text(code_content)
                self.status_label.config(text="📋 Reference code copied to main editor")
        else:
            messagebox.showinfo("No Content", "Reference code area is empty")

    def _save_reference_to_file(self):
        """Save reference code to file"""
        from tkinter import filedialog
        content = self.reference_text.get('1.0', 'end-1c')
        if content.strip():
            filepath = filedialog.asksaveasfilename(
                defaultextension=".py", 
                filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if filepath:
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    messagebox.showinfo("Success", f"Reference code saved to {filepath}")
                    self.status_label.config(text=f"💾 Reference code saved to {filepath}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            messagebox.showinfo("No Content", "Reference code area is empty")

    def _create_visualization_tab(self, parent):
        """Create visualization tab"""
        viz_frame = ttk.Frame(parent, style='Left.TFrame')
        
        # Header
        ttk.Label(viz_frame, text="📊 Concept Visualizations", 
                 style='Header.TLabel', background='#252526').pack(pady=10)
        
        # Visualization controls
        control_frame = ttk.Frame(viz_frame, style='Left.TFrame')
        control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(control_frame, text="Select Visualization:", 
                 style='TLabel', background='#252526').pack(anchor='w')
        
        self.viz_var = tk.StringVar(value="Neural Network")
        viz_options = [
            "Neural Network", "Backpropagation", "Activation Functions", 
            "Self-Attention", "Tokenization", "Loss Functions"
        ]
        
        viz_dropdown = ttk.OptionMenu(
            control_frame, self.viz_var, viz_options[0], *viz_options,
            command=self._on_visualization_change
        )
        viz_dropdown.pack(fill='x', pady=5)
        
        # Visualization display area
        self.visualization_manager.parent = viz_frame
        viz_display = self.visualization_manager.create_visualization_frame()
        viz_display.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Default visualization
        self.visualization_manager.show_visualization("neural_network")
        
        return viz_frame

    def _create_codegen_tab(self, parent):
        """Create AI code generation tab"""
        # This will be set when we create the code editor
        self.codegen_placeholder = ttk.Frame(parent, style='Left.TFrame')
        return self.codegen_placeholder

    def _create_settings_tab(self, parent):
        """Create settings tab"""
        settings_frame = ttk.Frame(parent, style='Left.TFrame')

        # Language settings
        self.language_selector = LanguageSelector(settings_frame, self.tts_system)
        self.language_selector.pack(fill='x', padx=10, pady=10)

        # Audio settings
        audio_frame = ttk.Frame(settings_frame, style='Left.TFrame')
        audio_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(audio_frame, text="🔊 Audio Settings",
                 style='TLabel', background='#252526').pack(anchor='w')

        self.audio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(audio_frame, text="Enable Sandra's Voice",
                       variable=self.audio_var, style='TCheckbutton').pack(anchor='w', pady=2)

        # AI Tutor Narrator Information
        narrator_frame = ttk.Frame(settings_frame, style='Left.TFrame')
        narrator_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(narrator_frame, text="🎙️ AI Tutor Narrator",
                 style='TLabel', background='#252526', font=('Segoe UI', 11, 'bold')).pack(anchor='w')

        ttk.Label(narrator_frame, text="Sandra guides you line by line like a real tutor!",
                 style='TLabel', background='#252526', font=('Segoe UI', 8),
                 foreground='#6c757d').pack(anchor='w', pady=(2, 5))

        info_text = tk.Text(
            narrator_frame, wrap=tk.WORD, font=('Segoe UI', 9),
            bg='#2d2d30', fg='#cccccc', bd=1, relief='solid',
            padx=10, pady=10, height=6, state='disabled'
        )
        info_text.pack(fill='x', pady=5)

        info_message = """✨ How to use:
1. Select a learning session from the Sessions tab
2. Click "🎙️ Start Narration" button (next to Redo button)
3. Sandra will introduce the lesson
4. She'll guide you line by line as you type
5. Get encouragement after each line!

Use the button in the Code Practice Area to start/stop."""

        info_text.config(state='normal')
        info_text.insert('1.0', info_message)
        info_text.config(state='disabled')

        # Inactivity timeout slider
        timeout_frame = ttk.Frame(narrator_frame, style='Left.TFrame')
        timeout_frame.pack(fill='x', pady=10)

        ttk.Label(timeout_frame, text="⏱️ Inactivity Timeout (seconds):",
                 style='TLabel', background='#252526', font=('Segoe UI', 9)).pack(anchor='w')

        timeout_slider_frame = ttk.Frame(timeout_frame, style='Left.TFrame')
        timeout_slider_frame.pack(fill='x', pady=5)

        self.inactivity_timeout_var = tk.IntVar(value=20)
        timeout_slider = ttk.Scale(
            timeout_slider_frame, from_=5, to=60,
            variable=self.inactivity_timeout_var,
            orient='horizontal',
            command=lambda v: self._update_inactivity_timeout()
        )
        timeout_slider.pack(side='left', fill='x', expand=True, padx=(0, 10))

        self.timeout_label = ttk.Label(
            timeout_slider_frame, text="20s",
            style='TLabel', background='#252526', font=('Segoe UI', 9, 'bold'),
            width=5
        )
        self.timeout_label.pack(side='left')

        ttk.Label(timeout_frame, text="Sandra will encourage you if you're inactive for this long",
                 style='TLabel', background='#252526', font=('Segoe UI', 8),
                 foreground='#6c757d').pack(anchor='w', pady=(2, 0))

        # Visualization settings
        viz_settings_frame = ttk.Frame(settings_frame, style='Left.TFrame')
        viz_settings_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(viz_settings_frame, text="📊 Visualization Settings",
                 style='TLabel', background='#252526').pack(anchor='w')

        self.animation_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(viz_settings_frame, text="Enable Animations",
                       variable=self.animation_var, style='TCheckbutton',
                       command=self._toggle_animations).pack(anchor='w', pady=2)

        # Learning History section
        history_frame = ttk.Frame(settings_frame, style='Left.TFrame')
        history_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(history_frame, text="📚 Learning History",
                 style='TLabel', background='#252526', font=('Segoe UI', 11, 'bold')).pack(anchor='w')

        ttk.Label(history_frame, text="View your progress across all learning sessions",
                 style='TLabel', background='#252526', font=('Segoe UI', 8),
                 foreground='#6c757d').pack(anchor='w', pady=(2, 5))

        # Button to view all sessions history
        ttk.Button(
            history_frame, text="📊 View All Sessions Progress",
            command=self._show_all_sessions_history,
            style='Session.TButton'
        ).pack(anchor='w', pady=5)

        ttk.Button(
            history_frame, text="📁 Open Saved Conversations Folder",
            command=self._open_conversations_folder,
            style='TButton'
        ).pack(anchor='w', pady=5)

        return settings_frame

    def _create_terminal_tab(self, parent):
        """Create terminal tab for pip commands"""
        terminal_frame = ttk.Frame(parent, style='Left.TFrame')
        
        # Header
        header_frame = ttk.Frame(terminal_frame, style='Left.TFrame')
        header_frame.pack(fill='x', padx=8, pady=8)
        
        ttk.Label(
            header_frame, text="💻 Package Terminal", 
            style='Header.TLabel', background='#252526'
        ).pack(anchor='w')
        
        ttk.Label(
            header_frame, text="Install Python packages and view live logs", 
            style='TLabel', background='#252526', font=('Segoe UI', 9)
        ).pack(anchor='w', pady=(2, 0))
        
        # Sandbox info
        self.sandbox_info_label = ttk.Label(
            header_frame, text="🛡️ Sandboxed environment - Safe isolated execution", 
            style='TLabel', background='#252526', font=('Segoe UI', 8),
            foreground='#28a745'
        )
        self.sandbox_info_label.pack(anchor='w', pady=(2, 0))
        
        # Command input section
        input_frame = ttk.Frame(terminal_frame, style='Left.TFrame')
        input_frame.pack(fill='x', padx=8, pady=5)
        
        ttk.Label(input_frame, text="Command:", style='TLabel', background='#252526').pack(anchor='w')
        
        command_entry_frame = ttk.Frame(input_frame, style='Left.TFrame')
        command_entry_frame.pack(fill='x', pady=2)
        
        self.terminal_entry = tk.Entry(
            command_entry_frame, font=('Consolas', 10),
            bg='#2d3748', fg='#e2e8f0', insertbackground='white',
            bd=1, relief='solid'
        )
        self.terminal_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.terminal_entry.insert(0, "pip install ")
        
        # Execute button
        self.execute_button = ttk.Button(
            command_entry_frame, text="▶ Run", 
            command=self._execute_terminal_command, style='Run.TButton'
        )
        self.execute_button.pack(side='right')
        
        # Quick command buttons
        quick_frame = ttk.Frame(terminal_frame, style='Left.TFrame')
        quick_frame.pack(fill='x', padx=8, pady=2)
        
        ttk.Label(quick_frame, text="Quick Commands:", style='TLabel', background='#252526').pack(anchor='w')
        
        quick_buttons_frame = ttk.Frame(quick_frame, style='Left.TFrame')
        quick_buttons_frame.pack(fill='x', pady=2)
        
        # Common packages
        quick_commands = [
            ("TensorFlow", "pip install tensorflow"),
            ("NumPy", "pip install numpy"),
            ("Pandas", "pip install pandas"),
            ("Matplotlib", "pip install matplotlib"),
            ("Scikit-learn", "pip install scikit-learn")
        ]
        
        for i, (name, cmd) in enumerate(quick_commands):
            if i % 2 == 0:  # Start new row every 2 buttons
                button_row = ttk.Frame(quick_buttons_frame, style='Left.TFrame')
                button_row.pack(fill='x', pady=1)
            
            btn = ttk.Button(
                button_row, text=name, 
                command=lambda c=cmd: self._set_terminal_command(c),
                style='TButton'
            )
            btn.pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        # Terminal output
        output_frame = ttk.Frame(terminal_frame, style='Left.TFrame')
        output_frame.pack(fill='both', expand=True, padx=8, pady=5)
        
        ttk.Label(output_frame, text="Terminal Output:", style='TLabel', background='#252526').pack(anchor='w')
        
        # Terminal text widget with scrollbar
        self.terminal_output = scrolledtext.ScrolledText(
            output_frame, wrap=tk.WORD, font=('Consolas', 9), 
            bg='#1e1e1e', fg='#00ff00', bd=1, relief='solid', 
            state='disabled', padx=8, pady=8, height=12
        )
        self.terminal_output.pack(fill='both', expand=True, pady=(2, 0))
        
        # Configure terminal tags for colored output
        self.terminal_output.tag_configure('success', foreground='#00ff00')
        self.terminal_output.tag_configure('error', foreground='#ff4444') 
        self.terminal_output.tag_configure('warning', foreground='#ffaa00')
        self.terminal_output.tag_configure('info', foreground='#00aaff')
        self.terminal_output.tag_configure('command', foreground='#ffffff', font=('Consolas', 9, 'bold'))
        
        # Control buttons
        control_frame = ttk.Frame(terminal_frame, style='Left.TFrame')
        control_frame.pack(fill='x', padx=8, pady=5)
        
        ttk.Button(
            control_frame, text="🗑️ Clear", 
            command=self._clear_terminal, style='Clear.TButton'
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            control_frame, text="⏹️ Stop", 
            command=self._stop_terminal_command, style='Clear.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            control_frame, text="🔄 Reset Sandbox", 
            command=self._reset_sandbox, style='TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            control_frame, text="📊 Sandbox Info", 
            command=self._show_sandbox_info, style='TButton'
        ).pack(side='left', padx=5)
        
        # Terminal state
        self.terminal_process = None
        self.terminal_running = False
        
        # Bind Enter key to execute
        self.terminal_entry.bind('<Return>', lambda e: self._execute_terminal_command())
        
        # Show welcome message
        self._terminal_log("💻 Package Terminal Ready", 'info')
        self._terminal_log("Type 'pip install <package>' or use quick commands above", 'info')
        self._terminal_log("=" * 50, 'info')
        
        return terminal_frame

    def _create_right_panel(self, parent):
        """Create right panel with code editor and output"""
        # Code editor section
        editor_frame = ttk.Frame(parent)
        self._create_editor_section(editor_frame)
        parent.add(editor_frame, weight=3)
        
        # Output section  
        output_frame = ttk.Frame(parent)
        self._create_output_section(output_frame)
        parent.add(output_frame, weight=2)

    def _create_editor_section(self, parent):
        """Create code editor section"""
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=(10, 5), padx=10)

        ttk.Label(header_frame, text="💻 Code Practice Area",
                 style='Header.TLabel').pack(side='left')

        # Certificate button next to title
        ttk.Button(header_frame, text="🎓 Certificate",
                  command=self._open_certificate_portal,
                  style='Session.TButton',
                  width=12).pack(side='left', padx=10)

        ttk.Label(header_frame, text="Type code manually for better learning!",
                 style='TLabel', foreground='#ffc107').pack(side='right')
        
        # Code editor
        self.code_editor = ModernCodeEditor(parent)

        # Bind auto-save on code changes (typing or pasting)
        self.code_editor.text_widget.bind('<<Modified>>', self._on_code_change)
        self.code_editor.text_widget.bind('<KeyRelease>', self._on_code_change)
        self.code_editor.text_widget.bind('<<Paste>>', self._on_code_change)

        # Initialize AI Tutor Narrator
        if self.ai_system.is_available and self.tts_system.is_available:
            self.ai_tutor_narrator = AITutorNarrator(
                self.code_editor,
                self.ai_system,
                self.tts_system,
                self.language_selector
            )

        # Now create the code generation panel
        if self.ai_system.is_available and hasattr(self, 'codegen_placeholder'):
            codegen_panel = CodeGenerationPanel(
                self.codegen_placeholder, self.ai_system, self.code_editor
            )
            codegen_panel.pack(fill='both', expand=True)
        
        # Button toolbar
        button_bar = ttk.Frame(parent)
        button_bar.pack(fill='x', pady=5, padx=10)
        
        # Main action buttons
        self.run_button = ttk.Button(
            button_bar, text="▶ Run Code", command=self._run_code, 
            style='Run.TButton'
        )
        self.run_button.pack(side='left', padx=2)
        
        ttk.Button(button_bar, text="🧹 Clear", command=self.code_editor.clear, 
                  style='Clear.TButton').pack(side='left', padx=2)
        
        # Editor utilities
        ttk.Button(button_bar, text="↶ Undo",
                  command=lambda: self.code_editor.text_widget.edit_undo()).pack(side='left', padx=2)
        ttk.Button(button_bar, text="↷ Redo",
                  command=lambda: self.code_editor.text_widget.edit_redo()).pack(side='left', padx=2)

        # AI Tutor Narration button
        self.narration_button = ttk.Button(
            button_bar, text="🎙️ Start Narration",
            command=self._toggle_narration,
            style='Run.TButton'
        )
        self.narration_button.pack(side='left', padx=2)

        # Repeat Line button (for narration)
        self.repeat_line_button = ttk.Button(
            button_bar, text="🔄 Repeat",
            command=self._repeat_current_line,
            style='TButton'
        )
        self.repeat_line_button.pack(side='left', padx=2)

        # File operations
        ttk.Button(button_bar, text="💾 Save", command=self._save_code).pack(side='right', padx=2)
        ttk.Button(button_bar, text="📁 Load", command=self._load_code).pack(side='right', padx=2)

        self.code_editor.pack(fill='both', expand=True, pady=5, padx=10)

    def _create_output_section(self, parent):
        """Create output section"""
        self.output_frame = parent
        
        ttk.Label(self.output_frame, text="📤 Output & AI Feedback from Sandra", 
                 style='Header.TLabel').pack(pady=10)
        
        # Loading animation
        self.loading_label = ttk.Label(
            self.output_frame, text="", font=('Consolas', 14, 'bold'), 
            foreground="#00aaff", background='#1e1e1e'
        )
        
        # Output text
        self.output_text = scrolledtext.ScrolledText(
            self.output_frame, wrap=tk.WORD, font=('Consolas', 11), 
            bg='#282c34', fg='#f8f9fa', bd=0, relief='flat', 
            state='disabled', padx=10, pady=10
        )
        self.output_text.pack(fill='both', expand=True, pady=5, padx=10)
        
        # Configure text tags
        self._configure_output_tags()
        
        # Add context menu for copying errors
        self._create_output_context_menu()

    def _create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root, style='Left.TFrame', height=35)
        status_frame.pack(side='bottom', fill='x', padx=5, pady=(0, 5))
        status_frame.pack_propagate(False)
        
        self.status_label = ttk.Label(
            status_frame, text="🧠 ConvAI Innovations Ready.", 
            background='#252526', anchor='w', style='TLabel'
        )
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Sandbox status indicator
        self.sandbox_status_label = ttk.Label(
            status_frame, text="🛡️ Sandbox: Initializing...", 
            background='#252526', anchor='center', 
            style='TLabel', foreground='#ffc107'
        )
        self.sandbox_status_label.pack(side='left', padx=10, pady=5)
        
        # Progress indicator
        completion_pct = self.session_manager.progress.get_completion_percentage()
        self.progress_label = ttk.Label(
            status_frame, text=f"Progress: {completion_pct:.0f}% Complete", 
            background='#252526', anchor='e', 
            style='TLabel', foreground='#28a745'
        )
        self.progress_label.pack(side='right', padx=10, pady=5)

    def _configure_output_tags(self):
        """Configure output text tags"""
        tags = {
            'success': {'foreground': '#28a745', 'font': ('Consolas', 11, 'bold')},
            'error': {'foreground': '#dc3545', 'font': ('Consolas', 11, 'bold')},
            'ai_feedback': {'foreground': '#00aaff', 'font': ('Consolas', 12, 'italic')},
            'hint': {'foreground': '#ffc107', 'font': ('Consolas', 11, 'bold')},
            'info': {'foreground': '#17a2b8', 'font': ('Consolas', 11)},
            'session_msg': {'foreground': '#6f42c1', 'font': ('Consolas', 12, 'bold')}
        }
        
        for tag, config in tags.items():
            self.output_text.tag_config(tag, **config)

    def _create_output_context_menu(self):
        """Create context menu for output area"""
        self.output_context_menu = tk.Menu(self.root, tearoff=0)
        self.output_context_menu.add_command(
            label="📋 Copy Error to Code Generator", 
            command=self._copy_error_to_generator
        )
        self.output_context_menu.add_command(
            label="📄 Copy All Output", 
            command=self._copy_all_output
        )
        self.output_context_menu.add_command(
            label="🔍 Copy Selected Text", 
            command=self._copy_selected_output
        )
        self.output_context_menu.add_separator()
        self.output_context_menu.add_command(
            label="🤖 Ask Sandra About This Error", 
            command=self._ask_about_error
        )
        
        # Bind right-click to show context menu
        self.output_text.bind("<Button-3>", self._show_output_context_menu)

    def _show_output_context_menu(self, event):
        """Show context menu for output area"""
        try:
            self.output_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.output_context_menu.grab_release()

    def _copy_error_to_generator(self):
        """Copy error messages to code generator"""
        try:
            output_content = self.output_text.get('1.0', 'end-1c')
            
            # Extract error messages
            lines = output_content.split('\n')
            error_lines = []
            for line in lines:
                if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback', 'failed', '❌']):
                    # Clean up the line (remove emoji and extra characters)
                    clean_line = line.strip()
                    for emoji in ['❌', '✅', '🔍', '📋', '🤖']:
                        clean_line = clean_line.replace(emoji, '').strip()
                    if clean_line:
                        error_lines.append(clean_line)
            
            if error_lines:
                error_text = '\n'.join(error_lines[-3:])  # Last 3 error lines
                
                # Find the code generator and populate its followup area
                if hasattr(self, 'ai_system') and self.ai_system.is_available:
                    # Try to find the code generation panel
                    for child in self.root.winfo_children():
                        if self._find_code_generator_followup(child, error_text):
                            messagebox.showinfo("Error Copied", "Error copied to AI Code Generator followup area!")
                            return
                
                # Fallback: copy to clipboard
                self.root.clipboard_clear()
                self.root.clipboard_append(error_text)
                messagebox.showinfo("Error Copied", "Error copied to clipboard! Paste it in the AI Code Generator.")
            else:
                messagebox.showinfo("No Errors", "No error messages found in the output.")
                
        except Exception as e:
            messagebox.showerror("Copy Error", f"Could not copy error: {e}")

    def _find_code_generator_followup(self, widget, error_text):
        """Recursively find code generator followup area and populate it"""
        # Check if this widget has the followup_text attribute
        if hasattr(widget, 'followup_text'):
            try:
                widget.followup_text.delete('1.0', 'end')
                widget.followup_text.insert('1.0', f"I got this error when running the code:\n\n{error_text}\n\nCan you help me fix it?")
                return True
            except:
                pass
        
        # Recursively check children
        try:
            for child in widget.winfo_children():
                if self._find_code_generator_followup(child, error_text):
                    return True
        except:
            pass
        
        return False

    def _copy_all_output(self):
        """Copy all output to clipboard"""
        try:
            content = self.output_text.get('1.0', 'end-1c')
            if content.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                messagebox.showinfo("Copied", "All output copied to clipboard!")
            else:
                messagebox.showinfo("No Content", "Output area is empty.")
        except Exception as e:
            messagebox.showerror("Copy Error", f"Could not copy output: {e}")

    def _copy_selected_output(self):
        """Copy selected text from output"""
        try:
            if self.output_text.tag_ranges(tk.SEL):
                selected_text = self.output_text.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                messagebox.showinfo("Copied", "Selected text copied to clipboard!")
            else:
                messagebox.showinfo("No Selection", "Please select text first.")
        except Exception as e:
            messagebox.showerror("Copy Error", f"Could not copy selection: {e}")

    def _ask_about_error(self):
        """Ask Sandra about the current error"""
        try:
            output_content = self.output_text.get('1.0', 'end-1c')
            
            # Extract recent error
            lines = output_content.split('\n')
            error_lines = []
            for line in reversed(lines):  # Start from the end
                if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', '❌']):
                    clean_line = line.strip()
                    for emoji in ['❌', '✅', '🔍', '📋', '🤖']:
                        clean_line = clean_line.replace(emoji, '').strip()
                    if clean_line:
                        error_lines.append(clean_line)
                        if len(error_lines) >= 2:  # Get up to 2 error lines
                            break
            
            if error_lines:
                error_text = '\n'.join(reversed(error_lines))
                
                # Create a simple question about the error
                question = f"I got this error: {error_text}. What does this mean and how can I fix it?"
                
                # Add to conversation history and get response
                self._add_to_conversation_history("error_question", {
                    "question": question,
                    "error": error_text,
                    "language": self.language_selector.get_current_language().display_name
                })
                
                # Process the question
                current_language = self.language_selector.get_current_language()
                threading.Thread(
                    target=self._process_error_question, 
                    args=(question, current_language), 
                    daemon=True
                ).start()
                
                self.status_label.config(text="🤖 Sandra is analyzing your error...")
            else:
                messagebox.showinfo("No Errors", "No recent errors found to ask about.")
                
        except Exception as e:
            messagebox.showerror("Question Error", f"Could not ask about error: {e}")

    def _process_error_question(self, question: str, language):
        """Process error question in background"""
        try:
            context = self._get_conversation_context()
            session_id = self.session_manager.progress.current_session_id
            
            # Generate response
            response = self.ai_system.generate_followup_response(question, context, session_id, language)
            
            # Update UI on main thread
            self.root.after(0, self._show_error_explanation, question, response, language)
            
        except Exception as e:
            error_msg = f"Could not process error question: {e}"
            self.root.after(0, lambda: self._log_output(f"\n❌ {error_msg}", 'error'))

    def _show_error_explanation(self, question: str, response: str, language):
        """Show error explanation"""
        self._log_output(f"\n❓ You asked: {question}", 'info')
        self._log_output(f"\n🤖 Sandra explains: {response}", 'ai_feedback')
        
        # Add to conversation history
        self._add_to_conversation_history("error_response", {
            "question": question,
            "response": response,
            "language": language.display_name
        })
        
        # Speak the response if audio is enabled
        if self.audio_var.get():
            self._speak_with_stop_button(response, language)
        
        self.status_label.config(text="🧠 ConvAI Innovations Ready.")

    def _configure_pane_sizes(self, main_pane):
        """Configure pane sizes after window display"""
        try:
            total_width = self.root.winfo_width()
            if total_width > 100:
                left_width = min(550, int(total_width * 0.35))
                main_pane.sashpos(0, left_width)
        except tk.TclError:
            pass

    # Event handlers
    def _on_session_change(self, selected_session):
        """Handle session change and load conversation history"""
        session_mapping = {
            "🐍 Python Fundamentals": "python_fundamentals",
            "🔢 PyTorch & NumPy": "pytorch_numpy",
            "🧠 Neural Networks": "neural_networks",
            "⬅️ Backpropagation": "backpropagation",
            "📚 Python Data Structures": "python_data_structures",
            "🔢 NumPy Fundamentals": "numpy_fundamentals",
            "🔄 Data Preprocessing": "data_preprocessing",
            "📈 Linear Regression": "linear_regression",
            "🎯 Logistic Regression": "logistic_regression",
            "📊 Model Evaluation": "model_evaluation",
            "🛡️ Regularization": "regularization",
            "📉 Loss & Optimizers": "loss_optimizers",
            "🏗️ LLM Architecture": "llm_architecture",
            "🔤 Tokenization & BPE": "tokenization_bpe",
            "🎯 RoPE & Attention": "rope_attention",
            "⚖️ RMS Normalization": "rms_normalization",
            "🔄 FFN & Activations": "ffn_activations",
            "🚂 Training LLMs": "training_llms",
            "🎯 Inference & Generation": "inference_generation"
        }
        
        new_session_id = session_mapping.get(selected_session)
        if new_session_id and new_session_id != self.session_manager.progress.current_session_id:
            # Save current code before switching
            current_code = self.code_editor.get_text().strip()

            if current_code:
                self.session_code[self.current_session_id] = current_code
                self._save_session_code_to_file()

            # Update session ID
            old_session_id = self.current_session_id
            self.session_manager.progress.current_session_id = new_session_id
            self.current_session_id = new_session_id

            # Load conversation history for new session
            self.conversation_history = self.conversation_storage.load_session_history(new_session_id)

            # Get session stats
            stats = self.conversation_storage.get_session_stats(new_session_id)
            print(f"📚 Loaded session '{new_session_id}' - {stats['total_entries']} previous conversations")

            self._load_current_session()
            self._clear_output()

            # Load saved code for new session
            print(f"   Sessions in memory: {list(self.session_code.keys())}")
            if new_session_id in self.session_code:
                code_to_load = self.session_code[new_session_id]
                print(f"   Found code for {new_session_id}: {len(code_to_load)} characters")
                self.code_editor.set_text(code_to_load)
                print(f"✅ Restored code for session: {new_session_id}\n")
            else:
                print(f"   No saved code for {new_session_id}, clearing editor")
                self.code_editor.clear()

            self._show_initial_session_message()

            # Show session stats in status
            if stats['total_entries'] > 0:
                self.status_label.config(text=f"📚 Switched to: {selected_session} ({stats['total_entries']} saved entries)")
            else:
                self.status_label.config(text=f"📚 Switched to: {selected_session}")

    def _on_visualization_change(self, selected_viz):
        """Handle visualization change"""
        viz_mapping = {
            "Neural Network": "neural_network",
            "Backpropagation": "backpropagation", 
            "Activation Functions": "activation_function",
            "Self-Attention": "attention",
            "Tokenization": "tokenization",
            "Loss Functions": "loss_functions"
        }
        
        viz_type = viz_mapping.get(selected_viz, "neural_network")
        
        if viz_type == "activation_function":
            self.visualization_manager.show_visualization(viz_type, function="relu")
        elif viz_type == "tokenization":
            self.visualization_manager.show_visualization(
                viz_type, text="Hello world! This is tokenization.", method="bpe"
            )
        else:
            self.visualization_manager.show_visualization(viz_type)

    def _toggle_animations(self):
        """Toggle visualization animations"""
        self.visualization_manager.update_config(animate=self.animation_var.get())

    def _update_inactivity_timeout(self):
        """Update inactivity timeout for AI tutor narrator"""
        timeout = int(self.inactivity_timeout_var.get())
        self.timeout_label.config(text=f"{timeout}s")

        # Update AI tutor narrator timeout if it exists
        if hasattr(self, 'ai_tutor_narrator') and self.ai_tutor_narrator:
            self.ai_tutor_narrator.set_inactivity_timeout(timeout)

    def _next_session(self):
        """Move to next session and load its conversation history"""
        next_session_id = self.session_manager.get_next_session()
        if next_session_id:
            # Save current code before switching
            current_code = self.code_editor.get_text().strip()
            if current_code:
                self.session_code[self.current_session_id] = current_code
                self._save_session_code_to_file()

            self.session_manager.mark_session_complete(
                self.session_manager.progress.current_session_id
            )
            self.session_manager.progress.current_session_id = next_session_id
            self.current_session_id = next_session_id

            # Load conversation history for new session
            self.conversation_history = self.conversation_storage.load_session_history(next_session_id)

            # Get session stats
            stats = self.conversation_storage.get_session_stats(next_session_id)
            print(f"📚 Advanced to session '{next_session_id}' - {stats['total_entries']} previous conversations")

            self._load_current_session()
            self._clear_output()

            # Load saved code for new session
            if next_session_id in self.session_code:
                self.code_editor.set_text(self.session_code[next_session_id])
                print(f"✅ Restored code for session: {next_session_id}")
            else:
                self.code_editor.clear()

            self._show_initial_session_message()

            next_session = self.session_manager.get_session(next_session_id)
            if stats['total_entries'] > 0:
                self.status_label.config(text=f"🎉 Advanced to: {next_session.title} ({stats['total_entries']} saved entries)")
            else:
                self.status_label.config(text=f"🎉 Advanced to: {next_session.title}")
        else:
            messagebox.showinfo(
                "Congratulations!", 
                "🎉 You've completed all sessions! You're now ready to build your own LLMs!"
            )

    def _get_hint(self):
        """Get hint for current session"""
        current_session = self.session_manager.get_session(
            self.session_manager.progress.current_session_id
        )
        if current_session and current_session.hints:
            import random
            hint = random.choice(current_session.hints)
            self._log_output(f"\n💡 Sandra's Hint: {hint}", 'hint')

    def _copy_reference(self):
        """Copy reference code to clipboard"""
        content = self.reference_text.get('1.0', 'end-1c')
        if content.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.status_label.config(
                text="📋 Reference content copied! But try typing it manually for better learning."
            )
        else:
            messagebox.showinfo("No Content", "Reference code area is empty")

    def _run_code(self):
        """Run the code in the editor"""
        if self.is_loading:
            return
            
        code = self.code_editor.get_text()
        if not code.strip():
            messagebox.showwarning("Input Error", "Code editor is empty. Try typing some code first!")
            return
        
        self._set_ui_loading(True)
        self.tts_system.stop_speech()
        self._clear_output()
        self._start_loading_animation()
        
        # Run in background thread
        threading.Thread(target=self._execute_code, args=(code,), daemon=True).start()

    def _execute_code(self, code: str):
        """Execute code in sandbox environment"""
        if self.sandbox_initialized:
            # Execute in sandbox
            try:
                result = self.sandbox.execute_code(code, timeout=30)
                output = result.get('output', '')
                error = result.get('error', '') if not result.get('success', False) else ''
                
                # Process on main thread
                self.root.after(0, self._process_execution_result, code, output, error)
                
            except Exception as e:
                error_msg = f"Sandbox execution error: {e}"
                self.root.after(0, self._process_execution_result, code, '', error_msg)
        else:
            # Fallback to restricted execution (not recommended)
            self._execute_code_fallback(code)

    def _execute_code_fallback(self, code: str):
        """Fallback code execution (restricted)"""
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        # Redirect stdout and stderr
        sys.stdout, sys.stderr = output_buffer, error_buffer
        error_msg = ""
        
        try:
            # Basic security check
            if any(danger in code.lower() for danger in ['import os', 'import sys', 'exec(', 'eval(', '__import__']):
                error_msg = "Code contains restricted operations. Sandbox required for execution."
            else:
                exec(code, {'__builtins__': __builtins__})
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
        finally:
            sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
        
        # Process on main thread
        self.root.after(0, self._process_execution_result, code, 
                       output_buffer.getvalue(), error_msg)

    def _process_execution_result(self, code, output, error):
        """Process code execution results"""
        self._stop_loading_animation()
        
        # Get current language from the language selector (FIXED)
        current_language = self.language_selector.get_current_language()  # This was the issue!
        
        # Generate AI feedback with the selected language
        session_id = self.session_manager.progress.current_session_id
        feedback_text = self.ai_system.generate_feedback(code, error, session_id, current_language)
        
        # Display results
        if error:
            self._log_output(f"❌ ERROR:\n{error}", 'error')
            self._log_output(f"\n🔍 Debug tip: Check syntax, indentation, and variable names.", 'info')
            
            # Check for missing packages and suggest installation
            self._check_and_suggest_packages(error)
        else:
            self._log_output("✅ SUCCESS! Code executed without errors.", 'success')
            
        # Always show output if there is any (including print statements)
        if output and output.strip():
            self._log_output(f"\n📋 Output:\n{output}", 'info')
        elif not error and not output.strip():
            self._log_output(f"\n📋 No output produced (code ran silently).", 'info')
        
        # Display AI feedback
        if feedback_text:
            self._log_output(f"\n🤖 Sandra says: {feedback_text}", 'ai_feedback')
            if self.audio_var.get():
                self._speak_with_stop_button(feedback_text, current_language)
                
            # Add conversation to history
            self._add_to_conversation_history("code_execution", {
                "code": code,
                "output": output,
                "error": error,
                "feedback": feedback_text,
                "language": current_language.display_name
            })
            
            # Show followup question option
            self._show_followup_option()
        
        self.status_label.config(text="🧠 ConvAI Innovations Ready.")
        self._set_ui_loading(False)

    def _save_code(self):
        """Save code to file"""
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            defaultextension=".py", 
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.code_editor.get_text())
                messagebox.showinfo("Success", f"Code saved to {filepath}")
                self.status_label.config(text=f"💾 Code saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def _load_code(self):
        """Load code from file"""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.code_editor.set_text(f.read())
                self.status_label.config(text=f"📁 Code loaded from {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def _open_certificate_portal(self):
        """Open the certificate portal in the default browser"""
        try:
            webbrowser.open('https://dashboard.convaiinnovations.com/')
            self.status_label.config(text="🎓 Opening Certificate Portal in browser...")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open certificate portal: {e}")

    # UI state management
    def _set_ui_loading(self, is_loading):
        """Set UI loading state"""
        self.is_loading = is_loading
        state = tk.DISABLED if is_loading else tk.NORMAL
        self.run_button.config(state=state)
        
        if not is_loading:
            self.run_button.config(text="▶ Run Code")

    def _start_loading_animation(self):
        """Start loading animation"""
        self.loading_label.pack(pady=20)
        self.output_text.pack_forget()
        self._animate_loading()

    def _stop_loading_animation(self):
        """Stop loading animation"""
        self.loading_label.pack_forget()
        self.output_text.pack(fill='both', expand=True, pady=5, padx=10)

    def _animate_loading(self):
        """Animate loading indicator"""
        if self.is_loading:
            char = self.animation_chars[self.animation_index]
            self.loading_label.config(text=f"Sandra is analyzing your code... {char}")
            self.animation_index = (self.animation_index + 1) % len(self.animation_chars)
            self.root.after(150, self._animate_loading)

    def _speak_with_stop_button(self, text, language=None):
        """Speak text and manage stop button"""
        if not self.tts_system.is_available:
            self.audio_status_label.config(text="🔇 Audio: Not Available", foreground='#dc3545')
            return
            
        self.stop_audio_button.config(state=tk.NORMAL)
        self.audio_status_label.config(text="🔊 Audio: Speaking...", foreground='#ffc107')
        self.tts_system.speak(text, language)
        
        def check_status():
            if not self.tts_system.is_speaking:
                self.stop_audio_button.config(state=tk.NORMAL)  # Keep enabled for interrupting
                self.audio_status_label.config(text="🔇 Audio: Ready", foreground='#28a745')
            else:
                self.root.after(100, check_status)
        
        self.root.after(100, check_status)

    def _add_to_conversation_history(self, interaction_type: str, data: dict):
        """Add interaction to conversation history and save persistently"""
        import datetime

        # Extract user input and AI response based on interaction type
        user_input = ""
        ai_response = ""
        code_snippet = ""

        if interaction_type == "code_execution":
            user_input = f"Running code"
            code_snippet = data.get("code", "")
            ai_response = data.get("feedback", "")
        elif interaction_type == "error_question":
            user_input = data.get("question", "")
            code_snippet = ""
        elif interaction_type == "error_response":
            user_input = data.get("question", "")
            ai_response = data.get("response", "")
        elif interaction_type == "followup_question":
            user_input = data.get("question", "")
            ai_response = data.get("response", "")
        else:
            user_input = str(data)

        # Create conversation entry
        entry = ConversationEntry(
            session_id=self.current_session_id,
            user_input=user_input,
            ai_response=ai_response,
            code_snippet=code_snippet
        )

        # Save to persistent storage
        try:
            self.conversation_storage.save_conversation(entry)
            self.conversation_history.append(entry)
            print(f"✅ Conversation saved to ~/.convai/conversations/")
        except Exception as e:
            print(f"⚠️ Could not save conversation history: {e}")

    def _show_followup_option(self):
        """Show followup question option in output area"""
        # Add a button frame for followup
        if hasattr(self, 'followup_frame') and self.followup_frame.winfo_exists():
            self.followup_frame.destroy()
            
        self.followup_frame = ttk.Frame(self.output_frame)
        self.followup_frame.pack(fill='x', padx=10, pady=5)
        
        # Followup question input
        followup_label = ttk.Label(
            self.followup_frame, text="💬 Ask Sandra a followup question:", 
            style='TLabel'
        )
        followup_label.pack(anchor='w', pady=(5, 2))
        
        input_frame = ttk.Frame(self.followup_frame)
        input_frame.pack(fill='x', pady=2)
        
        self.followup_entry = tk.Text(
            input_frame, height=2, font=('Segoe UI', 10),
            bg='#2d3748', fg='#e2e8f0', insertbackground='white',
            wrap=tk.WORD, bd=1, relief='solid'
        )
        self.followup_entry.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(side='right', fill='y')
        
        ask_button = ttk.Button(
            button_frame, text="💬 Ask", 
            command=self._ask_followup_question, style='Next.TButton'
        )
        ask_button.pack(fill='x', pady=(0, 2))
        
        hide_button = ttk.Button(
            button_frame, text="✕ Hide", 
            command=self._hide_followup, style='TButton'
        )
        hide_button.pack(fill='x')
        
        # Bind Enter key to ask question
        self.followup_entry.bind('<Control-Return>', lambda e: self._ask_followup_question())
        
        # Auto-focus on the input
        self.followup_entry.focus_set()

    def _hide_followup(self):
        """Hide the followup question area"""
        if hasattr(self, 'followup_frame') and self.followup_frame.winfo_exists():
            self.followup_frame.destroy()

    def _ask_followup_question(self):
        """Process followup question"""
        if not hasattr(self, 'followup_entry'):
            return
            
        question = self.followup_entry.get('1.0', 'end-1c').strip()
        if not question:
            messagebox.showwarning("Input Required", "Please enter a question.")
            return
            
        if not self.ai_system.is_available:
            messagebox.showerror("AI Unavailable", "AI mentor is not available for followup questions.")
            return
        
        # Clear the input
        self.followup_entry.delete('1.0', 'end')
        
        # Show that we're processing
        self._log_output(f"\n❓ You asked: {question}", 'info')
        self._log_output("\n⏳ Sandra is thinking...", 'info')
        
        # Get current language
        current_language = self.language_selector.get_current_language()
        
        # Process in background
        threading.Thread(
            target=self._process_followup_question, 
            args=(question, current_language), 
            daemon=True
        ).start()

    def _process_followup_question(self, question: str, language: Language):
        """Process followup question in background"""
        try:
            # Get recent conversation context
            context = self._get_conversation_context()
            session_id = self.session_manager.progress.current_session_id
            
            # Generate followup response
            response = self.ai_system.generate_followup_response(question, context, session_id, language)
            
            # Update UI on main thread
            self.root.after(0, self._show_followup_response, question, response, language)
            
        except Exception as e:
            error_msg = f"Could not process followup question: {e}"
            self.root.after(0, lambda: self._log_output(f"\n❌ {error_msg}", 'error'))

    def _show_followup_response(self, question: str, response: str, language: Language):
        """Show followup response"""
        self._log_output(f"\n🤖 Sandra replies: {response}", 'ai_feedback')
        
        # Add to conversation history
        self._add_to_conversation_history("followup_question", {
            "question": question,
            "response": response,
            "language": language.display_name
        })
        
        # Speak the response if audio is enabled
        if self.audio_var.get():
            self._speak_with_stop_button(response, language)

    def _get_conversation_context(self) -> str:
        """Get recent conversation context for followup questions"""
        if not self.conversation_history:
            return "No previous conversation context."
        
        # Get last few interactions
        recent_interactions = self.conversation_history[-3:]
        context_parts = []
        
        for interaction in recent_interactions:
            if interaction["type"] == "code_execution":
                data = interaction["data"]
                context_parts.append(f"User ran code, got feedback: {data.get('feedback', '')}")
            elif interaction["type"] == "followup_question":
                data = interaction["data"]
                context_parts.append(f"User asked: {data.get('question', '')}, Sandra replied: {data.get('response', '')}")
        
        return " | ".join(context_parts)

    # Terminal methods
    def _set_terminal_command(self, command: str):
        """Set command in terminal entry"""
        self.terminal_entry.delete(0, 'end')
        self.terminal_entry.insert(0, command)
        self.terminal_entry.focus_set()

    def _execute_terminal_command(self):
        """Execute terminal command with live output"""
        command = self.terminal_entry.get().strip()
        if not command:
            messagebox.showwarning("Input Required", "Please enter a command.")
            return
        
        if self.terminal_running:
            messagebox.showinfo("Command Running", "A command is already running. Please wait or stop it first.")
            return
        
        # Validate command (security check)
        if not command.startswith(('pip ', 'python -m pip')):
            messagebox.showerror("Invalid Command", "Only pip commands are allowed for security reasons.")
            return
        
        self.terminal_running = True
        self.execute_button.config(text="⏳ Running...", state='disabled')
        
        # Log the command
        self._terminal_log(f"\n$ {command}", 'command')
        
        # Run in background thread
        threading.Thread(target=self._terminal_worker, args=(command,), daemon=True).start()

    def _terminal_worker(self, command: str):
        """Background worker for terminal commands using sandbox"""
        try:
            if self.sandbox_initialized and command.startswith('pip '):
                # Use sandbox for pip commands
                package_name = command[4:].strip()  # Remove 'pip ' prefix
                if package_name.startswith('install '):
                    package_name = package_name[8:].strip()  # Remove 'install ' prefix
                    
                    def progress_callback(message):
                        self.root.after(0, self._terminal_log, message, 'success')
                    
                    result = self.sandbox.install_package(package_name, progress_callback)
                    
                    # Update UI on main thread
                    if result['success']:
                        self.root.after(0, self._terminal_log, result['output'], 'success')
                        self.root.after(0, self._terminal_log, f"\n✅ Package installed successfully in sandbox", 'success')
                    else:
                        self.root.after(0, self._terminal_log, result['error'], 'error')
                        self.root.after(0, self._terminal_log, f"\n❌ Package installation failed", 'error')
                else:
                    # Other pip commands
                    result = self.sandbox._run_pip_command(package_name)
                    self.root.after(0, self._terminal_log, result['output'], 'success' if result['success'] else 'error')
                    
            else:
                # Fallback to direct execution (not recommended)
                self.root.after(0, self._terminal_log, "⚠️ Sandbox not available - using direct execution", 'warning')
                self._terminal_worker_fallback(command)
                
        except Exception as e:
            self.root.after(0, self._terminal_log, f"\n❌ Error executing command: {e}", 'error')
        
        finally:
            # Reset UI state on main thread
            self.root.after(0, self._terminal_command_finished)

    def _terminal_worker_fallback(self, command: str):
        """Fallback terminal worker for direct execution"""
        try:
            import subprocess
            
            # Split command for subprocess
            cmd_parts = command.split()
            
            # Start the process
            self.terminal_process = subprocess.Popen(
                cmd_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output line by line
            for line in iter(self.terminal_process.stdout.readline, ''):
                if not self.terminal_running:
                    break
                
                # Update UI on main thread
                self.root.after(0, self._terminal_log, line.rstrip(), 'success')
            
            # Wait for process to complete
            return_code = self.terminal_process.wait()
            
            # Update UI on main thread
            if return_code == 0:
                self.root.after(0, self._terminal_log, f"\n✅ Command completed successfully (exit code: {return_code})", 'success')
            else:
                self.root.after(0, self._terminal_log, f"\n❌ Command failed (exit code: {return_code})", 'error')
            
        except Exception as e:
            self.root.after(0, self._terminal_log, f"\n❌ Error executing command: {e}", 'error')

    def _terminal_command_finished(self):
        """Reset terminal state after command completion"""
        self.terminal_running = False
        self.terminal_process = None
        self.execute_button.config(text="▶ Run", state='normal')
        self._terminal_log("=" * 50, 'info')

    def _stop_terminal_command(self):
        """Stop running terminal command"""
        if not self.terminal_running:
            messagebox.showinfo("No Command Running", "No command is currently running.")
            return
        
        if self.terminal_process:
            try:
                self.terminal_process.terminate()
                self._terminal_log("\n⏹️ Command stopped by user", 'warning')
            except Exception as e:
                self._terminal_log(f"\n❌ Error stopping command: {e}", 'error')
        
        self.terminal_running = False
        self.terminal_process = None
        self.execute_button.config(text="▶ Run", state='normal')

    def _clear_terminal(self):
        """Clear terminal output"""
        self.terminal_output.config(state='normal')
        self.terminal_output.delete('1.0', 'end')
        self.terminal_output.config(state='disabled')
        
        # Show welcome message again
        self._terminal_log("💻 Package Terminal Ready", 'info')
        self._terminal_log("Type 'pip install <package>' or use quick commands above", 'info')
        self._terminal_log("=" * 50, 'info')

    def _terminal_log(self, message: str, tag: str = None):
        """Log message to terminal output"""
        self.terminal_output.config(state='normal')
        self.terminal_output.insert('end', message + '\n', tag)
        self.terminal_output.config(state='disabled')
        self.terminal_output.see('end')

    def _initialize_sandbox(self):
        """Initialize sandbox environment in background"""
        def sandbox_init_worker():
            def progress_callback(message):
                self.root.after(0, lambda m=message: self.status_label.config(text=f"🏗️ {m}"))

            try:
                self.status_label.config(text="🏗️ Initializing secure sandbox...")
                success = self.sandbox.initialize(progress_callback)

                if success:
                    self.sandbox_initialized = True
                    self.root.after(0, lambda: self.status_label.config(text="✅ Sandbox ready - Installing common packages..."))
                    self.root.after(0, self._update_sandbox_status)

                    # Install common ML packages in background
                    self.sandbox.install_common_ml_packages(progress_callback)

                    self.root.after(0, lambda: self.status_label.config(text="✅ Sandbox ready - All packages installed!"))
                else:
                    self.root.after(0, lambda: self.status_label.config(text="❌ Sandbox initialization failed - Using restricted mode"))

            except Exception as e:
                print(f"❌ Sandbox initialization error: {e}")
                self.root.after(0, lambda: self.status_label.config(text="❌ Sandbox error - Using restricted mode"))

        # Run in background thread
        threading.Thread(target=sandbox_init_worker, daemon=True).start()

    def _update_sandbox_status(self):
        """Update UI elements with sandbox status"""
        if hasattr(self, 'sandbox_status_label'):
            if self.sandbox_initialized:
                self.sandbox_status_label.config(
                    text="🛡️ Sandbox: Active", 
                    foreground='#28a745'
                )
            else:
                self.sandbox_status_label.config(
                    text="⚠️ Sandbox: Inactive", 
                    foreground='#dc3545'
                )

    def _reset_sandbox(self):
        """Reset the sandbox environment"""
        if not hasattr(self, 'sandbox'):
            messagebox.showinfo("Sandbox", "Sandbox is not available.")
            return
        
        result = messagebox.askyesno(
            "Reset Sandbox", 
            "This will reset the sandbox environment and remove all installed packages.\n\n"
            "All code execution and package installations will be affected.\n\n"
            "Continue?"
        )
        
        if result:
            def reset_worker():
                try:
                    self.root.after(0, lambda: self.status_label.config(text="🔄 Resetting sandbox..."))
                    self.sandbox_initialized = False
                    
                    success = self.sandbox.reset_sandbox()
                    
                    if success:
                        self.sandbox_initialized = True
                        self.root.after(0, lambda: self.status_label.config(text="✅ Sandbox reset successfully"))
                        self.root.after(0, self._update_sandbox_status)
                        self.root.after(0, lambda: self._terminal_log("✅ Sandbox environment reset successfully", 'success'))
                    else:
                        self.root.after(0, lambda: self.status_label.config(text="❌ Sandbox reset failed"))
                        self.root.after(0, lambda: self._terminal_log("❌ Sandbox reset failed", 'error'))
                        
                except Exception as e:
                    error_msg = f"Sandbox reset error: {e}"
                    self.root.after(0, lambda: self.status_label.config(text="❌ Sandbox reset error"))
                    self.root.after(0, lambda: self._terminal_log(f"❌ {error_msg}", 'error'))
            
            threading.Thread(target=reset_worker, daemon=True).start()

    def _show_sandbox_info(self):
        """Show sandbox information"""
        if not hasattr(self, 'sandbox'):
            messagebox.showinfo("Sandbox", "Sandbox is not available.")
            return
        
        try:
            info = self.sandbox.get_sandbox_info()
            
            info_text = "🛡️ Sandbox Environment Information\n\n"
            info_text += f"Status: {'✅ Active' if info['initialized'] else '❌ Inactive'}\n"
            info_text += f"Base Directory: {info['base_dir']}\n"
            info_text += f"Virtual Environment: {info['venv_path']}\n"
            info_text += f"Workspace: {info['workspace_path']}\n"
            info_text += f"Python Executable: {info['python_executable']}\n\n"
            
            packages = info['installed_packages']
            info_text += f"📦 Installed Packages ({len(packages)}):\n"
            if packages:
                # Show first 10 packages
                for pkg in packages[:10]:
                    info_text += f"  • {pkg}\n"
                if len(packages) > 10:
                    info_text += f"  ... and {len(packages) - 10} more\n"
            else:
                info_text += "  No packages installed\n"
            
            info_text += "\n🔒 Security Features:\n"
            info_text += "  • Isolated virtual environment\n"
            info_text += "  • Code execution restrictions\n"
            info_text += "  • Safe package installation\n"
            info_text += "  • Automatic cleanup on exit\n"
            
            messagebox.showinfo("Sandbox Information", info_text)
            
        except Exception as e:
            messagebox.showerror("Sandbox Info Error", f"Could not get sandbox information: {e}")

    # Session management
    def _load_current_session(self):
        """Load current session content"""
        current_session = self.session_manager.get_session(
            self.session_manager.progress.current_session_id
        )
        if not current_session:
            return
        
        # Update session display
        self.current_session_label.config(text=f"Current: {current_session.title}")
        
        # Load reference code - temporarily enable editing to load content
        was_edit_mode = self.edit_mode_var.get()
        self.reference_text.config(state='normal')
        self.reference_text.delete('1.0', 'end')
        
        full_content = (
            current_session.description + "\n\n" + "="*60 + 
            "\nREFERENCE CODE TO TYPE:\n" + "="*60 + "\n\n" + 
            current_session.reference_code
        )
        self.reference_text.insert('1.0', full_content)
        
        # Restore edit mode state
        if not was_edit_mode:
            self.reference_text.config(state='disabled')
        
        # Clear editor
        self.code_editor.clear()
        
        # Update session dropdown
        session_mapping = {
            "python_fundamentals": "🐍 Python Fundamentals",
            "pytorch_numpy": "🔢 PyTorch & NumPy",
            "neural_networks": "🧠 Neural Networks",
            "backpropagation": "⬅️ Backpropagation",
            "python_data_structures": "📚 Python Data Structures",
            "numpy_fundamentals": "🔢 NumPy Fundamentals",
            "data_preprocessing": "🔄 Data Preprocessing",
            "linear_regression": "📈 Linear Regression",
            "logistic_regression": "🎯 Logistic Regression",
            "model_evaluation": "📊 Model Evaluation",
            "regularization": "🛡️ Regularization",
            "loss_optimizers": "📉 Loss & Optimizers",
            "llm_architecture": "🏗️ LLM Architecture",
            "tokenization_bpe": "🔤 Tokenization & BPE",
            "rope_attention": "🎯 RoPE & Attention",
            "rms_normalization": "⚖️ RMS Normalization",
            "ffn_activations": "🔄 FFN & Activations",
            "training_llms": "🚂 Training LLMs",
            "inference_generation": "🎯 Inference & Generation"
        }
        
        display_name = session_mapping.get(current_session.id, current_session.title)
        self.session_var.set(display_name)
        
        # Update visualization if available
        if current_session.visualization_type:
            self.visualization_manager.show_visualization(current_session.visualization_type)

        # Update progress
        self._update_progress_display()

    def _update_progress_display(self):
        """Update progress display"""
        completion_pct = self.session_manager.progress.get_completion_percentage()
        completed_count = len(self.session_manager.progress.completed_sessions)
        total_count = self.session_manager.progress.total_sessions
        
        self.progress_label.config(
            text=f"Progress: {completed_count}/{total_count} sessions ({completion_pct:.0f}%)"
        )

    def _show_initial_session_message(self):
        """Show initial session message with conversation history info"""
        current_language = self.language_selector.get_current_language()

        # Show session history if available
        stats = self.conversation_storage.get_session_stats(self.current_session_id)
        if stats['total_entries'] > 0:
            self._log_output(f"\n📚 Session History: You have {stats['total_entries']} saved conversations for this session", 'info')
            self._log_output(f"   First activity: {stats['first_interaction']}", 'info')
            self._log_output(f"   Last activity: {stats['last_interaction']}", 'info')
            if stats['code_snippets'] > 0:
                self._log_output(f"   Code snippets saved: {stats['code_snippets']}\n", 'success')

        if self.ai_system.is_available:
            initial_msg = self.ai_system.initial_session_message(
                self.session_manager.progress.current_session_id, current_language
            )
            self._log_output(f"🤖 Sandra: {initial_msg}", 'session_msg')
        else:
            messages = {
                Language.ENGLISH: "👋 Welcome! Start by typing the reference code from the left panel to practice.",
                Language.SPANISH: "👋 ¡Bienvenido! Comienza escribiendo el código de referencia del panel izquierdo para practicar.",
                Language.FRENCH: "👋 Bienvenue ! Commencez par taper le code de référence du panneau de gauche pour vous entraîner.",
                Language.HINDI: "👋 स्वागत! अभ्यास के लिए बाएं पैनल से संदर्भ कोड टाइप करना शुरू करें।",
                Language.ITALIAN: "👋 Benvenuto! Inizia digitando il codice di riferimento dal pannello di sinistra per esercitarti.",
                Language.PORTUGUESE: "👋 Bem-vindo! Comece digitando o código de referência do painel esquerdo para praticar."
            }
            message = messages.get(current_language, messages[Language.ENGLISH])
            self._log_output(message, 'session_msg')

    def _clear_output(self):
        """Clear output area"""
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', 'end')
        self.output_text.config(state='disabled')

    def _log_output(self, message, tag=None):
        """Log message to output"""
        self.output_text.config(state='normal')
        self.output_text.insert('end', message + '\n', tag)
        self.output_text.config(state='disabled')
        self.output_text.see('end')

    def _on_code_change(self, event=None):
        """Auto-save when user types or pastes code"""
        # Save current code to session storage (debounced)
        if hasattr(self, '_save_timer'):
            self.root.after_cancel(self._save_timer)

        self._save_timer = self.root.after(2000, self._auto_save_session_code)

    def _auto_save_session_code(self):
        """Auto-save current code for the session"""
        try:
            code = self.code_editor.get_text().strip()

            # Save to session code dictionary
            self.session_code[self.current_session_id] = code

            # Persist to file
            self._save_session_code_to_file()

            # Also save as conversation entry if there's meaningful code
            if code and len(code) > 10:
                entry = ConversationEntry(
                    session_id=self.current_session_id,
                    user_input="Code editor content",
                    ai_response="",
                    code_snippet=code
                )
                self.conversation_storage.save_conversation(entry)
        except Exception as e:
            print(f"❌ Auto-save error: {e}")
            import traceback
            traceback.print_exc()

    def _save_session_code_to_file(self):
        """Save all session codes to a persistent file"""
        try:
            import json
            from pathlib import Path

            storage_dir = Path.home() / '.convai' / 'sessions'
            storage_dir.mkdir(parents=True, exist_ok=True)

            code_file = storage_dir / 'session_codes.json'

            with open(code_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_code, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"❌ Could not save session code to file: {e}")
            import traceback
            traceback.print_exc()

    def _load_session_code(self):
        """Load saved code for the current session"""
        try:
            import json
            from pathlib import Path

            storage_dir = Path.home() / '.convai' / 'sessions'
            code_file = storage_dir / 'session_codes.json'

            if code_file.exists():
                with open(code_file, 'r', encoding='utf-8') as f:
                    self.session_code = json.load(f)

                # Load code for current session if it exists
                if self.current_session_id in self.session_code:
                    saved_code = self.session_code[self.current_session_id]

                    if saved_code:
                        self.code_editor.set_text(saved_code)
                        return

        except Exception as e:
            print(f"❌ Could not load session code: {e}")
            import traceback
            traceback.print_exc()

        # If no saved code, session_code is empty dict
        if not hasattr(self, 'session_code'):
            self.session_code = {}

    def _show_all_sessions_history(self):
        """Show progress across all learning sessions"""
        try:
            all_sessions = self.conversation_storage.get_all_sessions()

            if not all_sessions:
                messagebox.showinfo(
                    "Learning History",
                    "No learning history found yet.\n\nStart typing code or running exercises to build your learning history!"
                )
                return

            # Build summary message
            summary = "📚 YOUR LEARNING JOURNEY\n"
            summary += "=" * 50 + "\n\n"

            # Get session names mapping
            session_names = {
                "python_fundamentals": "🐍 Python Fundamentals",
                "pytorch_numpy": "🔢 PyTorch & NumPy",
                "neural_networks": "🧠 Neural Networks",
                "backpropagation": "⬅️ Backpropagation",
                "python_data_structures": "📚 Python Data Structures",
                "numpy_fundamentals": "🔢 NumPy Fundamentals",
                "data_preprocessing": "🔄 Data Preprocessing",
                "linear_regression": "📈 Linear Regression",
                "logistic_regression": "🎯 Logistic Regression",
                "model_evaluation": "📊 Model Evaluation",
                "regularization": "🛡️ Regularization",
                "loss_optimizers": "📉 Loss & Optimizers",
                "llm_architecture": "🏗️ LLM Architecture",
                "tokenization_bpe": "🔤 Tokenization & BPE",
                "rope_attention": "🎯 RoPE & Attention",
                "rms_normalization": "⚖️ RMS Normalization",
                "ffn_activations": "🔄 FFN & Activations",
                "training_llms": "🚂 Training LLMs",
                "inference_generation": "🎯 Inference & Generation"
            }

            total_conversations = 0
            for session_id, info in sorted(all_sessions.items(), key=lambda x: x[1]['last_updated'], reverse=True):
                session_name = session_names.get(session_id, session_id)
                count = info['conversation_count']
                total_conversations += count
                last_updated = info['last_updated'].split('T')[0]  # Just the date

                summary += f"{session_name}\n"
                summary += f"  Conversations: {count}\n"
                summary += f"  Last activity: {last_updated}\n\n"

            summary += "=" * 50 + "\n"
            summary += f"TOTAL CONVERSATIONS: {total_conversations}\n"
            summary += f"SESSIONS EXPLORED: {len(all_sessions)}\n"
            summary += f"\n💾 Saved at: ~/.convai/conversations/"

            # Show in output area
            self._clear_output()
            self._log_output(summary, 'info')
            self.status_label.config(text=f"📊 Showing learning history ({total_conversations} total conversations)")

        except Exception as e:
            messagebox.showerror("Error", f"Could not load learning history:\n{str(e)}")

    def _open_conversations_folder(self):
        """Open the folder where conversations are saved"""
        try:
            from pathlib import Path
            storage_dir = Path.home() / '.convai' / 'conversations'

            if not storage_dir.exists():
                messagebox.showinfo(
                    "Folder Not Found",
                    f"No conversations saved yet.\n\nConversations will be saved to:\n{storage_dir}"
                )
                return

            # Open folder in file explorer
            import platform
            if platform.system() == "Windows":
                os.startfile(storage_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", storage_dir])
            else:  # Linux
                subprocess.Popen(["xdg-open", storage_dir])

            self.status_label.config(text=f"📁 Opened conversations folder")

        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")

    def _install_package(self, package_name: str):
        """Install a Python package"""
        if package_name in self.installed_packages:
            self._log_output(f"📦 Package '{package_name}' is already installed.", 'info')
            return True
            
        self._log_output(f"📥 Installing package: {package_name}...", 'info')
        self.status_label.config(text=f"Installing {package_name}...")
        
        try:
            # Use subprocess to install the package
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode == 0:
                self.installed_packages.add(package_name)
                self._log_output(f"✅ Successfully installed: {package_name}", 'success')
                self.status_label.config(text=f"✅ Package {package_name} installed")
                return True
            else:
                self._log_output(f"❌ Failed to install {package_name}:\n{result.stderr}", 'error')
                self.status_label.config(text=f"❌ Failed to install {package_name}")
                return False
                
        except subprocess.TimeoutExpired:
            self._log_output(f"⏰ Installation timeout for {package_name}", 'error')
            self.status_label.config(text=f"⏰ Installation timeout for {package_name}")
            return False
        except Exception as e:
            self._log_output(f"❌ Installation error for {package_name}: {e}", 'error')
            self.status_label.config(text=f"❌ Installation error for {package_name}")
            return False

    def _check_and_suggest_packages(self, error_msg: str):
        """Check error message for missing packages and suggest installation"""
        import re
        
        # Common patterns for missing packages
        patterns = [
            r"No module named '([^']+)'",
            r"ModuleNotFoundError: No module named '([^']+)'",
            r"ImportError: No module named ([^\s]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_msg)
            if match:
                package_name = match.group(1)
                self._suggest_package_installation(package_name)
                return
    
    def _suggest_package_installation(self, package_name: str):
        """Suggest package installation to user in sandbox"""
        result = messagebox.askyesno(
            "Missing Package",
            f"The package '{package_name}' is not installed in the sandbox.\n\n"
            f"Would you like to install it now?\n\n"
            f"This will run: pip install {package_name} (in sandbox)"
        )

        if result:
            # Install in sandbox using background thread
            def install_in_sandbox():
                if self.sandbox_initialized:
                    def progress_callback(message):
                        self.root.after(0, lambda m=message: self._log_output(m, 'info'))

                    self._log_output(f"📥 Installing {package_name} in sandbox...", 'info')
                    result = self.sandbox.install_package(package_name, progress_callback)

                    if result['success']:
                        self.root.after(0, lambda: self._log_output(f"✅ {package_name} installed successfully in sandbox! Try running your code again.", 'success'))
                    else:
                        self.root.after(0, lambda: self._log_output(f"❌ Failed to install {package_name}: {result.get('error', 'Unknown error')}", 'error'))
                else:
                    self.root.after(0, lambda: self._log_output("❌ Sandbox not initialized. Please use the Terminal tab to install packages.", 'error'))

            threading.Thread(target=install_in_sandbox, daemon=True).start()

    # Real-time tutor methods
    def _toggle_narration(self):
        """Toggle AI Tutor Narration on/off"""
        if not self.ai_tutor_narrator:
            messagebox.showwarning(
                "AI Tutor Narrator",
                "AI Tutor Narrator is not available.\nBoth AI system and TTS must be initialized."
            )
            return

        # Get current status
        status = self.ai_tutor_narrator.get_status()

        if status['is_narrating']:
            # Stop narration
            self.ai_tutor_narrator.stop_narration()
            self.narration_button.config(text="🎙️ Start Narration")
            self.status_label.config(text="🔇 Narration stopped")
        else:
            # Start narration
            session_id = self.session_manager.progress.current_session_id
            current_session = self.session_manager.get_session(session_id)
            if not current_session:
                messagebox.showwarning(
                    "AI Tutor Narrator",
                    "No session loaded. Please select a session first."
                )
                return

            # Clear the editor to start fresh
            if messagebox.askyesno(
                "Start Narration",
                f"Starting AI Tutor Narration for:\n{current_session.title}\n\n"
                "The code editor will be cleared.\nSandra will guide you line by line.\n\n"
                "Ready to begin?"
            ):
                self.code_editor.clear()
                self.ai_tutor_narrator.start_narration(
                    session_title=current_session.title,
                    session_description=current_session.description,
                    reference_code=current_session.reference_code
                )
                self.narration_button.config(text="🔇 Stop Narration")
                self.status_label.config(text=f"🎙️ Sandra is teaching: {current_session.title}")

    def _repeat_current_line(self):
        """Repeat the current line instruction"""
        if not self.ai_tutor_narrator:
            messagebox.showinfo("Repeat Line", "AI Tutor Narrator is not available.")
            return

        status = self.ai_tutor_narrator.get_status()
        if not status['is_narrating']:
            messagebox.showinfo("Repeat Line", "Narration is not active. Start narration first!")
            return

        # Call the repeat method
        self.ai_tutor_narrator.repeat_current_line()

    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to exit ConvAI Innovations?"):
            # Save current code before closing
            try:
                current_code = self.code_editor.get_text().strip()

                if current_code:
                    self.session_code[self.current_session_id] = current_code
                    self._save_session_code_to_file()
            except Exception as e:
                print(f"❌ Could not save code on close: {e}")
                import traceback
                traceback.print_exc()

            # Stop AI tutor narrator if active
            if self.ai_tutor_narrator:
                self.ai_tutor_narrator.stop_narration()

            self.tts_system.stop_speech()
            self.generation_stop_event.set()  # Stop any ongoing generation
            self.executor.shutdown(wait=False)
            self.root.destroy()


def main():
    """Main application entry point"""
    # Check dependencies
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        TRANSFORMERS_AVAILABLE = True
    except ImportError:
        TRANSFORMERS_AVAILABLE = False
        messagebox.showerror(
            "Dependency Error", 
            "Transformers library not found. Please install:\npip install transformers torch"
        )
        return
        
    try:
        from kokoro.pipeline import KPipeline
        import torch
        import sounddevice as sd
        KOKORO_TTS_AVAILABLE = True
    except ImportError:
        KOKORO_TTS_AVAILABLE = False
        messagebox.showwarning(
            "Audio Warning", 
            "Kokoro TTS not available. Audio features will be limited.\n"
            "To enable full audio: pip install kokoro-tts torch sounddevice"
        )

    # Initialize main window
    root = tk.Tk()
    root.withdraw()  # Hide until setup complete

    def on_setup_complete(model_path, ai_system=None):
        # Model path can be None when using default Hugging Face models
        root.deiconify()
        app = SessionBasedLLMLearningDashboard(root, model_path, ai_system)

    # Start model download and setup
    downloader = ModelDownloader(on_complete=on_setup_complete)
    downloader.run()
    
    # Start main event loop
    root.mainloop()


if __name__ == "__main__":
    main()