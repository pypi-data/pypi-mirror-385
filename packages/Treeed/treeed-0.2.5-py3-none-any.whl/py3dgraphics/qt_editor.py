import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QListWidgetItem, QLabel, QLineEdit, QPushButton,
                             QGroupBox, QFormLayout, QFileDialog, QMessageBox, QCheckBox,
                             QSplitter, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
import numpy as np

from .graphics import Scene3D, create_cube, Object3D

class SceneEditorQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Py3DGraphics Scene Editor (PyQt)")
        self.setGeometry(100, 100, 1000, 700)

        self.scene = Scene3D()
        self.objects = []
        self.selected_object = None

        self.init_ui()
        self.update_object_list()

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Left panel - Object list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Toolbar
        toolbar_layout = QHBoxLayout()
        add_btn = QPushButton("Add Cube")
        add_btn.clicked.connect(self.add_cube)
        toolbar_layout.addWidget(add_btn)

        delete_btn = QPushButton("Delete Object")
        delete_btn.clicked.connect(self.delete_object)
        toolbar_layout.addWidget(delete_btn)

        preview_btn = QPushButton("Preview Scene")
        preview_btn.clicked.connect(self.preview_scene)
        toolbar_layout.addWidget(preview_btn)

        save_btn = QPushButton("Save Scene")
        save_btn.clicked.connect(self.save_scene)
        toolbar_layout.addWidget(save_btn)

        load_btn = QPushButton("Load Scene")
        load_btn.clicked.connect(self.load_scene)
        toolbar_layout.addWidget(load_btn)

        left_layout.addLayout(toolbar_layout)

        # Object list
        self.object_list = QListWidget()
        self.object_list.itemSelectionChanged.connect(self.on_object_select)
        left_layout.addWidget(QLabel("Objects:"))
        left_layout.addWidget(self.object_list)

        main_layout.addWidget(left_panel, 1)

        # Right panel - Properties
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Properties group
        props_group = QGroupBox("Properties")
        props_layout = QFormLayout(props_group)

        # Position
        self.pos_x_edit = QLineEdit("0")
        self.pos_y_edit = QLineEdit("0")
        self.pos_z_edit = QLineEdit("0")

        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("X:"))
        pos_layout.addWidget(self.pos_x_edit)
        pos_layout.addWidget(QLabel("Y:"))
        pos_layout.addWidget(self.pos_y_edit)
        pos_layout.addWidget(QLabel("Z:"))
        pos_layout.addWidget(self.pos_z_edit)
        props_layout.addRow("Position:", pos_layout)

        # Size
        self.size_edit = QLineEdit("100")
        props_layout.addRow("Size:", self.size_edit)

        # Speed
        self.speed_edit = QLineEdit("0.01")
        props_layout.addRow("Speed:", self.speed_edit)

        # Individual speeds
        self.speed_x_edit = QLineEdit("0.01")
        self.speed_y_edit = QLineEdit("0.01")
        self.speed_z_edit = QLineEdit("0.01")

        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("X:"))
        speed_layout.addWidget(self.speed_x_edit)
        speed_layout.addWidget(QLabel("Y:"))
        speed_layout.addWidget(self.speed_y_edit)
        speed_layout.addWidget(QLabel("Z:"))
        speed_layout.addWidget(self.speed_z_edit)
        props_layout.addRow("Rotation Speed:", speed_layout)

        # Color
        self.color_r_edit = QLineEdit("1.0")
        self.color_g_edit = QLineEdit("0.0")
        self.color_b_edit = QLineEdit("0.0")

        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("R:"))
        color_layout.addWidget(self.color_r_edit)
        color_layout.addWidget(QLabel("G:"))
        color_layout.addWidget(self.color_g_edit)
        color_layout.addWidget(QLabel("B:"))
        color_layout.addWidget(self.color_b_edit)
        props_layout.addRow("Color:", color_layout)

        # Outline Color
        self.outline_r_edit = QLineEdit("1.0")
        self.outline_g_edit = QLineEdit("1.0")
        self.outline_b_edit = QLineEdit("1.0")

        outline_layout = QHBoxLayout()
        outline_layout.addWidget(QLabel("R:"))
        outline_layout.addWidget(self.outline_r_edit)
        outline_layout.addWidget(QLabel("G:"))
        outline_layout.addWidget(self.outline_g_edit)
        outline_layout.addWidget(QLabel("B:"))
        outline_layout.addWidget(self.outline_b_edit)
        props_layout.addRow("Outline Color:", outline_layout)

        # Line width
        self.line_width_edit = QLineEdit("2")
        props_layout.addRow("Line Width:", self.line_width_edit)

        # Fill checkbox
        self.fill_checkbox = QCheckBox("Fill faces")
        props_layout.addRow(self.fill_checkbox)

        # Apply button
        apply_btn = QPushButton("Apply Changes")
        apply_btn.clicked.connect(self.apply_changes)
        props_layout.addRow(apply_btn)

        right_layout.addWidget(props_group)
        right_layout.addStretch()

        main_layout.addWidget(right_panel, 2)

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
