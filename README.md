# MUSIC PLAYER
This code is a **Tkinter-based music player** with the following features:

### Core Functionality:
- **Audio Playback**: Uses Pygame mixer for MP3 playback with play/pause, skip (forward/backward), and track navigation.
- **Playlist Management**: Loads MP3 files from a folder, displays them in a scrollable list, and highlights the currently playing track.
- **Persistent Settings**: Saves/restores window size, state, and last-opened folder via `config.ini` (stored in OS-specific config directories).

### UI Elements:
- **Gradient Background**: Dynamic vertical gradient (blue to purple) that resizes with the window.
- **Timeline Controls**: 
  - Seekable progress bar with current/total time display.
  - Skip buttons (+10/-10 seconds) and keyboard shortcuts (arrow keys/spacebar).
- **Volume Slider**: Interactive slider with mute/unmute toggle and percentage display.
- **Night Mode Menu**: Options to pause after the current song or set a sleep timer (5–120 minutes).

### Additional Features:
- **System Integration**: 
  - Proper app ID setup for Windows taskbar.
  - Cross-platform config/file paths (Windows/Linux/macOS).
- **Error Handling**: Graceful fallback for missing icons/resources.
- **Keyboard Shortcuts**: Space (play/pause), arrows (navigation/skip), etc.
- **Mouse Click**: Right click on songs name, a "Delete" popup open to delte the song permanently
- **Shuffle**: Shuffle the Songs when playing

### Code Structure:
- Uses **OOP-like patterns** with global state management for playback/UI.
- Supports PyInstaller packaging via `resource_path()` for bundled resources.
- Event-driven updates for real-time progress/volume changes.

### Dependencies:
- `tkinter`, `pygame`, `PIL` (for images), `mutagen` (for MP3 metadata), `configparser`.

Aim: A lightweight, cross-platform music player with modern UI elements and essential playback controls.

# DEMO IMAGES
![Screenshot 2025-05-11 112036](https://github.com/user-attachments/assets/1b8ea7b0-5b6f-4f2d-b7ab-bd6ff4c92d2c)
![Screenshot 2025-05-11 111953](https://github.com/user-attachments/assets/32b35950-7c86-430d-b271-a57a0326df8e)
![Screenshot 2025-05-11 111912](https://github.com/user-attachments/assets/a1796692-ca94-4924-8512-dd805c25dee7)

