"""
File Handler - Drag & Drop functionality
Handles file drops and displays content on Pepper's tablet.
"""

import os
import logging
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

logger = logging.getLogger(__name__)

class DropZone(QLabel):
    """Drag and drop zone widget."""
    
    file_dropped = pyqtSignal(str)  # Emits file path when file is dropped
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("dropZone")
        self.setMinimumHeight(150)
        
        self.setText(
            "📄 Drag & Drop Files Here\n\n"
            "to display on Pepper's tablet\n\n"
            "Supported: Images, Videos, HTML, PDF"
        )
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dragActive", "true")
            self.style().unpolish(self)
            self.style().polish(self)
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """Handle drag leave."""
        self.setProperty("dragActive", "false")
        self.style().unpolish(self)
        self.style().polish(self)
    
    def dropEvent(self, event: QDropEvent):
        """Handle file drop."""
        self.setProperty("dragActive", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        
        if event.mimeData().hasUrls():
            # Get first file
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            
            if os.path.exists(file_path):
                self.file_dropped.emit(file_path)
                event.acceptProposedAction()
            else:
                logger.error(f"File not found: {file_path}")


class FileHandler:
    """Handles file operations for tablet display."""
    
    def __init__(self, tablet_service, session):
        self.tablet = tablet_service
        self.session = session
        
        # Supported file types
        self.image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        self.video_extensions = ['.mp4', '.avi', '.mov', '.webm']
        self.html_extensions = ['.html', '.htm']
        self.pdf_extensions = ['.pdf']
    
    def handle_file(self, file_path):
        """Process and display file on tablet."""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext in self.image_extensions:
                return self._display_image(file_path)
            elif file_ext in self.video_extensions:
                return self._display_video(file_path)
            elif file_ext in self.html_extensions:
                return self._display_html(file_path)
            elif file_ext in self.pdf_extensions:
                return self._display_pdf(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_ext}")
                return False
        except Exception as e:
            logger.error(f"Error displaying file: {e}")
            return False
    
    def _display_image(self, file_path):
        """Display image on tablet."""
        logger.info(f"Displaying image: {file_path}")
        
        # Convert local file path to URL
        file_url = f"file://{os.path.abspath(file_path)}"
        
        try:
            # Use tablet service to show image
            self.tablet.tablet.showImage(file_url)
            return True
        except Exception as e:
            logger.error(f"Failed to display image: {e}")
            
            # Fallback: Create simple HTML wrapper
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        background: #000;
                    }}
                    img {{
                        max-width: 100%;
                        max-height: 100vh;
                        object-fit: contain;
                    }}
                </style>
            </head>
            <body>
                <img src="{file_url}" alt="Dropped Image">
            </body>
            </html>
            """
            self.tablet.tablet.showWebview(html)
            return True
    
    def _display_video(self, file_path):
        """Display video on tablet."""
        logger.info(f"Playing video: {file_path}")
        
        file_url = f"file://{os.path.abspath(file_path)}"
        
        try:
            self.tablet.tablet.playVideo(file_url)
            return True
        except Exception as e:
            logger.error(f"Failed to play video: {e}")
            return False
    
    def _display_html(self, file_path):
        """Display HTML file on tablet."""
        logger.info(f"Displaying HTML: {file_path}")
        
        try:
            # Read HTML content
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Display on tablet
            self.tablet.tablet.showWebview(html_content)
            return True
        except Exception as e:
            logger.error(f"Failed to display HTML: {e}")
            return False
    
    def _display_pdf(self, file_path):
        """Display PDF on tablet (converted to image)."""
        logger.info(f"Displaying PDF: {file_path}")
        
        # PDF display would require conversion to images
        # For now, show a message
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    text-align: center;
                }}
                .message {{
                    background: rgba(255,255,255,0.15);
                    padding: 40px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                }}
            </style>
        </head>
        <body>
            <div class="message">
                <h1>📄 PDF Document</h1>
                <p style="font-size: 24px;">{os.path.basename(file_path)}</p>
                <p style="font-size: 18px; opacity: 0.8;">PDF preview not yet implemented</p>
            </div>
        </body>
        </html>
        """
        
        try:
            self.tablet.tablet.showWebview(html)
            return True
        except Exception as e:
            logger.error(f"Failed to display PDF: {e}")
            return False


class FileDropPanel(QWidget):
    """Panel widget that contains drop zone and file info."""
    
    file_displayed = pyqtSignal(str, bool)  # file_path, success
    
    def __init__(self, tablet_ctrl, session):
        super().__init__()
        
        self.tablet = tablet_ctrl
        self.session = session
        self.file_handler = FileHandler(tablet_ctrl, session)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_file_dropped)
        layout.addWidget(self.drop_zone)
        
        # Current file label
        self.current_file_label = QLabel("No file loaded")
        self.current_file_label.setStyleSheet("color: #8e8e8e; font-size: 11px;")
        self.current_file_label.setWordWrap(True)
        layout.addWidget(self.current_file_label)
    
    def _on_file_dropped(self, file_path):
        """Handle file drop."""
        logger.info(f"File dropped: {file_path}")
        
        # Update label
        self.current_file_label.setText(f"Processing: {os.path.basename(file_path)}")
        
        # Handle file
        success = self.file_handler.handle_file(file_path)
        
        if success:
            self.current_file_label.setText(f"✓ Displayed: {os.path.basename(file_path)}")
            self.current_file_label.setStyleSheet("color: #4ade80; font-size: 11px;")
        else:
            self.current_file_label.setText(f"✗ Failed: {os.path.basename(file_path)}")
            self.current_file_label.setStyleSheet("color: #f87171; font-size: 11px;")
        
        # Emit signal
        self.file_displayed.emit(file_path, success)