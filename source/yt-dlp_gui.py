import json
import sys

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
            self.save_app_config()

        # Check for ffmpeg installation
        self.ffmpeg_directory = self.set_ffmpeg_directory()

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
        radio_box_layout.addWidget(self.thumbnail_format_dropdown, 2, 1)
        self.thumbnail_radio_box.setLayout(radio_box_layout)


        # General options widgets
        self.general_options_box = (QGroupBox("General Options"))
        self.cookies_check_box = QCheckBox("Use Cookies from Browser")
        self.cookies_browser_dropdown = QComboBox()

        self.cookies_browser_dropdown.addItems(
            ["", "brave", "chrome", "chromium", "edge", "firefox", "opera", "safari", "vivaldi"]
        )
        self.cookies_check_box.setToolTip(
            "Use cookies from your browser. Useful for retrieving membership-gated content on YouTube."
        )

        general_options_box_layout = QGridLayout()
        general_options_box_layout.addWidget(self.cookies_check_box, 0, 0)
        general_options_box_layout.addWidget(self.cookies_browser_dropdown, 0, 1)
        self.general_options_box.setLayout(general_options_box_layout)


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
        video_box_layout.addWidget(self.video_convert_checkbox, 0, 0)
        video_box_layout.addWidget(self.video_format_dropdown, 0, 1)
        video_box_layout.addWidget(self.video_quality_label, 1, 0)
        video_box_layout.addWidget(self.video_quality_dropdown, 1, 1)
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
        audio_box_layout.addWidget(self.audio_format_dropdown, 0, 1)
        audio_box_layout.addWidget(self.audio_bitrate_checkbox, 1, 0)
        audio_box_layout.addWidget(self.audio_bitrate_input, 1, 1)
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


        # (widget, row, col, row_span, col_span, alignment)
        all_options_layout = QGridLayout()  
        all_options_layout.setColumnMinimumWidth(1, 15) # Add blank space
        all_options_layout.setRowMinimumHeight(4, 15)
        all_options_layout.addWidget(self.thumbnail_radio_box, 0, 0, 4, 1)
        all_options_layout.addWidget(self.general_options_box, 0, 2, 4, 1)
        all_options_layout.addWidget(self.video_options_box, 5, 0, 4, 1)
        all_options_layout.addWidget(self.audio_options_box, 5, 2, 4, 1)

        # Widgets - assemble main window
        main_layout.addWidget(self.url_input_label)
        main_layout.addWidget(self.url_input)
        main_layout.addLayout(all_options_layout)
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

    def set_ffmpeg_directory(self):
        if "ffmpeg_directory" not in self.app_config:
            self.pop_up_box = QMessageBox()
            self.pop_up_box.setText(
                "Please select your ffmpeg executable"
            )
            self.pop_up_box.exec()

            ffmpeg_directory = QFileDialog.getExistingDirectory()
            self.app_config["ffmpeg_directory"] = ffmpeg_directory
            self.save_app_config()
        else:
            ffmpeg_directory = self.app_config["ffmpeg_directory"]

        return ffmpeg_directory

    def save_app_config(self):
        with open(self.app_config_path, "w") as file:
            json.dump(self.app_config, file)

    def set_output_directory(self):
        self.output_directory = QFileDialog.getExistingDirectory()
        if DEBUG:
            self.output_check_text.appendPlainText(
                f"Output directory - {self.output_directory}"
            )

    def create_ytdlp_config(self):
        config = {
            "paths": {"home": self.output_directory},
            "writethumbnail": True,
            "ffmpeg_location": self.ffmpeg_directory,
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
            config["ffmpeg_location"] = self.ffmpeg_directory
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
        # Have user select an output directory
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
