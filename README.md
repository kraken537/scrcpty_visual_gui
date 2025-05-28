# Scrcpy & DroidCam Launcher GUI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A user-friendly desktop application to launch and manage [Scrcpy](https://github.com/Genymobile/scrcpy) for Android screen mirroring and [DroidCam](https://www.dev47apps.com/) for using your phone as a webcam. This tool provides a convenient GUI to configure various options without needing to remember command-line arguments.

![Scrcpy & DroidCam Launcher Screenshot](https://i.imgur.com/your-screenshot-url.png) ## ✨ Features

* **Scrcpy Launcher:**
    * Extensive GUI for most Scrcpy command-line options.
    * Categorized options: Basic, Display, Performance, Control, and Advanced.
    * Real-time command preview as you select options.
    * Support for TCP/IP (wireless) connections.
    * Options for video codec, resolution, FPS, bitrate, recording, and more.
    * Input custom Scrcpy parameters.
* **DroidCam Launcher:**
    * Simple interface to start/stop DroidCam.
    * Phone IP address detection via USB/ADB.
    * Guidance on setting up DroidCam.
* **General:**
    * Modern, readable, and aesthetically pleasing user interface built with PyQt5.
    * Automatic check for Scrcpy installation with an option to download.
    * Activity log to monitor application actions and process status.
    * Independent process management for Scrcpy and DroidCam.
    * Cross-platform (Windows support for Scrcpy download, Linux/macOS instructions provided).

## 📋 Requirements

* **Python 3**
* **PyQt5:** For the graphical user interface.
* **Scrcpy:** Installed and preferably added to your system's PATH.
    * The application can attempt to download Scrcpy for Windows if not found.
    * For Linux/macOS, installation via package managers (apt, dnf, pacman, brew) is recommended.
* **DroidCam:** (Optional) Installed on your computer and phone if you intend to use the DroidCam feature.
    * The DroidCam client needs to be available in your system's PATH (e.g., `droidcam-cli`).
* **ADB (Android Debug Bridge):** Required for phone IP detection and for Scrcpy to function. Usually included with Android SDK Platform Tools.

## 🚀 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
    cd your-repository-name
    ```
    *(Replace `your-username/your-repository-name` with your actual GitHub repository details)*

2.  **Install Python dependencies:**
    ```bash
    pip install PyQt5
    ```

3.  **Ensure Scrcpy is installed:**
    * **Windows:** If Scrcpy is not found, the application will offer to download it. Otherwise, download it from the [official Scrcpy GitHub page](https://github.com/Genymobile/scrcpy/releases) and add it to your PATH.
    * **Linux:**
        ```bash
        sudo apt install scrcpy  # Debian/Ubuntu
        sudo dnf install scrcpy  # Fedora
        sudo pacman -S scrcpy    # Arch Linux
        ```
    * **macOS:**
        ```bash
        brew install scrcpy
        ```

4.  **Ensure DroidCam is installed (Optional):**
    * Download and install DroidCam from [dev47apps.com](https://www.dev47apps.com/) on your computer and phone.
    * Ensure the DroidCam command-line tool (e.g., `droidcam-cli`) is in your PATH.

5.  **Ensure ADB is installed and in PATH:**
    * Download Android SDK Platform Tools from [developer.android.com](https://developer.android.com/studio/releases/platform-tools) and add ADB to your PATH.

## ▶️ Usage

1.  Run the Python script:
    ```bash
    python qt_scrcpty.py
    ```
2.  **Scrcpy Tab:**
    * Select your desired Scrcpy options from the various categories.
    * If using a wireless connection, check "TCP/IP connection" and enter your phone's IP address and port (e.g., `192.168.1.100:5555`). You might need to enable wireless ADB on your phone first (`adb tcpip 5555`).
    * Click "START SCRCPY".
3.  **DroidCam Tab:**
    * Ensure the DroidCam app is running on your phone and it's on the same WiFi network.
    * Optionally, click "Detect Phone IP (via USB)" to find your phone's IP if connected via USB with debugging enabled.
    * Click "START DROIDCAM" and enter your phone's IP address when prompted.
4.  Use the "STOP" buttons to terminate the respective processes.
5.  Check the "Activity Logs" for status updates and error messages.

## 🖼️ Screenshots

*Main Interface with Scrcpy Tab:*
![Scrcpy Tab Screenshot](https://i.imgur.com/your-scrcpy-tab-screenshot.png) *DroidCam Tab:*
![DroidCam Tab Screenshot](https://i.imgur.com/your-droidcam-tab-screenshot.png) *(Add more screenshots as needed, e.g., IP detection, error messages, etc.)*

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or bug fixes, please feel free to:
1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (though you'll need to create this file if you want to include it).

---

Crafted with ❤️ by [Your Name/GitHub Username]
