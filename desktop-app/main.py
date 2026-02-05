import sys
import os
import platform
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QScrollArea, QLineEdit, QTabWidget,
    QVBoxLayout, QHBoxLayout, QFileDialog, QListWidget, QListWidgetItem,
    QFrame, QMessageBox, QGridLayout, QSpacerItem, QSizePolicy,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QSize, QRect, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mplcursors

from api_client import (
    get_datasets, upload_csv, get_summary, delete_dataset,
    login, register, download_pdf, set_credentials,
    get_users, delete_user, get_current_user, get_records
)

class StyledButton(QPushButton):
    """Custom styled button with enhanced minimalistic design"""
    def __init__(self, text, primary=False, danger=False, small=False):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(28 if small else 36)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        size = "padding: 8px 16px; font-size: 12px;" if small else "padding: 12px 20px; font-size: 13px;"
        
        if danger:
            self.setStyleSheet(f"""
                QPushButton {{
                    {size}
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ef4444, stop:1 #dc2626);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #dc2626, stop:1 #b91c1c);
                }}
                QPushButton:pressed {{
                    background: #b91c1c;
                    padding-top: 14px;
                    padding-bottom: 10px;
                }}
            """)
        elif primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    {size}
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3b82f6, stop:1 #2563eb);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2563eb, stop:1 #1d4ed8);
                }}
                QPushButton:pressed {{
                    background: #1d4ed8;
                    padding-top: 14px;
                    padding-bottom: 10px;
                }}
                QPushButton:disabled {{
                    background: #bfdbfe;
                    opacity: 0.6;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    {size}
                    background: white;
                    color: #374151;
                    border: 2px solid #e5e7eb;
                    border-radius: 8px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: #f9fafb;
                    border-color: #d1d5db;
                }}
                QPushButton:pressed {{
                    background: #f3f4f6;
                    padding-top: 14px;
                    padding-bottom: 10px;
                }}
            """)

class StyledCard(QFrame):
    """Custom styled card with enhanced shadow and border"""
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e5e7eb;
                padding: 0px;
            }
        """)
        self.setGraphicsEffect(self.create_shadow())
    
    def create_shadow(self):
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 25))
        return shadow

class DatasetItem(QWidget):
    """Enhanced dataset item with modern styling"""
    def __init__(self, dataset_id, view_callback, delete_callback, owner_text=None):
        super().__init__()
        self.dataset_id = dataset_id
        self.setMinimumHeight(75)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Icon section
        icon_container = QFrame()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #dbeafe, stop:1 #bfdbfe);
                border-radius: 10px;
                border: none;
            }
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel("📊")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px; background: transparent; border: none;")
        icon_layout.addWidget(icon_label)

        # Info section
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        dataset_label = QLabel(f"Dataset #{dataset_id}")
        dataset_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        dataset_label.setStyleSheet("color: #111827;")
        
        info_layout.addWidget(dataset_label)

        if owner_text:
            owner_label = QLabel(owner_text)
            owner_label.setFont(QFont("Segoe UI", 9))
            owner_label.setStyleSheet("color: #6b7280;")
            info_layout.addWidget(owner_label)

        date_label = QLabel("Uploaded recently")
        date_label.setFont(QFont("Segoe UI", 9))
        date_label.setStyleSheet("color: #6b7280;")
        info_layout.addWidget(date_label)

        # Buttons section
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        view_btn = StyledButton("View", primary=False, small=True)
        delete_btn = StyledButton("Delete", danger=True, small=True)
        view_btn.setMaximumWidth(90)
        delete_btn.setMaximumWidth(90)

        view_btn.clicked.connect(lambda: view_callback(dataset_id))
        delete_btn.clicked.connect(lambda: delete_callback(dataset_id))

        buttons_layout.addWidget(view_btn)
        buttons_layout.addWidget(delete_btn)

        layout.addWidget(icon_container)
        layout.addLayout(info_layout, 1)
        layout.addStretch()
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fafbfc, stop:1 #f3f4f6);
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }
            QWidget:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f0f9ff, stop:1 #e0f2fe);
                border-color: #bfdbfe;
            }
        """)

class UserItem(QWidget):
    """Admin user list item"""
    def __init__(self, user, delete_callback, disable_delete=False):
        super().__init__()
        self.user = user
        self.setMinimumHeight(70)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Info section
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)

        username = user.get("username", "Unknown")
        email = user.get("email") or "No email"
        user_id = user.get("id", "")
        is_admin = user.get("is_staff") or user.get("is_superuser")

        name_label = QLabel(username)
        name_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name_label.setStyleSheet("color: #111827;")

        meta_text = f"{email} • ID #{user_id}"
        if is_admin:
            meta_text += " • Admin"
        meta_label = QLabel(meta_text)
        meta_label.setFont(QFont("Segoe UI", 9))
        meta_label.setStyleSheet("color: #6b7280;")

        info_layout.addWidget(name_label)
        info_layout.addWidget(meta_label)

        # Actions section
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)

        delete_btn = StyledButton("Delete", danger=True, small=True)
        delete_btn.setMaximumWidth(90)
        delete_btn.setEnabled(not disable_delete)
        if disable_delete:
            delete_btn.setToolTip("You cannot delete yourself")
        delete_btn.clicked.connect(lambda: delete_callback(user_id))
        actions_layout.addWidget(delete_btn)

        layout.addLayout(info_layout, 1)
        layout.addStretch()
        layout.addLayout(actions_layout)
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fafbfc, stop:1 #f3f4f6);
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }
            QWidget:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fff7ed, stop:1 #ffedd5);
                border-color: #f59e0b;
            }
        """)

class StatCard(QFrame):
    """Enhanced stat card with gradient background"""
    def __init__(self, label, value, icon="📊", color_start="#f0f9ff", color_end="#e0f2fe"):
        super().__init__()
        self.setFrameShape(QFrame.NoFrame)
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color_start}, stop:1 {color_end});
                border: 2px solid #e0f2fe;
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 20))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent; border: none;")
        
        # Label
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Segoe UI", 9, QFont.Bold))
        label_widget.setStyleSheet("color: #6b7280; text-transform: uppercase; background: transparent; border: none;")
        label_widget.setAlignment(Qt.AlignCenter)
        label_widget.setWordWrap(True)
        
        # Value
        value_widget = QLabel(str(value))
        value_widget.setFont(QFont("Segoe UI", 22, QFont.Bold))
        value_widget.setStyleSheet("color: #111827; background: transparent; border: none;")
        value_widget.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(icon_label)
        layout.addWidget(label_widget)
        layout.addWidget(value_widget)
        layout.addStretch()
        
        self.setLayout(layout)

class LoginDialog(QWidget):
    """Authentication dialog for login and registration"""
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Chemical Equipment Visualizer - Login")
        self.resize(450, 500)
        self.setStyleSheet("background-color: #f9fafb;")
        
        # Set window icon with full path and validation
        self._set_window_icon()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3b82f6, stop:1 #2563eb);
                padding: 30px 20px;
            }
        """)
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Chemical Equipment Visualizer")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        
        subtitle = QLabel("Analyze and visualize your data")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header.setLayout(header_layout)
        
        # Content
        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(16)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                padding: 10px 20px;
                font-weight: 600;
                color: #6b7280;
            }
            QTabBar::tab:selected {
                color: #3b82f6;
                border-bottom: 3px solid #3b82f6;
            }
        """)
        
        # Login tab
        login_tab = QWidget()
        login_layout = QVBoxLayout()
        login_layout.setSpacing(12)
        
        login_layout.addWidget(QLabel("Username"))
        self.login_username = QLineEdit()
        self.login_username.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                background: white;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        login_layout.addWidget(self.login_username)
        
        login_layout.addWidget(QLabel("Password"))
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                background: white;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        login_layout.addWidget(self.login_password)
        
        login_btn = StyledButton("Sign In", primary=True)
        login_btn.clicked.connect(self.handle_login)
        login_layout.addWidget(login_btn)
        login_layout.addStretch()
        login_tab.setLayout(login_layout)
        
        # Register tab
        register_tab = QWidget()
        register_layout = QVBoxLayout()
        register_layout.setSpacing(12)
        
        register_layout.addWidget(QLabel("Username"))
        self.register_username = QLineEdit()
        self.register_username.setStyleSheet(self.login_username.styleSheet())
        register_layout.addWidget(self.register_username)
        
        register_layout.addWidget(QLabel("Email"))
        self.register_email = QLineEdit()
        self.register_email.setStyleSheet(self.login_username.styleSheet())
        register_layout.addWidget(self.register_email)
        
        register_layout.addWidget(QLabel("Password"))
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_password.setStyleSheet(self.login_username.styleSheet())
        register_layout.addWidget(self.register_password)
        
        register_btn = StyledButton("Sign Up", primary=True)
        register_btn.clicked.connect(self.handle_register)
        register_layout.addWidget(register_btn)
        register_layout.addStretch()
        register_tab.setLayout(register_layout)
        
        self.tabs.addTab(login_tab, "Sign In")
        self.tabs.addTab(register_tab, "Sign Up")
        content_layout.addWidget(self.tabs)
        content.setLayout(content_layout)
        
        layout.addWidget(header)
        layout.addWidget(content, 1)
        self.setLayout(layout)
    
    def _set_window_icon(self):
        """Set window icon from file with error handling and Windows taskbar support"""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chem-visualizer-logo.ico")
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.setWindowIcon(icon)
                    
                    # Windows-specific taskbar icon fix
                    if platform.system() == "Windows":
                        try:
                            import ctypes
                            # Get window handle and set app user model ID
                            hwnd = self.winId()
                            if hwnd:
                                # This helps Windows taskbar recognize the custom icon
                                myappid = 'ChemicalVisualizer.App'
                                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                        except Exception as e:
                            print(f"Windows icon hint error (non-critical): {e}")
                else:
                    print(f"Warning: Icon at {icon_path} appears to be invalid")
            else:
                print(f"Warning: Icon file not found at: {icon_path}")
        except Exception as e:
            print(f"Error setting icon: {e}")
    
    def handle_login(self):
        username = self.login_username.text()
        password = self.login_password.text()
        
        if not username or not password:
            return
        
        result = login(username, password)
        if result:
            self.on_login_success()
            self.close()
        else:
            self.show_error("Invalid credentials")
    
    def handle_register(self):
        password = self.login_password.text()
        
        if not username or not password:
            return
        
        result = login(username, password)
        if result:
            self.on_login_success()
            self.close()
        else:
            self.show_error("Invalid credentials")
    
    def handle_register(self):
        username = self.register_username.text()
        password = self.register_password.text()
        email = self.register_email.text()
        
        if not username or not password:
            return
        
        result = register(username, password, email)
        if result:
            self.on_login_success()
            self.close()
        else:
            self.show_error("Registration failed")
    
    def show_error(self, message):
        msg = QMessageBox(self)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setIcon(QMessageBox.Warning)
        msg.exec_()


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Visualizer")
        self.resize(1200, 850)
        self.setMinimumSize(700, 600)
        self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f9fafb, stop:1 #f3f4f6);")
        
        # Set window icon with validation
        self._set_window_icon()
        
        # Current user context
        self.current_user = get_current_user() or {}
        self.is_admin = bool(self.current_user.get("is_admin"))

        # Initialize selected_id to track which dataset is being viewed
        self.selected_id = None

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Enhanced Header with gradient and icon
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1f2937, stop:1 #111827);
                padding: 24px 20px;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(16)
        
        # Icon
        icon_container = QFrame()
        icon_container.setFixedSize(64, 64)
        icon_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3b82f6, stop:1 #2563eb);
                border-radius: 16px;
                border: none;
            }
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel("📊")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 32px; background: transparent; border: none;")
        icon_layout.addWidget(icon_label)
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        title = QLabel("Chemical Equipment Visualizer")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        
        subtitle = QLabel("Analyze and visualize your equipment data with powerful insights")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.85); background: transparent;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        if self.is_admin:
            admin_badge = QLabel("Admin")
            admin_badge.setStyleSheet("""
                QLabel {
                    background: rgba(251, 191, 36, 0.2);
                    color: #fbbf24;
                    border: 1px solid rgba(251, 191, 36, 0.5);
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-weight: 700;
                    font-size: 10px;
                    letter-spacing: 1px;
                }
            """)
            admin_badge.setAlignment(Qt.AlignLeft)
            title_layout.addWidget(admin_badge)
        
        header_layout.addWidget(icon_container)
        header_layout.addLayout(title_layout, 1)
        
        # Logout button
        logout_btn = StyledButton("🚪 Logout", small=True)
        logout_btn.setMaximumWidth(100)
        logout_btn.clicked.connect(self.handle_logout)
        header_layout.addWidget(logout_btn)
        
        header_widget.setLayout(header_layout)

        # Scrollable content area with enhanced styling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f3f4f6;
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d1d5db, stop:1 #9ca3af);
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9ca3af, stop:1 #6b7280);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Content widget
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Top section: Upload and Datasets with enhanced spacing
        top_grid = QGridLayout()
        top_grid.setSpacing(20)
        top_grid.setContentsMargins(0, 0, 0, 0)

        # Enhanced Upload card
        upload_card = StyledCard()
        upload_layout = QVBoxLayout()
        upload_layout.setContentsMargins(20, 20, 20, 20)
        upload_layout.setSpacing(16)
        
        upload_header = QHBoxLayout()
        upload_icon = QLabel("📤")
        upload_icon.setStyleSheet("font-size: 24px; background: transparent;")
        upload_title = QLabel("Upload Dataset")
        upload_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        upload_title.setStyleSheet("color: #111827; background: transparent;")
        upload_header.addWidget(upload_icon)
        upload_header.addWidget(upload_title)
        upload_header.addStretch()
        
        self.upload_btn = StyledButton("📁 Select CSV File", primary=True)
        self.upload_btn.clicked.connect(self.upload_file)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setFont(QFont("Segoe UI", 10))
        self.file_label.setStyleSheet("color: #6b7280; background: transparent;")
        self.file_label.setWordWrap(True)
        
        upload_layout.addLayout(upload_header)
        upload_layout.addWidget(self.file_label)
        upload_layout.addWidget(self.upload_btn)
        upload_layout.addStretch()
        upload_card.setLayout(upload_layout)

        # Enhanced Datasets card
        datasets_card = StyledCard()
        datasets_card_layout = QVBoxLayout()
        datasets_card_layout.setContentsMargins(20, 20, 20, 20)
        datasets_card_layout.setSpacing(16)
        
        datasets_header = QHBoxLayout()
        datasets_icon = QLabel("📁")
        datasets_icon.setStyleSheet("font-size: 24px; background: transparent;")
        self.datasets_title = QLabel("Your Datasets")
        self.datasets_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.datasets_title.setStyleSheet("color: #111827; background: transparent;")
        if self.is_admin:
            self.datasets_title.setText("All Datasets")
        datasets_header.addWidget(datasets_icon)
        datasets_header.addWidget(self.datasets_title)
        datasets_header.addStretch()
        
        self.dataset_list = QListWidget()
        self.dataset_list.setMaximumHeight(250)
        self.dataset_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                outline: none;
            }
            QListWidget::item {
                padding: 0px;
                margin: 6px 0px;
                background: transparent;
            }
        """)
        
        datasets_card_layout.addLayout(datasets_header)
        datasets_card_layout.addWidget(self.dataset_list)
        datasets_card.setLayout(datasets_card_layout)

        top_grid.addWidget(upload_card, 0, 0)
        top_grid.addWidget(datasets_card, 0, 1)
        top_grid.setColumnStretch(0, 1)
        top_grid.setColumnStretch(1, 1)

        content_layout.addLayout(top_grid)

        # Admin user management section
        if self.is_admin:
            users_card = StyledCard()
            users_layout = QVBoxLayout()
            users_layout.setContentsMargins(20, 20, 20, 20)
            users_layout.setSpacing(16)

            users_header = QHBoxLayout()
            users_icon = QLabel("👥")
            users_icon.setStyleSheet("font-size: 24px; background: transparent;")
            users_title = QLabel("User Management")
            users_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
            users_title.setStyleSheet("color: #111827; background: transparent;")
            users_header.addWidget(users_icon)
            users_header.addWidget(users_title)
            users_header.addStretch()

            self.users_list = QListWidget()
            self.users_list.setMaximumHeight(260)
            self.users_list.setStyleSheet("""
                QListWidget {
                    border: none;
                    background-color: transparent;
                    outline: none;
                }
                QListWidget::item {
                    padding: 0px;
                    margin: 6px 0px;
                    background: transparent;
                }
            """)

            users_layout.addLayout(users_header)
            users_layout.addWidget(self.users_list)
            users_card.setLayout(users_layout)
            content_layout.addWidget(users_card)

        # Enhanced Summary section
        self.summary_card = StyledCard()
        self.summary_card.setVisible(False)
        self.summary_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        summary_layout = QVBoxLayout()
        summary_layout.setContentsMargins(20, 20, 20, 20)
        summary_layout.setSpacing(20)
        
        # Summary header with close button
        summary_header = QHBoxLayout()
        summary_icon = QLabel("📈")
        summary_icon.setStyleSheet("font-size: 24px; background: transparent;")
        summary_title = QLabel("Analysis Summary")
        summary_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        summary_title.setStyleSheet("color: #111827; background: transparent;")
        summary_header.addWidget(summary_icon)
        summary_header.addWidget(summary_title)
        summary_header.addStretch()
        
        close_btn = StyledButton("✕", small=True)
        close_btn.setMaximumWidth(40)
        close_btn.clicked.connect(self.close_summary)
        summary_header.addWidget(close_btn)
        
        summary_layout.addLayout(summary_header)
        
        # Enhanced Stats grid
        self.stats_layout = QGridLayout()
        self.stats_layout.setSpacing(16)
        self.stats_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.addLayout(self.stats_layout)
        
        # Charts section with enhanced styling
        charts_container = QFrame()
        charts_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fafbfc, stop:1 white);
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        charts_layout = QVBoxLayout(charts_container)
        
        charts_title = QLabel("Equipment Distribution Analysis")
        charts_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        charts_title.setStyleSheet("color: #111827; background: transparent;")
        charts_layout.addWidget(charts_title)
        
        self.figure = Figure(figsize=(10, 4), dpi=100)
        self.figure.patch.set_facecolor('#fafbfc')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(320)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        charts_layout.addWidget(self.canvas)
        
        summary_layout.addWidget(charts_container, 1)
        
        # Export buttons grid
        export_buttons_layout = QGridLayout()
        export_buttons_layout.setSpacing(12)
        export_buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.export_btn = StyledButton("📊 Export Chart", primary=True)
        self.export_btn.clicked.connect(self.export_chart)
        export_buttons_layout.addWidget(self.export_btn, 0, 0)
        
        self.pdf_export_btn = StyledButton("📄 Download PDF Report", primary=True)
        self.pdf_export_btn.clicked.connect(self.download_pdf_report)
        export_buttons_layout.addWidget(self.pdf_export_btn, 0, 1)
        
        summary_layout.addLayout(export_buttons_layout)

        # Filters section
        filters_container = QFrame()
        filters_container.setStyleSheet("""
            QFrame {
                background: #fafbfc;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        filters_layout = QVBoxLayout(filters_container)
        filters_layout.setContentsMargins(16, 16, 16, 16)
        filters_layout.setSpacing(12)

        filters_header = QHBoxLayout()
        filters_title = QLabel("Filter Equipment")
        filters_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        filters_title.setStyleSheet("color: #111827; background: transparent;")
        self.filters_count_label = QLabel("0 results")
        self.filters_count_label.setFont(QFont("Segoe UI", 9))
        self.filters_count_label.setStyleSheet("color: #6b7280; background: transparent;")
        filters_header.addWidget(filters_title)
        filters_header.addStretch()
        filters_header.addWidget(self.filters_count_label)
        filters_layout.addLayout(filters_header)

        filters_grid = QGridLayout()
        filters_grid.setHorizontalSpacing(12)
        filters_grid.setVerticalSpacing(10)

        self.filter_type = QComboBox()
        self.filter_type.addItem("All types", "")
        self.filter_type.setStyleSheet("padding: 6px; border: 1px solid #e5e7eb; border-radius: 6px;")
        filters_grid.addWidget(QLabel("Equipment Type"), 0, 0)
        filters_grid.addWidget(self.filter_type, 1, 0)

        self.filter_name = QLineEdit()
        self.filter_name.setPlaceholderText("Search equipment name")
        self.filter_name.setStyleSheet("padding: 6px; border: 1px solid #e5e7eb; border-radius: 6px;")
        filters_grid.addWidget(QLabel("Search Name"), 0, 1)
        filters_grid.addWidget(self.filter_name, 1, 1)

        self.filter_pressure_min = QLineEdit()
        self.filter_pressure_min.setPlaceholderText("Min")
        self.filter_pressure_min.setStyleSheet("padding: 6px; border: 1px solid #e5e7eb; border-radius: 6px;")
        self.filter_pressure_max = QLineEdit()
        self.filter_pressure_max.setPlaceholderText("Max")
        self.filter_pressure_max.setStyleSheet("padding: 6px; border: 1px solid #e5e7eb; border-radius: 6px;")
        filters_grid.addWidget(QLabel("Pressure Min"), 2, 0)
        filters_grid.addWidget(self.filter_pressure_min, 3, 0)
        filters_grid.addWidget(QLabel("Pressure Max"), 2, 1)
        filters_grid.addWidget(self.filter_pressure_max, 3, 1)

        self.filter_temperature_min = QLineEdit()
        self.filter_temperature_min.setPlaceholderText("Min")
        self.filter_temperature_min.setStyleSheet("padding: 6px; border: 1px solid #e5e7eb; border-radius: 6px;")
        self.filter_temperature_max = QLineEdit()
        self.filter_temperature_max.setPlaceholderText("Max")
        self.filter_temperature_max.setStyleSheet("padding: 6px; border: 1px solid #e5e7eb; border-radius: 6px;")
        filters_grid.addWidget(QLabel("Temperature Min"), 4, 0)
        filters_grid.addWidget(self.filter_temperature_min, 5, 0)
        filters_grid.addWidget(QLabel("Temperature Max"), 4, 1)
        filters_grid.addWidget(self.filter_temperature_max, 5, 1)

        filters_layout.addLayout(filters_grid)

        filters_actions = QHBoxLayout()
        filters_actions.addStretch()
        self.filters_clear_btn = StyledButton("Clear", small=True)
        self.filters_clear_btn.clicked.connect(self.clear_filters)
        self.filters_apply_btn = StyledButton("Apply Filters", primary=True, small=True)
        self.filters_apply_btn.clicked.connect(self.apply_filters)
        filters_actions.addWidget(self.filters_clear_btn)
        filters_actions.addWidget(self.filters_apply_btn)
        filters_layout.addLayout(filters_actions)

        summary_layout.addWidget(filters_container)

        # Records table
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(5)
        self.records_table.setHorizontalHeaderLabels(["Equipment Name", "Type", "Flowrate", "Pressure", "Temperature"])
        self.records_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.records_table.verticalHeader().setVisible(False)
        self.records_table.setAlternatingRowColors(True)
        self.records_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e5e7eb;
                border-radius: 10px;
                background: white;
            }
            QHeaderView::section {
                background: #f3f4f6;
                color: #374151;
                padding: 6px;
                border: none;
                font-weight: 600;
            }
        """)
        summary_layout.addWidget(self.records_table)
        
        self.summary_card.setLayout(summary_layout)
        content_layout.addWidget(self.summary_card, 1)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)

        main_layout.addWidget(header_widget)
        main_layout.addWidget(scroll_area, 1)

        self.setLayout(main_layout)
        self.refresh_datasets()

    def _set_window_icon(self):
        """Set window icon from file with error handling and Windows taskbar support"""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chem-visualizer-logo.ico")
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.setWindowIcon(icon)
                    
                    # Windows-specific taskbar icon fix
                    if platform.system() == "Windows":
                        try:
                            import ctypes
                            # Get window handle and set app user model ID
                            hwnd = self.winId()
                            if hwnd:
                                # This helps Windows taskbar recognize the custom icon
                                myappid = 'ChemicalVisualizer.App'
                                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                        except Exception as e:
                            print(f"Windows icon hint error (non-critical): {e}")
                else:
                    print(f"Warning: Icon at {icon_path} appears to be invalid")
            else:
                print(f"Warning: Icon file not found at: {icon_path}")
        except Exception as e:
            print(f"Error setting icon: {e}")

    def refresh_datasets(self):
        self.dataset_list.clear()
        datasets = get_datasets()
        if not datasets:
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.setContentsMargins(20, 40, 20, 40)
            
            empty_icon = QLabel("📭")
            empty_icon.setStyleSheet("font-size: 48px; background: transparent;")
            empty_icon.setAlignment(Qt.AlignCenter)
            
            empty_label = QLabel("No datasets yet.\nUpload one to get started.")
            empty_label.setFont(QFont("Segoe UI", 11))
            empty_label.setStyleSheet("color: #9ca3af; background: transparent;")
            empty_label.setAlignment(Qt.AlignCenter)
            
            empty_layout.addWidget(empty_icon)
            empty_layout.addWidget(empty_label)
            
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 160))
            self.dataset_list.addItem(item)
            self.dataset_list.setItemWidget(item, empty_widget)
            if self.is_admin:
                self.refresh_users()
            return
            
        for d in datasets:
            owner_text = None
            if self.is_admin and d.get("owner"):
                owner = d.get("owner", {})
                owner_text = f"Owner: {owner.get('username', 'Unknown')} (#{owner.get('id', '')})"
            item = QListWidgetItem()
            widget = DatasetItem(
                d["id"],
                self.view_dataset,
                self.delete_dataset_ui,
                owner_text=owner_text
            )
            item.setSizeHint(widget.sizeHint())
            self.dataset_list.addItem(item)
            self.dataset_list.setItemWidget(item, widget)

        if self.is_admin:
            self.refresh_users()

    def refresh_users(self):
        if not self.is_admin:
            return
        self.users_list.clear()
        users = get_users()
        if not users:
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.setContentsMargins(20, 30, 20, 30)

            empty_icon = QLabel("👤")
            empty_icon.setStyleSheet("font-size: 36px; background: transparent;")
            empty_icon.setAlignment(Qt.AlignCenter)

            empty_label = QLabel("No users found.")
            empty_label.setFont(QFont("Segoe UI", 11))
            empty_label.setStyleSheet("color: #9ca3af; background: transparent;")
            empty_label.setAlignment(Qt.AlignCenter)

            empty_layout.addWidget(empty_icon)
            empty_layout.addWidget(empty_label)

            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 120))
            self.users_list.addItem(item)
            self.users_list.setItemWidget(item, empty_widget)
            return

        current_id = self.current_user.get("id")
        for user in users:
            item = QListWidgetItem()
            widget = UserItem(
                user,
                self.delete_user_ui,
                disable_delete=(user.get("id") == current_id)
            )
            item.setSizeHint(widget.sizeHint())
            self.users_list.addItem(item)
            self.users_list.setItemWidget(item, widget)

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            try:
                file_name = file_path.split('/')[-1]
                self.file_label.setText(f"📄 {file_name}")
                result = upload_csv(file_path)
                if result and result.get("error"):
                    self.file_label.setText("❌ Upload failed")
                    self.file_label.setStyleSheet("color: #ef4444; background: transparent;")
                    QMessageBox.warning(self, "Upload Error", result.get("error"))
                else:
                    self.file_label.setText("✅ File uploaded successfully!")
                    self.file_label.setStyleSheet("color: #10b981; background: transparent;")
                    self.refresh_datasets()
            except Exception as e:
                self.file_label.setText(f"❌ Upload failed")
                self.file_label.setStyleSheet("color: #ef4444; background: transparent;")

    def close_summary(self):
        self.summary_card.setVisible(False)

    def plot_chart(self, distribution):
        self.figure.clear()

        # Create 2 subplots with minimalistic styling
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)

        labels = list(distribution.keys())
        values = list(distribution.values())

        # Minimalistic Bar Chart
        colors_bar = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
        bars = ax1.bar(labels, values, color=colors_bar[:len(labels)], 
                       edgecolor='white', linewidth=1.5, alpha=0.95)
        ax1.set_title("Equipment Type Count", fontsize=12, fontweight='600', 
                      pad=15, color='#111827', fontfamily='sans-serif')
        ax1.set_ylabel("Count", fontsize=10, fontweight='600', color='#6b7280')
        ax1.set_facecolor('white')
        ax1.grid(axis='y', alpha=0.15, linestyle='-', linewidth=0.5, color='#e5e7eb')
        ax1.tick_params(axis='x', rotation=35, labelsize=9, colors='#6b7280')
        ax1.tick_params(axis='y', labelsize=9, colors='#6b7280')
        
        # Remove all spines for cleaner look
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color('#e5e7eb')
        ax1.spines['bottom'].set_color('#e5e7eb')
        ax1.spines['left'].set_linewidth(0.8)
        ax1.spines['bottom'].set_linewidth(0.8)
        
        # Add subtle animation effect via alpha gradient
        for i, bar in enumerate(bars):
            bar.set_alpha(0.8 + (i % 2) * 0.15)

        # Minimalistic Pie Chart
        colors_pie = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
        wedges, texts, autotexts = ax2.pie(
            values, 
            labels=labels, 
            autopct='%1.1f%%',
            startangle=140,
            colors=colors_pie[:len(labels)],
            textprops={'fontsize': 9, 'weight': '600', 'fontfamily': 'sans-serif'},
            wedgeprops={'edgecolor': '#fafbfc', 'linewidth': 1.5},
            counterclock=False
        )
        ax2.set_title("Distribution", fontsize=12, fontweight='600', 
                      pad=15, color='#111827', fontfamily='sans-serif')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('600')
            autotext.set_fontsize(8)
        
        for text in texts:
            text.set_color('#374151')
            text.set_fontsize(9)
            text.set_fontweight('600')

        # Interactive cursor with subtle styling
        cursor = mplcursors.cursor(bars, hover=True)
        cursor.connect(
            "add", lambda sel: sel.annotation.set_text(
                f"{labels[sel.index]}: {values[sel.index]}"
            )
        )

        self.figure.patch.set_facecolor('white')
        self.figure.tight_layout(pad=2.0)
        self.canvas.draw()

    def update_stats_display(self, summary):
        """Update the stats grid with enhanced cards"""
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        stats = [
            ("Total Equipment", str(summary['total_equipment']), "🏭", "#eff6ff", "#dbeafe"),
            ("Avg Flowrate", f"{summary['average_flowrate']:.2f}", "💧", "#f0fdf4", "#dcfce7"),
            ("Avg Pressure", f"{summary['average_pressure']:.2f}", "⚡", "#fff7ed", "#ffedd5"),
            ("Avg Temperature", f"{summary['average_temperature']:.2f}", "🌡️", "#fef2f2", "#fee2e2"),
        ]
        
        for i, (label, value, icon, color_start, color_end) in enumerate(stats):
            stat_card = StatCard(label, value, icon, color_start, color_end)
            self.stats_layout.addWidget(stat_card, i // 2, i % 2)

    def _collect_filter_params(self):
        params = {}
        selected_type = self.filter_type.currentData()
        if selected_type:
            params["type"] = selected_type

        name_value = self.filter_name.text().strip()
        if name_value:
            params["name"] = name_value

        if self.filter_pressure_min.text().strip():
            params["pressure_min"] = self.filter_pressure_min.text().strip()
        if self.filter_pressure_max.text().strip():
            params["pressure_max"] = self.filter_pressure_max.text().strip()
        if self.filter_temperature_min.text().strip():
            params["temperature_min"] = self.filter_temperature_min.text().strip()
        if self.filter_temperature_max.text().strip():
            params["temperature_max"] = self.filter_temperature_max.text().strip()
        return params

    def apply_filters(self):
        if not self.selected_id:
            return
        self.fetch_records(self.selected_id, self._collect_filter_params())

    def clear_filters(self):
        if not self.selected_id:
            return
        self.filter_type.setCurrentIndex(0)
        self.filter_name.setText("")
        self.filter_pressure_min.setText("")
        self.filter_pressure_max.setText("")
        self.filter_temperature_min.setText("")
        self.filter_temperature_max.setText("")
        self.fetch_records(self.selected_id, {})

    def _update_filters_meta(self, meta, keep_type=None):
        types = meta.get("available_types", [])
        current_type = keep_type if keep_type is not None else self.filter_type.currentData()
        self.filter_type.blockSignals(True)
        self.filter_type.clear()
        self.filter_type.addItem("All types", "")
        for t in types:
            self.filter_type.addItem(str(t), str(t))
        if current_type and current_type in types:
            self.filter_type.setCurrentIndex(self.filter_type.findData(current_type))
        else:
            self.filter_type.setCurrentIndex(0)
        self.filter_type.blockSignals(False)

        name_supported = bool(meta.get("name_supported"))
        self.filter_name.setDisabled(not name_supported)
        if not name_supported:
            self.filter_name.setText("")
            self.filter_name.setPlaceholderText("Name column not available")
        else:
            self.filter_name.setPlaceholderText("Search equipment name")

        pressure_range = meta.get("pressure_range") or {}
        temperature_range = meta.get("temperature_range") or {}
        if pressure_range:
            self.filter_pressure_min.setPlaceholderText(str(pressure_range.get("min", "Min")))
            self.filter_pressure_max.setPlaceholderText(str(pressure_range.get("max", "Max")))
        if temperature_range:
            self.filter_temperature_min.setPlaceholderText(str(temperature_range.get("min", "Min")))
            self.filter_temperature_max.setPlaceholderText(str(temperature_range.get("max", "Max")))

        total = meta.get("total", 0)
        self.filters_count_label.setText(f"{total} result" + ("" if total == 1 else "s"))

    def _update_records_table(self, records, name_supported):
        headers = ["Type", "Flowrate", "Pressure", "Temperature"]
        if name_supported:
            headers = ["Equipment Name"] + headers
        self.records_table.setColumnCount(len(headers))
        self.records_table.setHorizontalHeaderLabels(headers)
        self.records_table.setRowCount(len(records))

        for row_idx, rec in enumerate(records):
            col = 0
            if name_supported:
                item = QTableWidgetItem(str(rec.get("name", "-")))
                self.records_table.setItem(row_idx, col, item)
                col += 1
            self.records_table.setItem(row_idx, col, QTableWidgetItem(str(rec.get("type", ""))))
            self.records_table.setItem(row_idx, col + 1, QTableWidgetItem(str(rec.get("flowrate", ""))))
            self.records_table.setItem(row_idx, col + 2, QTableWidgetItem(str(rec.get("pressure", ""))))
            self.records_table.setItem(row_idx, col + 3, QTableWidgetItem(str(rec.get("temperature", ""))))

    def fetch_records(self, dataset_id, params):
        payload = get_records(dataset_id, params)
        if payload.get("error"):
            QMessageBox.warning(self, "Records Error", payload.get("error"))
            return
        self._update_filters_meta(payload, keep_type=params.get("type") if params else None)
        records = payload.get("records", [])
        name_supported = bool(payload.get("name_supported"))
        self._update_records_table(records, name_supported)

    def view_dataset(self, dataset_id):
        self.selected_id = dataset_id
        summary = get_summary(dataset_id)
        if not summary or "equipment_type_distribution" not in summary:
            self.figure.clear()
            self.canvas.draw()
            return

        self.summary_card.setVisible(True)
        self.update_stats_display(summary)
        self.plot_chart(summary['equipment_type_distribution'])
        self.clear_filters()

    def delete_dataset_ui(self, dataset_id):
        delete_dataset(dataset_id)
        self.refresh_datasets()
        self.summary_card.setVisible(False)
        self.figure.clear()
        self.canvas.draw()

    def delete_user_ui(self, user_id):
        if not user_id:
            return
        reply = QMessageBox.question(
            self,
            "Delete User",
            "Are you sure you want to delete this user?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        status = delete_user(user_id)
        if status in [200, 204]:
            self.refresh_users()
            self.refresh_datasets()
        else:
            QMessageBox.warning(self, "Error", "Failed to delete user.")

    def download_pdf_report(self):
        """Download PDF report for current dataset"""
        if not self.selected_id:
            QMessageBox.warning(self, "No Dataset Selected", "Please select a dataset first by clicking 'View'")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Report", f"dataset_{self.selected_id}_report.pdf", "PDF Files (*.pdf)"
        )
        if file_path:
            if download_pdf(self.selected_id, file_path):
                QMessageBox.information(self, "Success", "PDF report downloaded successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to download PDF report")

    def handle_logout(self):
        """Handle user logout"""
        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Clear credentials
            set_credentials(None, None)
            # Close current app window
            self.close()
            # Create new login dialog and show it
            def on_login_success():
                global main_window
                main_window = App()
                main_window.show()
            global login_window
            login_window = LoginDialog(on_login_success)
            login_window.show()

    def export_chart(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Chart", "", "PNG Files (*.png);;PDF Files (*.pdf)"
        )
        if file_path:
            try:
                self.figure.savefig(file_path, dpi=200, bbox_inches='tight', 
                                   facecolor='white', edgecolor='none')
            except Exception as e:
                pass


if __name__ == "__main__":
    # Windows-specific: Set app user model ID for proper taskbar integration
    if platform.system() == "Windows":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('ChemicalVisualizer.App')
        except Exception as e:
            print(f"Warning: Could not set Windows app ID: {e}")
    
    app = QApplication(sys.argv)
    
    # Set application-wide font
    app.setFont(QFont("Segoe UI", 10))
    
    # Set application icon at the application level (using setApplicationName can help with taskbar)
    app.setApplicationName("Chemical Equipment Visualizer")
    icon_path = os.path.join(os.path.dirname(__file__), "chem-visualizer-logo.ico")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        if not app_icon.isNull():
            # Try to set via window manager hint for better taskbar integration
            pass  # Will be set on window level instead
    
    # Global variables to keep track of windows
    main_window = None
    login_window = None
    
    # Create a container to hold either login dialog or main app
    def show_app():
        """Show main application after successful login"""
        global main_window, login_window
        if login_window:
            login_window.close()
        main_window = App()
        main_window.show()
    
    # Start with login dialog
    login_window = LoginDialog(show_app)
    login_window.show()
    
    sys.exit(app.exec_())
