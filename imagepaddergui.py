#!/usr/bin/env python3
"""
Image and Video Padder GUI
A graphical interface for the Image and Video Padder tool.
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
import io
from PIL import Image, ImageTk
import re
import platform

# Import core functionality from imagepadder2
from imagepadder2 import (
    pad_image_aspect_ratio,
    pad_image_custom,
    pad_video_aspect_ratio,
    pad_video_custom,
    hex_to_rgb,
    get_background_color,
    check_heif_support,
    check_video_support,
    HEIF_SUPPORT,
    VIDEO_SUPPORT
)

class RedirectText:
    """Redirect stdout to a tkinter Text widget"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = io.StringIO()

    def write(self, string):
        self.buffer.write(string)
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state='disabled')
        
    def flush(self):
        pass

class ImagePadderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image & Video Padder")
        self.root.geometry("800x700")
        self.root.minsize(780, 650)
        
        # Variables
        self.file_path = tk.StringVar()
        self.mode = tk.StringVar(value="aspect")
        self.aspect_ratio = tk.StringVar(value="16x9")
        self.top_padding = tk.StringVar(value="20")
        self.right_padding = tk.StringVar(value="20")
        self.bottom_padding = tk.StringVar(value="20")
        self.left_padding = tk.StringVar(value="20")
        self.bg_color = tk.StringVar(value="#FFFFFF")
        self.opacity = tk.IntVar(value=255)
        self.preview_image = None
        self.file_type = None  # 'image' or 'video'
        self.settings_notebook = None  # Will store reference to settings notebook
        self.main_canvas = None  # Reference to main canvas for scrolling
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas with scrollbar for the content
        main_canvas = tk.Canvas(main_frame)
        self.main_canvas = main_canvas  # Store reference for scrolling
        main_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        # Configure scrolling
        scrollable_frame.bind("<Configure>", 
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Create a notebook for tabs
        notebook = ttk.Notebook(scrollable_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Tab 1: Padding options
        padding_frame = ttk.Frame(notebook, padding="10")
        notebook.add(padding_frame, text="Padding Options")
        
        # Tab 2: Log output
        log_frame = ttk.Frame(notebook, padding="10")
        notebook.add(log_frame, text="Log")
        
        # Tab 3: About
        about_frame = ttk.Frame(notebook, padding="10")
        notebook.add(about_frame, text="About")
        
        # File selection section
        file_frame = ttk.LabelFrame(padding_frame, text="File Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.file_path, width=50).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)
        
        # Mode selection section
        mode_frame = ttk.LabelFrame(padding_frame, text="Padding Mode", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="Aspect Ratio", variable=self.mode, value="aspect", 
                      command=self.update_mode).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(mode_frame, text="Custom Padding", variable=self.mode, value="custom", 
                      command=self.update_mode).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Settings notebook
        self.settings_notebook = ttk.Notebook(padding_frame)
        settings_notebook = self.settings_notebook  # Use local reference for readability
        settings_notebook.pack(fill=tk.BOTH, pady=(0, 10))
        
        # Aspect ratio settings
        aspect_frame = ttk.Frame(settings_notebook, padding="10")
        settings_notebook.add(aspect_frame, text="Aspect Ratio Settings")
        
        ttk.Label(aspect_frame, text="Aspect Ratio (WxH):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        aspect_entry = ttk.Entry(aspect_frame, textvariable=self.aspect_ratio, width=10)
        aspect_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Common ratios
        ttk.Label(aspect_frame, text="Common Ratios:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ratios_frame = ttk.Frame(aspect_frame)
        ratios_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        common_ratios = [("16:9", "16x9"), ("4:3", "4x3"), ("1:1", "1x1"), ("3:2", "3x2"), ("21:9", "21x9")]
        for i, (label, ratio) in enumerate(common_ratios):
            ttk.Button(ratios_frame, text=label, width=5,
                     command=lambda r=ratio: self.set_ratio(r)).grid(row=0, column=i, padx=2)
        
        # Custom padding settings
        custom_frame = ttk.Frame(settings_notebook, padding="10")
        settings_notebook.add(custom_frame, text="Custom Padding Settings")
        
        ttk.Label(custom_frame, text="Top:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(custom_frame, textvariable=self.top_padding, width=8).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(custom_frame, text="Right:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(custom_frame, textvariable=self.right_padding, width=8).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(custom_frame, text="Bottom:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(custom_frame, textvariable=self.bottom_padding, width=8).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(custom_frame, text="Left:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(custom_frame, textvariable=self.left_padding, width=8).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Equal padding shortcuts
        ttk.Label(custom_frame, text="Presets:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        presets_frame = ttk.Frame(custom_frame)
        presets_frame.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        for i, padding in enumerate([("10px", 10), ("20px", 20), ("50px", 50), ("100px", 100)]):
            ttk.Button(presets_frame, text=padding[0], width=6,
                     command=lambda p=padding[1]: self.set_equal_padding(p)).grid(row=0, column=i, padx=2)
        
        # Color settings section
        color_frame = ttk.LabelFrame(padding_frame, text="Background Settings", padding="10")
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(color_frame, text="Color:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        color_entry = ttk.Entry(color_frame, textvariable=self.bg_color, width=10)
        color_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Color picker button with preview
        self.color_preview = tk.Canvas(color_frame, width=20, height=20, bg=self.bg_color.get())
        self.color_preview.grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(color_frame, text="Select Color", command=self.pick_color).grid(row=0, column=3, padx=5, pady=5)
        
        # Color presets
        presets_frame = ttk.Frame(color_frame)
        presets_frame.grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        
        for i, (color, hex_code) in enumerate([("White", "#FFFFFF"), ("Black", "#000000"), 
                                              ("Red", "#FF0000"), ("Green", "#00FF00"), ("Blue", "#0000FF")]):
            frame = tk.Frame(presets_frame, bg=hex_code, width=20, height=20, borderwidth=1, relief="solid")
            frame.grid(row=0, column=i, padx=2, pady=2)
            frame.bind("<Button-1>", lambda e, h=hex_code: self.set_color(h))
        
        # Opacity slider
        ttk.Label(color_frame, text="Opacity:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        opacity_scale = ttk.Scale(color_frame, variable=self.opacity, from_=0, to=255, 
                                orient=tk.HORIZONTAL, length=200)
        opacity_scale.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        
        opacity_label = ttk.Label(color_frame, textvariable=tk.StringVar(value="255"))
        opacity_label.grid(row=1, column=4, padx=5, pady=5)
        opacity_scale.configure(command=lambda v: opacity_label.configure(text=str(int(float(v)))))
        
        # Action buttons
        button_frame = ttk.Frame(padding_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Process", command=self.process_file).pack(side=tk.RIGHT, padx=5)
        
        # Preview frame (with a "No preview available" message initially)
        preview_frame = ttk.LabelFrame(padding_frame, text="Preview & Results", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for the preview image
        preview_image_frame = ttk.Frame(preview_frame)
        preview_image_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.preview_label = ttk.Label(preview_image_frame, text="No preview available")
        self.preview_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a frame for results (output path and copy button)
        results_frame = ttk.Frame(preview_frame)
        results_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        ttk.Label(results_frame, text="Output:").pack(side=tk.LEFT, padx=(0, 5))
        self.output_path = ttk.Entry(results_frame, width=50)
        self.output_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(results_frame, text="Copy Path", command=self.copy_output_path).pack(side=tk.LEFT)
        
        # Processing indicator
        self.processing_var = tk.StringVar(value="")
        self.processing_label = ttk.Label(preview_frame, textvariable=self.processing_var, foreground="blue")
        self.processing_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        # Log output tab
        self.log_text = ScrolledText(log_frame, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state='disabled')
        
        # Redirect stdout to our log widget
        self.stdout_redirector = RedirectText(self.log_text)
        sys.stdout = self.stdout_redirector
        
        # About tab
        about_top_text = """
        Image and Video Padder
        
        A tool that pads images or videos to any aspect ratio while preserving the original resolution. Add space around your images/videos with custom padding or convert to specific aspect ratios like 16:9, 4:3, 1:1 square, and more. Perfect for social media posts or vlogs, video thumbnails, and printing.

        Features

        - Preserve original image/video resolution and quality
        - Choose any background color, with optional transparency
        - Pad images with specific aspect ratios or custom padding
        - Process multiple images at once (website only, for now)
        - Pad videos (command-line version only)
        - Works with all common image formats (JPG, PNG, HEIC etc.)
        - Works with all common video formats (mp4, mov, etc.)
        """
        
        about_frame_content = ttk.Frame(about_frame, padding=20)
        about_frame_content.pack(fill=tk.BOTH, expand=True)
        
        # Add the main description text
        about_label = ttk.Label(about_frame_content, text=about_top_text, justify=tk.LEFT, wraplength=700)
        about_label.pack(fill=tk.X, expand=False, anchor=tk.NW)
        
        # Create a frame for author info with text and button side by side
        author_frame = ttk.Frame(about_frame_content)
        author_frame.pack(fill=tk.X, expand=False, pady=(10, 0), anchor=tk.NW)
        
        # Add author text
        author_label = ttk.Label(author_frame, text="Originally created by Amit Joshi ", justify=tk.LEFT)
        author_label.pack(side=tk.LEFT)
        
        # Add GitHub button next to the text
        github_button = ttk.Button(author_frame, text="GitHub: @amitjoshi2724", 
                                 command=lambda: self.open_url("https://github.com/amitjoshi2724"))
        github_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Show correct frame based on initial mode
        self.update_mode()
        
        # Pack the canvas and scrollbar (must do this before binding events)
        self.main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # Enable mousewheel scrolling - platform specific
        if platform.system() == 'Windows':
            # Windows
            self.root.bind_all("<MouseWheel>", self.on_mousewheel)
        elif platform.system() == 'Darwin':
            # macOS
            self.root.bind_all("<MouseWheel>", self.on_mousewheel)
            self.root.bind_all("<Button-4>", self.on_mousewheel)
            self.root.bind_all("<Button-5>", self.on_mousewheel)
        else:
            # Linux
            self.root.bind_all("<Button-4>", self.on_mousewheel)
            self.root.bind_all("<Button-5>", self.on_mousewheel)
        
        # If HEIF support is available, announce it
        if HEIF_SUPPORT:
            print("HEIC/HEIF support is enabled.")
        else:
            print("HEIC/HEIF support not available. Install with 'pip install pillow-heif'")
        
        # If video support is available, announce it
        if VIDEO_SUPPORT:
            print("Video support is enabled.")
        else:
            print("Video support not available. Install with 'pip install moviepy'")
            
        print("Select a file to begin.")
    
    def update_mode(self):
        """Update the settings notebook based on the selected mode"""
        mode = self.mode.get()
        
        if mode == "aspect":
            self.settings_notebook.select(0)  # Select aspect ratio tab
        else:
            self.settings_notebook.select(1)  # Select custom padding tab
    
    def set_ratio(self, ratio):
        """Set the aspect ratio from a preset"""
        self.aspect_ratio.set(ratio)
    
    def set_equal_padding(self, padding):
        """Set equal padding for all sides"""
        self.top_padding.set(str(padding))
        self.right_padding.set(str(padding))
        self.bottom_padding.set(str(padding))
        self.left_padding.set(str(padding))
    
    def pick_color(self):
        """Open color picker dialog"""
        color = colorchooser.askcolor(initialcolor=self.bg_color.get())[1]
        if color:
            self.bg_color.set(color)
            self.color_preview.configure(bg=color)
    
    def set_color(self, hex_code):
        """Set color from a preset"""
        self.bg_color.set(hex_code)
        self.color_preview.configure(bg=hex_code)
    
    def copy_output_path(self):
        """Copy the output path to clipboard"""
        if self.output_path.get():
            self.root.clipboard_clear()
            self.root.clipboard_append(self.output_path.get())
            print("Output path copied to clipboard")
    
    def browse_file(self):
        """Open file browser dialog"""
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[
                ("All Supported Files", "*.jpg *.jpeg *.png *.bmp *.gif *.heic *.heif *.webp *.tiff *.mp4 *.mov *.avi *.mkv *.webm *.wmv"),
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif *.heic *.heif *.webp *.tiff"),
                ("Video Files", "*.mp4 *.mov *.avi *.mkv *.webm *.wmv"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.file_path.set(file_path)
            self.detect_file_type(file_path)
    
    def detect_file_type(self, file_path):
        """Detect if the file is an image or video"""
        path = Path(file_path)
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv']
        
        if path.suffix.lower() in video_extensions:
            self.file_type = 'video'
            if not VIDEO_SUPPORT:
                print("Warning: You've selected a video file but video support is not available.")
                print("Please install moviepy with: pip install moviepy")
            else:
                print(f"Video file selected: {path.name}")
        else:
            self.file_type = 'image'
            try:
                # Try to open and display a preview
                with Image.open(file_path) as img:
                    print(f"Image loaded: {img.size[0]}x{img.size[1]} pixels")
                    self.show_image_preview(img)
            except Exception as e:
                print(f"Error opening image: {str(e)}")
    
    def show_image_preview(self, img):
        """Display a preview of the loaded image"""
        if img:
            # Resize for preview while maintaining aspect ratio
            preview_width = 500  # maximum preview width
            width, height = img.size
            ratio = min(preview_width / width, preview_width / height)
            new_size = (int(width * ratio), int(height * ratio))
            
            # Make a copy to avoid modifying the original during resize
            preview_img = img.copy()
            preview_img.thumbnail(new_size, Image.LANCZOS)
            
            # Convert to PhotoImage for tkinter
            self.preview_image = ImageTk.PhotoImage(preview_img)
            
            # Update the preview label
            self.preview_label.configure(image=self.preview_image, text="")
    
    def validate_inputs(self):
        """Validate user inputs before processing"""
        # Check if file is selected
        if not self.file_path.get():
            print("Error: No file selected.")
            return False
        
        # Check if file exists
        if not os.path.exists(self.file_path.get()):
            print(f"Error: File not found: {self.file_path.get()}")
            return False
        
        # Validate aspect ratio if that mode is selected
        if self.mode.get() == "aspect":
            try:
                aspect_ratio = self.aspect_ratio.get()
                if not re.match(r'^\d+x\d+$', aspect_ratio):
                    print("Error: Aspect ratio must be in the format WIDTHxHEIGHT (e.g., 16x9)")
                    return False
                
                nw, nh = map(int, aspect_ratio.split("x"))
                if nw <= 0 or nh <= 0:
                    print("Error: Aspect ratio dimensions must be positive numbers")
                    return False
            except Exception as e:
                print(f"Error with aspect ratio: {str(e)}")
                return False
        
        # Validate custom padding if that mode is selected
        elif self.mode.get() == "custom":
            try:
                top = int(self.top_padding.get())
                right = int(self.right_padding.get())
                bottom = int(self.bottom_padding.get())
                left = int(self.left_padding.get())
                
                if top < 0 or right < 0 or bottom < 0 or left < 0:
                    print("Error: Padding values cannot be negative")
                    return False
            except ValueError:
                print("Error: Padding values must be integers")
                return False
        
        # Validate color
        color = self.bg_color.get()
        if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color):
            print("Error: Background color must be a valid hex code (e.g., #FFFFFF)")
            return False
        
        # Validate opacity
        opacity = self.opacity.get()
        if opacity < 0 or opacity > 255:
            print("Error: Opacity must be between 0 and 255")
            return False
        
        # Clear previous output path
        self.output_path.delete(0, tk.END)
        
        return True
    
    def process_file(self):
        """Process the file with the selected options"""
        if not self.validate_inputs():
            return
        
        # Run processing in a separate thread to avoid freezing the UI
        threading.Thread(target=self._process_file_thread).start()
    
    def update_processing_status(self, is_processing, message=""):
        """Update the processing status indicator"""
        print(f"Status: {'Processing' if is_processing else message}")
        self.processing_var.set("Processing... Please wait." if is_processing else message)
        self.root.update_idletasks()  # Force UI update
        # Ensure scrollbar is updated
        self.root.update()
    
    def _process_file_thread(self):
        """Thread function for file processing"""
        try:
            self.update_processing_status(True)
            file_path = Path(self.file_path.get())
            mode = self.mode.get()
            color = self.bg_color.get()
            opacity = self.opacity.get()
            
            # Convert color to RGB(A)
            bg_color = get_background_color(color, opacity)
            
            print(f"Processing {self.file_type} with {mode} padding...")
            print(f"Using background color: {color} with opacity: {opacity}/255")
            
            if self.file_type == 'image':
                # Process image
                im = Image.open(file_path)
                
                if mode == "aspect":
                    # Aspect ratio mode
                    nw, nh = map(int, self.aspect_ratio.get().split("x"))
                    result, save_path = pad_image_aspect_ratio(file_path, im, nw, nh, bg_color, opacity)
                else:
                    # Custom padding mode
                    top = int(self.top_padding.get())
                    right = int(self.right_padding.get())
                    bottom = int(self.bottom_padding.get())
                    left = int(self.left_padding.get())
                    result, save_path = pad_image_custom(file_path, im, top, right, bottom, left, bg_color, opacity)
                
                # Save the resulting image
                if result:
                    # Check if we're saving to a format that needs special handling
                    if im.mode != 'RGBA' and opacity == 255:
                        result = result.convert('RGB')
                    
                    if save_path.suffix.lower() in ['.jpg', '.jpeg']:
                        # JPEG doesn't support transparency, convert to RGB
                        result = result.convert('RGB')
                    
                    result.save(save_path, quality=100)
                    print(f"Done! New image size: {result.size[0]}x{result.size[1]} pixels")
                    print(f"Image saved to: {save_path}")
                    
                    # Show the output path
                    self.output_path.insert(0, str(save_path))
                    
                    # Show preview of the result
                    self.show_image_preview(result)
                    
                    # Update status to complete
                    self.update_processing_status(False, "Complete! Image processed successfully.")
            
            elif self.file_type == 'video':
                if not VIDEO_SUPPORT:
                    print("Error: Video support is not available. Please install moviepy.")
                    return
                
                if mode == "aspect":
                    # Aspect ratio mode
                    nw, nh = map(int, self.aspect_ratio.get().split("x"))
                    save_path = pad_video_aspect_ratio(file_path, nw, nh, bg_color, opacity)
                else:
                    # Custom padding mode
                    top = int(self.top_padding.get())
                    right = int(self.right_padding.get())
                    bottom = int(self.bottom_padding.get())
                    left = int(self.left_padding.get())
                    save_path = pad_video_custom(file_path, top, right, bottom, left, bg_color, opacity)
                
                print(f"Video processing complete with {opacity}/255 opacity background")
                print(f"Video saved to: {save_path}")
                
                # Show the output path
                self.output_path.insert(0, str(save_path))
                self.update_processing_status(False, "Complete! Video processed successfully.")
            
        except Exception as e:
            self.update_processing_status(False, f"Error: {str(e)}")
            print(f"Error during processing: {str(e)}")
        
        # Ensure we always update the status when done
        self.root.after(100, lambda: self.root.update())
    
    def open_url(self, url):
        """Open URL in default browser"""
        import webbrowser
        webbrowser.open_new(url)

    def on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        if platform.system() == 'Windows':
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        else:
            self.main_canvas.yview_scroll(int(-1*event.delta), "units")
            # For Linux, Button-4 is up, Button-5 is down
            if event.num == 4:
                self.main_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.main_canvas.yview_scroll(1, "units")
        return "break"  # Prevent default behavior

if __name__ == "__main__":
    root = tk.Tk()
    app = ImagePadderGUI(root)
    root.mainloop()
    
    # Restore stdout when the application closes
    sys.stdout = sys.__stdout__ 
