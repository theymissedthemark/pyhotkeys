import threading
import time
import tkinter as tk
from tkinter import ttk
import pyautogui
import keyboard
import random


class HotkeyAutomation:
    def __init__(self):
        self.is_running = False
        self.hotkey_rows = []
        self.hotkey_timers = {}
        self.run_time = 0
        self.GLOBAL_DELAY = 50
        self.send_hotkeys_thread = None

        self.root = tk.Tk()
        self.root.title("Hotkey Automation")
        self.root.attributes("-topmost", True)

        self.listview = ttk.Treeview(self.root, columns=("Hotkey", "Delay", "Random Add", "Status"), show="headings")
        self.listview.heading("Hotkey", text="Hotkey")
        self.listview.heading("Delay", text="Delay (ms)")
        self.listview.heading("Random Add", text="Random Add (ms)")
        self.listview.heading("Status", text="Status")
        self.listview.bind("<Double-1>", self.listview_handler)
        self.listview.bind("<Button-3>", self.show_context_menu)
        self.listview.pack()

        self.hotkey_entry = ttk.Entry(self.root)
        self.delay_entry = ttk.Entry(self.root)
        self.random_add_entry = ttk.Entry(self.root)

        ttk.Label(self.root, text="Hotkey:").pack()
        self.hotkey_entry.pack()
        ttk.Label(self.root, text="Delay (ms):").pack()
        self.delay_entry.pack()
        ttk.Label(self.root, text="Random Add (ms):").pack()
        self.random_add_entry.pack()

        ttk.Button(self.root, text="Add Hotkey", command=self.add_hotkey).pack()
        self.run_button = ttk.Button(self.root, text="Not Running", command=self.run_script)
        self.run_button.pack()

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Remove", command=self.remove_hotkey)

        keyboard.add_hotkey("f1", self.toggle_script)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def add_hotkey(self):
        hotkey = self.hotkey_entry.get()
        delay = self.delay_entry.get()
        random_add = self.random_add_entry.get()

        if hotkey and delay and random_add:
            self.listview.insert("", "end", values=(hotkey, delay, random_add, "Inactive"))
            self.hotkey_entry.delete(0, "end")
            self.delay_entry.delete(0, "end")
            self.random_add_entry.delete(0, "end")

    def listview_handler(self, event):
        selected_item = self.listview.focus()
        if selected_item:
            values = self.listview.item(selected_item, "values")
            status = values[3]

            if status == "Active":
                self.listview.set(selected_item, "#4", "Inactive")
                self.hotkey_rows.remove(selected_item)
                self.stop_hotkey_timer(selected_item)
            else:
                self.listview.set(selected_item, "#4", "Active")
                self.hotkey_rows.append(selected_item)
                self.start_hotkey_timer(selected_item)

    def show_context_menu(self, event):
        item = self.listview.identify_row(event.y)
        if item:
            self.listview.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def remove_hotkey(self):
        selected_item = self.listview.selection()[0]
        if selected_item in self.hotkey_rows:
            self.hotkey_rows.remove(selected_item)
            self.stop_hotkey_timer(selected_item)
        self.listview.delete(selected_item)

    def run_script(self):
        self.toggle_script()

    def toggle_script(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.run_button.config(text="Running")
            for row in self.hotkey_rows:
                self.start_hotkey_timer(row)
        else:
            self.run_button.config(text="Not Running")
            for row in self.hotkey_rows:
                self.stop_hotkey_timer(row)

    def start_hotkey_timer(self, row):
        if self.is_running:
            values = self.listview.item(row, "values")
            hotkey = values[0]
            delay = int(values[1])
            random_add = int(values[2])

            self.send_hotkey(hotkey)
            next_delay = delay + random.randint(0, random_add)
            timer = threading.Timer(next_delay / 1000.0, self.start_hotkey_timer, args=[row])
            timer.start()
            self.hotkey_timers[row] = timer

    def stop_hotkey_timer(self, row):
        if row in self.hotkey_timers:
            self.hotkey_timers[row].cancel()
            del self.hotkey_timers[row]

    def send_hotkeys(self):
        while self.is_running:
            self.run_time += self.GLOBAL_DELAY

            for row in self.hotkey_rows:
                values = self.listview.item(row, "values")
                hotkey = values[0]
                delay = int(values[1])
                random_add = int(values[2])
                status = values[3]

                if status == "Active" and self.run_time % delay == 0:
                    random_delay = random.uniform(0, float(random_add) / 1000.0)
                    threading.Timer(random_delay, HotkeyAutomation.send_hotkey, args=[hotkey]).start()

            time.sleep(self.GLOBAL_DELAY / 1000.0)

    @staticmethod
    def send_hotkey(hotkey):
        pyautogui.press(hotkey)

    def on_close(self):
        keyboard.remove_hotkey("f1")
        self.is_running = False
        for timer in self.hotkey_timers.values():
            timer.cancel()
        self.root.destroy()


if __name__ == "__main__":
    HotkeyAutomation()
