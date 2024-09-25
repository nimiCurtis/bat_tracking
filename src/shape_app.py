import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import json

class ShapeDrawerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shape Drawer")
        self.points = []
        self.shapes = []
        self.shape_count = 0

        self.shapes = {}

        self.canvas = None
        self.image = None
        self.img_display = None
        self.load_image()

    def load_image(self):
        """Load an image from a file and display it on the canvas."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
        if not file_path:
            return
        
        # Load the image using Pillow
        self.image = Image.open(file_path)
        self.img_display = ImageTk.PhotoImage(self.image)
        
        # Create the canvas with the image
        if self.canvas:
            self.canvas.destroy()
        self.canvas = tk.Canvas(self.root, width=self.img_display.width(), height=self.img_display.height())
        self.canvas.create_image(0, 0, image=self.img_display, anchor=tk.NW)
        self.canvas.pack()
        
        # Bind the mouse click event to draw shapes
        self.canvas.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        """Handles mouse clicks for shape drawing."""
        x, y = event.x, event.y
        self.points.append((x, y))
        
        # Display the point on the canvas
        self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")
        
        # If there are more than 1 points, allow closing the shape
        if len(self.points) > 1:
            self.canvas.create_line(self.points[-2], self.points[-1], fill="blue", width=2)

        # If right-click, close the shape and store it
        self.root.bind("<Button-3>", self.close_shape)

    def close_shape(self, event):
        """Close the current shape and store its vertices."""
        if len(self.points) > 2:
            self.shape_count += 1
            shape_name = f"shape{self.shape_count}"
            self.shapes[shape_name] = self.points.copy()

            # Draw the final line connecting last point to the first
            self.canvas.create_line(self.points[-1], self.points[0], fill="blue", width=2)
            self.points.clear()  # Reset points for new shape
            print(f"{shape_name} saved: {self.shapes[shape_name]}")
            self.save_shapes_to_json()

    def save_shapes_to_json(self):
        """Save all shapes to a JSON file."""
        with open("shapes.json", "w") as json_file:
            json.dump(self.shapes, json_file, indent=4)
        print("Shapes saved to shapes.json")

# Create the Tkinter application
root = tk.Tk()
app = ShapeDrawerApp(root)
root.mainloop()


