# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the linechart example from Qt v5.x"""

import paho.mqtt.client as mqtt
import sys,json,random
from PySide6.QtCore import QPointF
from PySide6.QtCore import (QDateTime, QDir, QLibraryInfo, QSysInfo, Qt,
                            QTimer, Slot, qVersion, QTimer)
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog,
                               QDialogButtonBox, QGridLayout, QGroupBox,
                               QFormLayout, QHBoxLayout, QLabel, QLineEdit,
                               QMenu, QMenuBar, QPushButton, QSpinBox,
                               QTextEdit, QVBoxLayout, QSlider, QWidget)

import animation_generator as generator
from types import ModuleType

from generator.mqtt_handler import MQTTHandler
from generator.animation_info import AnimInfo

class TestChart(QMainWindow):
    def __init__(self):
        super().__init__()

        self.default_plots = generator.init_plot_data()
        self.plot = AnimInfo(
            func = None,
            name = "Custom",
            arg = {
                "arg": 1,
                "power": 1,
            },
        )
        try:
            self.plot.arg = json.loads(open("last_data.json", "r").read())
        except:
            pass


        self._chart_view = None
        self.mqtt_client = None
        self.unused_widgets = []

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.__setup_group_box_chart_area())
        main_layout.addWidget(self.__setup_group_box_controls_area())

        central = QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        self.statusBar().showMessage("Starting...")

        self.mqtt = MQTTHandler(self.statusBar().showMessage)

        QTimer.singleShot(500, self.update_plot)


    def __setup_group_box_chart_area(self):
        self.series = QLineSeries()

        self._chart_view = QChartView()
        self._chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        layout = QHBoxLayout()
        layout.addWidget(self._chart_view)

        group_box = QGroupBox("Chart view")
        group_box.setLayout(layout)
        self.unused_widgets.append(group_box)
        return group_box

    def __setup_group_box_controls_area(self):
        layout = QVBoxLayout()

        layout.addWidget(self.__setup_group_box_code_area())
        layout.addWidget(self.__setup_group_box_control_buttons())
        layout.addWidget(self.__setup_group_box_argument_sliders())

        group_box = QGroupBox("")
        group_box.setLayout(layout)
        self.unused_widgets.append(group_box)
        return group_box


    def __setup_group_box_code_area(self):
        self.text_edit_code = QTextEdit()
        self.text_edit_code.setFontFamily("Consolas")
        try:
            self.text_edit_code.setText(open("last_plot.py", "r").read())
        except:
            pass

        self.text_edit_error = QTextEdit()
        self.text_edit_error.setReadOnly(True)
        self.text_edit_error.setFontFamily("Consolas")

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit_code)
        layout.addWidget(self.text_edit_error)

        group_box = QGroupBox("Code area")
        group_box.setLayout(layout)
        self.unused_widgets.append(group_box)
        return group_box

    def __setup_group_box_control_buttons(self):
        update_btn = QPushButton("Update")
        publish_btn = QPushButton("publish")

        self.unused_widgets.append(update_btn)
        self.unused_widgets.append(publish_btn)

        self.combobox_animation_selector = QComboBox()
        self.combobox_animation_selector.addItem("Custom")
        self.combobox_animation_selector.addItems([x.name for x in self.default_plots])
        self.combobox_animation_selector.setCurrentIndex(0)

        update_btn.clicked.connect(self.update_plot)
        publish_btn.clicked.connect(self.button_publish_clicked)

        self.combobox_animation_selector.currentIndexChanged.connect(self.update_series)

        layout = QHBoxLayout()
        layout.addWidget(update_btn)
        layout.addWidget(publish_btn)
        layout.addWidget(self.combobox_animation_selector)

        group_box = QGroupBox("Controls")
        group_box.setLayout(layout)
        self.unused_widgets.append(group_box)
        return group_box

    def __setup_group_box_argument_sliders(self):
        parent_layout = QVBoxLayout()

        arg = self.plot.arg
        span = 500

        def update_slider(slider, scale, arg_name, value):
            arg[arg_name] = value / scale
            self.update_plot()

        def create_slider(name, arg_name, scale, min, max):
            slider = QSlider()
            slider.setOrientation(Qt.Orientation.Horizontal)
            slider.setMinimum(min)
            slider.setMaximum(max)
            slider.setValue(arg[arg_name] * scale)
            layout = QHBoxLayout()
            layout.addWidget(QLabel(name))
            layout.addWidget(slider)
            w = QWidget()
            w.setLayout(layout)
            parent_layout.addWidget(w)
            slider.valueChanged.connect(lambda v: update_slider(slider, scale, arg_name, v))
            self.unused_widgets.append(slider)
            return slider

        create_slider(name = "Power", arg_name = "power", scale = 10, min = 0, max = span)
        create_slider(name = "Arg", arg_name = "arg",     scale = 10, min = 0, max = span)

        self.arg_label = QLabel("args")
        parent_layout.addWidget(self.arg_label)

        group_box = QGroupBox("Custom animation arguments")
        group_box.setLayout(parent_layout)
        self.unused_widgets.append(group_box)
        return group_box


    def update_series(self):
        self.series.clear()
        plot = self.current_plot()
        for x, y in zip(plot.x, plot.y):
            self.series.append(x / plot.DATA_LENGTH, y / plot.MAX_VALUE)

        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.addSeries(self.series)

        self.chart.createDefaultAxes()
        axis_y = self.chart.axes(Qt.Orientation.Horizontal)[0]
        axis_y.setMax(1)
        axis_y.setMin(0)

        self.chart.setTitle("Simple line chart example")

        if self._chart_view:
            self._chart_view.setChart(self.chart)

    def update_plot(self):
        text = self.text_edit_code.toPlainText()

        arg = self.plot.arg
        arg["code"] = text

        self.arg_label.setText(f'power={arg["power"]}  arg={arg["arg"]}')

        open("last_plot.py", "w").write(text)
        open("last_data.json", "w").write(json.dumps(arg, indent=4))

        try:
            compiled = compile(text, '', 'exec')
            module = ModuleType("generated")
            exec(compiled, module.__dict__)

            self.plot.func = module.func
            self.plot.regenerate()
            self.update_series()
            self.text_edit_error.setText("success")
        except Exception as e:
            self.text_edit_error.setText(str(e))

    def current_plot(self):
        which = self.combobox_animation_selector.currentIndex()
        if which == 0:
            return self.plot
        else:
            which = which - 1
            return self.default_plots[which]

    def button_publish_clicked(self):
        plot = self.current_plot()

        #plot.name
        self.publish(what="custom_animation", payload=plot.get_encoded_custom_anim_data())
        self.publish(what="animation", payload="Custom")

        self.statusBar().showMessage(f"Custom animation published")
        QTimer.singleShot(5000, self.mqtt.check_status)

    def publish(self, what, payload):
        self.mqtt.homie_set(what, payload)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestChart()
    window.show()
    window.resize(1400, 800)
    sys.exit(app.exec())