# YouTube Hover 🎬

![YouTube Hover Screenshot](YouTube%20Hover/images/screenshot.png)

Float YouTube videos above all your Mac apps with one click. 

A sleek, native-feeling Chrome extension that leverages the Picture-in-Picture API to detach YouTube videos into an OS-level floating window. Perfect for watching tutorials, podcasts, or music videos while working in other apps.

## Features

- **Native Floating Window**: Stays on top of all macOS applications (Slack, Finder, Notes, etc.).
- **In-Player Controls**: A subtle, beautiful hover button injected directly into the YouTube player.
- **Premium Dark UI**: A polished extension popup that matches YouTube's aesthetic.
- **Survives Minimize**: The floating window persists even if you minimize the Chrome browser window.

## Installation (Developer Mode)

Since this extension is not yet published on the Chrome Web Store, you can install it locally:

1. Clone or download this repository.
2. Open Chrome and navigate to `chrome://extensions/`.
3. Toggle **Developer mode** ON (top-right corner).
4. Click the **"Load unpacked"** button.
5. Select the `extension` folder from this repository.
6. The YouTube Hover icon will appear in your Chrome toolbar!

## Usage

1. Open any [YouTube](https://youtube.com) video.
2. **Method 1**: Click the "Hover" button that appears in the bottom-right corner of the video player.
3. **Method 2**: Click the extension icon in your Chrome toolbar and select "Hover Video".

To return the video to the browser, simply click the exit button on the floating window, or click "Exit Hover" in the player.

## Technologies Used

- Chrome Extension Manifest V3
- HTML/CSS/JavaScript (Vanilla)
- Native HTMLVideoElement `requestPictureInPicture()` API

## Credits

This project was built with Antigravity, an advanced agentic coding assistant developed by the Google DeepMind team.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
