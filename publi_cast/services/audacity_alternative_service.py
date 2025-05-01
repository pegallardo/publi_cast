import os
import sys
import time
import subprocess
import tempfile
import soundfile as sf
import numpy as np
import pyautogui
import pygetwindow as gw

class AudacityAlternativeAPI:
    """
    Alternative API for Audacity that uses GUI automation instead of pipes.
    This is a fallback solution when pipes don't work.
    """
    
    def __init__(self, logger):
        self.logger = logger
        self.audacity_path = os.environ.get('AUDACITY_PATH', "C:\\Program Files\\Audacity\\audacity.exe")
        self.logger.info("Initialized AudacityAlternativeAPI")
    
    def start_audacity(self):
        """Start Audacity if it's not already running"""
        # Check if Audacity is already running
        audacity_windows = gw.getWindowsWithTitle('Audacity')
        if audacity_windows:
            self.logger.info("Audacity is already running")
            return True
        
        # Start Audacity
        self.logger.info("Starting Audacity...")
        try:
            subprocess.Popen([self.audacity_path])
            time.sleep(5)  # Wait for Audacity to start
            
            # Check if Audacity started
            audacity_windows = gw.getWindowsWithTitle('Audacity')
            if audacity_windows:
                self.logger.info("Audacity started successfully")
                return True
            else:
                self.logger.error("Failed to start Audacity")
                return False
        except Exception as e:
            self.logger.error(f"Error starting Audacity: {e}")
            return False
    
    def focus_audacity(self):
        """Focus the Audacity window"""
        audacity_windows = gw.getWindowsWithTitle('Audacity')
        if audacity_windows:
            try:
                audacity_windows[0].activate()
                time.sleep(0.5)
                return True
            except Exception as e:
                self.logger.error(f"Error focusing Audacity window: {e}")
                return False
        else:
            self.logger.error("No Audacity window found")
            return False
    
    def import_audio(self, file_path):
        """Import audio file into Audacity using GUI automation"""
        if not self.focus_audacity():
            return False
        
        try:
            # Press Ctrl+O to open file
            pyautogui.hotkey('ctrl', 'o')
            time.sleep(1)
            
            # Type file path
            pyautogui.write(file_path)
            time.sleep(0.5)
            
            # Press Enter to confirm
            pyautogui.press('enter')
            time.sleep(2)
            
            self.logger.info(f"Imported audio file: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error importing audio file: {e}")
            return False
    
    def select_all(self):
        """Select all audio in Audacity"""
        if not self.focus_audacity():
            return False
        
        try:
            # Press Ctrl+A to select all
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.5)
            
            self.logger.info("Selected all audio")
            return True
        except Exception as e:
            self.logger.error(f"Error selecting all audio: {e}")
            return False
    
    def apply_effect(self, effect_name):
        """Apply an effect in Audacity"""
        if not self.focus_audacity():
            return False
        
        try:
            # Open Effect menu
            pyautogui.hotkey('alt', 'e')
            time.sleep(0.5)
            
            # Type effect name to find it
            pyautogui.write(effect_name)
            time.sleep(0.5)
            
            # Press Enter to select the effect
            pyautogui.press('enter')
            time.sleep(1)
            
            # Press Enter again to apply with default settings
            pyautogui.press('enter')
            time.sleep(2)
            
            self.logger.info(f"Applied effect: {effect_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error applying effect: {e}")
            return False
    
    def export_audio(self, file_path):
        """Export audio from Audacity"""
        if not self.focus_audacity():
            return False
        
        try:
            # Press Ctrl+Shift+E to export
            pyautogui.hotkey('ctrl', 'shift', 'e')
            time.sleep(1)
            
            # Type file path
            pyautogui.write(file_path)
            time.sleep(0.5)
            
            # Press Enter to confirm
            pyautogui.press('enter')
            time.sleep(1)
            
            # Handle any additional dialogs (format options, etc.)
            pyautogui.press('enter')
            time.sleep(2)
            
            self.logger.info(f"Exported audio to: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting audio: {e}")
            return False
    
    def close_audacity(self):
        """Close Audacity"""
        if not self.focus_audacity():
            return False
        
        try:
            # Press Alt+F4 to close
            pyautogui.hotkey('alt', 'f4')
            time.sleep(1)
            
            # Handle save dialog if it appears
            pyautogui.press('n')  # Press 'n' for "No" (don't save)
            time.sleep(1)
            
            self.logger.info("Closed Audacity")
            return True
        except Exception as e:
            self.logger.error(f"Error closing Audacity: {e}")
            return False