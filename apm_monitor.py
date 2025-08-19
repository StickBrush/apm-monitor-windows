import time
import threading
from collections import deque
import tkinter as tk
from pynput import mouse, keyboard
import sys

class APMMonitor:
    def __init__(self):
        self.actions = deque()
        self.lock = threading.Lock()
        self.root = tk.Tk()
        self.root.title("APM Monitor")
        self.root.attributes('-topmost', True)  
        self.root.attributes('-alpha', 0.8)    
        self.root.overrideredirect(True)     
        
        # bottom right corner
        window_width = 120
        window_height = 40
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - window_width - 20
        y = screen_height - window_height - 40
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.label = tk.Label(
            self.root, 
            text="APM: 0", 
            font=("Arial", 14, "bold"),
            bg="black",
            fg="lime",
            padx=10,
            pady=5
        )
        self.label.pack(expand=True, fill="both")

        self.start_listeners()
        self.update_apm()
        
    def record_action(self):
        current_time = time.time()
        with self.lock:
            self.actions.append(current_time)
            # remove actions older than 60 seconds
            while self.actions and current_time - self.actions[0] > 60:
                self.actions.popleft()
    
    def on_key_press(self, key):
        self.record_action()
    
    def on_click(self, x, y, button, pressed):
        if pressed:
            self.record_action()
    
    def start_listeners(self):
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()
        
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.daemon = True
        self.mouse_listener.start()
    
    def calculate_apm(self):
        current_time = time.time()
        with self.lock:
            # Clean old actions
            while self.actions and current_time - self.actions[0] > 60:
                self.actions.popleft()
            
            # actions per minute
            return len(self.actions)
    
    def update_apm(self):
        try:
            apm = self.calculate_apm()
            self.label.config(text=f"APM: {apm}")
            
            self.root.after(1000, self.update_apm)
        except:
            pass
    
    def run(self):
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
    
    def on_closing(self):
        try:
            self.keyboard_listener.stop()
            self.mouse_listener.stop()
            self.root.quit()
            self.root.destroy()
        except:
            pass
        sys.exit(0)

if __name__ == "__main__":
    print("Starting APM Monitor...")
    print("Press Ctrl+C in this console to stop, or close the overlay window")
    print("The overlay will appear in the bottom-right corner of your screen")
    
    try:
        monitor = APMMonitor()
        monitor.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)