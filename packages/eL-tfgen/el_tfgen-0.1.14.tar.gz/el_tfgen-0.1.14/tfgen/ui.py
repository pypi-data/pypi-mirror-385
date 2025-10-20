import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
from .terraform_parser import get_module_path, generate_module_with_gpt, split_and_save_outputs
from PIL import Image, ImageTk, ImageDraw
import math

# --- Only Dark Color Palette ---
DARK = {
    'BG_GRADIENT_TOP': "#232946",
    'BG_GRADIENT_BOTTOM': "#16161a",
    'CARD_COLOR': "#232946",
    'ACCENT_COLOR': "#8b5cf6",
    'ACCENT_HOVER': "#7c3aed",
    'SUCCESS_COLOR': "#22d3ee",
    'ERROR_COLOR': "#f43f5e",
    'TITLE_COLOR': "#f4f4f8",
    'LABEL_COLOR': "#b8c1ec",
    'CODE_BG': "#1a1a2e",
    'TOGGLE_OFF': "#444c6e",
    'TOGGLE_ON': "#8b5cf6",
    'ICON_CLOUD1': "#6366f1",
    'ICON_CLOUD2': "#8b5cf6",
    'ICON_CLOUD3': "#7c3aed",
    'ICON_CODE': "#fff",
    'TEXT': "#f4f4f8"
}

FONT = ("Segoe UI", 12)
TITLE_FONT = ("Segoe UI", 26, "bold")
BUTTON_FONT = ("Segoe UI", 13, "bold")

# --- Custom Icon (Cloud + Code) ---
def create_icon(theme):
    size = 44
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Cloud
    draw.ellipse((6, 18, 38, 38), fill=theme['ICON_CLOUD1'])
    draw.ellipse((18, 10, 34, 34), fill=theme['ICON_CLOUD2'])
    draw.ellipse((24, 18, 44, 38), fill=theme['ICON_CLOUD3'])
    # Code brackets
    draw.line((16, 28, 20, 24, 16, 20), fill=theme['ICON_CODE'], width=3)
    draw.line((32, 20, 36, 24, 32, 28), fill=theme['ICON_CODE'], width=3)
    return ImageTk.PhotoImage(img)

# --- Gradient Background ---
def draw_gradient(canvas, width, height, color1, color2):
    r1, g1, b1 = canvas.winfo_rgb(color1)
    r2, g2, b2 = canvas.winfo_rgb(color2)
    r_ratio = (r2 - r1) / height
    g_ratio = (g2 - g1) / height
    b_ratio = (b2 - b1) / height
    for i in range(height):
        nr = int(r1 + (r_ratio * i)) >> 8
        ng = int(g1 + (g_ratio * i)) >> 8
        nb = int(b1 + (b_ratio * i)) >> 8
        color = f"#{nr:02x}{ng:02x}{nb:02x}"
        canvas.create_line(0, i, width, i, fill=color)

# --- Animated Spinner ---
SPINNER_FRAMES = [
    "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
]
class Spinner:
    def __init__(self, label, theme):
        self.label = label
        self.running = False
        self.idx = 0
        self.theme = theme
    def start(self):
        self.running = True
        self.animate()
    def animate(self):
        if self.running:
            self.label.config(text=SPINNER_FRAMES[self.idx % len(SPINNER_FRAMES)], fg=self.theme['ACCENT_COLOR'])
            self.idx += 1
            self.label.after(100, self.animate)
    def stop(self):
        self.running = False
        self.label.config(text="")
    def update_theme(self, theme):
        self.theme = theme

# --- Custom Toggle Switch ---
class ToggleSwitch(tk.Canvas):
    def __init__(self, master, variable, theme, width=48, height=28, *args, **kwargs):
        super().__init__(master, width=width, height=height, bg=theme['CARD_COLOR'], highlightthickness=0, *args, **kwargs)
        self.variable = variable
        self.theme = theme
        self.width = width
        self.height = height
        self.bind("<Button-1>", self.toggle)
        self.draw()
        self.variable.trace_add("write", lambda *a: self.draw())
    def draw(self):
        self.config(bg=self.theme['CARD_COLOR'])
        self.delete("all")
        is_on = self.variable.get()
        color = self.theme['TOGGLE_ON'] if is_on else self.theme['TOGGLE_OFF']
        self.create_oval(2, 2, self.height-2, self.height-2, fill=color, outline=color)
        self.create_oval(self.width-self.height+2, 2, self.width-2, self.height-2, fill=color, outline=color)
        self.create_rectangle(self.height//2, 2, self.width-self.height//2, self.height-2, fill=color, outline=color)
        knob_x = self.width-self.height if is_on else 0
        self.create_oval(knob_x+2, 2, knob_x+self.height-2, self.height-2, fill="#fff", outline="#e5e7eb")
    def toggle(self, event=None):
        self.variable.set(not self.variable.get())
    def update_theme(self, theme):
        self.theme = theme
        self.config(bg=self.theme['CARD_COLOR'])
        self.draw()

class DarkButton(tk.Button):
    def __init__(self, master, text, command, theme, **kwargs):
        super().__init__(master, text=text, command=command, **kwargs)
        self.theme = theme
        self.default_bg = theme['ACCENT_COLOR']
        self.hover_bg = theme['ACCENT_HOVER']
        self.disabled_bg = "#2d3146"
        self.disabled_fg = "#888ca3"
        self.enabled_fg = "#fff"
        self['font'] = BUTTON_FONT
        self['bg'] = self.default_bg
        self['fg'] = self.enabled_fg
        self['activebackground'] = self.hover_bg
        self['activeforeground'] = self.enabled_fg
        self['relief'] = 'flat'
        self['bd'] = 0
        self['highlightthickness'] = 0
        self['cursor'] = 'hand2'
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.update_state()
    def on_enter(self, event):
        if self['state'] == tk.NORMAL:
            self['bg'] = self.hover_bg
    def on_leave(self, event):
        if self['state'] == tk.NORMAL:
            self['bg'] = self.default_bg
    def config(self, **kwargs):
        super().config(**kwargs)
        self.update_state()
    def update_state(self):
        if self['state'] == tk.DISABLED:
            self['bg'] = self.disabled_bg
            self['fg'] = self.disabled_fg
        else:
            self['bg'] = self.default_bg
            self['fg'] = self.enabled_fg

class TerraformGeneratorUI:
    def __init__(self, root):
        self.root = root
        self.theme = DARK
        self.root.title("Terraform Module Generator")
        self.root.geometry("760x600")
        self.root.minsize(600, 520)
        self.icon = create_icon(self.theme)
        self.root.iconphoto(True, self.icon)
        self.setup_ui()

    def setup_ui(self):
        # Set root background to match theme
        self.root.configure(bg=self.theme['BG_GRADIENT_BOTTOM'])
        self.bg_canvas = tk.Canvas(self.root, width=800, height=700, highlightthickness=0, bg=self.theme['BG_GRADIENT_BOTTOM'])
        self.bg_canvas.pack(fill="both", expand=True)
        self.root.update_idletasks()
        draw_gradient(self.bg_canvas, self.root.winfo_width(), self.root.winfo_height(), self.theme['BG_GRADIENT_TOP'], self.theme['BG_GRADIENT_BOTTOM'])
        self.bg_canvas.bind("<Configure>", self.on_resize)

        self.card = tk.Frame(self.bg_canvas, bg=self.theme['CARD_COLOR'], bd=0, highlightthickness=0)
        self.card.place(relx=0.5, rely=0.5, anchor="c", relwidth=0.92, relheight=0.92)
        self.card.grid_propagate(False)
        self.card.grid_rowconfigure(8, weight=1)
        self.card.grid_columnconfigure(0, weight=1)

        # Title with icon
        title_frame = tk.Frame(self.card, bg=self.theme['CARD_COLOR'])
        title_frame.grid(row=0, column=0, pady=(24, 10), sticky="ew")
        self.icon_label = tk.Label(title_frame, image=self.icon, bg=self.theme['CARD_COLOR'])
        self.icon_label.pack(side="left", padx=(0, 12))
        self.title_label = tk.Label(title_frame, text="Terraform Module Generator", font=TITLE_FONT, fg=self.theme['TITLE_COLOR'], bg=self.theme['CARD_COLOR'])
        self.title_label.pack(side="left")

        # URL input
        url_frame = tk.Frame(self.card, bg=self.theme['CARD_COLOR'])
        url_frame.grid(row=2, column=0, sticky="ew", padx=36, pady=(10, 0))
        self.url_label = tk.Label(url_frame, text="Resource URL:", font=FONT, fg=self.theme['LABEL_COLOR'], bg=self.theme['CARD_COLOR'])
        self.url_label.pack(side="left", padx=(0, 10))
        self.url_entry = ttk.Entry(url_frame, font=FONT, width=48)
        self.url_entry.pack(side="left", fill="x", expand=True)

        # Toggle switch for generate
        self.generate_var = tk.BooleanVar(value=True)
        self.toggle_frame = tk.Frame(self.card, bg=self.theme['CARD_COLOR'])
        self.toggle_frame.grid(row=3, column=0, sticky="w", padx=38, pady=(16, 0))
        self.toggle = ToggleSwitch(self.toggle_frame, self.generate_var, self.theme)
        self.toggle.pack(side="left")
        self.toggle_label = tk.Label(self.toggle_frame, text="Generate Terraform Files", font=FONT, fg=self.theme['LABEL_COLOR'], bg=self.theme['CARD_COLOR'])
        self.toggle_label.pack(side="left", padx=(10, 0))

        # Generate button
        self.generate_button = DarkButton(self.card, text="Generate Module", command=self.start_generation, theme=self.theme)
        self.generate_button.grid(row=4, column=0, pady=(28, 0))

        # Status
        status_frame = tk.Frame(self.card, bg=self.theme['CARD_COLOR'])
        status_frame.grid(row=5, column=0, sticky="w", padx=38, pady=(24, 0))
        self.status_label = tk.Label(status_frame, text="Ready", font=FONT, fg=self.theme['LABEL_COLOR'], bg=self.theme['CARD_COLOR'])
        self.status_label.pack(side="left")
        self.status_icon = tk.Label(status_frame, text="", font=("Segoe UI", 18, "bold"), bg=self.theme['CARD_COLOR'])
        self.status_icon.pack(side="left", padx=(10, 0))
        self.spinner = Spinner(self.status_icon, self.theme)

        # Output area
        self.output_frame = tk.LabelFrame(self.card, text="Output", font=("Segoe UI", 11, "bold"), fg=self.theme['ACCENT_COLOR'], bg=self.theme['CARD_COLOR'], bd=0, labelanchor="nw")
        self.output_frame.grid(row=6, column=0, sticky="nsew", padx=28, pady=(24, 18))
        self.output_frame.grid_propagate(False)
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_text = tk.Text(self.output_frame, wrap="word", font=("Consolas", 11), bg=self.theme['CODE_BG'], fg=self.theme['TEXT'], relief="flat", bd=0, height=10, padx=12, pady=10, insertbackground=self.theme['ACCENT_COLOR'])
        self.output_text.grid(row=0, column=0, sticky="nsew")
        self.output_text.config(state="disabled")
        scroll = ttk.Scrollbar(self.output_frame, command=self.output_text.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.output_text.config(yscrollcommand=scroll.set)

        # Entry field and label dark mode fix
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.TEntry", fieldbackground=self.theme['CARD_COLOR'], background=self.theme['CARD_COLOR'], foreground=self.theme['TEXT'], bordercolor=self.theme['CARD_COLOR'], lightcolor=self.theme['CARD_COLOR'], darkcolor=self.theme['CARD_COLOR'], insertcolor=self.theme['TEXT'])
        self.url_entry.configure(style="Custom.TEntry")
        self.url_entry['foreground'] = self.theme['TEXT']
        self.url_entry['background'] = self.theme['CARD_COLOR']
        self.url_label.config(bg=self.theme['CARD_COLOR'], fg=self.theme['LABEL_COLOR'])
        self.toggle_label.config(bg=self.theme['CARD_COLOR'], fg=self.theme['LABEL_COLOR'])
        self.status_label.config(bg=self.theme['CARD_COLOR'], fg=self.theme['LABEL_COLOR'])
        self.status_icon.config(bg=self.theme['CARD_COLOR'])
        self.output_frame.config(bg=self.theme['CARD_COLOR'], fg=self.theme['ACCENT_COLOR'])
        self.output_text.config(bg=self.theme['CODE_BG'], fg=self.theme['TEXT'])

    def on_resize(self, event):
        self.bg_canvas.delete("all")
        draw_gradient(self.bg_canvas, event.width, event.height, self.theme['BG_GRADIENT_TOP'], self.theme['BG_GRADIENT_BOTTOM'])

    def update_status(self, message, status=None):
        self.status_label.config(text=message)
        if status == "success":
            self.spinner.stop()
            self.status_icon.config(text="✓", fg=self.theme['SUCCESS_COLOR'])
        elif status == "error":
            self.spinner.stop()
            self.status_icon.config(text="✗", fg=self.theme['ERROR_COLOR'])
        elif status == "spinner":
            self.status_icon.config(text="")
            self.spinner.start()
        else:
            self.spinner.stop()
            self.status_icon.config(text="")

    def log_output(self, message):
        self.output_text.config(state="normal")
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.output_text.config(state="disabled")

    def clear_output(self):
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, "end")
        self.output_text.config(state="disabled")

    def start_generation(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a resource URL.")
            return
        self.generate_button.config(state="disabled")
        self.generate_button.update_state()
        self.update_status("Generating...", status="spinner")
        self.clear_output()
        thread = threading.Thread(target=self.run_generation, args=(url,))
        thread.daemon = True
        thread.start()

    def run_generation(self, url):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            module_path = get_module_path(url)
            self.log_output(f"Module path: {module_path}")
            azapi_mode = url.startswith("https://learn.microsoft.com")
            gpt_output = loop.run_until_complete(
                generate_module_with_gpt("", azapi_mode=azapi_mode, url=url)
            )
            if gpt_output:
                split_and_save_outputs(gpt_output, module_path)
                self.log_output("\n✅ Terraform files generated and saved!")
                self.update_status("Generation Complete", status="success")
            else:
                self.log_output("❌ AI did not return any output.")
                self.update_status("Generation Failed", status="error")
        except Exception as e:
            self.log_output(f"❌ Error: {str(e)}")
            self.update_status("Generation Failed", status="error")
        finally:
            self.generate_button.config(state="normal")
            self.generate_button.update_state()
            try:
                loop.close()
            except:
                pass

def main():
    root = tk.Tk()
    app = TerraformGeneratorUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 