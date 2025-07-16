#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script compares the overlap between two masks (reference and segmentation)
using the Adjusted Rand Index (ARI) score.
"""

import os
from sklearn.metrics.cluster import adjusted_rand_score as ari
from tifffile import imread
import pandas as pd
import sys

# Paths to mask directories
path_ref_masks = '/Users/csalatca/Desktop/temporary_microscopyfiles/fawzi_mpm_model/20250604/test_ARI/images/curated_vSM'
path_seg_masks = '/Users/csalatca/Desktop/temporary_microscopyfiles/fawzi_mpm_model/20250604/test_ARI/images/modelB_mean3'

def get_tif_filenames(directory):
    """
    Get all .tif files in the specified directory.
    Args:
        directory (str): Path to directory.
    Returns:
        list: Sorted list of .tif filenames.
    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")
    filenames = [f for f in os.listdir(directory) if f.endswith('.tif')]
    return sorted(filenames)

def find_matching_seg_file(ref_name, seg_dir):
    """
    Find the segmentation file matching the reference name prefix.
    Args:
        ref_name (str): Reference filename.
        seg_dir (str): Segmentation mask directory.
    Returns:
        str or None: Full path to matching segmentation file, or None if not found.
    """
    parts = ref_name.split('_')
    if len(parts) < 2:
        return None
    smp_prefix = f"{parts[0]}_{parts[1]}"
    for seg_name in os.listdir(seg_dir):
        if seg_name.endswith('.tif') and seg_name.startswith(smp_prefix):
            return os.path.join(seg_dir, seg_name)
    return None

def load_mask(filepath):
    """
    Load a mask image from file.
    Args:
        filepath (str): Path to the mask file.
    Returns:
        ndarray: Loaded mask.
    Raises:
        Exception: If the file cannot be read.
    """
    try:
        return imread(filepath)
    except Exception as e:
        raise IOError(f"Failed to read mask file: {filepath}. Error: {e}")

def collect_mask_pairs(ref_dir, seg_dir, ref_filenames):
    """
    Import and match mask pairs from reference and segmentation directories.
    Args:
        ref_dir (str): Reference mask directory.
        seg_dir (str): Segmentation mask directory.
        ref_filenames (list): List of reference mask filenames.
    Returns:
        list: List of (ref_mask, seg_mask, sample_name) tuples.
    Raises:
        ValueError: If no matching pairs are found.
    """
    pairs = []
    for ref_name in ref_filenames:
        ref_path = os.path.join(ref_dir, ref_name)
        seg_path = find_matching_seg_file(ref_name, seg_dir)
        sample_id = '_'.join(ref_name.split('_')[:2])
        if not os.path.exists(ref_path):
            print(f"[Warning] Reference file missing: {ref_path}")
            continue
        if not seg_path or not os.path.exists(seg_path):
            print(f"[Warning] No matching segmentation file for: {sample_id}")
            continue
        try:
            ref_mask = load_mask(ref_path)
            seg_mask = load_mask(seg_path)
        except Exception as e:
            print(f"[Error] Could not load masks for {sample_id}: {e}")
            continue
        if ref_mask.shape != seg_mask.shape:
            print(f"[Error] Shape mismatch for {sample_id}: ref {ref_mask.shape}, seg {seg_mask.shape}")
            continue
        print(f"[Info] Found matching pair for {sample_id}")
        pairs.append((ref_mask, seg_mask, sample_id))
    if not pairs:
        raise ValueError("No valid matching mask pairs were found!")
    print(f"\n[Info] Total valid matching pairs found: {len(pairs)}")
    return pairs

def calculate_ari_for_pairs(mask_pairs, output_dir):
    """
    Calculate ARI for each mask pair and store results in a DataFrame and Excel file.
    Args:
        mask_pairs (list): List of (ref_mask, seg_mask, sample_name) tuples.
        output_dir (str): Directory to save the results Excel file.
    Returns:
        pd.DataFrame: DataFrame with ARI results.
    Raises:
        Exception: If saving the results fails.
    """
    results = []
    for ref_mask, seg_mask, sample_id in mask_pairs:
        try:
            score = ari(ref_mask.ravel(), seg_mask.ravel())
            print(f"[Info] {sample_id}: ARI = {score:.4f}")
            results.append({'Sample_name': sample_id, 'ARI_value': score})
        except Exception as e:
            print(f"[Error] Failed to compute ARI for {sample_id}: {e}")
    df = pd.DataFrame(results)
    output_path = os.path.join(output_dir, 'ARI_results.xlsx')
    try:
        df.to_excel(output_path, index=False)
        print(f"\n[Info] Results saved to {output_path}")
    except Exception as e:
        print(f"[Error] Failed to save results to Excel: {e}")
        raise
    return df

def main():
    try:
        ref_filenames = get_tif_filenames(path_ref_masks)
        if not ref_filenames:
            print(f"[Error] No .tif files found in reference directory: {path_ref_masks}")
            sys.exit(1)
        mask_pairs = collect_mask_pairs(path_ref_masks, path_seg_masks, ref_filenames)
        print("[Info] Successfully loaded all valid mask pairs.")
        results_df = calculate_ari_for_pairs(mask_pairs, path_seg_masks)
        print("\n[Info] Final results:")
        print(results_df)
    except Exception as e:
        print(f"[Fatal Error] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

