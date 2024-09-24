import json
import cv2
import numpy as np

class ShapesVisualizer:
    def __init__(self, shapes_json):
        """Initializes the visualizer with a shapes JSON file."""
        self.shapes_json = shapes_json
        self.shapes = self.load_shapes()

    def load_shapes(self):
        """Loads the shapes from the JSON file."""
        try:
            with open(self.shapes_json, "r") as f:
                shapes = json.load(f)
        except Exception as e:
            print(f"Error loading shapes JSON: {e}")
            return None
        return shapes

    def plot_shapes(self, np_image):
        """
        Plots the shapes on a NumPy image and returns the modified image.

        :param np_image: Input image in NumPy array format.
        :return: Modified image with shapes drawn on it.
        """
        if self.shapes is None:
            print("No shapes to draw.")
            return np_image
        
        # Make sure we work on a copy of the image so the original isn't modified
        image_with_shapes = np_image.copy()

        # Draw each shape
        for shape_name, points in self.shapes.items():
            for i in range(1,len(points)):
                
                # Convert points to integer tuples
                pt1 = tuple(map(int, points[i-1]))
                pt2 = tuple(map(int, points[i]))
                
                # Draw the line connecting the two points
                cv2.line(image_with_shapes, pt1, pt2, (0, 0, 255), thickness=2)  # Red color line
                cv2.line(image_with_shapes, pt2, pt1, (0, 0, 255), thickness=2)  # Closing the shape

            # Convert points to integer tuples
            pt1 = tuple(map(int, points[0]))
            pt2 = tuple(map(int, points[-1]))
                
            # Draw the line connecting the two points
            cv2.line(image_with_shapes, pt1, pt2, (0, 0, 255), thickness=2)  # Red color line
            cv2.line(image_with_shapes, pt2, pt1, (0, 0, 255), thickness=2)  # Closing the shape
            
            print(f"Drew {shape_name} with points: {points}")
            
        
        return image_with_shapes
