import cv2
import numpy as np
from utils import ShapesVisualizer

# Load a NumPy image (e.g., using OpenCV)
image_path = "16.jpg"
np_image = cv2.imread(image_path)  # This returns the image as a NumPy array

# Path to the JSON file containing shapes
shapes_json = "shapes.json"

# Create an instance of the visualizer
visualizer = ShapesVisualizer(shapes_json)

# Draw shapes on the image
image_with_shapes = visualizer.plot_shapes(np_image)

# Show the image with the shapes
cv2.imshow('Image with Shapes', image_with_shapes)

# Wait for a key press and close the image window
cv2.waitKey(0)
cv2.destroyAllWindows()

# Optionally, save the result
cv2.imwrite('output_with_shapes.png', image_with_shapes)
