#!/usr/bin/env python3
"""
Batch processing example for multiple Fluke thermal images.
"""

import os
import glob
from fluke_thermal_reader import read_is2
import numpy as np

# Optional dependencies
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Note: pandas not available. Install with: pip install pandas")

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Note: matplotlib not available. Install with: pip install matplotlib")

def process_thermal_files(directory_path):
    """Process all .is2 files in a directory."""
    
    # Find all .is2 files
    pattern = os.path.join(directory_path, "*.is2")
    files = glob.glob(pattern)
    
    if not files:
        print(f"No .is2 files found in {directory_path}")
        return
    
    print(f"Found {len(files)} thermal image files")
    
    # Process each file
    results = []
    
    for file_path in files:
        try:
            print(f"\nProcessing: {os.path.basename(file_path)}")
            
            # Load thermal data
            data = read_is2(file_path)
            temperatures = data['data']
            
            # Calculate statistics
            stats = {
                'filename': os.path.basename(file_path),
                'camera_model': data['CameraModel'],
                'camera_serial': data['CameraSerial'],
                'image_size': f"{data['size'][0]}x{data['size'][1]}",
                'capture_date': data['CaptureDateTime'],
                'min_temp': temperatures.min(),
                'max_temp': temperatures.max(),
                'mean_temp': temperatures.mean(),
                'std_temp': temperatures.std(),
                'emissivity': data['Emissivity'],
                'background_temp': data['BackgroundTemp']
            }
            
            results.append(stats)
            print(f"  Temperature range: {stats['min_temp']:.1f}°C - {stats['max_temp']:.1f}°C")
            print(f"  Average: {stats['mean_temp']:.1f}°C")
            
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
            continue
    
    if not results:
        print("No files were successfully processed.")
        return
    
    # Display summary
    print(f"\n=== BATCH PROCESSING SUMMARY ===")
    print(f"Successfully processed: {len(results)} files")
    
    # Calculate overall statistics
    min_temps = [r['min_temp'] for r in results]
    max_temps = [r['max_temp'] for r in results]
    mean_temps = [r['mean_temp'] for r in results]
    camera_models = list(set([r['camera_model'] for r in results]))
    
    print(f"Camera models: {camera_models}")
    print(f"Overall temperature range: {min(min_temps):.1f}°C - {max(max_temps):.1f}°C")
    print(f"Overall average temperature: {np.mean(mean_temps):.1f}°C")
    
    # Save results to CSV (if pandas available)
    if HAS_PANDAS:
        df = pd.DataFrame(results)
        output_file = "thermal_analysis_results.csv"
        df.to_csv(output_file, index=False)
        print(f"\nResults saved to: {output_file}")
        
        # Create summary plots
        create_summary_plots(df)
        return df
    else:
        print("\nNote: Install pandas to save results to CSV and create plots:")
        print("pip install pandas matplotlib")
        return results

def create_summary_plots(df):
    """Create summary plots for the batch processing results."""
    
    if not HAS_MATPLOTLIB:
        print("Matplotlib not available. Install with: pip install matplotlib")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Temperature range plot
    axes[0, 0].scatter(df['mean_temp'], df['max_temp'] - df['min_temp'], alpha=0.7)
    axes[0, 0].set_xlabel('Mean Temperature (°C)')
    axes[0, 0].set_ylabel('Temperature Range (°C)')
    axes[0, 0].set_title('Temperature Range vs Mean Temperature')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Temperature distribution
    axes[0, 1].hist(df['mean_temp'], bins=20, alpha=0.7, edgecolor='black')
    axes[0, 1].set_xlabel('Mean Temperature (°C)')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Distribution of Mean Temperatures')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Camera model comparison
    camera_stats = df.groupby('camera_model').agg({
        'mean_temp': ['mean', 'std'],
        'max_temp': 'max',
        'min_temp': 'min'
    }).round(1)
    
    camera_models = df['camera_model'].unique()
    x_pos = range(len(camera_models))
    
    axes[1, 0].bar(x_pos, [df[df['camera_model'] == model]['mean_temp'].mean() 
                           for model in camera_models], alpha=0.7)
    axes[1, 0].set_xlabel('Camera Model')
    axes[1, 0].set_ylabel('Mean Temperature (°C)')
    axes[1, 0].set_title('Average Temperature by Camera Model')
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(camera_models, rotation=45)
    axes[1, 0].grid(True, alpha=0.3)
    
    # Temperature vs Emissivity
    axes[1, 1].scatter(df['emissivity'], df['mean_temp'], alpha=0.7)
    axes[1, 1].set_xlabel('Emissivity')
    axes[1, 1].set_ylabel('Mean Temperature (°C)')
    axes[1, 1].set_title('Temperature vs Emissivity')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('thermal_batch_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"Summary plots saved to: thermal_batch_analysis.png")

def main():
    """Main function for batch processing."""
    
    # Replace with your directory containing .is2 files
    directory_path = "thermal_images"
    
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} not found.")
        print("Please create the directory and add your .is2 files, or modify the path.")
        return
    
    # Process all thermal files
    results_df = process_thermal_files(directory_path)
    
    if results_df is not None:
        print(f"\n=== DETAILED RESULTS ===")
        if HAS_PANDAS:
            print(results_df.to_string(index=False))
        else:
            # Print results without pandas
            for i, result in enumerate(results_df, 1):
                print(f"\n{i}. {result['filename']}")
                print(f"   Camera: {result['camera_model']} (Serial: {result['camera_serial']})")
                print(f"   Temperature: {result['min_temp']:.1f}°C - {result['max_temp']:.1f}°C (avg: {result['mean_temp']:.1f}°C)")
                print(f"   Emissivity: {result['emissivity']}, Background: {result['background_temp']:.1f}°C")

if __name__ == "__main__":
    main()