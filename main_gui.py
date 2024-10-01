import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QTextEdit, QLabel, QFileDialog, QMessageBox
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
import main  # Import your existing main.py file

class EmailProcessorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Email Processor")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f7;
            }
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
            QListWidget, QTextEdit {
                background-color: white;
                border: 1px solid #d2d2d7;
                border-radius: 6px;
                padding: 5px;
                
                color: #1d1d1f;  /* Ensure text is visible */
            }
            QLabel {
                color: #1d1d1f;
                font-size: 14px;
            }
        """)
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        instructions_label = QLabel("Welcome to Email Processor. Start by selecting a JSON file containing email data.")
        instructions_label.setWordWrap(True)
        left_layout.addWidget(instructions_label)
        
        self.file_button = QPushButton("Select File")
        self.file_button.clicked.connect(self.select_file)
        left_layout.addWidget(self.file_button)

        self.file_label = QLabel("No file selected")
        left_layout.addWidget(self.file_label)

        email_list_label = QLabel("Processed Emails:")
        left_layout.addWidget(email_list_label)

        self.email_list = QListWidget()
        self.email_list.itemClicked.connect(self.display_email)
        left_layout.addWidget(self.email_list)

        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.subject_label = QLabel("Subject: ")
        self.subject_label.setFont(QFont("SF Pro Display", 16, QFont.Bold))
        right_layout.addWidget(self.subject_label)

        self.sender_label = QLabel("Sender: ")
        self.sender_label.setFont(QFont("SF Pro Text", 14))
        right_layout.addWidget(self.sender_label)

        self.sent_time_label = QLabel("Sent Time: ")
        self.sent_time_label.setFont(QFont("SF Pro Text", 14))
        right_layout.addWidget(self.sent_time_label)

        content_label = QLabel("Email Content:")
        right_layout.addWidget(content_label)

        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        right_layout.addWidget(self.content_text)

        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

        self.processed_results = []

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json);;Text Files (*.txt)")
        if file_path:
            self.file_label.setText(f"Selected file: {file_path}")
            try:
                self.processed_results = main.process_file(file_path)
                self.update_email_list()
                QMessageBox.information(self, "Success", f"Successfully processed {len(self.processed_results)} emails.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while processing the file: {str(e)}")

    def update_email_list(self):
        self.email_list.clear()
        for result in self.processed_results:
            subject = result['subject'].strip()
            if subject:  # Only add non-empty subjects
                self.email_list.addItem(f"{result['index']}. {subject}")
        
        if not self.email_list.count():
            self.email_list.addItem("No emails found in the selected file.")

    def display_email(self, item):
        if not self.processed_results:
            return
        
        index = int(item.text().split('.')[0]) - 1
        email_data = self.processed_results[index]
        
        self.subject_label.setText(f"Subject: {email_data['subject']}")
        self.sender_label.setText(f"Sender: {email_data['sender_name']} <{email_data['sender_address']}>")
        self.sent_time_label.setText(f"Sent Time: {email_data['sent_time']}")
        self.content_text.setText(email_data['cleaned_content'])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EmailProcessorGUI()
    window.show()
    sys.exit(app.exec_())