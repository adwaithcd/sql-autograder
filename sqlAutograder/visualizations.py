"""
Visualization module for grading analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Optional


class GradingVisualizer:
    """Creates visualizations for grading analysis."""
    
    def __init__(self, csv_path: str):
        """
        Initialize visualizer.
        
        Args:
            csv_path: Path to the results CSV file
        """
        self.csv_path = csv_path
        self.df: pd.DataFrame = None
        self.valid_df: pd.DataFrame = None
    
    def load_data(self) -> bool:
        """
        Load and filter data.
        
        Returns:
            bool: True if successful
        """
        try:
            self.df = pd.read_csv(self.csv_path)
            
            # Filter to valid results
            self.valid_df = self.df[self.df['q4_1_llm_score'] >= 0].copy()
            
            # Drop rows with missing grader scores
            required_cols = [
                'q4_1_grader_score', 'q4_2_grader_score', 
                'q4_3_grader_score', 'q4_4_grader_score', 
                'q4_5_grader_score'
            ]
            self.valid_df = self.valid_df.dropna(subset=required_cols)
            
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def assign_grader(self, index: int) -> str:
        """Assign grader based on index."""
        if 0 <= index < 55:
            return 'G1'
        elif 55 <= index < 110:
            return 'G2'
        elif 110 <= index < 165:
            return 'G3'
        elif 165 <= index < 220:
            return 'G4'
        elif 220 <= index < 275:
            return 'G5'
        else:
            return 'G6'
    
    def plot_overall_distribution(self, output_path: str = "output/overall_distribution.png"):
        """
        Create side-by-side histogram comparing overall LLM vs Human grade distribution.
        
        Args:
            output_path: Path to save the figure
        """
        if not self.load_data():
            return False
        
        # Create side-by-side subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Get total scores
        human_scores = self.valid_df['total_grader_score']
        llm_scores = self.valid_df['total_llm_score']
        
        # Create bins (0-50 in steps of 5)
        bins = np.arange(0, 55, 5)
        
        # Plot Human histogram
        counts_human, _, _ = ax1.hist(human_scores, bins=bins, 
                                       color='#FF6B6B', edgecolor='black', alpha=0.8)
        ax1.set_xlabel('Total Score (out of 50)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Number of Students', fontsize=12, fontweight='bold')
        ax1.set_title('Human Grader Distribution', fontsize=14, fontweight='bold', pad=15)
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for i, count in enumerate(counts_human):
            if count > 0:
                ax1.text(bins[i] + 2.5, count, str(int(count)), 
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Add statistics
        stats_text_human = (
            f"N = {len(human_scores)}\n"
            f"Mean = {human_scores.mean():.1f}\n"
            f"Std Dev = {human_scores.std():.1f}"
        )
        ax1.text(0.02, 0.98, stats_text_human, transform=ax1.transAxes,
                fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='#FFE5E5', alpha=0.8))
        
        # Plot LLM histogram
        counts_llm, _, _ = ax2.hist(llm_scores, bins=bins, 
                                     color='#4ECDC4', edgecolor='black', alpha=0.8)
        ax2.set_xlabel('Total Score (out of 50)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Number of Students', fontsize=12, fontweight='bold')
        ax2.set_title('LLM Grader Distribution', fontsize=14, fontweight='bold', pad=15)
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for i, count in enumerate(counts_llm):
            if count > 0:
                ax2.text(bins[i] + 2.5, count, str(int(count)), 
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Add statistics
        stats_text_llm = (
            f"N = {len(llm_scores)}\n"
            f"Mean = {llm_scores.mean():.1f}\n"
            f"Std Dev = {llm_scores.std():.1f}\n"
            f"Diff = {(llm_scores.mean() - human_scores.mean()):+.1f}"
        )
        ax2.text(0.02, 0.98, stats_text_llm, transform=ax2.transAxes,
                fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='#E5F9F7', alpha=0.8))
        
        # Match y-axis limits
        max_count = max(counts_human.max(), counts_llm.max())
        ax1.set_ylim(0, max_count * 1.15)
        ax2.set_ylim(0, max_count * 1.15)
        
        plt.suptitle('Grade Distribution: Human vs LLM Grader', 
                    fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        # Create output directory if needed
        Path(output_path).parent.mkdir(exist_ok=True)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Overall distribution saved to: {output_path}")
        return True
    
    def plot_per_grader_distributions(self, output_dir: str = "output"):
        """
        Create separate side-by-side histograms for each grader (G1-G6).
        
        Args:
            output_dir: Directory to save the figures
        """
        if not self.load_data():
            return False
        
        # Assign graders
        self.valid_df['grader'] = self.valid_df.index.map(self.assign_grader)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        graders = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6']
        student_ranges = ["1-55", "56-110", "111-165", "166-220", "221-275", "276-330"]
        
        for grader, student_range in zip(graders, student_ranges):
            grader_data = self.valid_df[self.valid_df['grader'] == grader]
            
            if len(grader_data) == 0:
                continue
            
            # Create side-by-side subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            
            # Get scores
            human_scores = grader_data['total_grader_score']
            llm_scores = grader_data['total_llm_score']
            
            # Create bins
            bins = np.arange(0, 55, 5)
            
            # Plot Human histogram
            counts_human, _, _ = ax1.hist(human_scores, bins=bins, 
                                           color='#FF6B6B', edgecolor='black', alpha=0.8)
            ax1.set_xlabel('Total Score (out of 50)', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Number of Students', fontsize=12, fontweight='bold')
            ax1.set_title('Human Grader Distribution', fontsize=14, fontweight='bold', pad=15)
            ax1.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Add value labels on bars
            for i, count in enumerate(counts_human):
                if count > 0:
                    ax1.text(bins[i] + 2.5, count, str(int(count)), 
                            ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            # Add statistics
            stats_text_human = (
                f"N = {len(human_scores)}\n"
                f"Mean = {human_scores.mean():.1f}\n"
                f"Std Dev = {human_scores.std():.1f}"
            )
            ax1.text(0.02, 0.98, stats_text_human, transform=ax1.transAxes,
                    fontsize=11, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='#FFE5E5', alpha=0.8))
            
            # Plot LLM histogram
            counts_llm, _, _ = ax2.hist(llm_scores, bins=bins, 
                                         color='#4ECDC4', edgecolor='black', alpha=0.8)
            ax2.set_xlabel('Total Score (out of 50)', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Number of Students', fontsize=12, fontweight='bold')
            ax2.set_title('LLM Grader Distribution', fontsize=14, fontweight='bold', pad=15)
            ax2.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Add value labels on bars
            for i, count in enumerate(counts_llm):
                if count > 0:
                    ax2.text(bins[i] + 2.5, count, str(int(count)), 
                            ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            # Add statistics
            stats_text_llm = (
                f"N = {len(llm_scores)}\n"
                f"Mean = {llm_scores.mean():.1f}\n"
                f"Std Dev = {llm_scores.std():.1f}\n"
                f"Diff = {(llm_scores.mean() - human_scores.mean()):+.1f}"
            )
            ax2.text(0.02, 0.98, stats_text_llm, transform=ax2.transAxes,
                    fontsize=11, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='#E5F9F7', alpha=0.8))
            
            # Match y-axis limits
            max_count = max(counts_human.max(), counts_llm.max())
            ax1.set_ylim(0, max_count * 1.15)
            ax2.set_ylim(0, max_count * 1.15)
            
            plt.suptitle(f'{grader} Grade Distribution: Human vs LLM (Students {student_range})', 
                        fontsize=16, fontweight='bold', y=0.98)
            plt.tight_layout()
            
            output_file = output_path / f"{grader}_distribution.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✓ {grader} distribution saved to: {output_file}")
        
        return True
    
    def plot_all_graders_grid(self, output_path: str = "output/all_graders_grid.png"):
        """
        Create a 6x2 grid showing all 6 graders (Human | LLM side by side).
        
        Args:
            output_path: Path to save the figure
        """
        if not self.load_data():
            return False
        
        # Assign graders
        self.valid_df['grader'] = self.valid_df.index.map(self.assign_grader)
        
        # Create figure with 6x2 subplots (6 graders, 2 columns: Human | LLM)
        fig, axes = plt.subplots(6, 2, figsize=(16, 24))
        
        graders = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6']
        student_ranges = ["1-55", "56-110", "111-165", "166-220", "221-275", "276-330"]
        
        for idx, (grader, student_range) in enumerate(zip(graders, student_ranges)):
            ax_human = axes[idx, 0]
            ax_llm = axes[idx, 1]
            
            grader_data = self.valid_df[self.valid_df['grader'] == grader]
            
            if len(grader_data) == 0:
                ax_human.text(0.5, 0.5, 'No Data', ha='center', va='center')
                ax_llm.text(0.5, 0.5, 'No Data', ha='center', va='center')
                ax_human.set_title(f'{grader} Human (Students {student_range})')
                ax_llm.set_title(f'{grader} LLM')
                continue
            
            # Get scores
            human_scores = grader_data['total_grader_score']
            llm_scores = grader_data['total_llm_score']
            
            # Create bins
            bins = np.arange(0, 55, 5)
            
            # Plot Human histogram
            counts_human, _, _ = ax_human.hist(human_scores, bins=bins, 
                                                color='#FF6B6B', edgecolor='black', alpha=0.8)
            ax_human.set_ylabel('# Students', fontsize=10)
            if idx == 5:  # Only bottom row
                ax_human.set_xlabel('Score', fontsize=10)
            ax_human.set_title(f'{grader} Human (Students {student_range})\n'
                              f'N={len(human_scores)}, μ={human_scores.mean():.1f}, σ={human_scores.std():.1f}',
                              fontsize=11, fontweight='bold')
            ax_human.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Plot LLM histogram
            counts_llm, _, _ = ax_llm.hist(llm_scores, bins=bins, 
                                            color='#4ECDC4', edgecolor='black', alpha=0.8)
            ax_llm.set_ylabel('# Students', fontsize=10)
            if idx == 5:  # Only bottom row
                ax_llm.set_xlabel('Score', fontsize=10)
            ax_llm.set_title(f'{grader} LLM\n'
                            f'N={len(llm_scores)}, μ={llm_scores.mean():.1f}, σ={llm_scores.std():.1f}, '
                            f'Diff={llm_scores.mean() - human_scores.mean():+.1f}',
                            fontsize=11, fontweight='bold')
            ax_llm.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Match y-axis limits
            max_count = max(counts_human.max(), counts_llm.max())
            ax_human.set_ylim(0, max_count * 1.15)
            ax_llm.set_ylim(0, max_count * 1.15)
        
        plt.suptitle('Grade Distribution by Grader: Human vs LLM', 
                    fontsize=18, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        # Create output directory if needed
        Path(output_path).parent.mkdir(exist_ok=True)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ All graders grid saved to: {output_path}")
        return True