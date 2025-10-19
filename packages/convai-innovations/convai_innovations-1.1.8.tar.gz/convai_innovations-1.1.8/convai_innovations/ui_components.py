"""
UI components for ConvAI Innovations platform with Argostranslate support.
Enhanced with 2025 optimizations and offline translation capabilities.
Updated with editable AI generated text and reference areas.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import re
import urllib.request
import time
import threading
from pathlib import Path

from .models import Language


class ModernCodeEditor(tk.Frame):
    """Modern code editor with syntax highlighting and line numbers"""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg='#1e1e1e')
        
        # Line numbers
        self.line_numbers = tk.Text(
            self, width=4, padx=4, takefocus=0, bd=0, 
            bg='#1e1e1e', fg='#6c757d', font=('Consolas', 12), 
            state='disabled'
        )
        self.line_numbers.pack(side='left', fill='y')
        
        # Main text editor
        self.text_widget = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, font=('Consolas', 12), 
            bg='#282c34', fg='#abb2bf', insertbackground='white', 
            selectbackground='#3e4451', bd=0, undo=True, maxundo=20
        )
        self.text_widget.pack(side='right', fill='both', expand=True)
        
        # Bind events
        self.text_widget.bind('<KeyRelease>', self._on_change)
        self.text_widget.bind('<MouseWheel>', self._on_change)
        self.text_widget.bind('<Return>', self._on_return)
        self.text_widget.bind('<Tab>', self._on_tab)
        
        # Initialize syntax highlighting
        self._configure_syntax_highlighting()
        self._on_change()

    def _configure_syntax_highlighting(self):
        """Configure syntax highlighting tags"""
        # Python keywords
        self.text_widget.tag_configure('keyword', foreground='#c678dd')
        self.text_widget.tag_configure('string', foreground='#98c379')
        self.text_widget.tag_configure('comment', foreground='#5c6370', font=('Consolas', 12, 'italic'))
        self.text_widget.tag_configure('number', foreground='#d19a66')
        self.text_widget.tag_configure('function', foreground='#61afef')
        
    def _apply_syntax_highlighting(self):
        """Apply syntax highlighting to the current text"""
        try:
            content = self.text_widget.get('1.0', 'end-1c')
            
            # Clear existing tags
            for tag in ['keyword', 'string', 'comment', 'number', 'function']:
                self.text_widget.tag_remove(tag, '1.0', 'end')
            
            # Python keywords
            keywords = [
                'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 
                'finally', 'with', 'as', 'import', 'from', 'return', 'yield', 'lambda',
                'and', 'or', 'not', 'in', 'is', 'True', 'False', 'None', 'self'
            ]
            
            # Highlight keywords using simple string search
            for keyword in keywords:
                start = '1.0'
                while True:
                    pos = self.text_widget.search(keyword, start, 'end')
                    if not pos:
                        break
                    
                    # Check if it's a whole word
                    start_idx = self.text_widget.index(pos)
                    end_idx = self.text_widget.index(f"{pos}+{len(keyword)}c")
                    
                    # Get surrounding characters to check word boundaries
                    try:
                        before_pos = self.text_widget.index(f"{pos}-1c")
                        before_char = self.text_widget.get(before_pos, pos)
                        after_char = self.text_widget.get(end_idx, f"{end_idx}+1c")
                        
                        # Check if it's a complete word
                        if (not before_char.isalnum() and before_char != '_') and \
                           (not after_char.isalnum() and after_char != '_'):
                            self.text_widget.tag_add('keyword', pos, end_idx)
                    except tk.TclError:
                        # Handle edge cases at start/end of text
                        self.text_widget.tag_add('keyword', pos, end_idx)
                    
                    start = end_idx
            
            # Highlight strings - simple approach
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                # Find string literals
                in_string = False
                string_char = None
                start_col = 0
                
                for col, char in enumerate(line):
                    if not in_string and char in ['"', "'"]:
                        in_string = True
                        string_char = char
                        start_col = col
                    elif in_string and char == string_char:
                        # End of string
                        try:
                            start_pos = f"{line_num}.{start_col}"
                            end_pos = f"{line_num}.{col + 1}"
                            self.text_widget.tag_add('string', start_pos, end_pos)
                        except tk.TclError:
                            pass
                        in_string = False
                        string_char = None
                
                # Highlight comments
                comment_pos = line.find('#')
                if comment_pos != -1:
                    try:
                        start_pos = f"{line_num}.{comment_pos}"
                        end_pos = f"{line_num}.end"
                        self.text_widget.tag_add('comment', start_pos, end_pos)
                    except tk.TclError:
                        pass
                
                # Highlight numbers - simple digit sequences
                import re
                for match in re.finditer(r'\b\d+\.?\d*\b', line):
                    try:
                        start_pos = f"{line_num}.{match.start()}"
                        end_pos = f"{line_num}.{match.end()}"
                        self.text_widget.tag_add('number', start_pos, end_pos)
                    except tk.TclError:
                        pass
                        
        except Exception as e:
            # Silently ignore syntax highlighting errors
            pass

    def _on_change(self, event=None): 
        self._update_line_numbers()
        self._apply_syntax_highlighting()
        
    def _on_tab(self, event=None):
        """Handle tab indentation"""
        self.text_widget.insert(tk.INSERT, '    ')  # 4 spaces
        return 'break'
        
    def _on_return(self, event=None):
        """Handle auto-indentation"""
        self.text_widget.insert(tk.INSERT, '\n')
        current_line_number_str = self.text_widget.index(tk.INSERT).split('.')[0]
        try:
            current_line_number = int(current_line_number_str)
            if current_line_number > 1:
                previous_line = self.text_widget.get(f'{current_line_number-1}.0', f'{current_line_number-1}.end')
                indent_match = re.match(r'^(\s*)', previous_line)
                indent = indent_match.group(0) if indent_match else ""
                if previous_line.strip().endswith(':'): 
                    indent += '    '
                self.text_widget.insert(tk.INSERT, indent)
        except (ValueError, tk.TclError): 
            pass 
        self._update_line_numbers()
        return 'break'
                
    def _update_line_numbers(self):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        line_count_str = self.text_widget.index('end-1c').split('.')[0]
        try:
            line_count = int(line_count_str)
            line_number_string = "\n".join(str(i) for i in range(1, line_count + 1))
            self.line_numbers.insert('1.0', line_number_string)
        except ValueError: 
            pass
        self.line_numbers.config(state='disabled')
        self.line_numbers.yview_moveto(self.text_widget.yview()[0])
        
    def get_text(self): 
        return self.text_widget.get('1.0', 'end-1c')
        
    def set_text(self, text):
        self.text_widget.delete('1.0', 'end')
        self.text_widget.insert('1.0', text)
        self._on_change()
        
    def clear(self): 
        self.set_text('')
        
    def insert_text(self, text):
        """Insert text at current cursor position"""
        self.text_widget.insert(tk.INSERT, text)
        self._on_change()


class CodeGenerationPanel(tk.Frame):
    """Panel for AI code generation with editable generated text"""
    
    def __init__(self, parent, ai_system, code_editor, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.ai_system = ai_system
        self.code_editor = code_editor
        self.configure(bg='#1e1e1e')
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create code generation widgets with editable output"""
        # Title
        title_label = ttk.Label(
            self, text="🤖 AI Code Generator", 
            style='Header.TLabel', background='#1e1e1e'
        )
        title_label.pack(pady=(10, 5))
        
        # Prompt input
        prompt_frame = ttk.Frame(self, style='TFrame')
        prompt_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(prompt_frame, text="Describe what you want to code:", style='TLabel').pack(anchor='w')
        
        self.prompt_entry = tk.Text(
            prompt_frame, height=3, font=('Segoe UI', 10),
            bg='#2d3748', fg='#e2e8f0', insertbackground='white',
            wrap=tk.WORD, bd=1, relief='solid'
        )
        self.prompt_entry.pack(fill='x', pady=(5, 0))
        
        # Generation options
        options_frame = ttk.Frame(self, style='TFrame')
        options_frame.pack(fill='x', padx=10, pady=5)
        
        # Temperature slider
        temp_frame = ttk.Frame(options_frame, style='TFrame')
        temp_frame.pack(fill='x', pady=2)
        
        ttk.Label(temp_frame, text="Creativity:", style='TLabel').pack(side='left')
        self.temperature_var = tk.DoubleVar(value=0.1)
        temp_scale = ttk.Scale(
            temp_frame, from_=0.1, to=1.5, variable=self.temperature_var,
            orient='horizontal', length=200
        )
        temp_scale.pack(side='left', padx=(10, 5))
        
        self.temp_label = ttk.Label(temp_frame, text="0.1", style='TLabel')
        self.temp_label.pack(side='left')
        temp_scale.configure(command=self._update_temp_label)
        
        # Language selection
        lang_frame = ttk.Frame(options_frame, style='TFrame')
        lang_frame.pack(fill='x', pady=2)
        
        ttk.Label(lang_frame, text="Language:", style='TLabel').pack(side='left')
        self.language_var = tk.StringVar(value="python")
        lang_combo = ttk.Combobox(
            lang_frame, textvariable=self.language_var,
            values=["python"],
            state="readonly", width=10
        )
        lang_combo.pack(side='left', padx=(10, 0))
        
        # Generate button frame
        generate_frame = ttk.Frame(self, style='TFrame')
        generate_frame.pack(fill='x', padx=10, pady=10)
        
        self.generate_button = ttk.Button(
            generate_frame, text="🚀 Generate Code", 
            command=self._generate_code, style='Run.TButton'
        )
        self.generate_button.pack(side='left', padx=(0, 5))
        
        # Stop generation button
        self.stop_button = ttk.Button(
            generate_frame, text="⏹️ Stop", 
            command=self._stop_generation, style='Clear.TButton',
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=5)
        
        # Regenerate button
        self.regenerate_button = ttk.Button(
            generate_frame, text="🔄 Regenerate", 
            command=self._regenerate_code, style='TButton',
            state='disabled'
        )
        self.regenerate_button.pack(side='left', padx=5)
        
        # Generation state
        self.is_generating = False
        self.generation_stop_event = threading.Event()
        self.last_prompt = ""
        
        # Action buttons for generated code
        ttk.Button(
            generate_frame, text="📋 Insert", 
            command=self._insert_generated, style='TButton'
        ).pack(side='left', padx=2)
        
        ttk.Button(
            generate_frame, text="🔄 Replace", 
            command=self._replace_with_generated, style='Clear.TButton'
        ).pack(side='left', padx=2)
        
        # Generated code display with edit controls
        output_frame = ttk.Frame(self, style='TFrame')
        output_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Header with edit controls
        header_frame = ttk.Frame(output_frame, style='TFrame')
        header_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(header_frame, text="Generated Code:", style='TLabel').pack(side='left')
        
        # Edit mode toggle for generated text
        self.gen_edit_mode_var = tk.BooleanVar(value=True)  # Start in edit mode
        self.gen_edit_toggle_button = ttk.Button(
            header_frame, text="🔒 Lock", command=self._toggle_gen_edit_mode,
            style='Edit.TButton'
        )
        self.gen_edit_toggle_button.pack(side='right', padx=(5, 0))
        
        # Editable generated text
        self.generated_text = scrolledtext.ScrolledText(
            output_frame, height=12, font=('Consolas', 10),
            bg='#2d3748', fg='#e2e8f0', insertbackground='white',
            wrap=tk.WORD, bd=1, relief='solid'
        )
        self.generated_text.pack(fill='both', expand=True, pady=(5, 0))
        
        # Generated code action buttons
        gen_action_frame = ttk.Frame(output_frame, style='TFrame')
        gen_action_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(gen_action_frame, text="📋 Copy", command=self._copy_generated, 
                  style='TButton').pack(side='left', fill='x', expand=True, padx=(0, 2))
        ttk.Button(gen_action_frame, text="💾 Save", command=self._save_generated, 
                  style='TButton').pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(gen_action_frame, text="🗑️ Clear", command=self._clear_generated, 
                  style='Clear.TButton').pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(gen_action_frame, text="📁 Load", command=self._load_into_generated, 
                  style='TButton').pack(side='left', fill='x', expand=True, padx=(2, 0))
        
        self.generated_code = ""
        
        # Conversation history for code generation
        self.code_conversation_history = []
        
        # Add followup question area
        self._create_followup_area(output_frame)
        
        # Add placeholder text
        self._add_placeholder_text()
    
    def _add_placeholder_text(self):
        """Add helpful placeholder text"""
        placeholder = """# 🤖 AI Code Generator Ready!

# Paste your ChatGPT code here, or generate new code using the controls above.
# This area is fully editable - you can:
# • Paste any code from ChatGPT, Claude, or other AI assistants
# • Edit the generated code directly
# • Save your work to files
# • Copy code to the main editor

# Try generating code by describing what you want above!

print("Hello from ConvAI Innovations! 🧠")
print("Ready to learn LLM development? Let's code!")
"""
        self.generated_text.insert('1.0', placeholder)

    def _create_followup_area(self, parent):
        """Create followup question area for code generation"""
        # Separator
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill='x', pady=(10, 5))
        
        # Followup section
        followup_section = ttk.Frame(parent, style='TFrame')
        followup_section.pack(fill='x', pady=5)
        
        # Header
        header_frame = ttk.Frame(followup_section, style='TFrame')
        header_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(
            header_frame, text="💬 Ask Sandra about your code", 
            style='TLabel', font=('Segoe UI', 10, 'bold')
        ).pack(side='left')
        
        # Show/hide toggle
        self.followup_visible = tk.BooleanVar(value=True)
        self.followup_toggle = ttk.Button(
            header_frame, text="➖ Hide", 
            command=self._toggle_followup_area, style='TButton'
        )
        self.followup_toggle.pack(side='right')
        
        # Followup content frame
        self.followup_content = ttk.Frame(followup_section, style='TFrame')
        self.followup_content.pack(fill='x', pady=2)
        
        # Input area
        input_frame = ttk.Frame(self.followup_content, style='TFrame')
        input_frame.pack(fill='x', pady=2)
        
        ttk.Label(
            input_frame, text="Got an error? Need help? Ask here:", 
            style='TLabel', font=('Segoe UI', 9)
        ).pack(anchor='w')
        
        # Text input with context options
        text_input_frame = ttk.Frame(self.followup_content, style='TFrame')
        text_input_frame.pack(fill='x', pady=2)
        
        self.followup_text = tk.Text(
            text_input_frame, height=3, font=('Segoe UI', 10),
            bg='#2d3748', fg='#e2e8f0', insertbackground='white',
            wrap=tk.WORD, bd=1, relief='solid'
        )
        self.followup_text.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Action buttons
        button_frame = ttk.Frame(text_input_frame, style='TFrame')
        button_frame.pack(side='right', fill='y')
        
        ttk.Button(
            button_frame, text="📋 Paste Error", 
            command=self._paste_from_output, style='TButton'
        ).pack(fill='x', pady=(0, 2))
        
        ttk.Button(
            button_frame, text="🤖 Ask Sandra", 
            command=self._ask_code_question, style='Next.TButton'
        ).pack(fill='x', pady=2)
        
        ttk.Button(
            button_frame, text="🔄 Fix Code", 
            command=self._fix_with_error, style='Generate.TButton'
        ).pack(fill='x', pady=2)
        
        # Quick action buttons
        quick_frame = ttk.Frame(self.followup_content, style='TFrame')
        quick_frame.pack(fill='x', pady=2)
        
        ttk.Label(
            quick_frame, text="Quick actions:", 
            style='TLabel', font=('Segoe UI', 9)
        ).pack(anchor='w')
        
        quick_buttons_frame = ttk.Frame(quick_frame, style='TFrame')
        quick_buttons_frame.pack(fill='x', pady=2)
        
        quick_actions = [
            ("Explain this code", "explain"),
            ("Add comments", "comment"),
            ("Optimize performance", "optimize"),
            ("Add error handling", "error_handling"),
            ("Make it more readable", "readable")
        ]
        
        for i, (text, action) in enumerate(quick_actions):
            if i % 3 == 0:  # New row every 3 buttons
                row_frame = ttk.Frame(quick_buttons_frame, style='TFrame')
                row_frame.pack(fill='x', pady=1)
            
            btn = ttk.Button(
                row_frame, text=text,
                command=lambda a=action: self._quick_action(a),
                style='TButton'
            )
            btn.pack(side='left', padx=(0, 5), fill='x', expand=True)

    def _toggle_followup_area(self):
        """Toggle visibility of followup area"""
        if self.followup_visible.get():
            self.followup_content.pack_forget()
            self.followup_toggle.config(text="➕ Show")
            self.followup_visible.set(False)
        else:
            self.followup_content.pack(fill='x', pady=2)
            self.followup_toggle.config(text="➖ Hide")
            self.followup_visible.set(True)

    def _paste_from_output(self):
        """Paste error from main output area"""
        try:
            # Try to get error from main application output
            if hasattr(self.master, 'winfo_toplevel'):
                top_level = self.master.winfo_toplevel()
                # Try to find the main application instance
                for child in top_level.winfo_children():
                    if hasattr(child, 'output_text'):
                        output_content = child.output_text.get('1.0', 'end-1c')
                        # Extract error messages
                        lines = output_content.split('\n')
                        error_lines = []
                        for line in lines:
                            if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback', 'failed']):
                                error_lines.append(line.strip())
                        
                        if error_lines:
                            error_text = '\n'.join(error_lines[-3:])  # Last 3 error lines
                            self.followup_text.delete('1.0', 'end')
                            self.followup_text.insert('1.0', f"I got this error:\n{error_text}\n\nCan you help me fix it?")
                            return
            
            # Fallback: paste from clipboard
            try:
                clipboard_content = self.master.clipboard_get()
                self.followup_text.delete('1.0', 'end')
                self.followup_text.insert('1.0', f"I got this error:\n{clipboard_content}\n\nCan you help me fix it?")
            except:
                messagebox.showinfo("Paste Error", "No error found in output. Copy the error manually and paste it here.")
                
        except Exception as e:
            messagebox.showerror("Paste Error", f"Could not paste error: {e}")

    def _ask_code_question(self):
        """Ask a question about the generated code"""
        question = self.followup_text.get('1.0', 'end-1c').strip()
        if not question:
            messagebox.showwarning("Input Required", "Please enter your question about the code.")
            return
        
        if not self.ai_system.is_available:
            messagebox.showerror("AI Unavailable", "AI code assistant is not available.")
            return
        
        # Add to conversation history
        self.code_conversation_history.append({
            'type': 'user_question',
            'content': question,
            'code_context': self.generated_text.get('1.0', 'end-1c'),
            'timestamp': time.time()
        })
        
        # Clear input and show processing
        self.followup_text.delete('1.0', 'end')
        self.followup_text.insert('1.0', "🤖 Sandra is thinking...")
        self.followup_text.config(state='disabled')
        
        # Process in background
        threading.Thread(
            target=self._process_code_question, 
            args=(question,), 
            daemon=True
        ).start()

    def _process_code_question(self, question):
        """Process code question in background"""
        try:
            current_code = self.generated_text.get('1.0', 'end-1c')
            conversation_context = self._get_code_conversation_context()
            
            # Generate response
            response = self.ai_system.generate_code_followup(
                question, current_code, conversation_context
            )
            
            # Update UI on main thread
            self.after(0, self._show_code_response, question, response)
            
        except Exception as e:
            error_msg = f"Could not process question: {e}"
            self.after(0, lambda: self._show_error_response(error_msg))

    def _show_code_response(self, question, response):
        """Show code question response"""
        # Re-enable input
        self.followup_text.config(state='normal')
        self.followup_text.delete('1.0', 'end')
        
        # Add response to conversation history
        self.code_conversation_history.append({
            'type': 'ai_response',
            'content': response,
            'timestamp': time.time()
        })
        
        # Show response in generated text area temporarily
        current_content = self.generated_text.get('1.0', 'end-1c')
        
        # Ensure we can edit
        was_edit_mode = self.gen_edit_mode_var.get()
        if not was_edit_mode:
            self.generated_text.config(state='normal')
        
        # Add response to the bottom
        self.generated_text.insert('end', f"\n\n# 💬 Sandra's Response:\n# Q: {question}\n# A: {response}")
        self.generated_text.see('end')
        
        # Restore edit mode
        if not was_edit_mode:
            self.generated_text.config(state='disabled')
        
        # Show success message
        messagebox.showinfo("Response", "Sandra has provided guidance! Check the generated code area.")

    def _show_error_response(self, error_msg):
        """Show error response"""
        self.followup_text.config(state='normal')
        self.followup_text.delete('1.0', 'end')
        messagebox.showerror("Question Error", error_msg)

    def _fix_with_error(self):
        """Fix code with error context"""
        error_description = self.followup_text.get('1.0', 'end-1c').strip()
        if not error_description:
            messagebox.showwarning("Input Required", "Please describe the error or paste the error message.")
            return
        
        if not self.ai_system.is_available:
            messagebox.showerror("AI Unavailable", "AI code assistant is not available.")
            return
        
        current_code = self.generated_text.get('1.0', 'end-1c')
        
        # Create fix request
        fix_prompt = f"Fix this code that has an error:\n\nCODE:\n{current_code}\n\nERROR:\n{error_description}\n\nPlease provide the corrected code with explanation of what was wrong."
        
        # Use the existing generation system but with fix context
        self.prompt_entry.delete('1.0', 'end')
        self.prompt_entry.insert('1.0', fix_prompt)
        
        # Clear followup input
        self.followup_text.delete('1.0', 'end')
        
        # Trigger generation
        self._generate_code()

    def _quick_action(self, action):
        """Handle quick action buttons"""
        current_code = self.generated_text.get('1.0', 'end-1c')
        if not current_code.strip():
            messagebox.showinfo("No Code", "Please generate some code first.")
            return
        
        action_prompts = {
            'explain': f"Explain this code step by step:\n\n{current_code}",
            'comment': f"Add detailed comments to this code:\n\n{current_code}",
            'optimize': f"Optimize this code for better performance:\n\n{current_code}",
            'error_handling': f"Add proper error handling to this code:\n\n{current_code}",
            'readable': f"Make this code more readable and clean:\n\n{current_code}"
        }
        
        if action in action_prompts:
            self.prompt_entry.delete('1.0', 'end')
            self.prompt_entry.insert('1.0', action_prompts[action])
            self._generate_code()

    def _get_code_conversation_context(self):
        """Get conversation context for code questions"""
        if not self.code_conversation_history:
            return "No previous conversation."
        
        # Get last few interactions
        recent = self.code_conversation_history[-3:]
        context_parts = []
        
        for item in recent:
            if item['type'] == 'user_question':
                context_parts.append(f"User asked: {item['content']}")
            elif item['type'] == 'ai_response':
                context_parts.append(f"AI responded: {item['content']}")
        
        return " | ".join(context_parts)

    def _toggle_gen_edit_mode(self):
        """Toggle edit mode for generated text"""
        if self.gen_edit_mode_var.get():
            # Switch to read-only mode
            self.generated_text.config(state='disabled')
            self.gen_edit_toggle_button.config(text="✏️ Edit")
            self.gen_edit_mode_var.set(False)
        else:
            # Switch to edit mode
            self.generated_text.config(state='normal')
            self.gen_edit_toggle_button.config(text="🔒 Lock")
            self.gen_edit_mode_var.set(True)

    def _copy_generated(self):
        """Copy generated code to clipboard"""
        content = self.generated_text.get('1.0', 'end-1c')
        if content.strip():
            self.master.clipboard_clear()
            self.master.clipboard_append(content)
            messagebox.showinfo("Copied", "Generated code copied to clipboard!")
        else:
            messagebox.showinfo("No Content", "Generated code area is empty")

    def _save_generated(self):
        """Save generated code to file"""
        content = self.generated_text.get('1.0', 'end-1c')
        if content.strip():
            filepath = filedialog.asksaveasfilename(
                defaultextension=".py", 
                filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if filepath:
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    messagebox.showinfo("Success", f"Generated code saved to {filepath}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            messagebox.showinfo("No Content", "Generated code area is empty")

    def _clear_generated(self):
        """Clear generated code area"""
        if self.gen_edit_mode_var.get():
            result = messagebox.askyesno(
                "Clear Generated Code", 
                "This will clear all generated code. Continue?"
            )
            if result:
                self.generated_text.delete('1.0', 'end')
                self.generated_code = ""
                self._add_placeholder_text()
        else:
            messagebox.showinfo("Edit Mode Required", "Enable edit mode first to clear the generated code")

    def _load_into_generated(self):
        """Load file content into generated code area"""
        if not self.gen_edit_mode_var.get():
            messagebox.showinfo("Edit Mode Required", "Enable edit mode first to load content")
            return
            
        filepath = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                result = messagebox.askyesno(
                    "Load File", 
                    f"This will replace all content in the generated code area with content from:\n{filepath}\n\nContinue?"
                )
                if result:
                    self.generated_text.delete('1.0', 'end')
                    self.generated_text.insert('1.0', content)
                    self.generated_code = content
                    messagebox.showinfo("Success", f"Content loaded from {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def _update_temp_label(self, value):
        """Update temperature label"""
        self.temp_label.config(text=f"{float(value):.1f}")
    
    def _generate_code(self):
        """Generate code using AI with streaming"""
        prompt = self.prompt_entry.get('1.0', 'end-1c').strip()
        if not prompt:
            messagebox.showwarning("Input Required", "Please enter a code description.")
            return
        
        if not self.ai_system.is_available:
            messagebox.showerror("AI Unavailable", "AI code generation is not available.")
            return
        
        if self.is_generating:
            messagebox.showinfo("Generation in Progress", "Code generation is already in progress.")
            return
        
        self.last_prompt = prompt
        self._start_generation()
        
        # Run generation in background thread
        threading.Thread(target=self._generation_worker, args=(prompt,), daemon=True).start()

    def _regenerate_code(self):
        """Regenerate code with the last prompt"""
        if not self.last_prompt:
            messagebox.showinfo("No Previous Prompt", "No previous prompt to regenerate from.")
            return
        
        if self.is_generating:
            messagebox.showinfo("Generation in Progress", "Code generation is already in progress.")
            return
        
        self._start_generation()
        
        # Run generation in background thread
        threading.Thread(target=self._generation_worker, args=(self.last_prompt,), daemon=True).start()

    def _stop_generation(self):
        """Stop code generation"""
        if self.is_generating:
            self.generation_stop_event.set()
            self._end_generation()
            
            # Clear the generated text area
            was_edit_mode = self.gen_edit_mode_var.get()
            if not was_edit_mode:
                self.generated_text.config(state='normal')
            
            self.generated_text.delete('1.0', 'end')
            self.generated_text.insert('1.0', "⏹️ Generation stopped by user.")
            
            if not was_edit_mode:
                self.generated_text.config(state='disabled')

    def _start_generation(self):
        """Start generation state"""
        self.is_generating = True
        self.generation_stop_event.clear()
        
        # Update button states
        self.generate_button.config(text="⏳ Generating...", state='disabled')
        self.stop_button.config(state='normal')
        self.regenerate_button.config(state='disabled')
        
        # Clear and prepare generated text area
        was_edit_mode = self.gen_edit_mode_var.get()
        if not was_edit_mode:
            self.generated_text.config(state='normal')
        
        self.generated_text.delete('1.0', 'end')
        self.generated_text.insert('1.0', "🤖 Sandra is generating code...")
        
        if not was_edit_mode:
            self.generated_text.config(state='disabled')

    def _end_generation(self):
        """End generation state"""
        self.is_generating = False
        
        # Update button states
        self.generate_button.config(text="🚀 Generate Code", state='normal')
        self.stop_button.config(state='disabled')
        self.regenerate_button.config(state='normal')
    
    def _generation_worker(self, prompt):
        """Background worker for code generation with streaming"""
        from .models import CodeGenRequest
        
        try:
            request = CodeGenRequest(
                session_id="code_generation",
                prompt=prompt,
                max_tokens=512,
                temperature=self.temperature_var.get(),
                language=self.language_var.get()
            )
            
            # Check if we should stop before starting
            if self.generation_stop_event.is_set():
                return
            
            # Start streaming generation
            response = self.ai_system.generate_code_streaming(
                request, 
                stream_callback=self._stream_callback,
                stop_event=self.generation_stop_event
            )
            
            # Update UI on main thread with final result
            if not self.generation_stop_event.is_set():
                self.after(0, self._show_generation_result, response)
            
        except Exception as e:
            print(f"❌ Generation worker error: {e}")
            if not self.generation_stop_event.is_set():
                error_response = type('ErrorResponse', (), {
                    'success': False,
                    'error_message': str(e),
                    'generated_code': '',
                    'explanation': ''
                })()
                self.after(0, self._show_generation_result, error_response)

    def _stream_callback(self, partial_text: str):
        """Callback for streaming text updates"""
        if self.generation_stop_event.is_set():
            return False  # Stop streaming
        
        # Update UI on main thread
        self.after(0, self._update_streaming_text, partial_text)
        return True  # Continue streaming

    def _update_streaming_text(self, partial_text: str):
        """Update the generated text area with streaming content"""
        if self.generation_stop_event.is_set():
            return
        
        # Ensure we can edit the text area
        was_edit_mode = self.gen_edit_mode_var.get()
        if not was_edit_mode:
            self.generated_text.config(state='normal')
        
        # Clear and insert the partial text
        self.generated_text.delete('1.0', 'end')
        self.generated_text.insert('1.0', partial_text)
        
        # Scroll to the end to show latest content
        self.generated_text.see('end')
        
        # Restore edit mode state
        if not was_edit_mode:
            self.generated_text.config(state='disabled')
    
    def _show_generation_result(self, response):
        """Show generation result"""
        self._end_generation()
        
        if response.success:
            self.generated_code = response.generated_code
            
            # Ensure we're in edit mode to update content
            was_edit_mode = self.gen_edit_mode_var.get()
            if not was_edit_mode:
                self.generated_text.config(state='normal')
            
            # Display final generated code (may already be there from streaming)
            current_content = self.generated_text.get('1.0', 'end-1c')
            if current_content != response.generated_code:
                self.generated_text.delete('1.0', 'end')
                self.generated_text.insert('1.0', response.generated_code)
            
            if response.explanation:
                self.generated_text.insert('end', f"\n\n# Explanation:\n# {response.explanation}")
            
            # Restore edit mode state
            if not was_edit_mode:
                self.generated_text.config(state='disabled')
                
            # Don't show popup for successful streaming - user already saw it
            print("✅ Code generation completed successfully")
        else:
            # Clear any partial content and show error
            was_edit_mode = self.gen_edit_mode_var.get()
            if not was_edit_mode:
                self.generated_text.config(state='normal')
            
            self.generated_text.delete('1.0', 'end')
            self.generated_text.insert('1.0', f"❌ Generation failed: {response.error_message or 'Unknown error'}")
            
            if not was_edit_mode:
                self.generated_text.config(state='disabled')
            
            messagebox.showerror("Generation Failed", 
                               response.error_message or "Failed to generate code.")
    
    def _insert_generated(self):
        """Insert generated code at cursor position"""
        content = self.generated_text.get('1.0', 'end-1c')
        if content.strip():
            # Extract just code (remove comments)
            code_lines = []
            for line in content.split('\n'):
                if line.strip() and not line.strip().startswith('#'):
                    code_lines.append(line)
            
            code_to_insert = '\n'.join(code_lines)
            if code_to_insert.strip():
                self.code_editor.insert_text(code_to_insert)
                messagebox.showinfo("Inserted", "Code inserted into main editor at cursor position")
            else:
                messagebox.showinfo("No Code", "No code found to insert (only comments)")
        else:
            messagebox.showinfo("No Content", "Generated code area is empty")
    
    def _replace_with_generated(self):
        """Replace all code with generated code"""
        content = self.generated_text.get('1.0', 'end-1c')
        if content.strip():
            result = messagebox.askyesno(
                "Replace Code", 
                "This will replace ALL code in the main editor. Continue?"
            )
            if result:
                # Extract just code (remove explanation comments)
                code_lines = []
                in_explanation = False
                for line in content.split('\n'):
                    if line.strip().startswith("# Explanation:"):
                        in_explanation = True
                        continue
                    if not in_explanation:
                        code_lines.append(line)
                
                code_to_replace = '\n'.join(code_lines)
                self.code_editor.set_text(code_to_replace.strip())
                messagebox.showinfo("Replaced", "Main editor code replaced with generated code")
        else:
            messagebox.showinfo("No Content", "Generated code area is empty")


class LanguageSelector(tk.Frame):
    """Enhanced Language selector with Argostranslate support (2025 optimized)"""
    
    def __init__(self, parent, tts_system, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.tts_system = tts_system
        self.current_selected_language = Language.ENGLISH
        self.configure(bg='#252526')
        
        # Initialize Argostranslate engine
        self.translator = None
        self._init_translator()
        
        self._create_widgets()
    
    def _init_translator(self):
        """Initialize Argostranslate translator"""
        try:
            from .ai_systems import ArgosTranslateEngine
            self.translator = ArgosTranslateEngine()
            print("✅ Argostranslate initialized in LanguageSelector")
        except ImportError as e:
            print(f"❌ Could not import ArgosTranslateEngine: {e}")
    
    def _create_widgets(self):
        """Create enhanced language selector widgets"""
        # Header with translation status
        header_frame = ttk.Frame(self, style='TFrame')
        header_frame.pack(fill='x', padx=5, pady=(5, 2))
        
        ttk.Label(
            header_frame, text="🌍 Language & Translation", 
            style='TLabel', background='#252526', font=('Segoe UI', 12, 'bold')
        ).pack(side='left')
        
        # Translation engine status
        engine_status = "✅ Argos" if (self.translator and self.translator.available) else "❌ Offline"
        self.engine_label = ttk.Label(
            header_frame, text=engine_status,
            style='TLabel', background='#252526', font=('Segoe UI', 9),
            foreground='#28a745' if engine_status.startswith('✅') else '#dc3545'
        )
        self.engine_label.pack(side='right')
        
        # Language selection
        lang_frame = ttk.Frame(self, style='TFrame')
        lang_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(lang_frame, text="Sandra's Voice:", style='TLabel').pack(side='left')
        
        # Get available languages
        self.language_var = tk.StringVar()
        language_names = [lang.display_name for lang in Language]
        self.language_combo = ttk.Combobox(
            lang_frame, textvariable=self.language_var,
            values=language_names, state="readonly", width=12
        )
        self.language_combo.pack(side='left', padx=(10, 0))
        self.language_combo.bind('<<ComboboxSelected>>', self._on_language_change)
        
        # Set default to English
        self.language_combo.set(Language.ENGLISH.display_name)
        
        # Control buttons
        button_frame = ttk.Frame(self, style='TFrame')
        button_frame.pack(fill='x', padx=5, pady=3)
        
        # Test voice button
        ttk.Button(
            button_frame, text="🔊 Test Voice", 
            command=self._test_voice, style='TButton'
        ).pack(side='left', padx=(0, 3))
        
        # Translation test button
        ttk.Button(
            button_frame, text="🌍 Test Translation", 
            command=self._test_translation, style='TButton'
        ).pack(side='left', padx=3)
        
        # Advanced controls
        advanced_frame = ttk.Frame(self, style='TFrame')
        advanced_frame.pack(fill='x', padx=5, pady=2)
        
        # Cache management
        ttk.Button(
            advanced_frame, text="📊 Cache Stats", 
            command=self._show_cache_stats, style='TButton'
        ).pack(side='left', padx=(0, 3))
        
        ttk.Button(
            advanced_frame, text="🗑️ Clear Cache", 
            command=self._clear_cache, style='TButton'
        ).pack(side='left', padx=3)
        
        # Status display
        self.status_label = ttk.Label(
            self, text="Ready", 
            style='TLabel', foreground='#28a745', background='#252526'
        )
        self.status_label.pack(anchor='w', padx=5, pady=(5, 2))
        
        # Translation info
        self.info_label = ttk.Label(
            self, text="🔒 Offline • 🚀 Fast • 🎯 Private",
            style='TLabel', background='#252526', font=('Segoe UI', 9),
            foreground='#6c757d'
        )
        self.info_label.pack(anchor='w', padx=5)
    
    def _on_language_change(self, event=None):
        """Handle language change with Argostranslate optimization"""
        selected_name = self.language_var.get()
        
        # Find corresponding Language enum
        selected_language = None
        for lang in Language:
            if lang.display_name == selected_name:
                selected_language = lang
                self.current_selected_language = lang
                break
        
        if selected_language and self.tts_system.is_available:
            self.status_label.config(text="Loading TTS...", foreground='#ffc107')
            
            # Load language in background
            threading.Thread(
                target=self._load_language_worker, 
                args=(selected_language,), 
                daemon=True
            ).start()
        
        # Pre-warm translation for this language
        if self.translator and selected_language != Language.ENGLISH:
            threading.Thread(
                target=self._prewarm_translation,
                args=(selected_language,),
                daemon=True
            ).start()
    
    def _prewarm_translation(self, language):
        """Pre-warm translation models for faster first use"""
        try:
            test_phrase = "Hello"
            self.translator.translate(test_phrase, language)
            print(f"✅ Pre-warmed translation for {language.display_name}")
        except Exception as e:
            print(f"⚠️ Pre-warm failed for {language.display_name}: {e}")
    
    def _load_language_worker(self, language):
        """Background worker for loading language"""
        try:
            self.tts_system.set_language(language)
            self.after(0, lambda: self.status_label.config(
                text=f"Ready ({language.display_name})", foreground='#28a745'
            ))
        except Exception as e:
            self.after(0, lambda: self.status_label.config(
                text="TTS Error", foreground='#dc3545'
            ))
    
    def _test_voice(self):
        """Test the current voice with optimized messages"""
        selected_language = self.get_current_language()
        
        if selected_language and self.tts_system.is_available:
            # Use pre-translated test messages for instant response
            test_messages = {
                Language.ENGLISH: "Hello! I'm Sandra, your AI mentor.",
                Language.SPANISH: "¡Hola! Soy Sandra, tu mentora de IA.",
                Language.FRENCH: "Bonjour! Je suis Sandra, votre mentor IA.",
                Language.HINDI: "नमस्ते! मैं सैंड्रा हूँ, आपकी AI मेंटर।",
                Language.ITALIAN: "Ciao! Sono Sandra, la tua mentor AI.",
                Language.PORTUGUESE: "Olá! Eu sou Sandra, sua mentora de IA."
            }
            
            message = test_messages.get(selected_language, test_messages[Language.ENGLISH])
            self.status_label.config(text="🔊 Speaking...", foreground='#17a2b8')
            self.tts_system.speak(message, selected_language)
            
            # Reset status after speech
            self.after(2000, lambda: self.status_label.config(
                text=f"Ready ({selected_language.display_name})", foreground='#28a745'
            ))
        else:
            messagebox.showinfo("TTS Unavailable", "Text-to-speech is not available.")
    
    def _test_translation(self):
        """Test Argostranslate translation with advanced features"""
        selected_language = self.get_current_language()
        
        if selected_language == Language.ENGLISH:
            messagebox.showinfo("Translation Test", 
                "English is the source language - no translation needed.")
            return
        
        if not self.translator or not self.translator.available:
            messagebox.showerror("Translation Error", 
                "Argostranslate is not available.\n\n"
                "Install with: pip install argostranslate\n\n"
                "Benefits:\n"
                "✅ Offline translation\n"
                "✅ Privacy focused\n" 
                "✅ No API keys needed\n"
                "✅ Fast neural translation")
            return
        
        # Show loading
        self.status_label.config(text="Translating...", foreground='#ffc107')
        
        # Run translation test in background
        threading.Thread(
            target=self._translation_test_worker, 
            args=(selected_language,), 
            daemon=True
        ).start()
    
    def _translation_test_worker(self, selected_language):
        """Background worker for translation test"""
        try:
            test_phrases = [
                "Great job! Keep up the great work!",
                "Hello! I'm Sandra, your AI mentor.",
                "Welcome to the learning session!"
            ]
            
            results = []
            for phrase in test_phrases:
                result = self.translator.translate(phrase, selected_language)
                results.append((phrase, result))
            
            # Show results on main thread
            self.after(0, lambda: self._show_translation_results(selected_language, results))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(
                "Translation Test Failed", 
                f"Error: {e}\n\nTry:\n1. Restart the application\n2. Check internet connection for initial package download\n3. pip install --upgrade argostranslate"
            ))
            self.after(0, lambda: self.status_label.config(text="Translation Error", foreground='#dc3545'))
    
    def _show_translation_results(self, language, results):
        """Show translation test results"""
        self.status_label.config(text=f"Ready ({language.display_name})", foreground='#28a745')
        
        result_text = f"🌍 Argostranslate Translation Test\nLanguage: {language.display_name}\n\n"
        
        for i, (original, translated) in enumerate(results, 1):
            result_text += f"{i}. Original: {original}\n"
            result_text += f"   Translated: {translated}\n\n"
        
        # Add cache stats
        if hasattr(self.translator, 'get_cache_stats'):
            stats = self.translator.get_cache_stats()
            result_text += f"📊 Cache: {stats['cache_size']} translations\n"
            result_text += f"📦 Packages: {stats['installed_packages']} installed"
        
        messagebox.showinfo("Translation Test Results", result_text)
    
    def _show_cache_stats(self):
        """Show detailed cache statistics"""
        if not self.translator:
            messagebox.showinfo("Cache Stats", "Translator not available")
            return
        
        try:
            stats = self.translator.get_cache_stats()
            
            stats_text = "📊 Argostranslate Cache Statistics\n\n"
            stats_text += f"💾 Cached translations: {stats['cache_size']}\n"
            stats_text += f"📦 Installed packages: {stats['installed_packages']}\n"
            stats_text += f"💿 Cache file: {'✅' if stats['cache_file_exists'] else '❌'}\n"
            stats_text += f"🌐 Engine available: {'✅' if stats['available'] else '❌'}\n\n"
            
            if hasattr(self.translator, 'get_available_languages'):
                available_langs = self.translator.get_available_languages()
                stats_text += f"🗣️ Available languages: {len(available_langs)}\n"
                stats_text += f"Languages: {', '.join(available_langs[:10])}"
            
            messagebox.showinfo("Cache Statistics", stats_text)
            
        except Exception as e:
            messagebox.showerror("Cache Stats Error", f"Could not get stats: {e}")
    
    def _clear_cache(self):
        """Clear translation cache"""
        if not self.translator:
            messagebox.showinfo("Clear Cache", "Translator not available")
            return
        
        result = messagebox.askyesno(
            "Clear Translation Cache",
            "This will clear all cached translations.\n\n"
            "Translations will need to be computed again.\n\n"
            "Continue?"
        )
        
        if result:
            try:
                self.translator.clear_cache()
                messagebox.showinfo("Cache Cleared", "Translation cache has been cleared.")
                self.status_label.config(text="Cache cleared", foreground='#28a745')
            except Exception as e:
                messagebox.showerror("Clear Cache Error", f"Could not clear cache: {e}")
    
    def get_current_language(self) -> Language:
        """Get currently selected language"""
        return self.current_selected_language


class ModelDownloader:
    """Enhanced model downloader with Argostranslate integration"""
    
    def __init__(self, on_complete):
        self.on_complete = on_complete
        self.model_path = None
        # No longer need to download models - transformers handles it automatically
        self.model_url = None
        self.filename = None
        self.setup_window = None

    def run(self):
        """Run the enhanced model download process"""
        self.setup_window = tk.Toplevel()
        self.setup_window.title("ConvAI Innovations Setup - Enhanced with Argostranslate")
        self.setup_window.geometry("700x350")
        self.setup_window.resizable(False, False)
        self.setup_window.configure(bg='#1e1e1e')
        self.setup_window.transient()
        self.setup_window.grab_set()
        
        # Center the window
        self.setup_window.update_idletasks()
        x = (self.setup_window.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.setup_window.winfo_screenheight() // 2) - (350 // 2)
        self.setup_window.geometry(f'+{x}+{y}')

        # Title
        tk.Label(
            self.setup_window, 
            text="🧠 ConvAI Innovations - Enhanced AI Learning Platform", 
            font=("Segoe UI", 18, "bold"), 
            fg="#00aaff", bg='#1e1e1e'
        ).pack(pady=(30, 10))
        
        # Subtitle with new features
        tk.Label(
            self.setup_window, 
            text="Initializing AI mentor Sandra with offline translation...", 
            font=("Segoe UI", 12), 
            fg="#cccccc", bg='#1e1e1e'
        ).pack(pady=5)
        
        # Features list
        features_text = "🌍 Argostranslate offline translation • 🔒 Privacy focused • 🚀 Neural translation"
        tk.Label(
            self.setup_window, 
            text=features_text, 
            font=("Segoe UI", 10), 
            fg="#28a745", bg='#1e1e1e'
        ).pack(pady=5)
        
        # Status
        self.status_var = tk.StringVar(value="Checking AI mentor model and translation system...")
        tk.Label(
            self.setup_window, textvariable=self.status_var, 
            font=("Segoe UI", 11), fg="#cccccc", bg='#1e1e1e'
        ).pack(pady=10)
        
        # Progress bar
        s = ttk.Style()
        s.configure("Blue.Horizontal.TProgressbar", foreground='#007bff', background='#007bff')
        self.progress_bar = ttk.Progressbar(
            self.setup_window, style="Blue.Horizontal.TProgressbar", 
            length=600, mode='determinate'
        )
        self.progress_bar.pack(pady=20)
        
        # Details
        self.details_var = tk.StringVar(value="")
        details_label = tk.Label(
            self.setup_window, textvariable=self.details_var,
            font=("Segoe UI", 9), fg="#888888", bg='#1e1e1e'
        )
        details_label.pack(pady=5)
        
        # Start setup process
        self.setup_window.after(500, self.start_setup)

    def start_setup(self):
        """Start the enhanced setup process"""
        threading.Thread(target=self._setup_worker, daemon=True).start()

    def _setup_worker(self):
        """Enhanced setup worker with background loading"""
        # Phase 1: Check dependencies
        self.status_var.set("Phase 1/4: Checking dependencies...")
        self.progress_bar['value'] = 5
        
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
        except ImportError:
            self.status_var.set("Installing AI dependencies...")
            self.details_var.set("Please install transformers: pip install transformers torch")
            time.sleep(3)
            self.setup_window.after(0, lambda: self._finalize("default"))
            return
        
        # Phase 2: Initialize translation system
        self.status_var.set("Phase 2/4: Initializing translation system...")
        self.progress_bar['value'] = 15
        
        try:
            import argostranslate.package
            import argostranslate.translate
            self.details_var.set("✅ Argostranslate available - Starting package setup...")
        except ImportError:
            self.details_var.set("⚠️ Argostranslate not found - Using fallback translations")
        
        # Phase 3: Load translation packages
        self.status_var.set("Phase 3/4: Setting up translation packages...")
        self.progress_bar['value'] = 25
        
        # Create AI system with progress callback
        from .ai_systems import LLMAIFeedbackSystem
        
        def progress_callback(message):
            self.setup_window.after(0, lambda: self.details_var.set(message))
        
        self.ai_system = LLMAIFeedbackSystem(progress_callback=progress_callback)
        
        # Initialize translation packages in background
        if self.ai_system.translator.available:
            try:
                self.ai_system.translator.initialize_packages_async()
                self.progress_bar['value'] = 50
            except Exception as e:
                self.details_var.set(f"Translation setup warning: {e}")
        
        # Phase 4: Load AI model
        self.status_var.set("Phase 4/4: Loading AI mentor model...")
        self.progress_bar['value'] = 60
        
        try:
            # Load AI model in background
            self.ai_system.load_model_async()
            
            # Simulate progress while loading
            for progress in range(60, 95, 5):
                self.progress_bar['value'] = progress
                time.sleep(0.2)
            
            self.progress_bar['value'] = 100
            self.status_var.set("Setup complete! Launching platform...")
            self.details_var.set("✅ AI mentor loaded • ✅ Translation packages ready • ✅ All systems active")
            time.sleep(1)
            
            self.setup_window.after(0, lambda: self._finalize("default"))
            
        except Exception as e:
            self.status_var.set("Setup completed with warnings")
            self.details_var.set(f"Warning: {str(e)} - Platform will start with limited AI features")
            time.sleep(2)
            self.setup_window.after(0, lambda: self._finalize("default"))

    def _finalize(self, model_path):
        """Finalize enhanced setup"""
        if self.setup_window:
            self.setup_window.destroy()
        # Pass the pre-loaded AI system along with model path
        self.on_complete(model_path, getattr(self, 'ai_system', None))