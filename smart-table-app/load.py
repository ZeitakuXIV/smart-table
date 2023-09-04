from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QTimer
from PyQt5.QtPrintSupport import *
from PyQt5.uic import loadUi
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import os
import RPi.GPIO as GPIO
import psycopg2
from psycopg2 import extras
from mfrc522 import SimpleMFRC522
import time
import uuid
import pytz
import datetime
from git import Repo


# init git
repo_path = '/home/aot/smart-table/smart-table/'
remote_url = "https://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@github.com/ichifour/smart-table.git"
presence_id = ""
userid = ""
repo = Repo(repo_path)

remote_name = "origin"
existing_remotes = [remote.name for remote in repo.remotes]
if remote_name not in existing_remotes:
    origin = repo.create_remote(remote_name, url=remote_url)
    print(f"Remote '{remote_name}' added.")
else:
    print(f"Remote '{remote_name}' already exists.")

reader = SimpleMFRC522()

db_params = {
    "host": "us-east-1.51f491bd-0de0-4448-89e0-b9433d120543.aws.ybdb.io",
    "port": 5433,
    "database": "postgres",
    "user": "aotpy",
    "password": "zeitakuXIV"
}

# class RFIDReader(QThread):
#     rfid_id = pyqtSignal(int)
    
#     def __init__(self):
#         super(RFIDReader, self).__init__()
#         print("start rfid thread")
#         self.run()

#     def run(self):
#         while True:
#             global userid
#             print("rfid thread loop")
#             id, text = reader.read()
#             self.rfid_id.emit(id) # emit rfid id
            
#             print(id)
#             print(text)
#             userid = text
#             time.sleep(0.1)

class IntroPage(QDialog):
    def __init__(self):
        super(IntroPage, self).__init__()
        loadUi('Login.ui', self)
        
        # bikin timer untuk run code dibawah
        # jadi code dibawah jalan saat aplikasi sudah siap
        self.timer = QTimer()
        self.timer.timeout.connect(self.try_read)
        self.timer.start(1000)  # Timer interval in milliseconds (1 second)
        # self.rfid_read = RFIDReader()
        # self.rfid_read.rfid_id.connect(self.auth_handler)

    # def auth_handler(self, rfid_id):
    #     global userid, presence_id  # Declare them as global
    #     try:
    #         # rfid = RFIDReader()
    #         # rfid.rfid_id.connect()
    #         dir_path = r'/home/aot/smart-table/smart-table/{}'.format(userid.strip())
    #         print(dir_path)
    #         self.pull_from_repo()
    #         # Initialize EditorPage with dir_path
    #         editor_page = EditorPage(dir_path)
    #         widget.addWidget(editor_page)
    #     finally:
    #         pass
        
    #     try:
    #         connection = psycopg2.connect(**db_params)
    #         print("Connected to the database")
    #     except (Exception, psycopg2.Error) as error:
    #         print("Error while connecting to the database:", error)

    #     try:
    #         cursor = connection.cursor()

    #         # Example: Execute a SELECT query
    #         query = "SELECT name, class_name FROM users WHERE id = '{}'".format(text.strip())
    #         cursor.execute(query)
    #         row = cursor.fetchone()
    #         if row:
    #             auth = True
    #             self.goto_editor()
    #             name, user_class = row
    #             presence_id = uuid.uuid4()
    #             # Get the current time with time zone information
    #             current_time = datetime.datetime.now(pytz.utc)
    #             # Convert the time to timestamptz format (string)
    #             timestamptz_format = current_time.strftime('%Y-%m-%d %H:%M:%S %Z')
    #             presence_query = "INSERT INTO presences (id, time_in, user_id) VALUES (%s, %s, %s)"
    #             presence_values = (str(presence_id).strip(), current_time, text.strip())
    #             cursor.execute(presence_query, presence_values)
    #             connection.commit()
    #             print("Name:", name)
    #             print("Class:", user_class)
    #         else:
    #             print("No matching record found.")

    #     except (Exception, psycopg2.Error) as error:
    #         print("Error executing query:", error)

    #     finally:
    #         # Close the cursor and connection
    #         if cursor:
    #             cursor.close()
    #         if connection:
    #             connection.close()
    #             print("Connection closed")
    
    def try_read(self):
        global userid, presence_id  # Declare them as global
        try:
            global userid
            id, text = reader.read()        
            print(id)
            print(text)
            userid = text
            time.sleep(0.1)
            # rfid = RFIDReader()
            # rfid.rfid_id.connect()
            dir_path = r'/home/aot/smart-table/smart-table/{}'.format(userid.strip())
            print(dir_path)
            self.pull_from_repo()
            # Initialize EditorPage with dir_path
            editor_page = EditorPage(dir_path)
            widget.addWidget(editor_page)
        finally:
            pass
            GPIO.cleanup()

        try:
            connection = psycopg2.connect(**db_params)
            print("Connected to the database")
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to the database:", error)

        try:
            cursor = connection.cursor()

            # Example: Execute a SELECT query
            query = "SELECT name, class_name FROM users WHERE id = '{}'".format(userid.strip())
            cursor.execute(query)
            row = cursor.fetchone()
            if row:
                auth = True
                self.goto_editor()
                name, user_class = row
                presence_id = uuid.uuid4()
                # Get the current time with time zone information
                current_time = datetime.datetime.now(pytz.utc)
                # Convert the time to timestamptz format (string)
                timestamptz_format = current_time.strftime('%Y-%m-%d %H:%M:%S %Z')
                presence_query = "INSERT INTO presences (id, time_in, user_id) VALUES (%s, %s, %s)"
                presence_values = (str(presence_id).strip(), current_time, text.strip())
                cursor.execute(presence_query, presence_values)
                connection.commit()
                print("Name:", name)
                print("Class:", user_class)
            else:
                print("No matching record found.")

        except (Exception, psycopg2.Error) as error:
            print("Error executing query:", error)

        finally:
            # Close the cursor and connection
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                print("Connection closed")
                self.timer.stop()
    
    def pull_from_repo(self):
        try:
            origin = repo.remote("origin")  # Get the "origin" remote
            origin.pull()  # Pull changes from the remote repository
            print("Changes pulled from 'origin'.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to pull changes: {str(e)}")

    def goto_editor(self):
        widget.setCurrentIndex(1)

class EditorPage(QDialog):
    def __init__(self, dir_path):
        super(EditorPage, self).__init__()
        print(dir_path)
        loadUi('Editor.ui', self)
        self.model = QFileSystemModel()
        self.model.setRootPath(dir_path)
        root_index = self.model.index(dir_path)
        self.treeView.setModel(self.model) # Set the model for the QTreeView
        self.treeView.setRootIndex(root_index) # Set the root index for the QTreeView
        self.treeView.doubleClicked.connect(self.open_file)
        self.save_button.clicked.connect(self.save_file)
        self.delete_button.clicked.connect(self.handle_delete_file)
        self.new_file_button.clicked.connect(self.create_new_file)
        self.new_folder_button.clicked.connect(self.create_new_folder)
        self.sync_button.clicked.connect(self.push_to_repo)
        self.logout_button.clicked.connect(self.logout)
        self.treeView.viewport().installEventFilter(self)  # Install event filter
        # self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None

    def eventFilter(self, source, event):
        if source == self.treeView.viewport() and event.type() == QEvent.MouseButtonPress:
            index = self.treeView.indexAt(event.pos())
            if not index.isValid():  # Blank space clicked
                self.handle_blank_space_click()
                return True  # Stop processing the event further

        return super().eventFilter(source, event)
    def current_file_path(self):
        return self.path
        
    def handle_blank_space_click(self):
        self.path = None  # Clear path
        self.update_title()
        self.plainTextEdit.setPlainText("")  # Clear text
        print(self.path)

    def open_file(self, index):
        if self.path and self.plainTextEdit.document().isModified():
            self.save_file()
        file_path = self.model.filePath(index)
        self.path = file_path
        if not self.model.isDir(index):  # Check if the index represents a file
            with open(file_path, 'r') as file:
                file_contents = file.read()
                self.plainTextEdit.setPlainText(file_contents)
                self.plainTextEdit.moveCursor(QTextCursor.Start)  # Move cursor to the beginning

        current_open_file = self.current_file_path()
        file_name = os.path.basename(current_open_file)
        if current_open_file:
            self.selected_file_label.setText(f"Now editing: {file_name}")
        else:
            print("No file is currently open.")

    def save_file(self):
        self._save_to_path(self.path)

    def _save_to_path(self, path):
        text = self.plainTextEdit.toPlainText()
        try:
            with open(path, 'w') as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            self.update_title()

    def update_title(self):
        self.setWindowTitle("%s - Zei not pad" % (os.path.basename(self.path) if self.path else "Untitled"))

    def create_new_file(self):
        if self.path and self.plainTextEdit.document().isModified():
            self.save_file()

        current_index = self.treeView.currentIndex()
        selected_path = self.model.filePath(current_index) if current_index.isValid() else self.model.rootPath()

        if self.model.isDir(current_index):
            new_file_name, ok = QInputDialog.getText(self, "Create New File", "Enter new file name:")
            if ok and new_file_name:
                if not new_file_name.endswith(".txt"):
                    new_file_name += ".txt"
                new_file_path = os.path.join(selected_path, new_file_name)
                with open(new_file_path, 'w') as file:
                    file.write("")
                self.path = new_file_path
                self.update_title()
                self.plainTextEdit.setPlainText("")
        else:
            dir_path = os.path.dirname(selected_path)
            new_file_name, ok = QInputDialog.getText(self, "Create New File", "Enter new file name:")
            if ok and new_file_name:
                if not new_file_name.endswith(".txt"):
                    new_file_name += ".txt"
                new_file_path = os.path.join(dir_path, new_file_name)
                with open(new_file_path, 'w') as file:
                    file.write("")
                self.path = new_file_path
                self.update_title()
                self.plainTextEdit.setPlainText("")

    def create_new_folder(self):
        if self.path and self.plainTextEdit.document().isModified():
            self.save_file()

        new_folder_name, ok = QInputDialog.getText(self, "Create New Folder", "Enter new folder name:")
        if ok and new_folder_name:
            new_folder_path = os.path.join(os.path.dirname(self.path) if self.path else self.model.rootPath(), new_folder_name)
            os.mkdir(new_folder_path)

    def delete_file(self, file_path):
        try:
            os.remove(file_path)
            self.plainTextEdit.setPlainText("")  # Clear text
            QMessageBox.information(self, "File Deleted", "File deleted successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete file: {str(e)}")

    def handle_delete_file(self):
        current_index = self.treeView.currentIndex()
        if current_index.isValid() and not self.model.isDir(current_index):
            file_path = self.model.filePath(current_index)
            reply = QMessageBox.question(self, "Delete File", f"Are you sure you want to delete {file_path}?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.delete_file(file_path)

    def push_to_repo(self):
        global userid# Declare them as global
        repo.index.add(["*"])
        commit_message = "New commit by {}".format(userid.strip())
        repo.index.commit(commit_message)
        try:
            origin = repo.remote("origin")  # Get the "origin" remote

            # Set the upstream branch for the local master branch
            repo.git.branch("--set-upstream-to", f"origin/main", "main")

            # Push changes to the "origin" remote
            origin.push()
            print("Changes pushed to 'origin'.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to push changes: {str(e)}")
    
    def logout(self):
        reply = QMessageBox.question(self, "Logout", f"Are you sure want to logout?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
                self.update_time_out()  # Update time_out in the database
                self.push_to_repo()
                QApplication.instance().quit()

    def update_time_out(self):
        global userid, presence_id  # Declare them as global
        try:
            connection = psycopg2.connect(**db_params)
            print("Connected to the database")
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to the database:", error)
            return

        try:
            cursor = connection.cursor()

            # Example: Execute an UPDATE query to set the time_out
            query = "UPDATE presences SET time_out = %s WHERE user_id = %s AND time_out IS NULL AND id = %s"
            current_time = datetime.datetime.now(pytz.utc)
            timestamptz_format = current_time.strftime('%Y-%m-%d %H:%M:%S %Z')
            presence_values = (current_time, userid.strip(), str(presence_id).strip())
            cursor.execute(query, presence_values)
            connection.commit()
            print("Time_out updated successfully.")

        except (Exception, psycopg2.Error) as error:
            print("Error updating time_out:", error)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                print("Connection closed")

# GUI app
app = QApplication(sys.argv)
widget = QStackedWidget()
widget.addWidget(IntroPage())

widget.setFixedWidth(1024)
widget.setFixedHeight(600)
widget.show()

try:
    sys.exit(app.exec_())
    GPIO.cleanup()
except:
    pass