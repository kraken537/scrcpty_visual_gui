#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrcpy & DroidCam Launcher - GUI Application for Mobile Screen Mirroring

This application provides a user-friendly interface for:
- Launching scrcpy with various configuration options
- Launching DroidCam for using phone as webcam
- Managing both processes independently
- Automatic scrcpy installation check

Requirements:
- PyQt5
- scrcpy installed and available in PATH (or auto-download)
- DroidCam installed and available in PATH (optional)

Author: Your Name
License: MIT
"""

import sys
import subprocess
import os
import platform
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QMessageBox, QFrame, QCheckBox, QSpinBox, 
                             QGroupBox, QGridLayout, QTabWidget, QScrollArea,
                             QLineEdit, QComboBox, QProgressDialog, QInputDialog)
from PyQt5.QtCore import QProcess, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette
from PyQt5.Qt import Qt

class ScrcpyDownloader(QThread):
    """Thread for downloading scrcpy in background"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.system = platform.system().lower()
        
    def run(self):
        try:
            # Determine download URL based on system
            if self.system == 'windows':
                url = "https://github.com/Genymobile/scrcpy/releases/latest/download/scrcpy-win64.zip"
                filename = "scrcpy-win64.zip"
            elif self.system == 'linux':
                self.status.emit("Na Linuxie zalecamy instalację przez menedżer pakietów:\n"
                               "Ubuntu/Debian: sudo apt install scrcpy\n"
                               "Fedora: sudo dnf install scrcpy\n"
                               "Arch: sudo pacman -S scrcpy")
                self.finished.emit(False)
                return
            elif self.system == 'darwin':
                self.status.emit("Na macOS zalecamy instalację przez Homebrew:\n"
                               "brew install scrcpy")
                self.finished.emit(False)
                return
            else:
                self.status.emit("Nieobsługiwany system operacyjny")
                self.finished.emit(False)
                return
                
            # Download scrcpy
            self.status.emit(f"Pobieranie {filename}...")
            self.download_file(url, filename)
            
            # Extract
            self.status.emit("Rozpakowywanie...")
            self.extract_file(filename)
            
            # Add to PATH or move to appropriate location
            self.status.emit("Konfigurowanie...")
            self.configure_scrcpy()
            
            self.finished.emit(True)
            
        except Exception as e:
            self.status.emit(f"Błąd: {str(e)}")
            self.finished.emit(False)
    
    def download_file(self, url, filename):
        """Download file with progress"""
        response = urllib.request.urlopen(url)
        total_size = int(response.headers.get('Content-Length', 0))
        downloaded = 0
        
        with open(filename, 'wb') as f:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    progress = int((downloaded / total_size) * 100)
                    self.progress.emit(progress)
    
    def extract_file(self, filename):
        """Extract downloaded archive"""
        if filename.endswith('.zip'):
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall('.')
        elif filename.endswith('.tar.gz'):
            with tarfile.open(filename, 'r:gz') as tar_ref:
                tar_ref.extractall('.')
                
    def configure_scrcpy(self):
        """Configure scrcpy after extraction"""
        # This would need system-specific configuration
        # For now, just inform user
        self.status.emit("Scrcpy pobrane. Dodaj folder scrcpy do PATH.")

class ScrcpyLauncher(QMainWindow):
    """
    Main application window for Scrcpy & DroidCam Launcher
    
    This class provides the main GUI interface with tabs for Scrcpy and DroidCam
    configuration and launching capabilities.
    """
    
    def __init__(self):
        """Initialize the main window and UI components"""
        super().__init__()
        self.scrcpy_process = None      # QProcess for scrcpy
        self.droidcam_process = None    # QProcess for droidcam
        self.init_ui()
        
        # Check scrcpy installation on startup
        QTimer.singleShot(500, self.check_and_offer_scrcpy_install)
        
    def init_ui(self):
        """Initialize the user interface with modern, readable styling"""
        # Main window settings
        self.setWindowTitle('Scrcpy & DroidCam Launcher v2.0')
        self.setGeometry(100, 100, 750, 850)
        
        # Modern color scheme with high contrast for readability
        # NAPRAWIONO: Usunięto właściwość 'transform' która powodowała błędy
        self.setStyleSheet("""
            /* Main window background */
            QMainWindow {
                background-color: #f5f5f5;
                color: #333333;
            }
            
            /* Primary buttons styling */
            QPushButton {
                background-color: #4285f4;
                border: none;
                color: white;
                padding: 12px 24px;
                text-align: center;
                font-size: 13px;
                font-weight: 600;
                margin: 3px;
                border-radius: 6px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
            QPushButton:pressed {
                background-color: #2a56c6;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
            }
            
            /* Labels styling */
            QLabel {
                color: #424242;
                font-size: 13px;
                font-weight: 500;
            }
            
            /* Text areas and logs */
            QTextEdit {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                padding: 8px;
            }
            QTextEdit:focus {
                border-color: #4285f4;
            }
            
            /* Line edits */
            QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #4285f4;
            }
            
            /* Combo boxes */
            QComboBox {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px 8px;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #4285f4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #5f6368;
                margin-right: 5px;
            }
            
            /* Checkboxes styling */
            QCheckBox {
                color: #424242;
                font-size: 12px;
                font-weight: 500;
                spacing: 8px;
                padding: 4px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #ffffff;
                border: 2px solid #dadce0;
            }
            QCheckBox::indicator:unchecked:hover {
                border-color: #4285f4;
            }
            QCheckBox::indicator:checked {
                background-color: #4285f4;
                border: 2px solid #4285f4;
            }
            
            /* Group boxes styling */
            QGroupBox {
                color: #1a73e8;
                font-weight: 600;
                font-size: 14px;
                border: 2px solid #e8f0fe;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background-color: #f5f5f5;
            }
            
            /* Spin boxes styling */
            QSpinBox {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px 8px;
                min-width: 70px;
                font-weight: 500;
            }
            QSpinBox:focus {
                border-color: #4285f4;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #f8f9fa;
                border: none;
                width: 20px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #e8f0fe;
            }
            
            /* Tab widget styling */
            QTabWidget::pane {
                border: 2px solid #e0e0e0;
                background-color: #ffffff;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                color: #5f6368;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background-color: #4285f4;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
            
            /* Scroll area styling */
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f1f3f4;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #dadce0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #bdc1c6;
            }
        """)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Application title
        title = QLabel('📱 Scrcpy & DroidCam Launcher')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Segoe UI', 20, QFont.Bold))
        title.setStyleSheet("color: #1a73e8; margin: 10px 0 20px 0;")
        main_layout.addWidget(title)
        
        # Create tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("QTabWidget::pane { margin-top: 5px; }")
        
        # Tab 1: Scrcpy configuration
        scrcpy_tab = self.create_scrcpy_tab()
        tabs.addTab(scrcpy_tab, "📱 Scrcpy Mirror")
        
        # Tab 2: DroidCam configuration
        droidcam_tab = self.create_droidcam_tab()
        tabs.addTab(droidcam_tab, "📷 DroidCam Webcam")
        
        main_layout.addWidget(tabs)
        
        # Status and logs section at bottom
        self.create_status_section(main_layout)
        
        central_widget.setLayout(main_layout)
    
    def create_scrcpy_tab(self):
        """
        Create the Scrcpy configuration tab with all available options
        
        Returns:
            QWidget: Configured tab widget with scrcpy options
        """
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Scroll area for options
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(420)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(15)
        
        # Basic Options Group
        basic_group = QGroupBox("⚙️ Podstawowe opcje")
        basic_layout = QGridLayout()
        basic_layout.setSpacing(8)
        
        self.scrcpy_fullscreen = QCheckBox("Tryb pełnoekranowy (-f)")
        self.scrcpy_stay_awake = QCheckBox("Utrzymuj urządzenie włączone (-w)")
        self.scrcpy_show_touches = QCheckBox("Pokazuj dotknięcia palcem (-t)")
        self.scrcpy_disable_screensaver = QCheckBox("Wyłącz wygaszacz ekranu (-S)")
        
        basic_layout.addWidget(self.scrcpy_fullscreen, 0, 0)
        basic_layout.addWidget(self.scrcpy_stay_awake, 0, 1)
        basic_layout.addWidget(self.scrcpy_show_touches, 1, 0)
        basic_layout.addWidget(self.scrcpy_disable_screensaver, 1, 1)
        basic_group.setLayout(basic_layout)
        
        # Display Options Group
        display_group = QGroupBox("🖥️ Opcje wyświetlania")
        display_layout = QGridLayout()
        display_layout.setSpacing(8)
        
        self.scrcpy_borderless = QCheckBox("Okno bez ramki (-b)")
        self.scrcpy_always_on_top = QCheckBox("Zawsze na wierzchu (-T)")
        self.scrcpy_turn_screen_off = QCheckBox("Wyłącz ekran urządzenia (-o)")
        self.scrcpy_no_audio = QCheckBox("Wyłącz dźwięk (--no-audio)")
        
        display_layout.addWidget(self.scrcpy_borderless, 0, 0)
        display_layout.addWidget(self.scrcpy_always_on_top, 0, 1)
        display_layout.addWidget(self.scrcpy_turn_screen_off, 1, 0)
        display_layout.addWidget(self.scrcpy_no_audio, 1, 1)
        display_group.setLayout(display_layout)
        
        # Performance Options Group
        performance_group = QGroupBox("⚡ Ustawienia wydajności")
        performance_layout = QGridLayout()
        performance_layout.setSpacing(8)
        
        # Video codec selection
        performance_layout.addWidget(QLabel("Kodek wideo:"), 0, 0)
        self.scrcpy_video_codec = QComboBox()
        self.scrcpy_video_codec.addItems(["domyślny", "h264", "h265", "av1"])
        performance_layout.addWidget(self.scrcpy_video_codec, 0, 1)
        
        self.scrcpy_max_fps = QCheckBox("Ogranicz FPS:")
        self.scrcpy_fps_value = QSpinBox()
        self.scrcpy_fps_value.setRange(1, 120)
        self.scrcpy_fps_value.setValue(60)
        self.scrcpy_fps_value.setSuffix(" fps")
        
        self.scrcpy_max_size = QCheckBox("Maks. rozdzielczość:")
        self.scrcpy_size_value = QSpinBox()
        self.scrcpy_size_value.setRange(480, 4000)
        self.scrcpy_size_value.setValue(1920)
        self.scrcpy_size_value.setSuffix(" px")
        
        self.scrcpy_bit_rate = QCheckBox("Bitrate:")
        self.scrcpy_bitrate_value = QSpinBox()
        self.scrcpy_bitrate_value.setRange(1, 50)
        self.scrcpy_bitrate_value.setValue(8)
        self.scrcpy_bitrate_value.setSuffix(" Mbps")
        
        performance_layout.addWidget(self.scrcpy_max_fps, 1, 0)
        performance_layout.addWidget(self.scrcpy_fps_value, 1, 1)
        performance_layout.addWidget(self.scrcpy_max_size, 2, 0)
        performance_layout.addWidget(self.scrcpy_size_value, 2, 1)
        performance_layout.addWidget(self.scrcpy_bit_rate, 3, 0)
        performance_layout.addWidget(self.scrcpy_bitrate_value, 3, 1)
        performance_group.setLayout(performance_layout)
        
        # Control Options Group
        control_group = QGroupBox("🎮 Kontrola wejścia")
        control_layout = QGridLayout()
        control_layout.setSpacing(8)
        
        self.scrcpy_mouse_control = QCheckBox("Kontrola myszą (-M)")
        self.scrcpy_mouse_control.setChecked(True)
        
        self.scrcpy_keyboard_control = QCheckBox("Kontrola klawiaturą (-K)")
        self.scrcpy_keyboard_control.setChecked(True)
        
        self.scrcpy_no_control = QCheckBox("Tylko wyświetlanie, bez kontroli (-n)")
        
        # Keyboard mode selection
        control_layout.addWidget(QLabel("Tryb klawiatury:"), 2, 0)
        self.scrcpy_keyboard_mode = QComboBox()
        self.scrcpy_keyboard_mode.addItems(["domyślny", "uhid", "aoa"])
        control_layout.addWidget(self.scrcpy_keyboard_mode, 2, 1)
        
        control_layout.addWidget(self.scrcpy_mouse_control, 0, 0)
        control_layout.addWidget(self.scrcpy_keyboard_control, 0, 1)
        control_layout.addWidget(self.scrcpy_no_control, 1, 0, 1, 2)
        control_group.setLayout(control_layout)
        
        # Advanced Options Group
        advanced_group = QGroupBox("🔧 Opcje zaawansowane")
        advanced_layout = QGridLayout()
        advanced_layout.setSpacing(8)
        
        # Recording
        self.scrcpy_record = QCheckBox("Nagrywaj do pliku:")
        self.scrcpy_record_filename = QLineEdit("recording.mp4")
        self.scrcpy_record_filename.setPlaceholderText("nazwa_pliku.mp4")
        
        # Video source
        advanced_layout.addWidget(QLabel("Źródło wideo:"), 1, 0)
        self.scrcpy_video_source = QComboBox()
        self.scrcpy_video_source.addItems(["ekran", "kamera"])
        advanced_layout.addWidget(self.scrcpy_video_source, 1, 1)
        
        # TCP/IP connection
        self.scrcpy_tcpip = QCheckBox("Połączenie TCP/IP:")
        self.scrcpy_tcpip_address = QLineEdit()
        self.scrcpy_tcpip_address.setPlaceholderText("192.168.1.100:5555")
        
        # Screen timeout
        self.scrcpy_screen_timeout = QCheckBox("Timeout ekranu (s):")
        self.scrcpy_timeout_value = QSpinBox()
        self.scrcpy_timeout_value.setRange(0, 3600)
        self.scrcpy_timeout_value.setValue(300)
        
        # Orientation lock
        advanced_layout.addWidget(QLabel("Blokada orientacji:"), 4, 0)
        self.scrcpy_orientation = QComboBox()
        self.scrcpy_orientation.addItems(["auto", "0°", "90°", "180°", "270°"])
        advanced_layout.addWidget(self.scrcpy_orientation, 4, 1)
        
        advanced_layout.addWidget(self.scrcpy_record, 0, 0)
        advanced_layout.addWidget(self.scrcpy_record_filename, 0, 1)
        advanced_layout.addWidget(self.scrcpy_tcpip, 2, 0)
        advanced_layout.addWidget(self.scrcpy_tcpip_address, 2, 1)
        advanced_layout.addWidget(self.scrcpy_screen_timeout, 3, 0)
        advanced_layout.addWidget(self.scrcpy_timeout_value, 3, 1)
        advanced_group.setLayout(advanced_layout)
        
        # Custom parameters group
        custom_group = QGroupBox("✏️ Parametry własne")
        custom_layout = QVBoxLayout()
        
        custom_label = QLabel("Dodatkowe parametry (opcjonalne):")
        self.scrcpy_custom_params = QLineEdit()
        self.scrcpy_custom_params.setPlaceholderText("np. --prefer-text --legacy-paste")
        
        custom_layout.addWidget(custom_label)
        custom_layout.addWidget(self.scrcpy_custom_params)
        custom_group.setLayout(custom_layout)
        
        # Add groups to scroll layout
        scroll_layout.addWidget(basic_group)
        scroll_layout.addWidget(display_group)
        scroll_layout.addWidget(performance_group)
        scroll_layout.addWidget(control_group)
        scroll_layout.addWidget(advanced_group)
        scroll_layout.addWidget(custom_group)
        scroll_layout.addStretch()
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.scrcpy_start_button = QPushButton('▶️ URUCHOM SCRCPY')
        self.scrcpy_start_button.clicked.connect(self.start_scrcpy)
        self.scrcpy_start_button.setMinimumHeight(50)
        self.scrcpy_start_button.setStyleSheet("""
            QPushButton {
                background-color: #34a853;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2d8f3f;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        
        self.scrcpy_stop_button = QPushButton('⏹️ ZATRZYMAJ SCRCPY')
        self.scrcpy_stop_button.clicked.connect(self.stop_scrcpy)
        self.scrcpy_stop_button.setMinimumHeight(50)
        self.scrcpy_stop_button.setEnabled(False)
        self.scrcpy_stop_button.setStyleSheet("""
            QPushButton {
                background-color: #ea4335;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d33b2c;
            }
            QPushButton:pressed {
                background-color: #b52d20;
            }
        """)
        
        button_layout.addWidget(self.scrcpy_start_button)
        button_layout.addWidget(self.scrcpy_stop_button)
        layout.addLayout(button_layout)
        
        # Command preview
        self.scrcpy_command_label = QLabel("Komenda: scrcpy")
        self.scrcpy_command_label.setStyleSheet("""
            color: #5f6368; 
            margin: 10px; 
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11px;
            background-color: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #e0e0e0;
        """)
        self.scrcpy_command_label.setWordWrap(True)
        layout.addWidget(self.scrcpy_command_label)
        
        # Connect checkboxes to command update
        self.connect_scrcpy_checkboxes()
        
        tab.setLayout(layout)
        return tab
    
    def create_droidcam_tab(self):
        """
        Create the DroidCam configuration tab
        
        Returns:
            QWidget: Configured tab widget for DroidCam
        """
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Information about DroidCam
        info_container = QWidget()
        info_container.setStyleSheet("""
            QWidget {
                background-color: #e8f5e8;
                border-radius: 8px;
                border: 2px solid #c8e6c9;
            }
        """)
        info_layout = QVBoxLayout()
        
        info_title = QLabel("📷 DroidCam - Użyj telefonu jako kamery internetowej")
        info_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        info_title.setStyleSheet("color: #2e7d32; margin: 5px;")
        
        info_text = QLabel("""
<b>Przed użyciem DroidCam upewnij się, że:</b><br>
• DroidCam jest zainstalowany na komputerze i telefonie<br>
• Telefon i komputer są w tej samej sieci WiFi<br>
• Aplikacja DroidCam jest uruchomiona na telefonie<br>
• Twój telefon pokazuje adres IP i port<br><br>

<b>Jak używać:</b><br>
1. Otwórz aplikację DroidCam na telefonie<br>
2. Zanotuj pokazany adres IP (np. 192.168.1.100)<br>
3. Kliknij "URUCHOM DROIDCAM" poniżej<br>
4. Wprowadź adres IP gdy zostaniesz poproszony<br>
        """)
        info_text.setStyleSheet("""
            color: #1b5e20; 
            margin: 10px 15px; 
            line-height: 1.6;
            font-size: 12px;
        """)
        info_text.setWordWrap(True)
        
        info_layout.addWidget(info_title)
        info_layout.addWidget(info_text)
        info_container.setLayout(info_layout)
        
        layout.addWidget(info_container)
        layout.addStretch()
        
        # Control buttons for DroidCam
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.droidcam_start_button = QPushButton('▶️ URUCHOM DROIDCAM')
        self.droidcam_start_button.clicked.connect(self.start_droidcam)
        self.droidcam_start_button.setMinimumHeight(50)
        self.droidcam_start_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
            QPushButton:pressed {
                background-color: #ef6c00;
            }
        """)
        
        self.droidcam_stop_button = QPushButton('⏹️ ZATRZYMAJ DROIDCAM')
        self.droidcam_stop_button.clicked.connect(self.stop_droidcam)
        self.droidcam_stop_button.setMinimumHeight(50)
        self.droidcam_stop_button.setEnabled(False)
        self.droidcam_stop_button.setStyleSheet("""
            QPushButton {
                background-color: #ea4335;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d33b2c;
            }
            QPushButton:pressed {
                background-color: #b52d20;
            }
        """)
        
        button_layout.addWidget(self.droidcam_start_button)
        button_layout.addWidget(self.droidcam_stop_button)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_status_section(self, layout):
        """
        Create the status and logs section at the bottom of the window
        
        Args:
            layout: Parent layout to add the status section to
        """
        # Status indicator
        self.status_label = QLabel('✅ Gotowy do uruchomienia aplikacji')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #34a853; 
            margin: 10px; 
            font-weight: bold;
            font-size: 14px;
            background-color: #e8f5e8;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #c8e6c9;
        """)
        layout.addWidget(self.status_label)
        
        # Logs section
        log_label = QLabel('📝 Logi aktywności:')
        log_label.setStyleSheet("color: #1a73e8; font-weight: 600; margin-top: 10px;")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("Logi aplikacji pojawią się tutaj...")
        layout.addWidget(self.log_text)
    
    def connect_scrcpy_checkboxes(self):
        """Connect all checkboxes and inputs to the command update function"""
        # List of all checkboxes that affect the command
        checkboxes = [
            self.scrcpy_fullscreen, self.scrcpy_stay_awake, self.scrcpy_show_touches,
            self.scrcpy_disable_screensaver, self.scrcpy_borderless, self.scrcpy_always_on_top,
            self.scrcpy_turn_screen_off, self.scrcpy_max_fps, self.scrcpy_max_size,
            self.scrcpy_mouse_control, self.scrcpy_keyboard_control, self.scrcpy_no_control,
            self.scrcpy_no_audio, self.scrcpy_bit_rate, self.scrcpy_record,
            self.scrcpy_tcpip, self.scrcpy_screen_timeout
        ]
        
        # Connect each checkbox to the update function
        for checkbox in checkboxes:
            checkbox.stateChanged.connect(self.update_scrcpy_command)
        
        # Connect spinboxes to the update function
        self.scrcpy_fps_value.valueChanged.connect(self.update_scrcpy_command)
        self.scrcpy_size_value.valueChanged.connect(self.update_scrcpy_command)
        self.scrcpy_bitrate_value.valueChanged.connect(self.update_scrcpy_command)
        self.scrcpy_timeout_value.valueChanged.connect(self.update_scrcpy_command)
        
        # Connect combo boxes
        self.scrcpy_video_codec.currentTextChanged.connect(self.update_scrcpy_command)
        self.scrcpy_keyboard_mode.currentTextChanged.connect(self.update_scrcpy_command)
        self.scrcpy_video_source.currentTextChanged.connect(self.update_scrcpy_command)
        self.scrcpy_orientation.currentTextChanged.connect(self.update_scrcpy_command)
        
        # Connect line edits
        self.scrcpy_record_filename.textChanged.connect(self.update_scrcpy_command)
        self.scrcpy_tcpip_address.textChanged.connect(self.update_scrcpy_command)
        self.scrcpy_custom_params.textChanged.connect(self.update_scrcpy_command)
        
        # Initial command update
        self.update_scrcpy_command()
    
    def update_scrcpy_command(self):
        """Update the displayed scrcpy command based on selected options"""
        command = self.get_scrcpy_command()
        command_str = ' '.join(command)
        self.scrcpy_command_label.setText(f"Komenda: {command_str}")
    
    def get_scrcpy_command(self):
        """
        Generate the current scrcpy command based on selected options
        
        Returns:
            list: Command arguments for scrcpy execution
        """
        command = ['scrcpy']
        
        # TCP/IP connection takes precedence
        if self.scrcpy_tcpip.isChecked() and self.scrcpy_tcpip_address.text():
            command.append(f'--tcpip={self.scrcpy_tcpip_address.text()}')
        
        # Video codec
        if self.scrcpy_video_codec.currentText() != "domyślny":
            command.extend(['--video-codec', self.scrcpy_video_codec.currentText()])
        
        # Video source
        if self.scrcpy_video_source.currentText() == "kamera":
            command.append('--video-source=camera')
        
        # Control options
        if self.scrcpy_mouse_control.isChecked():
            command.append('-M')
        if self.scrcpy_keyboard_control.isChecked():
            command.append('-K')
            # Keyboard mode
            if self.scrcpy_keyboard_mode.currentText() != "domyślny":
                command.append(f'--keyboard={self.scrcpy_keyboard_mode.currentText()}')
        if self.scrcpy_no_control.isChecked():
            command.append('-n')
        
        # Resolution setting
        if self.scrcpy_max_size.isChecked():
            command.extend(['-m', str(self.scrcpy_size_value.value())])
        
        # FPS limitation
        if self.scrcpy_max_fps.isChecked():
            command.extend(['--max-fps', str(self.scrcpy_fps_value.value())])
        
        # Bitrate
        if self.scrcpy_bit_rate.isChecked():
            command.extend(['-b', f'{self.scrcpy_bitrate_value.value()}M'])
        
        # Recording
        if self.scrcpy_record.isChecked() and self.scrcpy_record_filename.text():
            command.extend(['--record', self.scrcpy_record_filename.text()])
        
        # Screen timeout
        if self.scrcpy_screen_timeout.isChecked():
            command.extend(['--screen-off-timeout', str(self.scrcpy_timeout_value.value())])
        
        # Orientation
        if self.scrcpy_orientation.currentText() != "auto":
            orientation_map = {
                "0°": "@0",
                "90°": "@90",
                "180°": "@180",
                "270°": "@270"
            }
            command.append(f'--capture-orientation={orientation_map[self.scrcpy_orientation.currentText()]}')
        
        # Display options
        if self.scrcpy_fullscreen.isChecked():
            command.append('-f')
        if self.scrcpy_stay_awake.isChecked():
            command.append('-w')
        if self.scrcpy_show_touches.isChecked():
            command.append('-t')
        if self.scrcpy_disable_screensaver.isChecked():
            command.append('-S')
        if self.scrcpy_borderless.isChecked():
            command.append('-b')
        if self.scrcpy_always_on_top.isChecked():
            command.append('-T')
        if self.scrcpy_turn_screen_off.isChecked():
            command.append('-o')
        if self.scrcpy_no_audio.isChecked():
            command.append('--no-audio')
        
        # Custom parameters
        if self.scrcpy_custom_params.text():
            custom_params = self.scrcpy_custom_params.text().split()
            command.extend(custom_params)
        
        return command
    
    def check_and_offer_scrcpy_install(self):
        """Check if scrcpy is installed and offer to install if not"""
        if not self.check_scrcpy_available(silent=True):
            reply = QMessageBox.question(
                self, 
                'Scrcpy nie znalezione',
                'Scrcpy nie jest zainstalowane lub nie jest dostępne w PATH.\n\n'
                'Czy chcesz pobrać i zainstalować scrcpy automatycznie?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.download_scrcpy()
    
    def download_scrcpy(self):
        """Start scrcpy download process"""
        self.downloader = ScrcpyDownloader()
        
        # Create progress dialog
        self.progress_dialog = QProgressDialog("Pobieranie scrcpy...", "Anuluj", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(True)
        
        # Connect signals
        self.downloader.progress.connect(self.progress_dialog.setValue)
        self.downloader.status.connect(self.update_download_status)
        self.downloader.finished.connect(self.on_download_finished)
        
        # Start download
        self.downloader.start()
    
    def update_download_status(self, status):
        """Update download status"""
        self.log_text.append(f"📥 {status}")
        self.progress_dialog.setLabelText(status)
    
    def on_download_finished(self, success):
        """Handle download completion"""
        self.progress_dialog.close()
        
        if success:
            QMessageBox.information(
                self,
                "Pobieranie zakończone",
                "Scrcpy zostało pobrane pomyślnie.\n"
                "Może być konieczne dodanie folderu scrcpy do zmiennej PATH."
            )
        else:
            # Check if it was Linux/macOS with package manager instructions
            if "menedżer pakietów" in self.log_text.toPlainText() or "Homebrew" in self.log_text.toPlainText():
                # Don't show error, instructions were already provided
                pass
            else:
                QMessageBox.warning(
                    self,
                    "Błąd pobierania",
                    "Nie udało się pobrać scrcpy.\n"
                    "Sprawdź logi lub zainstaluj ręcznie."
                )
    
    def start_scrcpy(self):
        """Launch scrcpy with the selected configuration options"""
        try:
            # Check if scrcpy is available
            if not self.check_scrcpy_available():
                return
                
            # Get the command with current settings
            command = self.get_scrcpy_command()
            
            # Create and configure the process
            self.scrcpy_process = QProcess(self)
            self.scrcpy_process.finished.connect(self.on_scrcpy_finished)
            self.scrcpy_process.errorOccurred.connect(self.on_scrcpy_error)
            
            # Start the process
            self.scrcpy_process.start(command[0], command[1:])
            
            # Update UI state
            self.scrcpy_start_button.setEnabled(False)
            self.scrcpy_stop_button.setEnabled(True)
            self.status_label.setText('📱 Scrcpy działa...')
            self.status_label.setStyleSheet("""
                color: #1565c0; 
                margin: 10px; 
                font-weight: bold;
                font-size: 14px;
                background-color: #e3f2fd;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #bbdefb;
            """)
            
            # Log the action
            self.log_text.append(f"🚀 Uruchamianie: {' '.join(command)}")
            
        except Exception as e:
            self.show_error(f"Błąd uruchamiania Scrcpy: {str(e)}")
            self.log_text.append(f"❌ BŁĄD (Scrcpy): {str(e)}")
    
    def stop_scrcpy(self):
        """Stop the running scrcpy process"""
        if self.scrcpy_process:
            self.scrcpy_process.terminate()
            if not self.scrcpy_process.waitForFinished(3000):  # Wait 3 seconds
                self.scrcpy_process.kill()  # Force kill if needed
            self.on_scrcpy_finished()
    
    def on_scrcpy_finished(self):
        """Handle scrcpy process termination"""
        self.scrcpy_start_button.setEnabled(True)
        self.scrcpy_stop_button.setEnabled(False)
        self.update_status()
        self.log_text.append("⏹️ Scrcpy zatrzymane")
        self.scrcpy_process = None
    
    def on_scrcpy_error(self, error):
        """
        Handle scrcpy process errors
        
        Args:
            error: QProcess error type
        """
        error_messages = {
            QProcess.FailedToStart: "Nie udało się uruchomić scrcpy. Sprawdź czy jest zainstalowane i dostępne w PATH.",
            QProcess.Crashed: "Scrcpy nieoczekiwanie przestało działać.",
            QProcess.Timedout: "Scrcpy przekroczyło limit czasu.",
            QProcess.WriteError: "Błąd zapisu do procesu scrcpy.",
            QProcess.ReadError: "Błąd odczytu z procesu scrcpy.",
            QProcess.UnknownError: "Nieznany błąd procesu scrcpy."
        }
        
        message = error_messages.get(error, "Wystąpił nieznany błąd")
        self.show_error(f"Błąd Scrcpy: {message}")
        self.log_text.append(f"❌ BŁĄD (Scrcpy): {message}")
        self.on_scrcpy_finished()
    
    def start_droidcam(self):
        """Launch DroidCam application"""
        try:
            # Check if DroidCam is available
            if not self.check_droidcam_available():
                return
            
            # Ask for IP address
            ip_address, ok = QInputDialog.getText(
                self,
                "Adres IP DroidCam",
                "Wprowadź adres IP telefonu (widoczny w aplikacji DroidCam):",
                text="192.168.1.100"
            )
            
            if not ok or not ip_address:
                return
                
            # Create and configure the process
            self.droidcam_process = QProcess(self)
            self.droidcam_process.finished.connect(self.on_droidcam_finished)
            self.droidcam_process.errorOccurred.connect(self.on_droidcam_error)
            
            # Platform-specific command
            if sys.platform.startswith('win'):
                command = ['droidcam-cli', ip_address, '4747']
            else:
                command = ['droidcam-cli', ip_address, '4747']
            
            # Start the process
            self.droidcam_process.start(command[0], command[1:] if len(command) > 1 else [])
            
            # Update UI state
            self.droidcam_start_button.setEnabled(False)
            self.droidcam_stop_button.setEnabled(True)
            self.status_label.setText('📷 DroidCam działa...')
            self.status_label.setStyleSheet("""
                color: #f57c00; 
                margin: 10px; 
                font-weight: bold;
                font-size: 14px;
                background-color: #fff3e0;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #ffe0b2;
            """)
            
            # Log the action
            self.log_text.append(f"🚀 Uruchamianie DroidCam: {' '.join(command)}")
            
        except Exception as e:
            self.show_error(f"Błąd uruchamiania DroidCam: {str(e)}")
            self.log_text.append(f"❌ BŁĄD (DroidCam): {str(e)}")
    
    def stop_droidcam(self):
        """Stop the running DroidCam process"""
        if self.droidcam_process:
            self.droidcam_process.terminate()
            if not self.droidcam_process.waitForFinished(3000):  # Wait 3 seconds
                self.droidcam_process.kill()  # Force kill if needed
            self.on_droidcam_finished()
    
    def on_droidcam_finished(self):
        """Handle DroidCam process termination"""
        self.droidcam_start_button.setEnabled(True)
        self.droidcam_stop_button.setEnabled(False)
        self.update_status()
        self.log_text.append("⏹️ DroidCam zatrzymane")
        self.droidcam_process = None
    
    def on_droidcam_error(self, error):
        """
        Handle DroidCam process errors
        
        Args:
            error: QProcess error type
        """
        error_messages = {
            QProcess.FailedToStart: "Nie udało się uruchomić DroidCam. Sprawdź czy jest zainstalowane i dostępne w PATH.",
            QProcess.Crashed: "DroidCam nieoczekiwanie przestało działać.",
            QProcess.Timedout: "DroidCam przekroczyło limit czasu.",
            QProcess.WriteError: "Błąd zapisu do procesu DroidCam.",
            QProcess.ReadError: "Błąd odczytu z procesu DroidCam.",
            QProcess.UnknownError: "Nieznany błąd procesu DroidCam."
        }
        
        message = error_messages.get(error, "Wystąpił nieznany błąd")
        self.show_error(f"Błąd DroidCam: {message}")
        self.log_text.append(f"❌ BŁĄD (DroidCam): {message}")
        self.on_droidcam_finished()
    
    def update_status(self):
        """Update the status label based on running processes"""
        if self.scrcpy_process and self.droidcam_process:
            self.status_label.setText('📱📷 Scrcpy i DroidCam działają')
            self.status_label.setStyleSheet("""
                color: #7b1fb8; 
                margin: 10px; 
                font-weight: bold;
                font-size: 14px;
                background-color: #f3e5f5;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #e1bee7;
            """)
        elif self.scrcpy_process:
            self.status_label.setText('📱 Scrcpy działa...')
            self.status_label.setStyleSheet("""
                color: #1565c0; 
                margin: 10px; 
                font-weight: bold;
                font-size: 14px;
                background-color: #e3f2fd;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #bbdefb;
            """)
        elif self.droidcam_process:
            self.status_label.setText('📷 DroidCam działa...')
            self.status_label.setStyleSheet("""
                color: #f57c00; 
                margin: 10px; 
                font-weight: bold;
                font-size: 14px;
                background-color: #fff3e0;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #ffe0b2;
            """)
        else:
            self.status_label.setText('✅ Gotowy do uruchomienia aplikacji')
            self.status_label.setStyleSheet("""
                color: #34a853; 
                margin: 10px; 
                font-weight: bold;
                font-size: 14px;
                background-color: #e8f5e8;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #c8e6c9;
            """)
    
    def check_scrcpy_available(self, silent=False):
        """
        Check if scrcpy is available in the system PATH
        
        Args:
            silent: If True, don't show error dialog
            
        Returns:
            bool: True if scrcpy is available, False otherwise
        """
        try:
            subprocess.run(['scrcpy', '--version'], 
                         capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            if not silent:
                self.show_error(
                    "Scrcpy nie znalezione!\n\n"
                    "Upewnij się, że scrcpy jest zainstalowane i dostępne w PATH.\n"
                    "Pobierz z: https://github.com/Genymobile/scrcpy\n\n"
                    "Na Ubuntu/Debian: sudo apt install scrcpy\n"
                    "Na Fedora: sudo dnf install scrcpy\n"
                    "Na Arch: sudo pacman -S scrcpy"
                )
            return False
    
    def check_droidcam_available(self):
        """
        Check if DroidCam is available in the system PATH
        
        Returns:
            bool: True if DroidCam is available, False otherwise
        """
        # Try different DroidCam executable names
        droidcam_commands = ['droidcam', 'droidcam-cli', 'droidcamapp']
        
        for cmd in droidcam_commands:
            try:
                subprocess.run([cmd], 
                             capture_output=True, timeout=5)
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        self.show_error(
            "DroidCam nie znalezione!\n\n"
            "Upewnij się, że DroidCam jest zainstalowane i dostępne w PATH.\n"
            "Pobierz z: https://www.dev47apps.com/"
        )
        return False
    
    def show_error(self, message):
        """
        Display an error message dialog
        
        Args:
            message (str): Error message to display
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle('Błąd')
        msg_box.setText(message)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                color: #333333;
            }
            QMessageBox QPushButton {
                background-color: #4285f4;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        msg_box.exec_()
    
    def closeEvent(self, event):
        """
        Handle application close event - terminate running processes
        
        Args:
            event: Close event object
        """
        # Stop running processes before closing
        if self.scrcpy_process:
            self.stop_scrcpy()
        if self.droidcam_process:
            self.stop_droidcam()
        event.accept()

def main():
    """
    Main application entry point
    
    Creates and runs the Qt application with the ScrcpyLauncher window.
    """
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use modern Fusion style
    
    # Set application metadata
    app.setApplicationName("Scrcpy & DroidCam Launcher")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Mobile Tools")
    
    # Create and show the main window
    launcher = ScrcpyLauncher()
    launcher.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()