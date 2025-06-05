import configparser
import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pygame
from PIL import Image, ImageTk
from mutagen.mp3 import MP3
import time
import sys
import ctypes
from sys import platform
import random
app_name = "MusicPlayer"

if platform == "win32":
    config_dir = os.path.join(os.getenv('APPDATA'), app_name)
elif platform == "linux" or platform == "linux2":
    config_dir = os.path.join(os.path.expanduser("~"), ".config", app_name)
elif platform == "darwin":
    config_dir = os.path.join(os.path.expanduser("~"), "Library", "Application Support", app_name)
os.makedirs(config_dir, exist_ok=True)
config_file = os.path.join(config_dir, 'config.ini')

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_gradient_image(width, height, start_color, end_color):
    gradient = Image.new('RGB', (1, height))
    start = hex_to_rgb(start_color)
    end = hex_to_rgb(end_color)

    for y in range(height):
        r = start[0] + (end[0] - start[0]) * y // height
        g = start[1] + (end[1] - start[1]) * y // height
        b = start[2] + (end[2] - start[2]) * y // height
        gradient.putpixel((0, y), (r, g, b))
    return gradient.resize((width, height), Image.NEAREST)

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("YourAppID.UniqueName")
bg_color = "#2100d9"
gradient_start = "#2100d9" # blue
gradient_end = "#ee15ff" # purple
pygame.mixer.init()
pygame.mixer.music.set_volume(1.0)
root = tk.Tk()
root.title("Music Player")
root.geometry("1000x700")
background_canvas = tk.Canvas(root, highlightthickness=0)
background_canvas.place(x=0, y=0, relwidth=1, relheight=1)

def update_gradient(event=None):
    global background_canvas

    if not background_canvas or not background_canvas.winfo_exists():
        return
    width = root.winfo_width()
    height = root.winfo_height()
    gradient_image = create_gradient_image(width, height, gradient_start, gradient_end)
    photo = ImageTk.PhotoImage(gradient_image)
    background_canvas.create_image(0, 0, image=photo, anchor='nw')
    background_canvas.image = photo
root.bind('<Configure>', update_gradient)
update_gradient()
current_folder = ""
songs = []
song_labels = []
paused = False
current_index = 0
is_seeking = False
total_duration = 0
last_update_time = 0
seek_start_time = 0
last_seek_time = 0
base_time = 0
is_playing = False
song_name_bg_clor = "#110392"
is_dragging = False
drag_start_x = 0
pause_after_current  = False
timer_id = None
timer_end_time = 0
shuffle_enabled = False
is_volume_dragging = False
last_volume = 1.0
last_highlighted_index = -1
shuffled_songs = []
played_indices = set()

def resource_path(relative_path):
    """ Get absolute path to resources for both dev and PyInstaller """

    try:
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")
    full_path = os.path.join(base_path, relative_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Resource not found: {full_path}")
    return full_path

try:
    root.iconbitmap(resource_path(r"icons/icon.ico"))

except Exception as e:
    print("Icon load error:", e)

class ToolTip:

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind("<Enter>", self.showtip)
        self.widget.bind("<Leave>", self.hidetip)

    def showtip(self, event=None):

        if self.tipwindow:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        self.ToolTip_label = tk.Label(tw, text=self.text, bg='blue', fg="cyan", font=("Consolas", 13, "italic","bold"))
        self.ToolTip_label.pack()

    def hidetip(self, event=None):

        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None

def load_window_geometry():
    global current_folder

    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        if "Geometry" in config:
            geometry = config["Geometry"].get("size", "")
            state = config["Geometry"].get("state", "normal")

            if geometry:
                root.geometry(geometry)

        if "Preferences" in config:
            current_folder = config["Preferences"].get("last_folder", "")

    if current_folder and os.path.isdir(current_folder):
        root.after(500, lambda: load_folder(current_folder))

def save_window_geometry():
    config = configparser.ConfigParser()
    config["Geometry"] = {
        "size": root.geometry(),
        "state": root.state()
    }
    config["Preferences"] = {}

    if os.path.isdir(current_folder):
        config["Preferences"]["last_folder"] = current_folder

    with open(config_file, "w") as f:
        config.write(f)

def on_close():
    """Handle window close event"""
    save_window_geometry()
    root.destroy()

def convert_seconds_to_time(seconds):
    """Convert seconds to MM:SS format"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02d}"

def load_folder(folder_path=None):
    global current_folder, songs,last_highlighted_index, song_labels, current_index, is_playing, paused

    if folder_path is None:
        folder_path = filedialog.askdirectory()

    if not folder_path:
        return
    stop()
    current_index = -1
    last_highlighted_index = -1
    is_playing = False
    paused = False
    current_folder = folder_path
    songs.clear()
    song_labels.clear()

    for widget in song_frame.winfo_children():
        widget.destroy()

    for file in os.listdir(current_folder):

        if file.endswith(".mp3"):
            songs.append(file)

    for i, song in enumerate(songs):
        add_song_entry(song, i)
    folder_frame.place_forget()
    song_name_frame.pack(fill="x", pady=0, padx=10)
    main_frame.pack(fill="both", expand=True, padx=30)
    open_folder_btn.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)
    song_var.set("")
    update_window_title()

def add_song_entry(song_name, index):
    song_entry_frame = tk.Frame(song_frame, bg=bg_color)
    song_entry_frame.pack(fill="x", pady=(0, 0))
    full_path = os.path.join(current_folder, song_name)

    try:
        audio = MP3(full_path)
        duration = audio.info.length
        duration_str = convert_seconds_to_time(duration)

    except:
        duration_str = "0:00"
    duration_label = tk.Label(
        song_entry_frame,
        text=duration_str,
        fg="white",
        bg=song_name_bg_clor,
        font=("Arial", 13),
        width=6,
        anchor="e",
        padx=5
    )
    duration_label.pack(side="left")
    song_label = tk.Label(
        song_entry_frame,
        text=song_name,
        fg="white",
        bg=song_name_bg_clor,
        font=("Arial", 13),
        anchor="w",
        padx=10
    )
    song_label.pack(side="left", fill="x", expand=True)
    separator = tk.Frame(song_entry_frame, height=2, bg="magenta")
    separator.pack(fill="x", pady=(0, 6), side=tk.BOTTOM)
    song_entry_frame.index = index
    duration_label.index = index
    song_label.index = index

    for widget in [song_entry_frame, duration_label, song_label]:
        widget.bind("<Button-1>", play_song_by_event)
        widget.bind("<Button-3>", show_context_menu_event)
    song_labels.append(song_entry_frame)
    separator = tk.Frame(song_frame, height=2, bg="magenta")
    separator.pack(fill="x", pady=(0, 6))

def play_song_by_event(event):
    index = event.widget.index
    play_song_by_index(index)

def show_context_menu_event(event):
    index = event.widget.index
    show_context_menu(event, index)

def play_song_by_index(index):
    global paused, current_index, total_duration, last_update_time, is_playing, base_time, last_highlighted_index

    if 0 <= index < len(songs):

        if last_highlighted_index != -1 and last_highlighted_index < len(song_labels):
            prev_frame = song_labels[last_highlighted_index]

            for child in prev_frame.winfo_children():

                if isinstance(child, tk.Label):
                    child.config(bg=song_name_bg_clor, fg='white')

            if len(prev_frame.winfo_children()) > 1 and isinstance(prev_frame.winfo_children()[1], tk.Label):
                prev_frame.winfo_children()[1].config(font=("Arial", 13))
        current_frame = song_labels[index]

        for child in current_frame.winfo_children():

            if isinstance(child, tk.Label):
                child.config(bg="#ee15ff", fg='black')

        if len(current_frame.winfo_children()) > 1 and isinstance(current_frame.winfo_children()[1], tk.Label):
            current_frame.winfo_children()[1].config(font=("Arial", 15, 'italic'))
        last_highlighted_index = index
        is_playing = True
        paused = False
        current_index = index
        play_btn.place_forget()
        pause_btn.place(relx=0.5, rely=0.5, anchor="center")
        skip_back_btn.place(relx=0.35, rely=0.5, anchor="center")
        skip_forward_btn.place(relx=0.65, rely=0.5, anchor="center")
        night_btn.place(relx=0.75, rely=0.5, anchor="center")
        suffle_btn.place(relx=0.29, rely=0.5, anchor="center")

        if current_index == 0:
            prev_btn.place_forget()
            fade_prev_btn.place(relx=0.43, rely=0.5, anchor="center")
        else:
            fade_prev_btn.place_forget()
            prev_btn.place(relx=0.43, rely=0.5, anchor="center")

        if current_index == len(songs) - 1:
            next_btn.place_forget()
            fade_next_btn.place(relx=0.57, rely=0.5, anchor="center")
        else:
            fade_next_btn.place_forget()
            next_btn.place(relx=0.57, rely=0.5, anchor="center")
        full_path = os.path.join(current_folder, songs[index])

        try:
            audio = MP3(full_path)
            total_duration = audio.info.length

        except:
            total_duration = 0
        timeline_canvas.coords(progress_line, 10, 10, 10, 10)
        timeline_canvas.itemconfig(slider_handle, state="hidden")
        total_time_label.config(text=convert_seconds_to_time(total_duration))
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play()
        song_var.set(songs[index])
        canvas.yview_moveto(index / max(1, len(songs)))
        last_update_time = time.time()
        base_time = 0
        update_window_title()
        root.update_idletasks()

def show_context_menu(event, index):
    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Delete",background=bg_color,foreground="white",font=('Arial',10), command=lambda: delete_song(index))
    context_menu.tk_popup(event.x_root, event.y_root)

def delete_song(index):
    global current_index, is_playing,last_highlighted_index, songs, song_labels

    if 0 <= index < len(songs):
        song_name = songs[index]
        file_path = os.path.join(current_folder, song_name)
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{song_name}'?",
            parent=root
        )

        if not confirm:
            return

        try:

            if index == current_index:
                stop()
                pygame.mixer.music.unload()
                is_playing = False
                song_var.set("")
            os.remove(file_path)
            del songs[index]
            frame_to_remove = song_labels[index]
            separator = frame_to_remove.winfo_children()[-1]
            frame_to_remove.destroy()
            separator.destroy()
            del song_labels[index]

            if last_highlighted_index == index:
                last_highlighted_index = -1
            elif last_highlighted_index > index:
                last_highlighted_index -= 1

            for i in range(index, len(song_labels)):
                frame = song_labels[i]
                frame.index = i

                for child in frame.winfo_children():

                    if hasattr(child, 'index'):
                        child.index = i

            if current_index == -1:
                play_btn.place(relx=0.5, rely=0.5, anchor="center")
                pause_btn.place_forget()
                skip_back_btn.place_forget()
                skip_forward_btn.place_forget()
                night_btn.place_forget()
                suffle_btn.place_forget()
                prev_btn.place_forget()
                next_btn.place_forget()
                fade_prev_btn.place_forget()
                fade_next_btn.place_forget()
            update_window_title()

            if shuffle_enabled:
                shuffle()

        except Exception as e:
            messagebox.showerror("Error", f"Could not delete song: {e}")

def check_song_end():
    global is_playing, pause_after_current

    if is_playing and not pygame.mixer.music.get_busy() and not paused:

        if pause_after_current:
            pause_after_timer()
            pause_after_current = False
        else:
            play_next_song()
    root.after(1000, check_song_end)

def update_time_slider():
    global last_seek_time, base_time, is_seeking, is_playing

    if is_seeking or not is_playing:
        root.after(1000, update_time_slider)
        return

    if not is_seeking and pygame.mixer.music.get_busy() and not paused:
        current_pos = pygame.mixer.music.get_pos() / 1000
        current_time = base_time + current_pos
        current_time = min(current_time, total_duration)
        current_time_label.config(text=convert_seconds_to_time(current_time))
        update_slider_position(current_time)
    root.after(1000, update_time_slider)

def start_seek(event):
    global is_seeking, seek_start_time, base_time
    is_seeking = True
    seek_start_time = time.time()
    slider = event.widget
    trough_width = slider.winfo_width()

    if trough_width == 0:
        return
    click_x = event.x
    min_val = slider.cget("from")
    max_val = slider.cget("to")
    desired_value = (click_x / trough_width) * (max_val - min_val) + min_val
    desired_value = max(min(desired_value, max_val), min_val)
    seek()

def seek(event=None):
    global last_seek_time, base_time, paused, is_playing

    if not is_playing or not songs:
        return
    pygame.mixer.music.stop()
    pygame.mixer.music.load(os.path.join(current_folder, songs[current_index]))
    pygame.mixer.music.play(start=current_time)

    if paused:
        pygame.mixer.music.pause()
    base_time = current_time
    last_seek_time = time.time()

def on_release(event):
    global is_seeking
    is_seeking = False
    seek()

def play_next_song(event=None):
    global current_index

    if not is_playing or not songs:
        return

    if shuffle_enabled:
        next_index = get_next_shuffle_index()
    else:
        next_index = current_index + 1

        if next_index >= len(songs):
            return

    if next_index is not None and 0 <= next_index < len(songs):
        play_song_by_index(next_index)

def pause_unpause(event = None):
    global paused

    if not is_playing:
        return

    if paused:
        pygame.mixer.music.unpause()
        paused = False
        fade_play_btn.place_forget()
        play_btn.place_forget()
        pause_btn.place(relx=0.5, rely=0.5, anchor="center")
    else:
        pygame.mixer.music.pause()
        paused = True
        pause_btn.place_forget()
        fade_play_btn.place_forget()
        play_btn.place(relx=0.5, rely=0.5, anchor="center")

def stop():
    global is_playing
    pygame.mixer.music.stop()
    is_playing = False

def on_mousewheel(event):

    if event.state & 0x0001:
        canvas.xview_scroll(-1 * (event.delta // 120), "units")
    else:
        canvas.yview_scroll(-1 * (event.delta // 120), "units")

def resize_song_label(event):
    song_label.config(wraplength=event.width - 100)

def play_previous_song(event=None):

    if not is_playing:
        return
    global current_index

    if current_index > 0:
        play_song_by_index(current_index - 1)

def update_slider_position(time_pos):
    """Update slider position and progress line based on time"""
    global current_time
    current_time = max(0, min(time_pos, total_duration))

    if total_duration == 0:
        return
    canvas_width = timeline_canvas.winfo_width()

    if canvas_width < 20:
        return
    x_pos = 10 + (current_time / total_duration) * (canvas_width - 20)
    x_pos = max(10, min(x_pos, canvas_width - 10))
    timeline_canvas.coords(progress_line, 10, 10, x_pos, 10)
    timeline_canvas.coords(slider_handle, x_pos-8, 3, x_pos+8, 19)
    timeline_canvas.itemconfig(slider_handle, state="normal")
    current_time_label.config(text=convert_seconds_to_time(current_time))

def start_drag(event):
    global is_dragging, drag_start_x, base_time
    is_dragging = True
    drag_start_x = event.x
    canvas_width = timeline_canvas.winfo_width()

    if canvas_width > 20:
        proportion = (event.x - 10) / (canvas_width - 20)
        proportion = max(0.0, min(proportion, 1.0))
        desired_value = proportion * total_duration
        update_slider_position(desired_value)

def during_drag(event):

    if is_dragging:
        canvas_width = timeline_canvas.winfo_width()

        if canvas_width > 20:
            proportion = (event.x - 10) / (canvas_width - 20)
            proportion = max(0.0, min(proportion, 1.0))
            current_time = proportion * total_duration
            update_slider_position(current_time)

def end_drag(event):
    global is_dragging
    is_dragging = False
    seek()

def on_timeline_configure(event):
    canvas_width = event.width
    timeline_canvas.coords(timeline_line, 10, 10, canvas_width-10, 10)
    current_time_label.place(x=30, y=15)
    total_time_label.place(relx=1.0, x=-30, y=15, anchor='ne')

    if is_playing:
        update_slider_position(current_time)

def skip_forward(event = None):
    global current_time, base_time, is_playing

    if not is_playing or not songs:
        return
    new_time = current_time + 10

    if new_time > total_duration:
        new_time = total_duration
    current_time = new_time
    base_time = current_time
    update_slider_position(current_time)
    seek()

def skip_backward(event = None):
    global current_time, base_time, is_playing

    if not is_playing or not songs:
        return
    new_time = current_time - 10

    if new_time < 0:
        new_time = 0
    current_time = new_time
    base_time = current_time
    update_slider_position(current_time)
    seek()

def show_night_options():
    x = night_btn.winfo_rootx()
    y = night_btn.winfo_rooty() + night_btn.winfo_height()
    night_menu.post(x, y)

def toggle_pause_after_current():
    global pause_after_current
    pause_after_current = not pause_after_current
    night_menu.entryconfig(0, label=("✓ " if pause_after_current else "") + "Pause when song ends")

def pause_after_timer():
    global paused, timer_id, timer_end_time
    pygame.mixer.music.pause()
    paused = True
    pause_after_current = False
    night_menu.entryconfig(0, label=("✓ " if pause_after_current else "") + "Pause when song ends")
    pause_btn.place_forget()
    fade_play_btn.place_forget()
    pause_btn.place_forget()
    play_btn.place(relx=0.5, rely=0.5, anchor="center")
    timer_label.config(text="")
    timer_end_time = 0

    if timer_id:
        root.after_cancel(timer_id)
        timer_id = None

def update_timer_label():
    global timer_end_time

    if timer_end_time > time.time():
        remaining = timer_end_time - time.time()
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        timer_label.config(text=f"Sleep: {mins}:{secs:02d}")
        root.after(1000, update_timer_label)
    else:
        timer_label.config(text="")
        timer_end_time = 0

def set_timer(minutes):
    global timer_id, timer_end_time

    if timer_id:
        root.after_cancel(timer_id)
    timer_id = root.after(minutes * 60000, pause_after_timer)
    timer_end_time = time.time() + minutes * 60
    update_timer_label()

def start_volume_drag(event):
    global is_volume_dragging
    is_volume_dragging = True
    during_volume_drag(event)

def during_volume_drag(event):
    global last_volume

    if is_volume_dragging:
        x = event.x
        x = max(10, min(x, 90))
        volume_slider_canvas.coords(volume_handle, x-5, 10, x+5, 20)
        volume_slider_canvas.coords(volume_progress, 10, 15, x, 15)
        volume_percent = int(((x - 10) / 80) * 100)
        volume = volume_percent / 100
        pygame.mixer.music.set_volume(volume)
        volume_slider_canvas.itemconfig(volume_percent_text, text=f"{volume_percent}%")

        if volume == 0:
            unmute_btn.pack_forget()
            mute_btn.pack(side=tk.LEFT, padx=(0, 2))
        else:
            mute_btn.pack_forget()
            unmute_btn.pack(side=tk.LEFT, padx=(0, 2))
            last_volume = volume

def end_volume_drag(event):
    global is_volume_dragging
    is_volume_dragging = False

def mute_unmute():
    global last_volume
    current_volume = pygame.mixer.music.get_volume()

    if current_volume > 0:
        last_volume = current_volume
        pygame.mixer.music.set_volume(0)
        x = 10
        volume_slider_canvas.coords(volume_handle, x-5, 10, x+5, 20)
        volume_slider_canvas.coords(volume_progress, 10, 15, x, 15)
        volume_slider_canvas.itemconfig(volume_percent_text, text="0%")
        unmute_btn.pack_forget()
        mute_btn.pack(side=tk.LEFT, padx=(0, 2))
    else:
        pygame.mixer.music.set_volume(last_volume)
        volume_percent = int(last_volume * 100)
        x = 10 + (volume_percent * 80) // 100
        x = max(10, min(x, 90))
        volume_slider_canvas.coords(volume_handle, x-5, 10, x+5, 20)
        volume_slider_canvas.coords(volume_progress, 10, 15, x, 15)
        volume_slider_canvas.itemconfig(volume_percent_text, text=f"{volume_percent}%")
        mute_btn.pack_forget()
        unmute_btn.pack(side=tk.LEFT, padx=(0, 2))

def shuffle():
    global shuffle_enabled, shuffled_songs, played_indices
    shuffle_enabled = not shuffle_enabled
    suffle_btn.config(bg="blue" if shuffle_enabled else bg_color)

    if shuffle_enabled:
        shuffled_songs = songs.copy()
        random.shuffle(shuffled_songs)
        played_indices.clear()

def get_next_shuffle_index():
    global shuffled_songs, played_indices

    if not shuffled_songs:
        shuffled_songs = songs.copy()
        random.shuffle(shuffled_songs)
        played_indices.clear()

    while shuffled_songs:
        next_song = shuffled_songs.pop(0)
        next_index = songs.index(next_song)

        if next_index not in played_indices:
            played_indices.add(next_index)
            return next_index
    return None

def update_window_title():
    """Update window title with current song position"""

    if songs and current_index >= 0 and current_index < len(songs):
        root.title(f"Music Player - {current_index+1}/{len(songs)}")
    else:
        root.title("Music Player")
song_name_frame = tk.Frame(root, bg=bg_color, height=100)
song_name_frame.bind("<Configure>", resize_song_label)
song_var = tk.StringVar()
song_label  = tk.Label(song_name_frame, textvariable=song_var, fg="white", bg=bg_color, font=("Arial", 14))
song_label.pack(expand=True, pady=5)
main_frame = tk.Frame(root, background=bg_color)
canvas_frame = tk.Frame(main_frame)
canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
style = ttk.Style()
style.theme_use('clam')
style.configure(
    "Vertical.TScrollbar",
    gripcount=0,
    background='#0d02d5', # blue
    darkcolor='#00ffff',
    lightcolor='#00ffff',
    troughcolor='#00ffff', # black
    bordercolor='#00ffff', # black
    arrowcolor='#00ffff', # black
    relief="flat",
    width=5
)
style.map(
    "Vertical.TScrollbar",
    background=[('active', 'magenta')],
    arrowcolor=[('active', 'blue')]
)
canvas = tk.Canvas(canvas_frame, bg=bg_color, highlightthickness=0)
scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", style="Vertical.TScrollbar",  command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind_all("<MouseWheel>", on_mousewheel)
canvas.bind_all("<Shift-MouseWheel>", on_mousewheel)
canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
song_frame = tk.Frame(canvas, bg = bg_color)
canvas.create_window((0, 0), window=song_frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
song_frame.bind("<Configure>", on_frame_configure)
open_folder_btn_img= Image.open(resource_path(r"icons\folder.png")).resize((100, 100))
open_folder_btn_icon= ImageTk.PhotoImage(open_folder_btn_img)
open_folder_btn_small_img= Image.open(resource_path(r"icons\folder.png")).resize((30, 30))
open_folder_btn_small_icon= ImageTk.PhotoImage(open_folder_btn_small_img)
play_btn_img= Image.open(resource_path(r"icons\play.png")).resize((50, 50))
play_btn_icon= ImageTk.PhotoImage(play_btn_img)
fade_play_btn_img= Image.open(resource_path(r"icons\faded_play.png")).resize((50, 50))
fade_play_btn_icon= ImageTk.PhotoImage(fade_play_btn_img)
pause_img= Image.open(resource_path(r"icons\pause.png")).resize((50, 50))
pause_icon= ImageTk.PhotoImage(pause_img)
next_btn_img = Image.open(resource_path(r"icons\next.png")).resize((40, 40))
next_btn_icon = ImageTk.PhotoImage(next_btn_img)
prev_btn_img = Image.open(resource_path(r"icons\previous.png")).resize((40, 40))
prev_btn_icon = ImageTk.PhotoImage(prev_btn_img)
fade_next_btn_img = Image.open(resource_path(r"icons\faded_next.png")).resize((40, 40))
fade_next_btn_icon = ImageTk.PhotoImage(fade_next_btn_img)
fade_prev_btn_img = Image.open(resource_path(r"icons\faded_previous.png")).resize((40, 40))
fade_prev_btn_icon = ImageTk.PhotoImage(fade_prev_btn_img)
skip_back_btn_img = Image.open(resource_path(r"icons\skip_back.png")).resize((40, 40))
skip_back_btn_icon = ImageTk.PhotoImage(skip_back_btn_img)
skip_forward_btn_img = Image.open(resource_path(r"icons\skip_fd.png")).resize((40, 40))
skip_forward_btn_icon = ImageTk.PhotoImage(skip_forward_btn_img)
night_mode_img = Image.open(resource_path(r"icons\night_mode.png")).resize((30, 30))
night_mode_icon = ImageTk.PhotoImage(night_mode_img)
mute_img = Image.open(resource_path(r"icons\mute.png")).resize((20, 20))
mute_icon = ImageTk.PhotoImage(mute_img)
unmute_img = Image.open(resource_path(r"icons\unmute.png")).resize((20, 20))
unmute_icon = ImageTk.PhotoImage(unmute_img)
suffle_img = Image.open(resource_path(r"icons\suffle.png")).resize((35, 35))
suffle_icon = ImageTk.PhotoImage(suffle_img)
timeline_frame = tk.Frame(main_frame, bg=bg_color,height=50)
timeline_frame.pack(side=tk.TOP, fill="x", padx=10, pady=5)
timeline_frame.pack_propagate(False)
timeline_canvas = tk.Canvas(timeline_frame, bg=bg_color, height=20, highlightthickness=0)
timeline_canvas.pack(fill="x", expand=True, padx=100, pady=5)
timeline_canvas.bind("<Configure>", on_timeline_configure)
timeline_canvas.bind("<Button-1>", start_drag)
timeline_canvas.bind("<B1-Motion>", during_drag)
timeline_canvas.bind("<ButtonRelease-1>", end_drag)
timeline_line = timeline_canvas.create_line(10, 10, 10, 10, fill="#5357fb", width=3)
progress_line = timeline_canvas.create_line(10, 10, 10, 10, fill="#00ff00", width=3)
slider_handle = timeline_canvas.create_oval(0, 0, 16, 16, fill="magenta", outline="magenta", state="hidden")
current_time = 0
current_time_label = tk.Label(timeline_frame, text="0:00", fg="white", bg=bg_color, font=("Arial", 12))
total_time_label = tk.Label(timeline_frame, text="0:00", fg="white", bg=bg_color, font=("Arial", 12))
controls = tk.Frame(main_frame, bg=bg_color, height=80)
controls.pack(side=tk.BOTTOM, fill="x",padx=10, pady=10)
controls.pack_propagate(False)
folder_frame = tk.Frame(root, bg=bg_color, width=600,height=600)
folder_frame.place(relx=0.5, rely=0.45, anchor="center")
folder_frame.bind('<Configure>', update_gradient)
big_open_folder_btn = tk.Button(folder_frame, image=open_folder_btn_icon, command=load_folder, bg=bg_color, fg="white", border=0, borderwidth=0, activebackground=bg_color)
big_open_folder_btn.place(relx=0.5, rely=0.5, anchor="center")
tk.Label(folder_frame, text="No song folder selected!\nPlease select a song folder", bg=bg_color, fg="white", font=("Arial", 18)).place(relx=0.5, rely=0.63, anchor="center")
open_folder_btn = tk.Button(song_name_frame, image=open_folder_btn_small_icon, command=load_folder, bg=bg_color, fg="white", border=0, borderwidth=0, activebackground=bg_color)
play_btn = tk.Button(controls, image=play_btn_icon, command=pause_unpause, bg=bg_color, fg="white", border=0, borderwidth=0, activebackground=bg_color)
play_btn.place(relx=0.5, rely=0.5, anchor="center")
fade_play_btn = tk.Button(controls, image=fade_play_btn_icon, command=None, bg=bg_color, fg="white", border=0, borderwidth=0, activebackground=bg_color)
fade_play_btn.place(relx=0.5, rely=0.5, anchor="center")
pause_btn = tk.Button(controls, image=pause_icon, command=pause_unpause, bg=bg_color, fg="white",  border=0, borderwidth=0, activebackground=bg_color)
prev_btn = tk.Button(
    controls,
    image=prev_btn_icon,
    command=play_previous_song,
    bg=bg_color,
    border=0,
    activebackground=bg_color
)
next_btn = tk.Button(
    controls,
    image=next_btn_icon,
    command=play_next_song,
    bg=bg_color,
    border=0,
    activebackground=bg_color
)
fade_prev_btn = tk.Button(
    controls,
    image=fade_prev_btn_icon,
    command=None,
    bg=bg_color,
    border=0,
    activebackground=bg_color
)
fade_prev_btn.place(relx=0.43, rely=0.5, anchor="center")
fade_next_btn = tk.Button(
    controls,
    image=fade_next_btn_icon,
    command=None,
    bg=bg_color,
    border=0,
    activebackground=bg_color
)
fade_next_btn.place(relx=0.57, rely=0.5, anchor="center")
skip_back_btn = tk.Button(
    controls,
    image=skip_back_btn_icon,
    command=skip_backward,
    bg=bg_color,
    border=0,
    activebackground=bg_color
)
ToolTip(skip_back_btn, "'LEFT ARROW'\nskip back for 10 seconds")
skip_forward_btn = tk.Button(
    controls,
    image=skip_forward_btn_icon,
    command=skip_forward,
    bg=bg_color,
    border=0,
    activebackground=bg_color
)
ToolTip(skip_forward_btn, "'RIGHT ARROW'\nSkip Forword for 10 seconds")
night_btn = tk.Button(controls, image=night_mode_icon, font=("Arial", 14),
                     bg=bg_color, fg="white", border=0,
                     command=show_night_options,
                     activebackground=bg_color)
ToolTip(night_btn, "Night Mode")
night_menu = tk.Menu(root, tearoff=0)
night_menu.add_command(label="Pause when song ends",background=bg_color,foreground="white",font=('Arial',14), command=toggle_pause_after_current)
timer_menu = tk.Menu(night_menu, tearoff=0)

for mins in [5, 10, 15, 30, 45, 60, 90, 120]:
    timer_menu.add_command(label=f"{mins} minutes",background=bg_color,foreground="white",font=('Arial',14),
                          command=lambda m=mins: set_timer(m))
night_menu.add_cascade(label="Set Sleep Timer",foreground="white",font=('Arial',14),background=bg_color, menu=timer_menu)
timer_label = tk.Label(controls, text="", fg="white", bg=bg_color, font=("Arial", 14))
timer_label.place(relx=0.85, rely=0.5, anchor="center")
volume_frame = tk.Frame(controls, width=140, height=30, bg=bg_color)
volume_frame.place(relx=0.15, rely=0.5, anchor="center")
volume_slider_canvas = tk.Canvas(volume_frame, width=140, height=30, bg=bg_color
                                 , highlightthickness=0)
volume_slider_canvas.pack(side=tk.RIGHT,fill='both', expand=True)
volume_slider_canvas.create_line(10, 15, 90, 15, fill="#5357fb", width=3)
volume_progress = volume_slider_canvas.create_line(10, 15, 90, 15, fill="#00ff00", width=3)
volume_handle = volume_slider_canvas.create_oval(85, 10, 95, 20, fill="magenta", outline="magenta")
volume_percent_text = volume_slider_canvas.create_text(100, 15, text="100%", fill="white",
                                                font=("Arial", 10), anchor="w")
volume_slider_canvas.bind("<Button-1>", start_volume_drag)
volume_slider_canvas.bind("<B1-Motion>", during_volume_drag)
volume_slider_canvas.bind("<ButtonRelease-1>", end_volume_drag)
mute_btn = tk.Button(volume_frame, image=mute_icon, font=("Arial", 14),
                     bg=bg_color, fg="white", border=0,
                     command=mute_unmute,
                     activebackground=bg_color)
unmute_btn = tk.Button(volume_frame, image=unmute_icon, font=("Arial", 14),
                     bg=bg_color, fg="white", border=0,
                     command=mute_unmute,
                     activebackground=bg_color)
unmute_btn.pack(side=tk.LEFT, padx=(0, 2))
suffle_btn = tk.Button(controls,
                        image=suffle_icon,
                        text="Shuffle",
                        font=("Arial", 14),
                        bg=bg_color, fg="white", border=0,
                        command=shuffle,
                        activebackground=bg_color,
                        borderwidth=0,
                        highlightthickness=0,
                        )
ToolTip(suffle_btn, "Shuffle Songs to Play")
root.bind("<Up>", play_previous_song)
root.bind("<Down>", play_next_song)
root.bind("<Right>", skip_forward)
root.bind("<Left>", skip_backward)
root.bind("<space>", pause_unpause)
load_window_geometry()
root.protocol("WM_DELETE_WINDOW", on_close)
root.after(1000, update_time_slider)
check_song_end()
root.mainloop()
