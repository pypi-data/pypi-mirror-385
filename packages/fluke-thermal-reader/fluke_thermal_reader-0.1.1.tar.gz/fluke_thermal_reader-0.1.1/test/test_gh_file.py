#!/usr/bin/env python3
"""
Test script for GHtempe2_2429.IS2 file
"""

import os
import sys
from fluke_reader.parsers import IS2Parser

def test_gh_file():
    """Test the GHtempe2_2429.IS2 file"""
    print("Testing GHtempe2_2429.IS2 file...")
    
    # Check if file exists
    is2_file = "GHtempe2_2429.IS2"
    if not os.path.exists(is2_file):
        print(f"Error: File {is2_file} not found!")
        return
    
    try:
        # Parse the file
        parser = IS2Parser()
        result = parser.parse(is2_file)
        
        print(f"\n=== PARSING RESULTS ===")
        print(f"Camera Model: {result.get('CameraModel', 'Unknown')}")
        print(f"Camera Serial: {result.get('CameraSerial', 'Unknown')}")
        print(f"Image Size: {result.get('size', 'Unknown')}")
        print(f"IR Width: {result.get('IRWidth', 'Unknown')}")
        print(f"IR Height: {result.get('IRHeight', 'Unknown')}")
        print(f"Temperature Range: {result.get('minTemp', 'Unknown')}°C - {result.get('maxTemp', 'Unknown')}°C")
        print(f"Background Temperature: {result.get('backgroundtemperature', 'Unknown')}°C")
        print(f"Emissivity: {result.get('emissivity', 'Unknown')}")
        print(f"Transmission: {result.get('transmission', 'Unknown')}")
        
        # Check thermal data
        if 'data' in result and len(result['data']) > 0:
            thermal_data = result['data']
            print(f"\n=== THERMAL DATA ===")
            print(f"Data shape: {thermal_data.shape}")
            print(f"Data type: {thermal_data.dtype}")
            print(f"Min temperature: {thermal_data.min():.2f}°C")
            print(f"Max temperature: {thermal_data.max():.2f}°C")
            print(f"Mean temperature: {thermal_data.mean():.2f}°C")
            print(f"Valid pixels: {(thermal_data > 0).sum()}/{thermal_data.size}")
            
            # Check for any shift issues
            print(f"\n=== SHIFT ANALYSIS ===")
            print(f"First row first 10 pixels: {thermal_data[0, :10]}")
            print(f"First row last 10 pixels: {thermal_data[0, -10:]}")
            print(f"Middle row first 10 pixels: {thermal_data[thermal_data.shape[0]//2, :10]}")
            print(f"Middle row last 10 pixels: {thermal_data[thermal_data.shape[0]//2, -10:]}")
            
        else:
            print("\n=== ERROR ===")
            print("No thermal data found!")
            
    except Exception as e:
        print(f"Error parsing file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gh_file()
