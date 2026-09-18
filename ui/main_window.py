DE_BUG = True

from pathlib import Path
import traceback
import matplotlib.pyplot as plt

from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QPushButton,
    QMessageBox,
    QVBoxLayout,
    QWidget,
    QHBoxLayout
)

from core.data_processor import DataProcessor
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtWidgets import QStackedWidget
from ui.chart_settings import ChartSettings
from ui.chart_picker import ChartPicker

class MainWindow(QWidget):
    '''
    Consists of 3 pages:
        - file page
        - chart type page
        - setting page
    '''
    def __init__(self):
        super().__init__()

        self.processor = DataProcessor()

        self.setWindowTitle("Data Visualizer")
        self.resize(600, 400)

        root_layout = QVBoxLayout(self)
        self.toast = QLabel()
        self.toast.setTextFormat(Qt.TextFormat.PlainText)
        self.toast.setWordWrap(True)
        self.toast.setMargin(8)
        self.toast.setAccessibleName("Chart notification")
        self.toast.hide()
        root_layout.addWidget(self.toast)
        self.toast_timer = QTimer(self)
        self.toast_timer.setSingleShot(True)
        self.toast_timer.timeout.connect(self.toast.hide)

        self.pages = QStackedWidget()
        root_layout.addWidget(self.pages)

        file_page = QWidget()
        layout = QVBoxLayout(file_page)
        self.pages.addWidget(file_page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        '''
            The first page: choose your file
                - browse button: allows you to browse file and choose
                - file list: list of file you choose
                - next button: go to second page
        '''
        # The list of file you choose
        self.file_list = QListWidget()
        self.file_list.itemChanged.connect(self.toggle_file)
        # 'next' button to the second page
        self.next_button = QPushButton("Next")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(1)
        )
        # delete button
        self.delete_button = QPushButton("Delete")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_files)
        
        # browse button
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_files)
        # upper row
        upload_row = QHBoxLayout()
        upload_row.addWidget(QLabel("Upload file:"))
        upload_row.addWidget(browse_button)
        # bottom row
        bottom_row = QHBoxLayout()
        bottom_row.addWidget(self.delete_button)
        bottom_row.addWidget(self.next_button)

        layout.addLayout(upload_row)
        layout.addWidget(self.file_list)
        layout.addLayout(bottom_row)

        '''
            The second page: choose your chart
                - a box helps you choose type of charts you want
                - back button: back to the first page
                - next button: lead you to the third page
        '''
        chart_page = QWidget()
        chart_layout = QVBoxLayout(chart_page)
        chart_layout.setContentsMargins(32, 32, 32, 32)
        chart_layout.setSpacing(16)

        chart_layout.addWidget(QLabel("Choose Chart"))
        self.chart_choice = ChartPicker()
        chart_layout.addWidget(self.chart_choice)
        chart_layout.addStretch()
        # back button
        back_button = QPushButton("Back")
        back_button.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        chart_navigation = QHBoxLayout()
        chart_navigation.addWidget(back_button)
        chart_navigation.addStretch()
        chart_layout.addLayout(chart_navigation)
        self.pages.addWidget(chart_page)

        '''
            The third page: set your charts
            refering to chart_settings.py for more info
        '''
        self.settings_page = ChartSettings()
        self.settings_page.generate_button.clicked.connect(
            self.generate_chart
        )

        self.pages.addWidget(self.settings_page)
        self.settings_page.back_button.clicked.connect(
            lambda: self.pages.setCurrentWidget(chart_page)
        )

        settings_button = QPushButton("Next")
        settings_button.clicked.connect(self.open_settings)
        chart_navigation.addWidget(settings_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setStyleSheet(
            "QPushButton { border: 1px solid red; padding: 6px 16px; }"
        )
        self.reset_button.clicked.connect(self.reset_program)
        root_layout.addWidget(self.reset_button, alignment=Qt.AlignmentFlag.AlignRight)

    def reset_program(self):
        answer = QMessageBox.question(
            self,
            "Reset program?",
            "This will clear all selected files and settings and close all graphs. "
            "Your files on disk will not be deleted. Start over?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        plt.close("all")
        self.processor = DataProcessor()
        self.refresh_files()
        self.chart_choice.setCurrentIndex(0)

        # settings page restores every field and removes extra series.
        old_settings = self.settings_page
        self.pages.removeWidget(old_settings)
        old_settings.deleteLater()
        self.settings_page = ChartSettings()
        self.settings_page.generate_button.clicked.connect(self.generate_chart)
        self.settings_page.back_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(1)
        )
        self.pages.addWidget(self.settings_page)

        self.toast_timer.stop()
        self.toast.clear()
        self.toast.hide()
        self.pages.setCurrentIndex(0)

    def browse_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select data files",
            "",
            "Data files (*.csv *.xlsx)",
        )

        if paths:
            self.processor.add_filenames(paths)
            self.refresh_files()

    def delete_files(self):
        paths = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                paths.append(item.data(Qt.ItemDataRole.UserRole))

        if not paths:
            return

        # remove files from processor
        self.processor.remove_filenames(paths)
        # refresh the window
        self.refresh_files()

    def refresh_files(self):
        filenames, active_filenames = self.processor.get_filenames()

        self.file_list.blockSignals(True)
        self.file_list.clear()

        for path in filenames:
            item = QListWidgetItem(Path(path).name)
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setToolTip(path)
            state = (
                Qt.CheckState.Checked
                if path in active_filenames
                else Qt.CheckState.Unchecked
            )
            item.setCheckState(state)
            self.file_list.addItem(item)

        self.file_list.blockSignals(False)
        self.update_next_button()
        # add delete button:
        self.update_delete_button()

    def toggle_file(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if item.checkState() == Qt.CheckState.Checked:
            self.processor.activate_filenames(path)
        else:
            self.processor.deactivate_filenames(path)

        self.update_next_button()
        # add delete button:
        self.update_delete_button()

    def update_next_button(self):
        _, active_filenames = self.processor.get_filenames()
        self.next_button.setEnabled(bool(active_filenames))

    def update_delete_button(self):
        _, active_filenames = self.processor.get_filenames()
        self.delete_button.setEnabled(bool(active_filenames))

    def open_settings(self):
        chart_name = self.chart_choice.currentText()
        self.settings_page.configure_for_chart(chart_name)
        self.pages.setCurrentWidget(self.settings_page)

    def call_chart_function(self, settings):
        match settings["chart_name"]:
            case "Pie Chart":
                self.processor.pie_chart(
                    id=settings["ids"][0],
                    is_col=settings["is_col"],
                    selection=settings["selections"][0],
                    first_element=settings["first_elements"][0],
                    title=settings["title"],
                )
            case "Line Chart":
                self.processor.line_plot(
                    ids=settings["ids"],
                    is_col=settings["is_col"],
                    selections=settings["selections"],
                    first_elements=settings["first_elements"],
                    title=settings["title"],
                    x_label=settings["x_label"],
                    y_label=settings["y_label"],
                    x_scale=settings["x_scale"],
                    y_scale=settings["y_scale"],
                )
            case "Scatter Plot":
                self.processor.scatter_plot(
                    ids=settings["ids"],
                    is_col=settings["is_col"],
                    selections=settings["selections"],
                    first_elements=settings["first_elements"],
                    title=settings["title"],
                    x_label=settings["x_label"],
                    y_label=settings["y_label"],
                    x_scale=settings["x_scale"],
                    y_scale=settings["y_scale"],
                )
            case "Histogram":
                self.processor.histogram(
                    ids=settings["ids"],
                    is_col=settings["is_col"],
                    selections=settings["selections"],
                    first_elements=settings["first_elements"],
                    title=settings["title"],
                    x_label=settings["x_label"],
                    y_label=settings["y_label"],
                    x_scale=settings["x_scale"],
                    y_scale=settings["y_scale"],
                    bins=settings["bins"],
                )
            case "Box Plot":
                self.processor.box_plot(
                    ids=settings["ids"],
                    is_col=settings["is_col"],
                    selections=settings["selections"],
                    first_elements=settings["first_elements"],
                    title=settings["title"],
                    label=settings["y_label"],
                    axis_scale=settings["y_scale"],
                )
            case _:
                raise ValueError("Choose a supported chart type.")
        if DE_BUG:
            print(f"inside call_chart_function")
            print(f"The file you selected to analyse is: {self.processor.get_filenames()[1]}")
            print(f"The file you have is: {self.processor.get_filenames()[0]}")

    def generate_chart(self):
        previous_figures = {plt.figure(number) for number in plt.get_fignums()}
        self.settings_page.generate_button.setEnabled(False)
        try:
            settings = self.settings_page.get_settings()
            if not self.processor.get_filenames()[1]:
                raise ValueError("Select at least one file before generating a chart.")
            settings["ids"] = [value.strip() for value in settings["ids"]]
            if not settings["ids"] or not all(settings["ids"]):
                raise ValueError("Fill in every visible data selector.")

            # Qt already runs the event loop; Matplotlib must not start another.
            with plt.ion():
                self.call_chart_function(settings)
            if not plt.get_fignums():
                raise ValueError("No graph was created. Check your data selections.")
            manager = plt.get_current_fig_manager()
            manager.canvas.draw_idle()
            manager.show()
            manager.window.raise_()
            manager.window.activateWindow()
            self.show_toast("Graph opened in a separate window.")
        except Exception as error:
            for number in plt.get_fignums():
                figure = plt.figure(number)
                if figure not in previous_figures:
                    plt.close(figure)
            if isinstance(error, NameError) and str(error) == "no data found":
                message = (
                    "No matching data. Check the selected files and every row/column "
                    "label, including spaces and underscores."
                )
            else:
                message = f"Could not generate chart: {error}"
            self.show_toast(message)
            traceback.print_exc()
        finally:
            self.settings_page.generate_button.setEnabled(True)

    def show_toast(self, message):
        self.toast.setText(message)
        self.toast.show()
        self.toast_timer.start(10000)
