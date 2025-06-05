# MUSIC PLAYER

This Python music player offers a comprehensive set of features with an elegant gradient-based UI. Here's a breakdown of its capabilities:

1. **Modern UI Design**
   - Dynamic blue-purple gradient background
   - Responsive layout that adapts to window resizing
   - Custom icons for all controls
   - Platform-specific configuration storage (Windows/macOS/Linux)

2. **Playback Controls**
   - Play/Pause toggle
   - Next/Previous track navigation
   - 10-second skip forward/backward
   - Shuffle mode with visual indicator
   - Volume control with mute/unmute
   - Draggable progress bar

3. **Playlist Management**
   - Load folders of MP3 files
   - Scrollable song list with duration display
   - Highlight currently playing track
   - Right-click context menu to delete songs
   - Auto-scroll to current track

4. **Advanced Features**
   - **Sleep Timer**: Set auto-pause after time intervals (5-120 min)
   - **End-of-Song Pause**: Option to stop after current track
   - **Keyboard Shortcuts**:
     - Space: Play/Pause
     - Arrow Keys: Navigation/skipping
     - Up/Down: Previous/Next track
     - Left/Right: 10-sec skip

5. **Technical Implementation**
   - Pygame for audio playback
   - Mutagen for MP3 metadata/duration
   - PIL/Pillow for image processing
   - Persistent configuration (remembers last folder/window size)
   - Tooltips for all controls
   - Custom scrollbar styling
   - Proper resource handling for PyInstaller

6. **Visual Indicators**
   - Current/total time display
   - Timer status indicator
   - Volume percentage readout
   - Active track highlighting with font enhancement
   - Disabled buttons when unavailable (e.g., prev/next at ends)

7. **Optimizations**
   - Efficient gradient rendering
   - Asynchronous song-end detection
   - Smooth seek operations
   - Minimal resource usage during idle

The player combines aesthetic design with robust functionality, featuring a distinctive purple/blue color scheme with magenta accents. Its thoughtful UX includes visual feedback for all interactions and intelligent state management.

# DEMO IMAGES
![Screenshot 2025-05-11 112036](https://github.com/user-attachments/assets/1b8ea7b0-5b6f-4f2d-b7ab-bd6ff4c92d2c)
![Screenshot 2025-05-11 111953](https://github.com/user-attachments/assets/32b35950-7c86-430d-b271-a57a0326df8e)
![Screenshot 2025-05-11 111912](https://github.com/user-attachments/assets/a1796692-ca94-4924-8512-dd805c25dee7)

