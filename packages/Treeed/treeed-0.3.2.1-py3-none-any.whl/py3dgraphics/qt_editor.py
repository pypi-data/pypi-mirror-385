import sys
import json
import qdarkstyle  # Для темной темы
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QListWidgetItem, QLabel, QLineEdit, QPushButton,
                             QGroupBox, QFormLayout, QFileDialog, QMessageBox, QCheckBox,
                             QSplitter, QFrame, QColorDialog, QSlider, QAction, QToolBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QDoubleValidator, QIntValidator
import numpy as np

from .graphics import Scene3D, create_cube, Object3D

class ColorButton(QPushButton):
    """Кнопка, которая хранит цвет и открывает диалог выбора цвета."""
    def __init__(self, color=(0, 0, 0)):
        super().__init__()
        self.set_color(color)
        self.clicked.connect(self.on_click)

    def set_color(self, color):
        self._color = color
        self.setStyleSheet(f"background-color: rgb({color[0]*255}, {color[1]*255}, {color[2]*255});")

    def color(self):
        return self._color

    def on_click(self):
        new_color = QColorDialog.getColor(QColor.fromRgbF(*self._color))
        if new_color.isValid():
            self.set_color(new_color.getRgbF()[:3])


class SceneEditorQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Py3DGraphics Scene Editor")
        self.setGeometry(100, 100, 1200, 800)

        self.scene = Scene3D()
        self.objects = []
        self.selected_object_index = -1

        self.init_ui()
        self.update_object_list()

    def init_ui(self):
        # --- Toolbar ---
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Действия для кнопок с иконками
        add_action = QAction(QIcon.fromTheme("list-add"), "Add Cube", self)
        add_action.triggered.connect(self.add_cube)
        toolbar.addAction(add_action)

        delete_action = QAction(QIcon.fromTheme("list-remove"), "Delete Object", self)
        delete_action.triggered.connect(self.delete_object)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()

        save_action = QAction(QIcon.fromTheme("document-save"), "Save Scene", self)
        save_action.triggered.connect(self.save_scene)
        toolbar.addAction(save_action)

        load_action = QAction(QIcon.fromTheme("document-open"), "Load Scene", self)
        load_action.triggered.connect(self.load_scene)
        toolbar.addAction(load_action)

        toolbar.addSeparator()

        preview_action = QAction(QIcon.fromTheme("media-playback-start"), "Preview Scene", self)
        preview_action.triggered.connect(self.preview_scene)
        toolbar.addAction(preview_action)

        # --- Main Layout ---
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        # Left panel (Object list)
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_layout = QVBoxLayout(left_panel)

        self.object_list = QListWidget()
        self.object_list.itemSelectionChanged.connect(self.on_object_select)
        left_layout.addWidget(QLabel("Scene Objects"))
        left_layout.addWidget(self.object_list)
        splitter.addWidget(left_panel)

        # Right panel (Properties)
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_panel)

        self.props_group = QGroupBox("Object Properties")
        props_layout = QFormLayout(self.props_group)

        # Name
        self.name_edit = QLineEdit("Cube")
        props_layout.addRow("Name:", self.name_edit)

        # Position
        self.pos_x_edit, self.pos_y_edit, self.pos_z_edit = QLineEdit("0"), QLineEdit("0"), QLineEdit("0")
        for edit in [self.pos_x_edit, self.pos_y_edit, self.pos_z_edit]: edit.setValidator(QDoubleValidator())
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("X")); pos_layout.addWidget(self.pos_x_edit)
        pos_layout.addWidget(QLabel("Y")); pos_layout.addWidget(self.pos_y_edit)
        pos_layout.addWidget(QLabel("Z")); pos_layout.addWidget(self.pos_z_edit)
        props_layout.addRow("Position:", pos_layout)

        # Size
        self.size_edit = QLineEdit("100")
        self.size_edit.setValidator(QDoubleValidator(0.1, 10000, 2))
        props_layout.addRow("Size:", self.size_edit)

        # Rotation Speed
        self.speed_x_edit, self.speed_y_edit, self.speed_z_edit = QLineEdit("0"), QLineEdit("0.01"), QLineEdit("0")
        for edit in [self.speed_x_edit, self.speed_y_edit, self.speed_z_edit]: edit.setValidator(QDoubleValidator(-1, 1, 4))
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("X:")); speed_layout.addWidget(self.speed_x_edit)
        speed_layout.addWidget(QLabel("Y:")); speed_layout.addWidget(self.speed_y_edit)
        speed_layout.addWidget(QLabel("Z:")); speed_layout.addWidget(self.speed_z_edit)
        props_layout.addRow("Rotation Speed:", speed_layout)

        # Appearance
        self.fill_checkbox = QCheckBox("Enable Fill")
        props_layout.addRow("", self.fill_checkbox)

        self.color_btn = ColorButton(color=(1,0,0))
        props_layout.addRow("Fill Color:", self.color_btn)

        self.outline_color_btn = ColorButton(color=(1,1,1))
        props_layout.addRow("Outline Color:", self.outline_color_btn)

        self.line_width_slider = QSlider(Qt.Horizontal)
        self.line_width_slider.setRange(1, 10)
        props_layout.addRow("Line Width:", self.line_width_slider)

        apply_btn = QPushButton("Apply Changes")
        apply_btn.clicked.connect(self.apply_changes)
        right_layout.addWidget(self.props_group)
        right_layout.addWidget(apply_btn)
        right_layout.addStretch()
        splitter.addWidget(right_panel)

        splitter.setSizes([250, 450])

    def add_cube(self):
        cube = create_cube(size=100, speed=0.01, color=(1.0, 0.0, 0.0))
        self.objects.append(cube)
        self.scene.add_object(cube)
        self.update_object_list()

    def delete_object(self):
        if self.selected_object:
            self.scene.objects.remove(self.selected_object)
            self.objects.remove(self.selected_object)
            self.selected_object = None
            self.update_object_list()
            self.clear_properties()

    def update_object_list(self):
        self.object_list.clear()
        for i, obj in enumerate(self.objects):
            item = QListWidgetItem(f"Object {i+1}")
            self.object_list.addItem(item)

    def on_object_select(self):
        current_item = self.object_list.currentItem()
        if current_item:
            index = self.object_list.row(current_item)
            self.selected_object = self.objects[index]
            self.load_properties()

    def load_properties(self):
        if self.selected_object:
            pos = self.selected_object.position
            self.pos_x_edit.setText(str(pos[0]))
            self.pos_y_edit.setText(str(pos[1]))
            self.pos_z_edit.setText(str(pos[2]))

            self.size_edit.setText(str(getattr(self.selected_object, 'size', 100)))
            self.speed_edit.setText(str(self.selected_object.speed))

            self.speed_x_edit.setText(str(self.selected_object.speed_x))
            self.speed_y_edit.setText(str(self.selected_object.speed_y))
            self.speed_z_edit.setText(str(self.selected_object.speed_z))

            color = self.selected_object.color
            self.color_r_edit.setText(str(color[0]))
            self.color_g_edit.setText(str(color[1]))
            self.color_b_edit.setText(str(color[2]))

            outline_color = self.selected_object.outline_color
            self.outline_r_edit.setText(str(outline_color[0]))
            self.outline_g_edit.setText(str(outline_color[1]))
            self.outline_b_edit.setText(str(outline_color[2]))

            self.line_width_edit.setText(str(self.selected_object.line_width))
            self.fill_checkbox.setChecked(self.selected_object.fill)

    def clear_properties(self):
        self.pos_x_edit.setText("0")
        self.pos_y_edit.setText("0")
        self.pos_z_edit.setText("0")
        self.size_edit.setText("100")
        self.speed_edit.setText("0")
        self.speed_x_edit.setText("0")
        self.speed_y_edit.setText("0")
        self.speed_z_edit.setText("0")
        self.color_r_edit.setText("0")
        self.color_g_edit.setText("0")
        self.color_b_edit.setText("0")
        self.outline_r_edit.setText("1.0")
        self.outline_g_edit.setText("1.0")
        self.outline_b_edit.setText("1.0")
        self.line_width_edit.setText("2")
        self.fill_checkbox.setChecked(False)

    def apply_changes(self):
        if self.selected_object:
            try:
                self.selected_object.set_position(
                    float(self.pos_x_edit.text()),
                    float(self.pos_y_edit.text()),
                    float(self.pos_z_edit.text())
                )
                self.selected_object.speed = float(self.speed_edit.text())
                self.selected_object.speed_x = float(self.speed_x_edit.text())
                self.selected_object.speed_y = float(self.speed_y_edit.text())
                self.selected_object.speed_z = float(self.speed_z_edit.text())
                self.selected_object.color = (
                    float(self.color_r_edit.text()),
                    float(self.color_g_edit.text()),
                    float(self.color_b_edit.text())
                )
                self.selected_object.outline_color = (
                    float(self.outline_r_edit.text()),
                    float(self.outline_g_edit.text()),
                    float(self.outline_b_edit.text())
                )
                self.selected_object.line_width = int(self.line_width_edit.text())
                self.selected_object.fill = self.fill_checkbox.isChecked()

                # Store size for saving/loading (though it doesn't affect existing object)
                self.selected_object.size = float(self.size_edit.text())

            except ValueError as e:
                QMessageBox.warning(self, "Invalid Input", f"Please enter valid numbers: {str(e)}")

    def preview_scene(self):
        if not self.objects:
            QMessageBox.information(self, "Preview", "No objects in scene to preview.")
            return

        # For now, use the existing Tkinter preview
        # TODO: Implement proper PyQt preview window
        from .editor import SceneEditor
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()  # Hide the root window

        preview_window = tk.Toplevel(root)
        preview_window.title("Scene Preview")

        from .graphics import Scene3D as TkScene3D
        preview_scene = TkScene3D(width=800, height=600, title="Scene Preview", bg="black", master=preview_window)

        for obj in self.objects:
            preview_scene.add_object(obj)

        preview_scene.run()

    def save_scene(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Scene", "", "JSON files (*.json);;All files (*.*)"
        )
        if file_path:
            scene_data = {"objects": []}
            for obj in self.objects:
                obj_data = {
                    "type": "cube",
                    "position": obj.position.tolist(),
                    "speed": obj.speed,
                    "speed_x": obj.speed_x,
                    "speed_y": obj.speed_y,
                    "speed_z": obj.speed_z,
                    "color": obj.color,
                    "outline_color": obj.outline_color,
                    "line_width": obj.line_width,
                    "fill": obj.fill,
                    "size": getattr(obj, 'size', 100)
                }
                scene_data["objects"].append(obj_data)

            try:
                with open(file_path, 'w') as f:
                    json.dump(scene_data, f, indent=4)
                QMessageBox.information(self, "Save", "Scene saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save scene: {str(e)}")

    def load_scene(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Scene", "", "JSON files (*.json);;All files (*.*)"
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    scene_data = json.load(f)

                self.scene.objects.clear()
                self.objects.clear()

                for obj_data in scene_data.get("objects", []):
                    if obj_data["type"] == "cube":
                        cube = create_cube(
                            size=obj_data.get("size", 100),
                            speed=obj_data.get("speed", 0.01),
                            position=tuple(obj_data["position"]),
                            color=tuple(obj_data["color"]),
                            fill=obj_data.get("fill", False),
                            outline_color=tuple(obj_data.get("outline_color", (1.0, 1.0, 1.0))),
                            line_width=obj_data.get("line_width", 2),
                            speed_x=obj_data.get("speed_x"),
                            speed_y=obj_data.get("speed_y"),
                            speed_z=obj_data.get("speed_z")
                        )
                        # Store additional properties
                        cube.size = obj_data.get("size", 100)
                        self.objects.append(cube)
                        self.scene.add_object(cube)

                self.update_object_list()
                QMessageBox.information(self, "Load", "Scene loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load scene: {str(e)}")

def run_qt_editor():
    app = QApplication(sys.argv)
    editor = SceneEditorQt()
    editor.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_qt_editor()
