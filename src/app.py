import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import json
import sleap
import matplotlib.pyplot as plt 
from utils import SimulatedCamera
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils import SimulatedCamera
import numpy as np
from shapely.geometry import Point, Polygon
import csv

sleap.disable_preallocation()


class LabelBatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bat Actions Auto-Label Tool")
        # Bind the X button to the exit handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.main_page()

    def on_exit(self):
        """Handles the cleanup process when the window is closed."""
        # Ask the user to confirm exit
        if messagebox.askokcancel("Quit", "Do you want to quit? Any unsaved work will be lost."):
            try:
                # Perform any cleanup here
                print("Performing cleanup before exit...")
                
                if hasattr(self,"frame_labels"):
                    # If necessary, check if labeling was done and prompt user to save
                    if self.frame_labels and not self.dataset_labeled:
                        if messagebox.askyesno("Save Labels", "You have unsaved labels. Do you want to save them before exiting?"):
                            self.finish_labeling()

                # Close the application
                self.root.quit()  # Close the Tkinter window
                self.root.destroy()  # Destroy the root window to exit the app

            except Exception as e:
                print(f"Error during cleanup: {e}")
                messagebox.showerror("Error", f"An error occurred while exiting: {e}")

    
    def main_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        welcome_label = tk.Label(self.root, text="Hi, welcome to the bat actions auto-label tool!", font=("Arial", 14))
        welcome_label.pack(pady=20)

        create_labels_button = tk.Button(self.root, text="Create Labels", command=self.create_labels_page, font=("Arial", 12))
        create_labels_button.pack(pady=10)

        start_auto_label_button = tk.Button(self.root, text="Start Auto Label", command=self.start_auto_label, font=("Arial", 12))
        start_auto_label_button.pack(pady=10)

    def create_labels_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        page_title = tk.Label(self.root, text="Create or Edit Labels", font=("Arial", 14))
        page_title.pack(pady=20)

        new_labels_button = tk.Button(self.root, text="New Labels", command=self.new_labels_page, font=("Arial", 12))
        new_labels_button.pack(pady=10)

        edit_labels_button = tk.Button(self.root, text="Edit Labels", command=self.edit_labels, font=("Arial", 12))
        edit_labels_button.pack(pady=10)

        back_button = tk.Button(self.root, text="Back", command=self.main_page, font=("Arial", 12))
        back_button.pack(pady=10)

    def new_labels_page(self):
        # Set up new page for labeling
        for widget in self.root.winfo_children():
            widget.destroy()

        self.shapes = {}
        self.current_points = []

        # Add file upload button
        upload_button = tk.Button(self.root, text="Load .mp4 File", command=self.upload_video, font=("Arial", 12))
        upload_button.pack(pady=10)

        # Label name input field
        self.label_name_var = tk.StringVar()
        label_entry = tk.Entry(self.root, textvariable=self.label_name_var, font=("Arial", 12))
        label_entry.pack(pady=10)

        # Add label button
        add_label_button = tk.Button(self.root, text="Add Label", font=("Arial", 12), command=self.add_label)
        add_label_button.pack(pady=10)

        # Finish button
        finish_button = tk.Button(self.root, text="Finish", font=("Arial", 12), command=self.finish_create_labels)
        finish_button.pack(pady=10)

        # Add canvas at the bottom
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(pady=10)

    def upload_video(self):
        """Opens file dialog to upload an mp4 file and displays the first frame."""
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
        if not file_path:
            return
        
        # Capture the first frame from the video
        video = cv2.VideoCapture(file_path)
        ret, frame = video.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            self.img_display = ImageTk.PhotoImage(image)

            # Display the image on the canvas
            self.canvas.config(width=self.img_display.width(), height=self.img_display.height())
            self.canvas.create_image(0, 0, image=self.img_display, anchor=tk.NW)
            self.canvas.bind("<Button-1>", self.on_click)
            self.root.bind("<Button-3>", self.close_shape)
        else:
            messagebox.showerror("Error", "Failed to load the video.")

    def on_click(self, event):
        """Handles left-click for adding points to create shapes."""
        x, y = event.x, event.y
        self.current_points.append((x, y))
        self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")

        if len(self.current_points) > 1:
            self.canvas.create_line(self.current_points[-2], self.current_points[-1], fill="blue", width=2)

    def close_shape(self, event):
        """Handles right-click to close the shape by connecting the last point to the first."""
        if len(self.current_points) > 2:
            self.canvas.create_line(self.current_points[-1], self.current_points[0], fill="blue", width=2)

    def add_label(self):
        """Adds the current shape to the shapes dictionary after labeling."""
        label_name = self.label_name_var.get()

        if not label_name:
            messagebox.showwarning("Input Error", "Please enter a label name.")
            return

        if len(self.current_points) < 3:
            messagebox.showwarning("Shape Error", "A shape must have at least 3 points.")
            return

        self.shapes[label_name] = {"shape_points": self.current_points.copy()}
        self.current_points.clear()
        self.label_name_var.set("")
        print(f"Added label '{label_name}' with shape points: {self.shapes[label_name]}")

    def finish_create_labels(self):
        """Saves all shapes to a JSON file."""
        if not self.shapes:
            messagebox.showwarning("No Labels", "No labels have been added.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "w") as json_file:
                json.dump(self.shapes, json_file, indent=4)
            print("Shapes saved to", file_path)
            messagebox.showinfo("Save Complete", "Labels have been saved successfully.")

        # After saving, go back to the previous page
        self.create_labels_page()

    def edit_labels(self):
        print("Edit Labels button pressed")
        # Add functionality for editing labels here

    def start_auto_label(self):
        """Navigates to the page for starting auto-labeling."""
        for widget in self.root.winfo_children():
            widget.destroy()

        # Page title
        page_title = tk.Label(self.root, text="Auto Label Task", font=("Arial", 14))
        page_title.pack(pady=20)

        # Input for shape JSON config file
        config_label = tk.Label(self.root, text="Enter path to the shape JSON config file:", font=("Arial", 12))
        config_label.pack(pady=10)

        self.config_path_var = tk.StringVar()
        config_entry = tk.Entry(self.root, textvariable=self.config_path_var, width=50, font=("Arial", 12))
        config_entry.pack(pady=10)

        # Button for browsing the config file
        browse_button = tk.Button(self.root, text="Browse", command=self.browse_config_file, font=("Arial", 12))
        browse_button.pack(pady=10)

        # Button for New Video Auto Label
        new_video_button = tk.Button(self.root, text="New Video Auto Label", command=self.new_video_auto_label, font=("Arial", 12))
        new_video_button.pack(pady=10)

        # Button for Edit Video Labels
        edit_video_button = tk.Button(self.root, text="Edit Video Labels", command=self.edit_video_labels, font=("Arial", 12))
        edit_video_button.pack(pady=10)

        # Back button to go back to the main page
        back_button = tk.Button(self.root, text="Back", command=self.main_page, font=("Arial", 12))
        back_button.pack(pady=10)

    def browse_config_file(self):
        """Opens a file dialog to browse and select the JSON config file."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.config_path_var.set(file_path)
    
    def new_video_auto_label(self):
        """Navigates to the page for uploading a video and starting the auto-labeling."""
        for widget in self.root.winfo_children():
            widget.destroy()

        # Page title
        page_title = tk.Label(self.root, text="New Video Auto Label", font=("Arial", 14))
        page_title.pack(pady=20)

        # Button to upload video file
        upload_button = tk.Button(self.root, text="Load .mp4 File", command=self.upload_video_file, font=("Arial", 12))
        upload_button.pack(pady=10)

        # Display the selected file path
        self.video_path_var = tk.StringVar()
        video_path_label = tk.Entry(self.root, textvariable=self.video_path_var, width=50, font=("Arial", 12))
        video_path_label.pack(pady=10)
        
        # Button to upload model directories
        # Centroid
        upload_centroid_model = tk.Button(self.root, text="Load Predictor Centroid Model Dir", command=self.upload_centroid, font=("Arial", 12))
        upload_centroid_model.pack(pady=10)
        self.centroid_model_path_var = tk.StringVar()
        centroid_model_path_label = tk.Entry(self.root, textvariable=self.centroid_model_path_var, width=50, font=("Arial", 12))
        centroid_model_path_label.pack(pady=10)

        # Display the selected file path
        upload_centered_model = tk.Button(self.root, text="Load Predictor Centered Model Dir", command=self.upload_centered, font=("Arial", 12))
        upload_centered_model.pack(pady=10)
        self.centered_model_path_var = tk.StringVar()
        centered_model_path_label = tk.Entry(self.root, textvariable=self.centered_model_path_var, width=50, font=("Arial", 12))
        centered_model_path_label.pack(pady=10)
        
        # Button to start the auto-labeling process
        start_button = tk.Button(self.root, text="Start", command=self.start_auto_labeling, font=("Arial", 12))
        start_button.pack(pady=10)

        # Back button to go back to the previous page
        back_button = tk.Button(self.root, text="Back", command=self.start_auto_label, font=("Arial", 12))
        back_button.pack(pady=10)

    def upload_video_file(self):
        """Opens a file dialog to upload an mp4 file."""
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
        if file_path:
            self.video_path_var.set(file_path)

    def upload_centroid(self):
        """Opens a file dialog to upload an mp4 file."""
        file_path = filedialog.askdirectory()
        if file_path:
            self.centroid_model_path_var.set(file_path)
            
    def upload_centered(self):
        """Opens a file dialog to upload an mp4 file."""
        file_path = filedialog.askdirectory()
        if file_path:
            self.centered_model_path_var.set(file_path)

    def start_auto_labeling(self):
        """Loads the JSON config and moves to a new page with auto-label and shape buttons."""
        video_path = self.video_path_var.get()
        config_path = self.config_path_var.get()
        centroid_model_path = self.centroid_model_path_var.get()
        centered_model_path = self.centered_model_path_var.get()

        if not video_path or not config_path or not centroid_model_path or not centered_model_path:
            messagebox.showwarning("Input Error", "Please provide the video file, models, and config file path.")
            return
        
        # Load the video and models
        try:
            video = sleap.load_video(video_path)
            predictor = sleap.load_model([centroid_model_path, centered_model_path], batch_size=1)

            # Initialize the simulated camera with pre-loaded frames
            self.camera = SimulatedCamera(video[:])
            self.current_frame_index = 0
            self.total_frames = len(video)

            # Load shapes config
            with open(config_path, 'r') as json_file:
                self.shapes_config = json.load(json_file)

            # Move to the next page
            self.auto_label_page(predictor)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load video or models: {e}")

    def initialize_dataset(self):
        """Initializes the dataset container and maps frames to labels."""
        self.frame_labels = {}  # This will map each frame index to its corresponding label
        self.dataset_labeled = False
        # Initialize polygons from the shapes config
        self.roi_polygons = {}  # Maps shape names to Polygon objects
        for shape_name, shape_data in self.shapes_config.items():
            shape_points = shape_data["shape_points"]
            poly = Polygon(shape_points)
            self.roi_polygons[shape_name] = poly

    def auto_label_page(self,predictor):
        """Displays the auto-label button and buttons for each shape in the JSON config."""
        for widget in self.root.winfo_children():
            widget.destroy()

        
        # Initialize the dataset container
        self.initialize_dataset()
        
        # Page title
        page_title = tk.Label(self.root, text="Auto Labeling Options", font=("Arial", 14))
        page_title.pack(pady=20)

        # Auto-label button
        labels_title = tk.Label(self.root, text="Auto labeling:", font=("Arial", 12))
        labels_title.pack(pady=10)
        
        auto_label_button = tk.Button(self.root, text="Auto Label", command=lambda: self.auto_label_task(predictor=predictor), font=("Arial", 12))
        auto_label_button.pack(pady=10)

        # Label for "Labels" section
        labels_title = tk.Label(self.root, text="Manual labeling:", font=("Arial", 12))
        labels_title.pack(pady=10)

        
        # Button for "Explore"
        explore_button = tk.Button(self.root, text="Explore", command=lambda: self.label_shape("Explore"), font=("Arial", 12))
        explore_button.pack(pady=5)

        # Button for "None"
        none_button = tk.Button(self.root, text="None", command=lambda: self.label_shape("None"), font=("Arial", 12))
        none_button.pack(pady=5)
        
        
        # Dynamically create buttons for each shape in the JSON config
        for shape_name in self.shapes_config:
            shape_button = tk.Button(self.root, text=shape_name, command=lambda name=shape_name: self.label_shape(name), font=("Arial", 12))
            shape_button.pack(pady=5)

        # Finish button
        finish_button = tk.Button(self.root, text="Finish", command=self.finish_labeling, font=("Arial", 12))
        finish_button.pack(pady=10)
        
                # Frame display
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()

        # Frame number display
        self.frame_label = tk.Label(self.root, text=f"Frame {self.current_frame_index + 1}", font=("Arial", 12))
        self.frame_label.pack(pady=10)

        
        self.label_display = tk.Label(self.root, text="", font=("Arial", 12))
        self.label_display.pack(pady=10)
    
        # Capture keyboard events for navigation
        self.root.bind("<Right>", lambda event: self.show_next_frame(predictor))
        self.root.bind("<Left>", lambda event: self.show_previous_frame(predictor))

        # Show the first frame
        self.show_frame(predictor)

    def show_frame(self, predictor):
        """Displays the current frame and inference results."""
        # Get the current frame from the camera
        frame = self.camera.frames[self.current_frame_index]

        # Predict the skeletons on the frame
        frame_predictions = predictor.inference_model.predict_on_batch(np.expand_dims(frame, axis=0))
        peaks_np = np.array(frame_predictions["instance_peaks"][0])

        # Process and display the peaks
        for peak in peaks_np:
            if len(peak) >= 1:
                x_head, y_head = peak[0][0], peak[0][1]

                # Only draw circle if the head coordinates are not NaN
                if not (np.isnan(x_head) or np.isnan(y_head)):
                    x_head, y_head = int(x_head), int(y_head)
                    cv2.circle(frame, (x_head, y_head), 5, (0, 255, 0), -1)  # Green circle for the head point

                # Check if there is a second peak (tail)
                if len(peak) >= 2:
                    x_tail, y_tail = peak[1][0], peak[1][1]

                    # Only draw circle if the head coordinates are not NaN
                    if not (np.isnan(x_tail) or np.isnan(y_tail)):
                        x_tail, y_tail = int(x_tail), int(y_tail)
                        cv2.circle(frame, (x_tail, y_tail), 5, (0, 255, 0), -1)  # Green circle for the tail point
                    
                    # Only draw circle and line if both head and tail coordinates are not NaN
                    if not (np.isnan(x_tail) or np.isnan(y_tail)) and not (np.isnan(x_head) or np.isnan(y_head)):
                        # Draw a red line connecting the two points (head and tail)
                        cv2.line(frame, (x_head, y_head), (x_tail, y_tail), (0, 0, 255), 2)  # Red line

        # Display the ROI shapes from shapes_config
        for shape_name, shape_data in self.shapes_config.items():
            shape_points = shape_data["shape_points"]

            # Convert shape points to integers and draw the polygon or line
            points = np.array(shape_points, dtype=np.int32)
            cv2.polylines(frame, [points], isClosed=True, color=(255, 0, 0), thickness=2)  # Blue lines for ROI

        
        if self.dataset_labeled:
            # Get the label for the current frame
            current_label = self.frame_labels.get(self.current_frame_index, "None")

            # Display the label
            self.label_display.config(text=f"Label: {current_label}")

        # Convert BGR frame to RGB and display it
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.ax.clear()
        self.ax.imshow(frame_rgb)
        self.ax.axis('off')
        self.canvas.draw()

        # Update frame label
        self.frame_label.config(text=f"Frame {self.current_frame_index + 1}")


    def show_next_frame(self, predictor):
        """Moves to the next frame."""
        if self.current_frame_index < self.total_frames - 1:
            self.current_frame_index += 1
            self.show_frame(predictor)
        else:
            print("Already at the last frame.")

    def show_previous_frame(self, predictor):
        """Moves to the previous frame."""
        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            self.show_frame(predictor)
        else:
            print("Already at the first frame.")

    def finish_labeling(self):
        """Handles the finish action after auto-labeling is complete."""
        print("Finished labeling process")

        # Step 1: Save the frame_labels container to a .csv file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, mode='w', newline='') as csv_file:
                    fieldnames = ['Frame', 'Label']
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                    writer.writeheader()
                    for frame, label in self.frame_labels.items():
                        writer.writerow({'Frame': frame, 'Label': label})

                print(f"Labels saved successfully to {file_path}")
                messagebox.showinfo("Save Complete", f"Labels saved successfully to {file_path}")

            except Exception as e:
                print(f"Failed to save labels to CSV: {e}")
                messagebox.showerror("Save Error", f"Failed to save labels: {e}")

        self.start_auto_label()
        
    def auto_label_task(self,predictor):
        """Automatically labels all frames based on the prediction and ROIs."""

        # Run auto-labeling in the background (no display)
        for frame_idx in range(self.total_frames):
            frame = self.camera.frames[frame_idx]

            # Get predictions for the current frame
            frame_predictions = predictor.inference_model.predict_on_batch(np.expand_dims(frame, axis=0))
            peaks_np = np.array(frame_predictions["instance_peaks"][0])

            # Check if there are predictions
            if len(peaks_np) > 0:
                # Loop through the peaks (predicted points)
                labeled = False
                for peak in peaks_np:
                    # Check head point first
                    if len(peak) >= 1:
                        x_head, y_head = peak[0][0], peak[0][1]
                        # Only draw circle if the head coordinates are not NaN
                        if not (np.isnan(x_head) or np.isnan(y_head)):
                            point_head = Point(x_head, y_head)

                            # Check if head point is inside any ROI
                            for shape_name, polygon in self.roi_polygons.items():
                                if polygon.contains(point_head):
                                    self.frame_labels[frame_idx] = shape_name  # Label with shape name
                                    labeled = True
                                    break  # No need to check other shapes if we have a match

                    # If labeled, we don't need to check tail or other shapes
                    if labeled:
                        break

                    # Check tail point if head didn't match
                    if len(peak) >= 2:
                        x_tail, y_tail = peak[1][0], peak[1][1]
                        if not (np.isnan(x_tail) or np.isnan(y_tail)):

                            point_tail = Point(x_tail, y_tail)
                            for shape_name, polygon in self.roi_polygons.items():
                                if polygon.contains(point_tail):
                                    self.frame_labels[frame_idx] = shape_name  # Label with shape name
                                    labeled = True
                                    break

                # If no point was inside any ROI, label it as "Explore"
                if not labeled:
                    self.frame_labels[frame_idx] = "Explore"
            else:
                # If there is no prediction for the current frame, label it as "None"
                self.frame_labels[frame_idx] = "None"

        # # After auto-labeling, display the frames with labels interactively
        # self.show_labeled_frames()
        self.dataset_labeled = True
        
        # Get the label for the current frame
        current_label = self.frame_labels.get(self.current_frame_index, "None")

        # Display the label
        self.label_display.config(text=f"Label: {current_label}")
        
    def label_shape(self, shape_name):
        """Handles the task for manually labeling the current frame with a specific shape."""

        # Update the label of the current frame with the selected shape name
        self.frame_labels[self.current_frame_index] = shape_name

        # Update the label display to reflect the change
        self.label_display.config(text=f"Label: {shape_name}")

        # Optional: Log or print the change for debugging purposes
        print(f"Frame {self.current_frame_index} manually labeled as '{shape_name}'")

    def edit_video_labels(self):
        """Placeholder function for editing video labels."""
        config_path = self.config_path_var.get()
        if not config_path:
            messagebox.showwarning("Input Error", "Please provide a valid config file path.")
            return
        print(f"Editing Video Labels with config: {config_path}")
        # Add functionality for editing labels in the video

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelBatApp(root)
    root.mainloop()
