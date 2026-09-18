from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QRadioButton, QToolButton, QButtonGroup,
)


def chart_preview(name):
    dark_background_color = "#303030"
    figure = Figure(figsize=(2, 2), dpi=100, facecolor=dark_background_color)
    canvas = FigureCanvasAgg(figure)
    axes = figure.add_subplot(111)
    axes.set_facecolor(dark_background_color)
    color = "#dddddd"

    # simple designs to display
    if name == "Pie Chart":
        axes.pie([45, 30, 25], colors=[color, "#999999", "#666666"],
                 wedgeprops={"edgecolor": dark_background_color, "linewidth": 3})
    elif name == "Histogram":
        axes.bar(range(5), [2, 5, 8, 6, 3], color=color, width=0.9)
    elif name == "Box Plot":
        axes.boxplot([[1, 3, 4, 5, 7], [2, 4, 6, 7, 9]],
                     boxprops={"color": color}, whiskerprops={"color": color},
                     capprops={"color": color}, medianprops={"color": color})
    elif name == "Line Chart":
        axes.plot([1, 2, 3, 4, 5], [2, 5, 3, 6, 8], color=color,
                  linewidth=3, marker="o")
    else:
        axes.scatter([1, 2, 3, 3.5, 4, 5], [2, 4, 3, 6, 5, 8],
                     color=color, s=45)
    axes.set_axis_off()
    figure.tight_layout(pad=0.5)
    canvas.draw()
    image = QImage(canvas.buffer_rgba(), 200, 200, QImage.Format.Format_RGBA8888)
    return QIcon(QPixmap.fromImage(image.copy()))


class ChartPicker(QWidget):
    def __init__(self):
        super().__init__()
        self.names = ["Pie Chart", "Histogram", "Box Plot", "Line Chart", "Scatter Plot"]
        self.group = QButtonGroup(self)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        #loop over each chart type and create QToolButton
        for index, name in enumerate(self.names):
            tile = QVBoxLayout()
            preview = QToolButton()
            preview.setIcon(chart_preview(name)) # sets image generated to icon
            preview.setIconSize(QSize(120, 120))
            preview.setFixedSize(140, 140)
            preview.setCheckable(True)
            preview.setAccessibleName(name)
            preview.setStyleSheet(
                "QToolButton { background: #303030; border: 2px solid #505050; "
                "border-radius: 4px; }"
                "QToolButton:hover { border-color: #aaaaaa; }"
                "QToolButton:checked { border-color: #eeeeee; border-style: solid; }"
            )
            radio = QRadioButton(name)
            self.group.addButton(radio, index)
            radio.toggled.connect(preview.setChecked)
            preview.clicked.connect(lambda checked=False, button=radio: button.setChecked(True))
            preview.clicked.connect(lambda checked=False, button=preview: button.setChecked(True))
            tile.addWidget(preview, alignment=Qt.AlignmentFlag.AlignHCenter)
            tile.addWidget(radio, alignment=Qt.AlignmentFlag.AlignHCenter)
            layout.addLayout(tile, index // 3, index % 3)
        self.setCurrentIndex(0)

    def currentText(self):
        return self.names[self.group.checkedId()]

    def setCurrentIndex(self, index):
        self.group.button(index).setChecked(True)
