#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Microscopy Image Z-Stack Projection Script

This script performs maximum or mean projections on microscopy images (TIFF format)
by automatically detecting the best-focused Z-slice and projecting a specified number of
slices around it.

Author: claudiasalatcanela
Created: Fri Jul 14 17:58:10 2023
Updated: [Current Date]
"""

import numpy as np
from tifffile import imsave, imread
import pandas as pd
import time
import warnings
from typing import Tuple, List, Dict, Optional
from pathlib import Path

# Suppress warnings
warnings.filterwarnings("ignore", message="In a future version")

class ImageProjector:
    """Class to handle image projection operations for microscopy data."""
    
    def __init__(self, folder: str, channels: List[str], projection_type: str = 'max', 
                 z_range: int = 1, output_dir: Optional[str] = None):
        """
        Initialize the ImageProjector.
        
        Args:
            folder: Path to the folder containing images
            channels: List of channel names to process
            projection_type: Type of projection ('max' or 'mean')
            z_range: Number of Z-slices above/below center for projection
            output_dir: Output directory (defaults to 'projection' in input folder)
        """
        self.folder = Path(folder)
        self.channels = channels
        self.projection_type = projection_type
        self.z_range = z_range
        self.output_dir = Path(output_dir) if output_dir else self.folder / 'projection'
        self.report_data = {}
        self.processed_count = 0
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
    def get_focused_z_slice(self, image: np.ndarray) -> Tuple[np.ndarray, int]:
        """
        Determine the most focused Z-slice by calculating standard deviation.
        Higher standard deviation indicates better focus.
        
        Args:
            image: 3D array (Z, Y, X)
            
        Returns:
            Tuple of (standard deviations, index of best focused slice)
        """
        # Calculate standard deviation for each Z-slice
        std_devs = image.std(axis=(1, 2))
        # Find the Z-slice with maximum standard deviation (best focus)
        best_z = std_devs.argmax()
        return std_devs, best_z
    
    def calculate_projection_range(self, best_z: int, total_z: int) -> Tuple[int, int, int]:
        """
        Calculate the Z-range for projection around the best focused slice.
        
        Args:
            best_z: Index of best focused Z-slice
            total_z: Total number of Z-slices
            
        Returns:
            Tuple of (start_index, stop_index, number_of_slices)
        """
        # Calculate range around best focused slice
        start = best_z - self.z_range
        stop = best_z + self.z_range + 1
        n_slices = 2 * self.z_range + 1
        
        # Handle edge cases (when best slice is near boundaries)
        if start < 0:
            start = 0
            stop = min(n_slices, total_z)
        elif stop > total_z:
            start = max(0, total_z - n_slices)
            stop = total_z
                
        return start, stop, n_slices
    
    def perform_projection(self, image_stack: np.ndarray) -> np.ndarray:
        """
        Perform projection on a Z-stack.
        
        Args:
            image_stack: 3D array (Z, Y, X)
            
        Returns:
            2D projected image
        """
        if self.projection_type == 'mean':
            return np.mean(image_stack, axis=0, dtype=np.uint16)
        elif self.projection_type == 'max':
            return np.max(image_stack, axis=0)
        else:
            raise ValueError(f"Unsupported projection type: {self.projection_type}")
    
    def process_tiff_file(self, file_path: Path) -> None:
        """Process a single TIFF file."""
        try:
            # Read the TIFF image
            img = imread(str(file_path))
            shape = img.shape
            
            # Check if image has enough dimensions (should be 4D: T, Z, Y, X)
            if len(shape) <= 3:
                print(f"Skipping {file_path.name}: insufficient dimensions")
                return
                
            self.processed_count += 1
            print(f"Processing TIFF: {file_path.name}")
            
            # Initialize output array for projected timepoints
            output_shape = (1, shape[2], shape[3])
            img_proj_tp = np.empty(output_shape, dtype=np.uint16)
            
            # Lists to store processing information for report
            timepoints, n_proj_z, proj_types, start_z, stop_z = [], [], [], [], []
            
            # Process each timepoint
            for t in range(shape[0]):
                # Extract single timepoint
                img_tp = img.take(t, axis=0)
                timepoints.append(t + 1)
                proj_types.append(self.projection_type)
                
                # Find best focused Z-slice
                _, best_z = self.get_focused_z_slice(img_tp)
                
                # Calculate which Z-slices to include in projection
                start, stop, n_slices = self.calculate_projection_range(best_z, shape[1])
                n_proj_z.append(n_slices)
                
                # Extract the Z-stack for projection
                indices = range(start, stop)
                start_z.append(indices[0] + 1)  # +1 for Fiji compatibility
                stop_z.append(indices[-1] + 1)
                
                img_z_stack = img_tp.take(indices, axis=0)
                img_proj = self.perform_projection(img_z_stack)
                
                # Add time dimension and concatenate with previous results
                img_proj = np.expand_dims(img_proj, axis=0)
                img_proj_tp = np.concatenate((img_proj_tp, img_proj), dtype=np.uint16)
            
            # Remove the initial empty array
            img_proj_tp = img_proj_tp[1:]
            
            # Save the projected image
            output_name = f"{file_path.stem}_{self.projection_type}proj.tif"
            output_path = self.output_dir / output_name
            imsave(str(output_path), img_proj_tp)
            
            # Store processing information for report
            self.report_data[file_path.stem] = {
                'Timepoint': timepoints,
                'Numb projected z': n_proj_z,
                'Type of proj': proj_types,
                'Start z': start_z,
                'Stop z': stop_z
            }
            
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
    
    def save_report(self) -> None:
        """Save processing report to Excel file."""
        if not self.report_data:
            print("No data to report")
            return
            
        report_path = self.output_dir / 'projection_report.xlsx'
        
        with pd.ExcelWriter(report_path) as writer:
            for image_name, report_data in self.report_data.items():
                df = pd.DataFrame(report_data)
                df.to_excel(writer, sheet_name=image_name)
        
        print(f"Report saved to: {report_path}")
    
    def run(self) -> None:
        """Run the projection process on all TIFF files in the folder."""
        start_time = time.time()
        
        print(f"Processing TIFF files in: {self.folder}")
        print(f"Channels: {self.channels}")
        print(f"Projection type: {self.projection_type}")
        print(f"Z-range: {self.z_range}")
        
        # Process all TIFF files in the folder
        for file_path in sorted(self.folder.iterdir()):
            if not file_path.is_file():
                continue
                
            # Check if file is TIFF and matches channel criteria
            if file_path.suffix.lower() == '.tif' and any(channel in file_path.name for channel in self.channels):
                self.process_tiff_file(file_path)
        
        # Save report
        self.save_report()
        
        # Print summary
        end_time = time.time()
        duration = (end_time - start_time) / 60
        print(f"\nProcessing complete!")
        print(f"Files processed: {self.processed_count}")
        print(f"Execution time: {duration:.2f} minutes")


def main():
    """Main function with user-defined parameters."""
    
    # USER-DEFINED PARAMETERS
    folder = '/Users/csalatca/Desktop/temporary_microscopyfiles/test_projections/test'
    channels = ['WL508']
    projection_type = 'max'  # 'max' or 'mean'
    z_range = 1  # Number of Z-slices above/below center
    
    # Create projector and run
    projector = ImageProjector(
        folder=folder,
        channels=channels,
        projection_type=projection_type,
        z_range=z_range
    )
    
    projector.run()


if __name__ == "__main__":
    main()            
