import subprocess
import sys 
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QLineEdit, QVBoxLayout, QLabel
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QResizeEvent
from time import sleep
from multiprocessing import Pool


# add your folder path here for storing presets here
preset_folder_path = "Personal_presets"
# add your path here for the default preset file
default_preset_file_name = 'Personal_presets/.defaults.txt'

# add your path here if you want to change the background image
background_image_folder_path = 'Assets/Background-image.png'

# function for loading the default preset
def load_default_preset():
    try:
        with open(default_preset_file_name, "r") as file:
            lines = file.readlines()
            preset = {}
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    preset[key.strip()] = value.strip().strip('"')
            print("Loaded default preset:", preset)
            return preset
    except FileNotFoundError:
        print("The default preset file was not found.")
        return None
    except PermissionError:
        print("You do not have permission to read the default preset file.")
        return None
    except ValueError:
        print("The default preset file content could not be parsed.")
        return None


default_preset = load_default_preset()
if default_preset is not None:
    default_task_related_apps = default_preset["default_task_related_apps"].split(", ")
    default_task_related_websites = default_preset["default_task_related_websites"].split(", ")
else:
    default_task_related_apps = []
    default_task_related_websites = []

# function for loading the task speseific preset
def load_preset(file_name):
    with open(file_name, "r") as file:
        lines = file.readlines()
        preset = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                preset[key.strip()] = value.strip().strip('"')
        print("Loaded preset:", preset)
        return preset


class TaskWorker(QThread):
    finished = pyqtSignal()
    
    def __init__(self, task_related_apps, task_related_websites, block_name, time_amount):
        super().__init__()
        self.task_related_apps = task_related_apps + default_task_related_apps
        self.task_related_websites = default_task_related_websites + task_related_websites
        self.block_name = block_name
        self.time_amount = time_amount
    
    def run(self):   
        running_apps = self.list_visible_apps_bundle_id()
        block_name = self.block_name
        running_apps = set(running_apps)
                
        apps_to_close = [app for app in running_apps if app not in self.task_related_apps]
        self.manage_apps(apps_to_close, 'close')

        apps_to_open = [app for app in self.task_related_apps if app not in running_apps]
        self.manage_apps(apps_to_open, 'open')

        thread1 = threading.Thread(target=self.manage_apps, args=(apps_to_close, 'close'))
        thread2 = threading.Thread(target=self.close_finder_windows)
        thread3 = threading.Thread(target=self.open_websites_in_new_window, args=(self.task_related_websites,))
        thread4 = threading.Thread(target=self.manage_apps, args=(apps_to_open, 'open'))
        thread5 = threading.Thread(target=self.start_cold_turkey_block, args=(block_name, self.time_amount,))
        
        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()
        thread5.start()
        
        thread1.join()
        thread2.join()
        thread3.join()
        thread4.join()
        thread5.join()
        
        self.finished.emit()  
         
            
    def list_visible_apps_bundle_id(self):
            script = '''
            tell application "System Events"
            set appList to every application process whose visible is true
            set output to {}
            repeat with appItem in appList
                set end of output to bundle identifier of appItem
            end repeat
            return output
        end tell
        '''
        
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            bundle_ids = result.stdout.strip().split(", ")
            return bundle_ids
 
    # a method for managing apps utulizing multiprocessing and close_app and open_app methods
    def manage_apps(self, app_bundle_ids, action):
        with Pool() as p:
            if action == 'open':
                p.map(TaskWorker.open_app, app_bundle_ids)
            elif action == 'close':
                p.map(TaskWorker.close_app, app_bundle_ids) 
        
    # a method for opening apps    
    @staticmethod    
    def open_app(app_bundle_id):
        script = f'''
        try
            tell application id "{app_bundle_id}"
                if it is not running then
                    launch
                end if
            end tell
        on error errMsg number errnum
            return "Open Error " & errNum & ": " & errMsg
        end try
        '''
        result = subprocess.run(["osascript", "-e", script])
        print(result.stdout) 
   
    # a method for closing apps
    @staticmethod    
    def close_app(app_bundle_id):
        script = f'''
        try
            tell application id "{app_bundle_id}"
                if it is running then
                    quit
                end if
            end tell
        on error errMsg number errNum
            return "Close Error " & ": " & errMsg
        end try
        '''
        result = subprocess.run(["osascript", "-e", script])
        
        print(result.stdout)
        
       
    # a method for minimizing current windows and opening websites in new window
    def open_websites_in_new_window(self, sites_to_open):
        minimize_script = '''
        tell application "Google Chrome"
            set every window's minimized to true
        end tell
        '''
        subprocess.run(["osascript", "-e", minimize_script])
        
        sites_to_open_str = "{" + ", ".join(f'"{site}"' for site in sites_to_open) + "}"
  
        script = f'''
        tell application "Google Chrome"
             make new window
             activate
             set firstTabOpened to false
             repeat with site in {sites_to_open_str}
                 if firstTabOpened is false then
                     set URL of active tab of front window to site
                     set firstTabOpened to true
                 else
                     make new tab at end of tabs of front window with properties {{URL:site}}            
                     end if
             end repeat
         end tell
        '''
        print(f"Opening websites: {sites_to_open}")
        subprocess.run(["osascript", "-e", script])
    
    # A method for starting a cold turkey block    
    def start_cold_turkey_block(self, block_name, time_amount):
        if block_name and time_amount is not None:
            subprocess.run(["/Applications/Cold Turkey Blocker.app/Contents/MacOS/Cold Turkey Blocker", "-start", block_name, "-lock", str(time_amount)])
        elif block_name and time_amount is None:
            subprocess.run(["/Applications/Cold Turkey Blocker.app/Contents/MacOS/Cold Turkey Blocker", "-start", block_name])
    
    # A method for closing all finder windows
    def close_finder_windows(self):
        script = '''
        tell application "Finder"
            close every window
        end tell
        '''
        subprocess.run(["osascript", "-e", script])      



class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App and Website Preset Launcher")
        self.worker = None
        self.initbackground()
        self.initUI()
        
    def initbackground(self):
        self.background = QPixmap(background_image_folder_path)
        self.update_background()
        
    def update_background(self):
        scaled_background = self.background.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(scaled_background))
        self.setPalette(palette)
        
    def resizeEvent(self, event):
        self.update_background()
        super().resizeEvent(event)
        
    def load_preset(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "open Preset File", preset_folder_path,"Text Files (*.txt)")
            if file_name:
                preset = load_preset(file_name)
                task_related_apps = preset["task_related_apps"].split(", ")
                task_related_websites = preset["websites"].split(", ")
                block_name = preset["cold_turkey_block_name"]
                try:
                    time_amount = min(int(self.time_input.text() or 0), 60)
                    self.time_input.clear()    
                except ValueError:
                    print("Please enter a valid number for the time amount.")

        except FileNotFoundError:
            print("The file was not found.")
        except PermissionError:
            print("You do not have permission to read the file.")
        except ValueError:
            print("The file content could not be parsed.")
            return
        
        self.worker = TaskWorker(task_related_apps, task_related_websites, block_name, time_amount)
        self.worker.finished.connect(self.app_done)
        self.worker.start()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
        self.load_preset_button = QPushButton("Load And Start Preset", self)
        self.load_preset_button.clicked.connect(self.load_preset)
        self.load_preset_button.setMinimumSize(200, 30)
        self.load_preset_button
             
        self.time_input = QLineEdit(self)
        self.time_input.setPlaceholderText("Enter locktime in minutes, leaving black means no lock (1-60)")
        layout.addWidget(self.time_input)

        self.setGeometry(300, 300, 512, 512)
        self.initbackground()
            
    def open_apps_and_websites(self):
        self.worker = TaskWorker()
        self.worker.finished.connect(self.app_done)
        self.worker.start()
       
    def app_done(self):
        print("Task completed")
        
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())   
   
   
  