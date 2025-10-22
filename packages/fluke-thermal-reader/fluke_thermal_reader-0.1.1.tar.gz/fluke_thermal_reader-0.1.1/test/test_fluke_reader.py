#!/usr/bin/env python3
"""
Test script for FlukeReader.
"""

import sys
import os
from pathlib import Path

# Add project path to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import fluke_reader
    print("OK FlukeReader imported successfully!")
    print(f"Version: {fluke_reader.__version__}")
    print(f"Author: {fluke_reader.__author__}")
    
    # Test the fluke_load function
    print("\nTesting fluke_load function...")
    
    # Search for .is2 files in current directory
    is2_files = list(Path(".").glob("*.is2"))
    is3_files = list(Path(".").glob("*.is3"))
    
    if is2_files:
        print(f"Found {len(is2_files)} .is2 files:")
        for file in is2_files:
            print(f"  - {file}")
        
        # Test the first .is2 file
        test_file = is2_files[0]
        print(f"\nTesting file: {test_file}")
        
        try:
            data = fluke_reader.fluke_load(test_file)
            print("OK File loaded successfully!")
            
            # Show data information
            print(f"Data information:")
            print(f"  - File name: {data.get('FileName', 'N/A')}")
            print(f"  - Dimensions: {data.get('size', 'N/A')}")
            print(f"  - Emissivity: {data.get('emissivity', 'N/A')}")
            print(f"  - Transmission: {data.get('transmission', 'N/A')}")
            print(f"  - Background temperature: {data.get('backgroundtemperature', 'N/A')}°C")
            print(f"  - Camera manufacturer: {data.get('CameraManufacturer', 'N/A')}")
            print(f"  - Camera model: {data.get('CameraModel', 'N/A')}")
            print(f"  - Camera serial: {data.get('CameraSerial', 'N/A')}")
            
            # Analyze temperature data
            if 'data' in data:
                temp_data = data['data']
                print(f"\nTemperature analysis:")
                print(f"  - Data shape: {temp_data.shape}")
                if temp_data.size > 0:
                    print(f"  - Min temperature: {temp_data.min():.2f}°C")
                    print(f"  - Max temperature: {temp_data.max():.2f}°C")
                    print(f"  - Average temperature: {temp_data.mean():.2f}°C")
                    print(f"  - Temperature std: {temp_data.std():.2f}°C")
                else:
                    print("  - No temperature data available (empty array)")
            
            # Check if images are available
            if 'thumbnail' in data and data['thumbnail'] is not None:
                print(f"  - Thumbnail available: {data['thumbnail'].shape}")
            if 'photo' in data and data['photo'] is not None:
                print(f"  - Visible photo available: {data['photo'].shape}")
                
        except Exception as e:
            print(f"ERROR loading file: {e}")
            import traceback
            traceback.print_exc()
    
    elif is3_files:
        print(f"Found {len(is3_files)} .is3 files:")
        for file in is3_files:
            print(f"  - {file}")
        print("WARNING: .is3 support not yet fully implemented")
    
    else:
        print("WARNING: No .is2 or .is3 files found in current directory")
        print("TIP: To test, copy a .is2 file to the current directory")
    
    # Test the FlukeReader class
    print(f"\nTesting FlukeReader class...")
    reader = fluke_reader.FlukeReader()
    print(f"OK FlukeReader created successfully!")
    print(f"Supported formats: {reader.get_supported_formats()}")
    
    print(f"\nAll tests completed!")

except ImportError as e:
    print(f"ERROR importing FlukeReader: {e}")
    print("TIP: Make sure you're in the project directory")
    sys.exit(1)
except Exception as e:
    print(f"ERROR Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
