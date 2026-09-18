# for debug use:
DE_BUG = True

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QLineEdit, QSpinBox
)

# dynamic settings
class ChartSettings(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        self.heading = QLabel("Chart Settings")
        layout.addWidget(self.heading)

        self.form = QFormLayout()
        layout.addLayout(self.form)

        # Zero row: set chart title
        self.chart_title = QLineEdit()
        self.form.addRow("Chart title:", self.chart_title)

        # First row: choose column/row
        self.orientation = QComboBox()
        self.orientation.addItems(["Column", "Row"])
        self.form.addRow("Read data by:", self.orientation)

        # Second row: choose label/index
        self.selection_mode = QComboBox()
        self.selection_mode.addItems(["Label", "Excel index"])
        self.form.addRow("Select using:", self.selection_mode)

        # Third row: include first entry or not
        self.include_first = QCheckBox("Include first entry")
        self.include_first.setChecked(False)
        self.include_first.setEnabled(False)
        self.form.addRow("", self.include_first)

        # Fourth row: choose your data series
        self.series_inputs = []
        self.series_box = QWidget()
        self.series_form = QFormLayout(self.series_box)
        self.series_form.setContentsMargins(0, 0, 0, 0)
        self.form.addRow("Data series:", self.series_box)

        # Fifth row: button to add series
        self.add_series_button = QPushButton("+ Add series")
        self.add_series_button.clicked.connect(self.add_data_series)
        self.form.addRow("", self.add_series_button)
        self.add_series()

        # Sixth row: button to remove series
        # add a button to remove series:
        self.remove_series_button = QPushButton("- Remove series")
        self.remove_series_button.clicked.connect(self.remove_data_series)
        self.form.addRow("", self.remove_series_button)

        # Seventh row: add x_label
        self.x_label = QLineEdit()
        self.form.addRow("X-axis label:", self.x_label)

        # Eighth row: add y_label
        self.y_label = QLineEdit()
        self.form.addRow("Y-axis label:", self.y_label)

        # Ninth row: choose x scale
        self.x_scale = QComboBox()
        self.x_scale.addItems(["linear", "log"])
        self.form.addRow("X-axis scale:", self.x_scale)

        # Tenth row: choose y scale
        self.y_scale = QComboBox()
        self.y_scale.addItems(["linear", "log"])
        self.form.addRow("Y-axis scale:", self.y_scale)

        # Eleventh row: set #bins
        self.bins = QSpinBox()
        self.bins.setRange(1, 1000)
        self.bins.setValue(10)
        self.form.addRow("Bins:", self.bins)


        self.selection_mode.currentTextChanged.connect(
            self.update_selection_mode
        )
        layout.addStretch()

        buttons = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.generate_button = QPushButton("Generate")
        self.generate_button.setEnabled(True)

        buttons.addWidget(self.back_button)
        buttons.addStretch()
        buttons.addWidget(self.generate_button)
        layout.addLayout(buttons)

    def update_selection_mode(self, mode):
        self.include_first.setEnabled(mode == "Excel index")

    def configure_for_chart(self, chart_name):
        self.chart_name = chart_name
        self.heading.setText(f"{chart_name} Settings")

        has_x_axis = chart_name in [
            "Histogram", "Line Chart", "Scatter Plot"
        ]
        has_y_axis = chart_name != "Pie Chart"

        self.form.setRowVisible(self.x_label, has_x_axis)
        self.form.setRowVisible(self.x_scale, has_x_axis)
        self.form.setRowVisible(self.y_label, has_y_axis)
        self.form.setRowVisible(self.y_scale, has_y_axis)
        self.form.setRowVisible(
            self.bins, chart_name == "Histogram"
        )

        self.configure_data_inputs()

    def configure_data_inputs(self):
        # TODO: check carefully for the maximum
        # The logic here is not complete
        match self.chart_name:
            case "Pie Chart":
                minimum, maximum = 1, 1
            case "Scatter Plot":
                minimum, maximum = 2, 2
            case "Line Chart":
                minimum, maximum = 2, None
            case "Histogram" | "Box Plot":
                minimum, maximum = 1, None
            case _:
                raise ValueError("Unknown chart type")

        while len(self.series_inputs) < minimum:
            self.add_series()

        self.form.setRowVisible(self.series_box, True)
        self.form.setRowVisible(self.add_series_button, maximum is None)
        # fix bug (2026/09/17): 'Remove button' is visible in 'Pie Chart', 'Box Plot' and 'Scatter Plot'
        self.form.setRowVisible(self.remove_series_button, maximum is None)

        for index, field in enumerate(self.series_inputs):
            visible = maximum is None or index < maximum
            self.series_form.setRowVisible(field, visible)

            if self.chart_name in ["Line Chart", "Scatter Plot"]:
                label = "X data:" if index == 0 else f"Y data {index}:"
            elif self.chart_name == "Pie Chart":
                label = "Data:"
            else:
                label = f"Series {index + 1}:"

            self.series_form.labelForField(field).setText(label)

    def add_data_series(self):
        self.add_series()
        self.configure_data_inputs()

    def add_series(self):
        field = QLineEdit()
        self.series_inputs.append(field)
        number = len(self.series_inputs)
        self.series_form.addRow(f"Series {number}:", field)

    # logic for 'remove' button:
    def remove_data_series(self):
        # be sure the number of data series is enough to plot the chart:
        match self.chart_name:
            case "Pie Chart":
                minimum, maximum = 1, 1
            case "Scatter Plot":
                minimum, maximum = 2, 2
            case "Line Chart":
                minimum, maximum = 2, float('inf')
            case "Histogram" | "Box Plot":
                minimum, maximum = 1, float('inf')
            case _:
                raise ValueError("Unknown chart type")
        # fix bug (2026/09/17): TypeError: '>' not supported between instances of 'int' and 'NoneType'
        if len(self.series_inputs) < minimum or len(self.series_inputs) > maximum:
            raise ValueError('Too much/less data series you choose')
        # remove the last data series in the list
        field = self.series_inputs.pop()

        # remove the last one from the windows
        self.series_form.removeRow(field)
        # fix bug (2026/09/17): RuntimeError: libshiboken: Internal C++ object (PySide6.QtWidgets.QLineEdit) already deleted.
        # the line below will over delete the object -> segmentation fault / Run time error
        # field.deleteLater()

        # update label/...
        self.configure_data_inputs()

        # raise NotImplementedError

    def get_settings(self):
        ids = []

        for field in self.series_inputs:
            if self.series_form.isRowVisible(field):
                ids.append(field.text())

        if self.orientation.currentText() == "Column":
            is_col = True
        else:
            is_col = False

        if self.selection_mode.currentText() == "Label":
            selection = "label"
        else:
            selection = "index"

        selections = []
        first_elements = []

        for _ in ids:
            selections.append(selection)
            first_elements.append(self.include_first.isChecked())

        if DE_BUG:
            print(f'the column/row ids you choose is: {ids}')

        return {
            "chart_name": self.chart_name,
            "ids": ids,
            "is_col": is_col,
            "selections": selections,
            "first_elements": first_elements,
            "title": self.chart_title.text(),
            "x_label": self.x_label.text(),
            "y_label": self.y_label.text(),
            "x_scale": self.x_scale.currentText(),
            "y_scale": self.y_scale.currentText(),
            "bins": self.bins.value(),
        }
