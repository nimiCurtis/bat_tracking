import sleap
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

class SleapEvaluator:
    """
    A class to encapsulate the SLEAP evaluation process, including metric computation and visualization.
    """
    def __init__(self, model_path, project_path):
        """
        Initializes the SleapEvaluator with paths to the model and project.

        Args:
            model_path (str): Path to the SLEAP model.
            project_path (str): Path to the .slp file containing ground truth labels.
        """
        self.model_path = model_path
        self.project_path = project_path
        self.predictor = None
        self.labels_gt = None
        self.labels_pr = None
        self.metrics = None

    def load_model_and_data(self):
        """
        Loads the SLEAP model and ground truth labels.
        """
        self.predictor = sleap.load_model(self.model_path)
        self.labels_gt = sleap.load_file(self.project_path)
        self.labels_pr = self.predictor.predict(self.labels_gt)
        print("Model and data loaded successfully.")

    def evaluate(self):
        """
        Computes evaluation metrics between the ground truth and predicted labels.
        """
        self.metrics = sleap.nn.evals.evaluate(self.labels_gt, self.labels_pr)
        print("Evaluation completed.")
    
    def display_metrics(self):
        """
        Displays key evaluation metrics.
        """
        print("Error distance (50%):", self.metrics["dist.p50"])
        print("Error distance (90%):", self.metrics["dist.p90"])
        print("Error distance (95%):", self.metrics["dist.p95"])
        print("mAP:", self.metrics["oks_voc.mAP"])
        print("mAR:", self.metrics["oks_voc.mAR"])
    
    def plot_error_distribution(self):
        """
        Plots the localization error distribution.
        """
        plt.figure(figsize=(6, 3), dpi=150, facecolor="w")
        sns.histplot(self.metrics["dist.dists"].flatten(), binrange=(0, 20), kde=True, kde_kws={"clip": (0, 20)}, stat="probability")
        plt.xlabel("Localization error (px)")
        plt.show()

    def plot_keypoint_similarity(self):
        """
        Plots the Object Keypoint Similarity (OKS) distribution.
        """
        plt.figure(figsize=(6, 3), dpi=150, facecolor="w")
        sns.histplot(self.metrics["oks_voc.match_scores"].flatten(), binrange=(0, 1), kde=True, kde_kws={"clip": (0, 1)}, stat="probability")
        plt.xlabel("Object Keypoint Similarity")
        plt.show()

    def plot_precision_recall(self):
        """
        Plots the Precision-Recall curve for various OKS thresholds.
        """
        plt.figure(figsize=(4, 4), dpi=150, facecolor="w")
        for precision, thresh in zip(self.metrics["oks_voc.precisions"][::2], self.metrics["oks_voc.match_score_thresholds"][::2]):
            plt.plot(self.metrics["oks_voc.recall_thresholds"], precision, "-", label=f"OKS @ {thresh:.2f}")
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.legend(loc="lower left")
        plt.show()

    def evaluate_and_visualize(self):
        """
        Runs the full evaluation pipeline: metric computation and visualization.
        """
        self.load_model_and_data()
        self.evaluate()
        self.display_metrics()
        self.plot_error_distribution()
        self.plot_keypoint_similarity()
        self.plot_precision_recall()


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Evaluate a SLEAP model on a given project.")
    parser.add_argument("--model_path", required=True, help="Path to the SLEAP model.")
    parser.add_argument("--project_path", required=True, help="Path to the .slp file with ground truth labels.")
    args = parser.parse_args()

    # Initialize evaluator
    evaluator = SleapEvaluator(args.model_path, args.project_path)

    # Run the evaluation and visualization
    evaluator.evaluate_and_visualize()
