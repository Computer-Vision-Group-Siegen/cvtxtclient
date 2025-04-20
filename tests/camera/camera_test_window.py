import sys
from typing import Optional
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import asyncio
import aiohttp
from cvtxtclient.api.controller import ControllerAPI 
from cvtxtclient.api.config import APIConfig
from cvtxtclient.models.camera_config import CameraConfig
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QByteArray
from PyQt5.QtGui import QPixmap, QImage

# --- Configuration ---
API_BASE_URL = "http://localhost:8080/api/v1"
API_KEY = "TEST"


class ImageStreamReceiver(QThread):
    """Receives and emits image frames from the camera stream."""
    new_frame = pyqtSignal(QImage)
    stream_error = pyqtSignal(str)
    stream_started = pyqtSignal(bool, str)
    stream_stopped = pyqtSignal(bool, str)

    def __init__(self, api_config: APIConfig):
        super().__init__()
        self.api_config = api_config
        self._running = False
        self._session = None
        self._controller_api = None
        self._event_loop = None
        self._receive_stream_task: Optional[asyncio.Task] = None

    def start_stream(self):
        self.start() # Start the QThread, which will execute the run method

    def stop(self):
        if self._event_loop and self._event_loop.is_running():
            asyncio.run_coroutine_threadsafe(self._stop_and_exit(), self._event_loop)
        else:
            asyncio.run(self._stop_and_exit()) # Fallback if loop isn't running yet

    async def _stop_and_exit(self):
        await self._stop_stream_api()
        self._stop_thread_loop()

    def run(self):
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)
        self._receive_stream_task = self._event_loop.create_task(self._receive_stream())
        self._event_loop.run_forever() 

    async def _stop_session(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
            self._controller_api = None

    async def _start_stream_api(self):
        self._session = aiohttp.ClientSession()
        self._controller_api = ControllerAPI(config=self.api_config, session=self._session)
        camera_config = CameraConfig()  # You can adjust the config here
        try:
            await asyncio.wait_for(self._controller_api.start_camera(camera_config), timeout=10)
            self.stream_started.emit(True, "Camera stream started successfully.")
        except Exception as e:
            self.stream_started.emit(False, f"Error starting camera stream: {e}")

    async def _stop_stream_api(self):
        if self._controller_api and self._session:
            try:
                # Check if receiver is running before stopping
                if self._running:
                    # Set running to False to trigger the stop
                    self._running = False
                    # Wait for the receiver to finish
                    if self._receive_stream_task:
                        await asyncio.wait_for(self._receive_stream_task, timeout=3)
                        # Ceck if still running, if so, stop the stream
                        if not self._receive_stream_task.done():
                            self._receive_stream_task.cancel()

                await asyncio.wait_for(self._controller_api.stop_camera(), timeout=10)
                self.stream_stopped.emit(True, "Camera stream stopped successfully.")
            except asyncio.TimeoutError:
                self.stream_stopped.emit(False, "Timeout error stopping camera stream.")
            except Exception as e:
                self.stream_stopped.emit(False, f"Error stopping camera stream: {e}")
            finally:
                await self._stop_session()
        self._running = False
        self.stream_stopped.emit(True, "Stream receiver thread finished.")

    def _stop_thread_loop(self):
        if self._event_loop and self._event_loop.is_running():
            self._event_loop.stop()

    async def _receive_stream(self):
        await self._start_stream_api() # Call start API here, within the thread's loop
        if not self._controller_api or not self._session:
            self.stream_error.emit("API client or session not initialized.")
            return
        self._running = True
        try:
            async for frame_bytes in self._controller_api.camera_image_stream():
                if not self._running:
                    break
                image = QImage.fromData(QByteArray(frame_bytes), "JPEG")
                if not image.isNull():
                    self.new_frame.emit(image)
                else:
                    print("Received invalid JPEG frame")
        except Exception as e:
            if self._running:
                self._event_loop.call_soon_threadsafe(self.stream_error.emit, f"Error receiving image stream: {e}")
                # Call stop
                self._running = False
                await self._stop_and_exit()
        finally:
            print("Image stream receiver loop finished.")
            self.stream_stopped.emit(True, "Stream receiver thread finished.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Stream Display")
        self.setGeometry(100, 100, 640, 480)  # Adjust size as needed

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Stream")
        self.stop_button = QPushButton("Stop Stream")
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.stop_button)
        self.layout.addLayout(self.button_layout)

        self.stream_receiver_thread = None

        self.start_button.clicked.connect(self._start_stream)
        self.stop_button.clicked.connect(self._stop_stream)
        self.stop_button.setEnabled(False)  # Initially disable stop button

    
    def _start_stream(self):
        if self.stream_receiver_thread is None or not self.stream_receiver_thread.isRunning():
            config = APIConfig(base_url=API_BASE_URL, api_key=API_KEY)
            self.stream_receiver_thread = ImageStreamReceiver(config)
            self.stream_receiver_thread.new_frame.connect(self._update_image)
            self.stream_receiver_thread.stream_error.connect(self._show_stream_error)
            self.stream_receiver_thread.stream_started.connect(self._handle_stream_started)
            self.stream_receiver_thread.stream_stopped.connect(self._handle_stream_stopped)
            self.stream_receiver_thread.start_stream()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

    def _stop_stream(self):
        if self.stream_receiver_thread and self.stream_receiver_thread.isRunning():
            self.stream_receiver_thread.stop()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def _handle_stream_started(self, success: bool, message: str):
        if not success:
            QMessageBox.critical(self, "Start Error", message)
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def _handle_stream_stopped(self, success: bool, message: str):
        if not success:
            QMessageBox.warning(self, "Stop Warning", message)
        self.image_label.clear()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if self.stream_receiver_thread:
            self.stream_receiver_thread.wait()
            self.stream_receiver_thread = None

    def _update_image(self, image: QImage):
        scaled_image = image.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap = QPixmap.fromImage(scaled_image)
        self.image_label.clear()
        self.image_label.setPixmap(pixmap)

    def _show_stream_error(self, message: str):
        QMessageBox.critical(self, "Stream Error", message)
        self._stop_stream()

    def closeEvent(self, event):
        self._stop_stream()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())