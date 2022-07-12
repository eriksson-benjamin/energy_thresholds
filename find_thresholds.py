# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 08:54:32 2022

@author: bener807
"""

'''
Calculates the energy thresholds for S1/S2 detectors.

Note
----
Data is stored locally on PC and on backup of PC.
'''

import sys
sys.path.insert(0, 'C:/python/definitions/')
import useful_defs as udfs
import definitions_heimdall as dfs
import numpy as np
import matplotlib.pyplot as plt
udfs.set_nes_plot_style()

def merge_data(shot_numbers, t0, t1):
    # Merge data from shots to single array
    energies = dfs.get_dictionaries('merged')
    for shot_number in shot_numbers:
        # Import energies
        erg = udfs.unpickle(f'data/coincident_energies/{shot_number}.pickle')
        
        for key, item in erg.items():
            energies[key] = np.append(energies[key], item)

    return energies

def plot_spectrum(detector, energies, bin_centres):
    plt.figure(detector)
    plt.title(detector.replace('_', '-'), loc='left')
    plt.plot(bin_centres, events, 'k.', markersize=2)
    plt.errorbar(bin_centres, events, yerr=np.sqrt(events), color='k', 
                 linestyle='None')
    plt.xlabel('light yield $(MeV_{ee})$')
    plt.ylabel('counts')
    
def plot_polynomial(x_dat, y_dat, deg, detector, fit_range):
    # Select fitting range
    fr = ((x_dat > fit_range[0]) & (x_dat < fit_range[1]))
    x = x_dat[fr]
    y = y_dat[fr]
    
    # Fit polynomial
    p = np.polyfit(x, y, deg)
    
    # Draw polynomial
    p1d = np.poly1d(p)
    ux = np.arange(fit_range[0], fit_range[1], 0.0001)
    uy = p1d(ux)
    plt.figure(detector)
    plt.plot(ux, uy, 'r-')

    return ux, uy

def get_fit_range(detector):
    # Detector specific fit ranges
    lines = np.loadtxt('data/fit_ranges.txt', dtype='str')
    ranges = {l[0]:[float(l[1]), float(l[2])] for l in lines}

    return ranges[detector]

def get_bin_edges(detector):
    # Detector specific binning
    lines = np.loadtxt('data/bin_edges.txt', dtype='str')
    edges = {l[0]:[float(l[1]), float(l[2]), float(l[3])] for l in lines}
    e = edges[detector]

    return np.arange(e[0], e[1], e[2])

def calculate_threshold(x_dat, y_dat, fraction):
    '''
    Return the x position at a given fraction of peak maximum.
    '''
    
    # Maximum index
    arg_max = np.argmax(y_dat)
    
    # Select events up to maximum
    x = x_dat[:arg_max+1]
    y = y_dat[:arg_max+1]
    
    # Half maximum
    arg_half = np.argmin(abs(y-np.max(y)*fraction))
   
    return x[arg_half]

def plot_threshold(detector, threshold):
    plt.figure(detector)
    plt.axvline(threshold, color='k', linestyle='--')
    plt.title(f'$E_{{thr}}$ = {threshold:.3f} MeV$_{{ee}}$', loc='right')
    
if __name__ == '__main__':
    # Analysed shots
    shot_numbers = [100054, 100055, 100056, 100057, 100058, 100059, 100060,
                    100061, 100062, 100063, 100064, 100068, 100069, 100070, 
                    100072, 100073, 100074, 100075]
    
    # Store thresholds in txt file
    with open('thresholds.txt', 'w') as handle:
        handle.write('# Detector Threshold (MeVee)\n')
    
    # Merge all data for given shot numbers
    energies = merge_data(shot_numbers, 20, 80)
    
    detectors = dfs.get_dictionaries('merged')
    for detector in detectors.keys():
        print(detector)
        bin_edges = get_bin_edges(detector)
        bin_centres = bin_edges[1:]-np.diff(bin_edges)/2
        
        # Histogram the energy spectrum
        events, _ = np.histogram(energies[detector], bin_edges)
    
        # Plot light yield spectrum
        plot_spectrum(detector, events, bin_centres)
    
        # Fit polnomial to to peak    
        fit_range = get_fit_range(detector)
        ux, uy = plot_polynomial(bin_centres, events, 15, detector, fit_range)
        
        # Find threshold from half maximum
        threshold = calculate_threshold(ux, uy, 0.1)
        print(f'{detector}: {threshold:.4f}')
        
        # Plot and save to file
        plot_threshold(detector, threshold)
    
        with open('thresholds.txt', 'a') as handle:
            handle.write(f'{detector} {threshold:.4f}\n')







