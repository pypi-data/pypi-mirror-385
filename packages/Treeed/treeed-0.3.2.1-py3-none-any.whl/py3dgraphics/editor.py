import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from .graphics import Scene3D, create_cube, Object3D

class SceneEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Py3DGraphics Scene Editor")
        self.root.geometry("800x600")

        self.scene = Scene3D()
        self.objects = []
        self.selected_object = None

        self.create_widgets()
        self.update_object_list()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(toolbar, text="Add Cube", command=self.add_cube).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Delete Object", command=self.delete_object).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Preview Scene", command=self.preview_scene).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Save Scene", command=self.save_scene).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Load Scene", command=self.load_scene).pack(side=tk.LEFT)

        # Object list
        list_frame = ttk.LabelFrame(main_frame, text="Objects")
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))

        self.object_listbox = tk.Listbox(list_frame, height=20)
        self.object_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.object_listbox.bind('<<ListboxSelect>>', self.on_object_select)

        # Properties panel
        props_frame = ttk.LabelFrame(main_frame, text="Properties")
        props_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        # Position
        pos_frame = ttk.Frame(props_frame)
        pos_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(pos_frame, text="Position:").grid(row=0, column=0, sticky=tk.W)
        self.pos_x_var = tk.DoubleVar()
        self.pos_y_var = tk.DoubleVar()
        self.pos_z_var = tk.DoubleVar()

        ttk.Entry(pos_frame, textvariable=self.pos_x_var, width=8).grid(row=0, column=1, padx=(5, 2))
        ttk.Entry(pos_frame, textvariable=self.pos_y_var, width=8).grid(row=0, column=2, padx=(2, 2))
        ttk.Entry(pos_frame, textvariable=self.pos_z_var, width=8).grid(row=0, column=3, padx=(2, 5))

        # Speed
        speed_frame = ttk.Frame(props_frame)
        speed_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(speed_frame, text="Speed:").grid(row=0, column=0, sticky=tk.W)
        self.speed_var = tk.DoubleVar()
        ttk.Entry(speed_frame, textvariable=self.speed_var, width=8).grid(row=0, column=1, padx=(5, 0))

        # Color
        color_frame = ttk.Frame(props_frame)
        color_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(color_frame, text="Color (R,G,B):").grid(row=0, column=0, sticky=tk.W)
        self.color_r_var = tk.DoubleVar()
        self.color_g_var = tk.DoubleVar()
        self.color_b_var = tk.DoubleVar()

        ttk.Entry(color_frame, textvariable=self.color_r_var, width=6).grid(row=0, column=1, padx=(5, 2))
        ttk.Entry(color_frame, textvariable=self.color_g_var, width=6).grid(row=0, column=2, padx=(2, 2))
        ttk.Entry(color_frame, textvariable=self.color_b_var, width=6).grid(row=0, column=3, padx=(2, 5))

        # Apply button
        ttk.Button(props_frame, text="Apply Changes", command=self.apply_changes).pack(pady=10)

    def add_cube(self):
        cube = create_cube(size=100, speed=0.01, color=(1.0, 0.0, 0.0))
        self.objects.append(cube)
        self.scene.add_object(cube)
        self.update_object_list()

    def delete_object(self):
        if self.selected_object is not None:
            self.scene.objects.remove(self.selected_object)
            self.objects.remove(self.selected_object)
            self.selected_object = None
            self.update_object_list()
            self.clear_properties()

    def update_object_list(self):
        self.object_listbox.delete(0, tk.END)
        for i, obj in enumerate(self.objects):
            self.object_listbox.insert(tk.END, f"Object {i+1}")

    def on_object_select(self, event):
        selection = self.object_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_object = self.objects[index]
            self.load_properties()

    def load_properties(self):
        if self.selected_object:
            pos = self.selected_object.position
            self.pos_x_var.set(pos[0])
            self.pos_y_var.set(pos[1])
            self.pos_z_var.set(pos[2])

            self.speed_var.set(self.selected_object.speed)

            color = self.selected_object.color
            self.color_r_var.set(color[0])
            self.color_g_var.set(color[1])
            self.color_b_var.set(color[2])

    def clear_properties(self):
        self.pos_x_var.set(0)
        self.pos_y_var.set(0)
        self.pos_z_var.set(0)
        self.speed_var.set(0)
        self.color_r_var.set(0)
        self.color_g_var.set(0)
        self.color_b_var.set(0)

    def apply_changes(self):
        if self.selected_object:
            self.selected_object.set_position(
                self.pos_x_var.get(),
                self.pos_y_var.get(),
                self.pos_z_var.get()
            )
            self.selected_object.speed = self.speed_var.get()
            self.selected_object.color = (
                self.color_r_var.get(),
                self.color_g_var.get(),
                self.color_b_var.get()
            )

    def preview_scene(self):
        if not self.objects:
            messagebox.showinfo("Preview", "No objects in scene to preview.")
            return

        # Create a new Toplevel window for preview
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Scene Preview")

        # Create a new Scene3D instance with the preview window as master
        preview_scene = Scene3D(width=800, height=600, title="Scene Preview", bg="black", master=preview_window)

        # Copy objects to the preview scene
        for obj in self.objects:
            preview_scene.add_object(obj)

        # Run the preview scene
        preview_scene.run()

    def save_scene(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            scene_data = {
                "objects": []
            }
            for obj in self.objects:
                obj_data = {
                    "type": "cube",  # For now, assume all are cubes
                    "position": obj.position.tolist(),
                    "speed": obj.speed,
                    "color": obj.color,
                    "size": 100  # Default size, could be improved
                }
                scene_data["objects"].append(obj_data)

            with open(file_path, 'w') as f:
                json.dump(scene_data, f, indent=4)
            messagebox.showinfo("Save", "Scene saved successfully!")

    def load_scene(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    scene_data = json.load(f)

                # Clear current scene
                self.scene.objects.clear()
                self.objects.clear()

                for obj_data in scene_data.get("objects", []):
                    if obj_data["type"] == "cube":
                        cube = create_cube(
                            size=obj_data.get("size", 100),
                            speed=obj_data["speed"],
                            position=tuple(obj_data["position"]),
                            color=tuple(obj_data["color"])
                        )
                        self.objects.append(cube)
                        self.scene.add_object(cube)

                self.update_object_list()
                messagebox.showinfo("Load", "Scene loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load scene: {str(e)}")

def run_editor():
    root = tk.Tk()
    editor = SceneEditor(root)
    root.mainloop()

if __name__ == "__main__":
    run_editor()
