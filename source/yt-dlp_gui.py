import json
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QSpacerItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from yt_dlp import YoutubeDL
from yt_dlp.utils import MEDIA_EXTENSIONS

DEBUG = False


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple yt-dlp GUI")
        default_width = 800
        default_height = 600
        self.resize(default_width, default_height)  # width, height

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Class variables
        self.urls = []
        self.app_config_path = "app_config.json"

        try:
            with open(self.app_config_path) as file:
                self.app_config = json.load(file)
        except FileNotFoundError:
            print("Config file not found. Generating...")
            self.app_config = {}
            self.save_app_config_file()


        # General options widgets
        self.general_options_box = (QGroupBox("General Options"))
        self.cookies_check_box = QCheckBox("Use browser cookies")
        self.cookies_browser_dropdown = QComboBox()
        self.output_directory_button = QPushButton("output directory", clicked=self.click_output_directory_button)
        self.output_directory_display = QLineEdit()
        self.ffmpeg_directory_button = QPushButton("ffmpeg directory", clicked=self.click_ffmpeg_directory_button)
        self.ffmpeg_directory_display = QLineEdit()

        # Would prefer a list maintained by yt-dlp, similar to ffmpeg codecs
        self.cookies_browser_dropdown.addItems(
            ["", "brave", "chrome", "chromium", "edge", "firefox", "opera", "safari", "vivaldi"]
        )
        self.cookies_check_box.setToolTip(
            "Use cookies from your browser. Useful for retrieving membership-gated content on YouTube."
        )
        self.output_directory_display.setReadOnly(True)
        self.ffmpeg_directory_display.setReadOnly(True)
        if "ffmpeg_directory" in self.app_config:
            self.ffmpeg_directory_display.setText(self.app_config["ffmpeg_directory"])
        if "output_directory" in self.app_config:
            self.output_directory_display.setText(self.app_config["output_directory"])

        # QGridLayout: (widget, row, col, row_span, col_span, alignment)
        general_options_box_layout = QGridLayout()
        general_options_box_layout.addWidget(self.cookies_check_box, 0, 0)
        general_options_box_layout.addWidget(self.cookies_browser_dropdown, 0, 1)
        general_options_box_layout.addWidget(self.output_directory_button, 1, 0)
        general_options_box_layout.addWidget(self.output_directory_display, 1, 1)
        general_options_box_layout.addWidget(self.ffmpeg_directory_button, 2, 0)
        general_options_box_layout.addWidget(self.ffmpeg_directory_display, 2, 1)
        general_options_box_layout.addItem(QSpacerItem(0, 0), 0, 2, 0, 5)
        self.general_options_box.setLayout(general_options_box_layout)


        # Thumbnail option widgets
        self.thumbnail_radio_box = QGroupBox("Thumbnail Options")
        self.thumbnail_embed_radio = QRadioButton("Embedded thumbnails")
        self.thumbnail_standalone_radio = QRadioButton("Standalone thumbnails")
        self.thumbnail_none_radio = QRadioButton("No thumbnails")
        self.thumbnail_format_dropdown = QComboBox()

        self.thumbnail_embed_radio.setChecked(True)
        self.thumbnail_format_dropdown.addItems(MEDIA_EXTENSIONS.thumbnails)
        self.thumbnail_format_dropdown.hide()
        self.thumbnail_embed_radio.setToolTip("Embed thumbnails in the media file")
        self.thumbnail_standalone_radio.setToolTip(
            "Save thumbnails as standalone image files"
        )

        self.thumbnail_button_group = QButtonGroup(
            buttonClicked=self.change_thumbnail_checkbox_state
        )
        self.thumbnail_button_group.addButton(self.thumbnail_embed_radio)
        self.thumbnail_button_group.addButton(self.thumbnail_standalone_radio)
        self.thumbnail_button_group.addButton(self.thumbnail_none_radio)

        radio_box_layout = QGridLayout()
        radio_box_layout.addWidget(self.thumbnail_none_radio, 0, 0)
        radio_box_layout.addWidget(self.thumbnail_embed_radio, 1, 0)
        radio_box_layout.addWidget(self.thumbnail_standalone_radio, 2, 0)
        radio_box_layout.addWidget(self.thumbnail_format_dropdown, 2, 1, alignment=Qt.AlignmentFlag(0x0001))
        self.thumbnail_radio_box.setLayout(radio_box_layout)


        # Video option widgets
        self.video_options_box = QGroupBox("Video Options")
        self.video_convert_checkbox = QCheckBox("Convert video")
        self.video_format_dropdown = QComboBox()
        self.video_quality_label = QLabel("Preferred quality")
        self.video_quality_dropdown = QComboBox()

        self.video_format_dropdown.addItem("")
        self.video_format_dropdown.addItems(MEDIA_EXTENSIONS.common_video)
        self.video_quality_dropdown.addItems(
            ["best", "1080p", "720p", "480p", "360p", "240p", "worst"]
        )
        self.video_quality_label.setToolTip(
            "Will attempt to download video at specified quality. If unavailable, it will grab the next best option"
        )

        video_box_layout = QGridLayout()
        video_box_layout.addWidget(self.video_quality_label, 0, 0)
        video_box_layout.addWidget(self.video_quality_dropdown, 0, 1, alignment=Qt.AlignmentFlag(0x0001))
        video_box_layout.addWidget(self.video_convert_checkbox, 1, 0)
        video_box_layout.addWidget(self.video_format_dropdown, 1, 1, alignment=Qt.AlignmentFlag(0x0001))
        video_box_layout.addItem(QSpacerItem(0, 0), 0, 2, 2, 5)
        self.video_options_box.setLayout(video_box_layout)


        # Audio option widgets
        self.audio_options_box = QGroupBox("Audio Options")
        self.strip_audio_checkbox = QCheckBox("Keep audio only")
        self.audio_format_label = QLabel("Convert audio file to:")
        self.audio_format_dropdown = QComboBox()
        self.audio_bitrate_checkbox = QLabel("Bitrate in kbps (optional)")
        self.audio_bitrate_input = QLineEdit()

        self.audio_format_dropdown.addItem("source format")
        self.audio_format_dropdown.addItems(MEDIA_EXTENSIONS.common_audio)
        self.strip_audio_checkbox.setToolTip("Saves only the audio, deletes the video")

        audio_box_layout = QGridLayout()
        audio_box_layout.addWidget(self.strip_audio_checkbox, 0, 0)
        audio_box_layout.addWidget(self.audio_format_dropdown, 0, 1, alignment=Qt.AlignmentFlag(0x0001))
        audio_box_layout.addWidget(self.audio_bitrate_checkbox, 1, 0)
        audio_box_layout.addWidget(self.audio_bitrate_input, 1, 1, alignment=Qt.AlignmentFlag(0x0001))
        audio_box_layout.addItem(QSpacerItem(0, 0), 0, 2, 2, 5)

        self.audio_options_box.setLayout(audio_box_layout)


        # All other widgets
        self.url_input_label = QLabel("Paste URLs, one per line:")
        self.url_input = QPlainTextEdit()

        self.confirm_button = QPushButton("Start Download", clicked=self.download)


        # Debug widgets
        self.output_check_button = QPushButton(
            "Check Output", clicked=self.output_check
        )
        self.output_check_text = QPlainTextEdit()
        self.output_check_text.setReadOnly(True)


        # Assemble tab bar
        self.settings_tab_bar = QTabWidget()
        self.settings_tab_bar.addTab(self.general_options_box, "General")
        self.settings_tab_bar.addTab(self.thumbnail_radio_box, "Thumbnail")
        self.settings_tab_bar.addTab(self.video_options_box, "Video")
        self.settings_tab_bar.addTab(self.audio_options_box, "Audio")


        # Widgets - assemble main window
        main_layout.addWidget(self.url_input_label)
        main_layout.addWidget(self.url_input)
        main_layout.addWidget(self.settings_tab_bar)
        main_layout.addItem(QSpacerItem(default_width, 60))
        main_layout.addWidget(self.confirm_button)


        if DEBUG:
            main_layout.addWidget(self.output_check_button)
            main_layout.addWidget(self.output_check_text)


    def change_thumbnail_checkbox_state(self):
        if self.thumbnail_standalone_radio.isChecked():
            self.thumbnail_format_dropdown.show()
        else:
            self.thumbnail_format_dropdown.hide()

    # DEBUG - Dry run, doesn't actually download anything
    def output_check(self):
        self.output_check_text.clear()
        self.set_output_directory()
        self.create_ytdlp_config()


    def click_ffmpeg_directory_button(self):
        if "ffmpeg_directory" in self.app_config:
            del self.app_config["ffmpeg_directory"]
        
        self.set_ffmpeg_directory()
        self.ffmpeg_directory_display.setText(self.app_config["ffmpeg_directory"])
    
    def click_output_directory_button(self):
        if "output_directory" in self.app_config:
            del self.app_config["output_directory"]
        
        self.set_output_directory()
        self.output_directory_display.setText(self.app_config["output_directory"])

    def set_ffmpeg_directory(self):
        if "ffmpeg_directory" not in self.app_config:
            ffmpeg_directory = QFileDialog.getExistingDirectory()
            self.app_config["ffmpeg_directory"] = ffmpeg_directory
            self.save_app_config_file()
        else:
            print("ffmpeg directory set!")

        if DEBUG:
            self.output_check_text.appendPlainText(
                f"ffmpeg directory - {self.app_config['ffmpeg_directory']}"
            )


    def set_output_directory(self):
        if "output_directory" not in self.app_config:
            output_directory = QFileDialog.getExistingDirectory()
            self.app_config["output_directory"] = output_directory
            self.save_app_config_file()
        else:
            print("output directory set!")
        
        if DEBUG:
            self.output_check_text.appendPlainText(
                f"Output directory - {self.app_config['output_directory']}"
            )

    def save_app_config_file(self):
        with open(self.app_config_path, "w") as file:
            json.dump(self.app_config, file)

    def create_ytdlp_config(self):
        config = {
            "paths": {"home": self.app_config["output_directory"]},
            "writethumbnail": True,
            "ffmpeg_location": self.app_config["ffmpeg_directory"],
            "postprocessors": [],
        }

        if self.cookies_check_box.isChecked():
            config["cookiesfrombrowser"] = (self.cookies_browser_dropdown.currentText(),)

        video_quality = self.video_quality_dropdown.currentText()

        if video_quality in ["best", "worst"]:
            config[
                "format"
            ] = f"{video_quality}video+{video_quality}audio/{video_quality}"
        else:
            video_quality = video_quality.replace("p", "")
            config["format"] = f"best[height<={video_quality}]"

        if self.video_convert_checkbox.isChecked():
            if self.video_format_dropdown.currentText() != "":
                config["postprocessors"].append(
                    {
                        "key": "FFmpegVideoConvertor",
                        "preferedformat": self.video_format_dropdown.currentText(),
                    }
                )
            else:
                print("No video format selected, conversion will be skipped.")

        if self.thumbnail_none_radio.isChecked():
            config["writethumbnail"] = False

        if self.strip_audio_checkbox.isChecked():
            config["format"] = "bestaudio"
            if self.audio_format_dropdown.currentText() != "source format":
                config["postprocessors"].append(
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": self.audio_format_dropdown.currentText(),
                        "preferredquality": self.audio_bitrate_input.text(),
                    }
                )
            else:
                print("No audio format selected, conversion will be skipped.")

        # Must come AFTER audio is stripped, otherwise it will embed
        # the thumbnail in video file that gets deleted
        if self.thumbnail_embed_radio.isChecked():
            config["postprocessors"].append({"key": "EmbedThumbnail"})

        if self.thumbnail_standalone_radio.isChecked():
            config["ffmpeg_location"] = self.app_config["ffmpeg_directory"]
            config["postprocessors"].append(
                {
                    "key": "FFmpegThumbnailsConvertor",
                    "format": self.thumbnail_format_dropdown.currentText(),
                }
            )

        if DEBUG:
            self.output_check_text.appendPlainText(f"{json.dumps(config, indent=2)}")

        return config

    def parse_urls(self):
        urls = self.url_input.toPlainText().split("\n")
        url_list = []
        # Remove whitespace from URLs
        for url in urls:
            url_list.append(url.strip())
        self.urls = url_list

        if DEBUG:
            self.output_check_text.appendPlainText(f"{self.urls}")

    
    def download(self):
        # Set ffmpeg directory
        if "ffmpeg_directory" not in self.app_config:
            ffmpeg_popup = QMessageBox()
            ffmpeg_popup.setText(
                "Please select your ffmpeg executable"
            )
            ffmpeg_popup.exec()
        self.set_ffmpeg_directory()
        
        # Set output directory
        if "output_directory" not in self.app_config:
            output_directory_popup = QMessageBox()
            output_directory_popup.setText("Please set an output directory")
            output_directory_popup.exec()
        self.set_output_directory()

        self.parse_urls()

        # Configure yt-dlp
        config = self.create_ytdlp_config()

        # Execute the download
        error_list = []
        for url in self.urls:
            try:
                with YoutubeDL(config) as ydl:
                    result = ydl.download(url)
            except Exception as e:
                error_list.append(e)

        if len(error_list) != 0:
            for error in error_list:
                print(error)
        print("Done!")


if __name__ == "__main__":
    # Create instance of application
    app = QApplication(sys.argv)

    # Set CSS style on app instance
    # QWidget applies a default to all widgets
    # You can also override settings for specific widgets
    css_style = """
    QWidget {
        font-size: 16px             
    }
    QPlainTextEdit {
        font-size: 16px
    }
    """
    app.setStyleSheet(css_style)
    app.setStyle("fusion")

    # Create a window and display it to the user
    window = MainWindow()
    window.show()

    # You're supposed to wrap the app execution in sys.exit() for some reason
    sys.exit(app.exec())
