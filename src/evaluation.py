import sleap
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os

class SleapEvaluator:
    """
    A class to encapsulate the SLEAP evaluation process, including metric computation and visualization.
    """
    def __init__(self, centroid_model_path, centered_instance_model_path, project_path):
        """
        Initializes the SleapEvaluator with paths to the centroid model, centered instance model, and project.

        Args:
            centroid_model_path (str): Path to the SLEAP centroid model.
            centered_instance_model_path (str): Path to the centered instance model.
            project_path (str): Path to the .slp file containing ground truth labels.
        """
        self.centroid_model_path = centroid_model_path
        self.centered_instance_model_path = centered_instance_model_path
        self.project_path = project_path
        self.centroid_predictor = None
        self.centered_instance_predictor = None
        self.labels_gt = None
        self.metrics_centroid = None
        self.metrics_centered = None

    def load_model_and_data(self):
        """
        Loads the SLEAP models (centroid and centered instance) and ground truth labels.
        """
        self.centroid_predictor = sleap.load_model(self.centroid_model_path)
        self.centered_instance_predictor = sleap.load_model(self.centered_instance_model_path)
        self.labels_gt = sleap.load_file(self.project_path)
        print("Models and data loaded successfully.")

    def evaluate(self):
        """
        Computes evaluation metrics between the ground truth and predicted labels for both models.
        """
        labels_pr_centroid = self.centroid_predictor.predict(self.labels_gt)
        self.metrics_centroid = sleap.nn.evals.evaluate(self.labels_gt, labels_pr_centroid)

        labels_pr_centered = self.centered_instance_predictor.predict(self.labels_gt)
        self.metrics_centered = sleap.nn.evals.evaluate(self.labels_gt, labels_pr_centered)

        print("Evaluation completed for both models.")

    def display_metrics(self, metrics, model_name):
        """
        Displays key evaluation metrics for a given model.

        Args:
            metrics (dict): Evaluation metrics.
            model_name (str): Name of the model being evaluated.
        """
        print(f"\n--- {model_name} Metrics ---")
        print("Error distance (50%):", metrics["dist.p50"])
        print("Error distance (90%):", metrics["dist.p90"])
        print("Error distance (95%):", metrics["dist.p95"])
        print("mAP:", metrics["oks_voc.mAP"])
        print("mAR:", metrics["oks_voc.mAR"])

    def plot_error_distribution(self, metrics, model_name):
        """
        Plots the localization error distribution for a given model.

        Args:
            metrics (dict): Evaluation metrics.
            model_name (str): Name of the model being evaluated.
        """
        plt.figure(figsize=(6, 3), dpi=150, facecolor="w")
        sns.histplot(metrics["dist.dists"].flatten(), binrange=(0, 20), kde=True, kde_kws={"clip": (0, 20)}, stat="probability")
        plt.xlabel(f"Localization error (px) - {model_name}")
        plt.show()

    def plot_keypoint_similarity(self, metrics, model_name):
        """
        Plots the Object Keypoint Similarity (OKS) distribution for a given model.

        Args:
            metrics (dict): Evaluation metrics.
            model_name (str): Name of the model being evaluated.
        """
        plt.figure(figsize=(6, 3), dpi=150, facecolor="w")
        sns.histplot(metrics["oks_voc.match_scores"].flatten(), binrange=(0, 1), kde=True, kde_kws={"clip": (0, 1)}, stat="probability")
        plt.xlabel(f"Object Keypoint Similarity - {model_name}")
        plt.show()

    def plot_precision_recall(self, metrics, model_name):
        """
        Plots the Precision-Recall curve for various OKS thresholds for a given model.

        Args:
            metrics (dict): Evaluation metrics.
            model_name (str): Name of the model being evaluated.
        """
        plt.figure(figsize=(4, 4), dpi=150, facecolor="w")
        for precision, thresh in zip(metrics["oks_voc.precisions"][::2], metrics["oks_voc.match_score_thresholds"][::2]):
            plt.plot(metrics["oks_voc.recall_thresholds"], precision, "-", label=f"OKS @ {thresh:.2f}")
        plt.xlabel(f"Recall - {model_name}")
        plt.ylabel("Precision")
        plt.legend(loc="lower left")
        plt.show()

    def plot_training_log(self, model_dir):
        """
        Searches for a training_log.csv file in the model directory and plots it.

        Args:
            model_dir (str): Path to the directory containing the training log.
        """
        training_log_path = os.path.join(model_dir, "training_log.csv")
        if os.path.exists(training_log_path):
            print(f"Found training log: {training_log_path}")
            # Load and plot the training log
            training_log = pd.read_csv(training_log_path)
            plt.figure(figsize=(10, 6))
            plt.plot(training_log["epoch"], training_log["train_loss"], "o-", label="Training Loss")
            plt.plot(training_log["epoch"], training_log["val_loss"], "x-", label="Validation Loss")
            plt.xlabel("Epoch")
            plt.ylabel("Loss")
            plt.title(f"Training and Validation Loss - {model_dir}")
            plt.legend()
            plt.show()
        else:
            print(f"No training log found in {model_dir}")

    def evaluate_and_visualize(self):
        """
        Runs the full evaluation pipeline for both models, including metric computation and visualization.
        """
        self.load_model_and_data()
        self.evaluate()

        # Display and visualize metrics for the centroid model
        self.display_metrics(self.metrics_centroid, "Centroid Model")
        self.plot_error_distribution(self.metrics_centroid, "Centroid Model")
        self.plot_keypoint_similarity(self.metrics_centroid, "Centroid Model")
        self.plot_precision_recall(self.metrics_centroid, "Centroid Model")
        self.plot_training_log(os.path.dirname(self.centroid_model_path))

        # Display and visualize metrics for the centered instance model
        self.display_metrics(self.metrics_centered, "Centered Instance Model")
        self.plot_error_distribution(self.metrics_centered, "Centered Instance Model")
        self.plot_keypoint_similarity(self.metrics_centered, "Centered Instance Model")
        self.plot_precision_recall(self.metrics_centered, "Centered Instance Model")
        self.plot_training_log(os.path.dirname(self.centered_instance_model_path))


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Evaluate two SLEAP models (centroid and centered instance) on a given project.")
    parser.add_argument("--centroid_model_path", required=True, help="Path to the centroid SLEAP model.")
    parser.add_argument("--centered_instance_model_path", required=True, help="Path to the centered instance model.")
    parser.add_argument("--project_path", required=True, help="Path to the .slp file with ground truth labels.")
    args = parser.parse_args()

    # Initialize evaluator
    evaluator = SleapEvaluator(args.centroid_model_path, args.centered_instance_model_path, args.project_path)

    # Run the evaluation and visualization
    evaluator.evaluate_and_visualize()
