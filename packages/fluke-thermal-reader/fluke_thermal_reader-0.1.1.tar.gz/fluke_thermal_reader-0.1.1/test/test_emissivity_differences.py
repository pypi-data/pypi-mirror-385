#!/usr/bin/env python3
"""
Test per verificare se le differenze nell'emissivity causano le piccole differenze
"""

import numpy as np
import matplotlib.pyplot as plt
from fluke_reader import fluke_load

def load_fluke_txt_data(filename):
    """Load temperature data from Fluke exported txt file."""
    for encoding in ['utf-8', 'utf-16', 'latin-1', 'cp1252']:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                lines = f.readlines()
            break
        except UnicodeDecodeError:
            continue
    
    # Find data start
    data_start = 0
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped and line_stripped[0].isdigit() and '\t' in line_stripped:
            parts = line_stripped.split('\t')
            if len(parts) > 100:
                if len(parts) > 1:
                    try:
                        second_val = float(parts[1])
                        if '.' in parts[1]:
                            data_start = i
                            break
                    except ValueError:
                        continue
    
    # Extract data
    temp_data = []
    for i, line in enumerate(lines[data_start:]):
        if line.strip():
            values = line.strip().split('\t')[1:]
            row_data = []
            for val in values:
                try:
                    row_data.append(float(val))
                except ValueError:
                    break
            if row_data and len(row_data) >= 240:
                temp_data.append(row_data)
    
    return np.array(temp_data)

def test_emissivity_sensitivity():
    """Testa la sensibilità alle differenze di emissivity"""
    
    print("=== TEST SENSIBILITÀ EMISSIVITY ===\n")
    
    # Test CBH file
    print("1. TEST CBH_450s_1277.IS2")
    print("-" * 50)
    
    try:
        our_data = fluke_load("CBH_450s_1277.IS2")
        our_temps = our_data['data']
        real_data = load_fluke_txt_data("CBH_450s_1277.txt")
        
        print(f"Emissivity nel JSON: {our_data.get('Emissivity', 'N/A')}")
        print(f"Background nel JSON: {our_data.get('BackgroundTemp', 'N/A')}°C")
        
        if our_temps.shape == real_data.shape:
            diff = our_temps - real_data
            
            print(f"\nDifferenze attuali:")
            print(f"  Media: {diff.mean():.3f}°C")
            print(f"  Deviazione standard: {diff.std():.3f}°C")
            
            # Test diverse emissivity
            emissivity_values = [0.949, 0.9499, 0.94999, 0.95, 0.9501, 0.951]
            
            print(f"\nTest diverse emissivity:")
            for emiss in emissivity_values:
                # Simula il calcolo con emissivity diversa
                # La formula è: temp_corrected = (temp_raw - (2 - transmission - emissivity) * background) / (transmission * emissivity)
                # Assumiamo transmission = 1.0 e background = 22.0
                transmission = 1.0
                background = 22.0
                
                # Calcola la differenza teorica
                # Se la temperatura originale è T, la nuova temperatura sarà:
                # T_new = (T_raw - (2 - 1 - emissivity) * background) / (1 * emissivity)
                # T_new = (T_raw - (1 - emissivity) * background) / emissivity
                
                # Per stimare l'effetto, usiamo la differenza relativa
                # Se T_old = (T_raw - (1 - emiss_old) * background) / emiss_old
                # e T_new = (T_raw - (1 - emiss_new) * background) / emiss_new
                
                # La differenza sarà approssimativamente:
                # delta_T ≈ T * (emiss_new - emiss_old) / emiss_old
                
                # Usa la media delle temperature per stimare l'effetto
                mean_temp = our_temps.mean()
                theoretical_diff = mean_temp * (emiss - 0.94999) / 0.94999
                
                print(f"  Emissivity {emiss:.5f}: differenza teorica ≈ {theoretical_diff:.3f}°C")
            
            # Test con valori specifici
            print(f"\nTest con valori specifici:")
            
            # Valori che potrebbero essere usati da Fluke
            test_emissivities = [
                (0.94999, "IRImageInfo"),
                (0.95, "JSON"),
                (0.949, "Valore arrotondato"),
                (0.9501, "Valore leggermente diverso")
            ]
            
            for emiss, label in test_emissivities:
                # Calcola la differenza teorica per ogni pixel
                theoretical_diff = our_temps * (emiss - 0.94999) / 0.94999
                
                print(f"  {label} ({emiss:.5f}):")
                print(f"    Differenza media teorica: {theoretical_diff.mean():.3f}°C")
                print(f"    Differenza std teorica: {theoretical_diff.std():.3f}°C")
                print(f"    Range differenza: {theoretical_diff.min():.3f}°C - {theoretical_diff.max():.3f}°C")
            
            # Confronta con le differenze reali
            print(f"\nConfronto con differenze reali:")
            print(f"  Differenza reale media: {diff.mean():.3f}°C")
            print(f"  Differenza reale std: {diff.std():.3f}°C")
            
            # Cerca la migliore corrispondenza
            best_match = None
            best_diff = float('inf')
            
            for emiss, label in test_emissivities:
                theoretical_diff = our_temps * (emiss - 0.94999) / 0.94999
                diff_error = abs(theoretical_diff.mean() - diff.mean())
                
                print(f"  {label}: errore = {diff_error:.3f}°C")
                
                if diff_error < best_diff:
                    best_diff = diff_error
                    best_match = (emiss, label)
            
            print(f"\nMigliore corrispondenza: {best_match[1]} ({best_match[0]:.5f}) con errore {best_diff:.3f}°C")
            
    except Exception as e:
        print(f"Error with CBH file: {e}")
    
    print("\n" + "="*80 + "\n")
    
    # Test GH file
    print("2. TEST GHtempe2_2429.IS2")
    print("-" * 50)
    
    try:
        our_data = fluke_load("GHtempe2_2429.IS2")
        our_temps = our_data['data']
        real_data = load_fluke_txt_data("GHtempe2_2429.txt")
        
        print(f"Emissivity nel JSON: {our_data.get('Emissivity', 'N/A')}")
        print(f"Background nel JSON: {our_data.get('BackgroundTemp', 'N/A')}°C")
        
        if our_temps.shape == real_data.shape:
            diff = our_temps - real_data
            
            print(f"\nDifferenze attuali:")
            print(f"  Media: {diff.mean():.3f}°C")
            print(f"  Deviazione standard: {diff.std():.3f}°C")
            
            # Test con valori specifici
            test_emissivities = [
                (0.94999, "IRImageInfo"),
                (0.95, "JSON"),
                (0.949, "Valore arrotondato"),
                (0.9501, "Valore leggermente diverso")
            ]
            
            print(f"\nTest con valori specifici:")
            for emiss, label in test_emissivities:
                theoretical_diff = our_temps * (emiss - 0.94999) / 0.94999
                
                print(f"  {label} ({emiss:.5f}):")
                print(f"    Differenza media teorica: {theoretical_diff.mean():.3f}°C")
                print(f"    Differenza std teorica: {theoretical_diff.std():.3f}°C")
                print(f"    Range differenza: {theoretical_diff.min():.3f}°C - {theoretical_diff.max():.3f}°C")
            
            # Confronta con le differenze reali
            print(f"\nConfronto con differenze reali:")
            print(f"  Differenza reale media: {diff.mean():.3f}°C")
            print(f"  Differenza reale std: {diff.std():.3f}°C")
            
            # Cerca la migliore corrispondenza
            best_match = None
            best_diff = float('inf')
            
            for emiss, label in test_emissivities:
                theoretical_diff = our_temps * (emiss - 0.94999) / 0.94999
                diff_error = abs(theoretical_diff.mean() - diff.mean())
                
                print(f"  {label}: errore = {diff_error:.3f}°C")
                
                if diff_error < best_diff:
                    best_diff = diff_error
                    best_match = (emiss, label)
            
            print(f"\nMigliore corrispondenza: {best_match[1]} ({best_match[0]:.5f}) con errore {best_diff:.3f}°C")
            
    except Exception as e:
        print(f"Error with GH file: {e}")
    
    print("\n" + "="*80 + "\n")
    
    # Conclusioni
    print("3. CONCLUSIONI SULL'EMISSIVITY")
    print("-" * 50)
    
    print("Le differenze nell'emissivity potrebbero spiegare le piccole differenze:")
    print("")
    print("1. **IRImageInfo vs JSON**:")
    print("   - IRImageInfo: 0.94999")
    print("   - JSON: 0.95")
    print("   - Differenza: 0.00001")
    print("")
    print("2. **Effetto sulla temperatura**:")
    print("   - La formula è: T = (T_raw - (1 - emissivity) * background) / emissivity")
    print("   - Piccole differenze in emissivity causano piccole differenze in temperatura")
    print("   - L'effetto è proporzionale alla temperatura")
    print("")
    print("3. **Possibili cause**:")
    print("   - Fluke potrebbe usare emissivity leggermente diversa")
    print("   - Arrotondamenti diversi")
    print("   - Precisione numerica diversa")
    print("")
    print("4. **Raccomandazioni**:")
    print("   - Usa IRImageInfo invece di JSON per emissivity")
    print("   - Verifica se Fluke usa valori leggermente diversi")
    print("   - Le differenze sono comunque minime e accettabili")

if __name__ == "__main__":
    test_emissivity_sensitivity()
