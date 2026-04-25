#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: plot_map.py

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

def ensure_dir(directory):
    """Ensure directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📁 Created folder: {directory}")

def plot_map(traj_file='map_data.txt', map_file='my_map.txt', output_dir='map_results'):
    """
    Read odometry trajectory and red line map points, generate map image
    """
    
    # Create output folder
    ensure_dir(output_dir)
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    plt.figure(figsize=(12, 10))
    
    # 1. Read and plot robot trajectory
    if not os.path.exists(traj_file):
        print(f"❌ File not found: {traj_file}")
        return None, None
    
    traj = np.loadtxt(traj_file, delimiter=',')
    plt.plot(traj[:,0], traj[:,1], 'b-', linewidth=2, label='Trajectory', alpha=0.7)
    plt.scatter(traj[0,0], traj[0,1], c='green', s=150, marker='o', 
               edgecolors='darkgreen', linewidth=2, label='Start', zorder=5)
    plt.scatter(traj[-1,0], traj[-1,1], c='red', s=150, marker='s', 
               edgecolors='darkred', linewidth=2, label='End', zorder=5)
    
    print(f"✅ Trajectory: {len(traj)} points")
    print(f"   Start: ({traj[0,0]:.3f}, {traj[0,1]:.3f})")
    print(f"   End: ({traj[-1,0]:.3f}, {traj[-1,1]:.3f})")
    total_dist = np.sum(np.sqrt(np.diff(traj[:,0])**2 + np.diff(traj[:,1])**2))
    print(f"   Total distance: {total_dist:.3f} m")
    
    # 2. Read and plot red line map points
    map_point_count = 0
    if os.path.exists(map_file):
        points = np.loadtxt(map_file, delimiter=',')
        map_point_count = len(points)
        plt.scatter(points[:,0], points[:,1], c='red', s=8, alpha=0.6, 
                   label=f'Map Points ({map_point_count})', marker='.')
        
        print(f"✅ Map points: {map_point_count}")
        print(f"   X range: [{points[:,0].min():.3f}, {points[:,0].max():.3f}]")
        print(f"   Y range: [{points[:,1].min():.3f}, {points[:,1].max():.3f}]")
    
    # 3. Set plot properties
    plt.xlabel('X (m)', fontsize=12)
    plt.ylabel('Y (m)', fontsize=12)
    plt.title(f'Mapping Result\nTotal Distance: {total_dist:.2f}m | Map Points: {map_point_count}', 
              fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.tight_layout()
    
    # 4. Save images
    output_png = os.path.join(output_dir, f'map_{timestamp}.png')
    output_pdf = os.path.join(output_dir, f'map_{timestamp}.pdf')
    
    plt.savefig(output_png, dpi=150, bbox_inches='tight')
    plt.savefig(output_pdf, bbox_inches='tight')
    plt.close()
    
    print(f"\n📸 Map saved:")
    print(f"   PNG: {output_png}")
    print(f"   PDF: {output_pdf}")
    
    # Save latest version (overwrite)
    latest_png = os.path.join(output_dir, 'latest_map.png')
    latest_pdf = os.path.join(output_dir, 'latest_map.pdf')
    
    plt.figure(figsize=(12, 10))
    plt.plot(traj[:,0], traj[:,1], 'b-', linewidth=2, alpha=0.7)
    plt.scatter(traj[0,0], traj[0,1], c='green', s=150, marker='o', edgecolors='darkgreen', linewidth=2)
    plt.scatter(traj[-1,0], traj[-1,1], c='red', s=150, marker='s', edgecolors='darkred', linewidth=2)
    if os.path.exists(map_file):
        points = np.loadtxt(map_file, delimiter=',')
        plt.scatter(points[:,0], points[:,1], c='red', s=8, alpha=0.6, marker='.')
    plt.xlabel('X (m)', fontsize=12)
    plt.ylabel('Y (m)', fontsize=12)
    plt.title('Latest Mapping Result')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(latest_png, dpi=150, bbox_inches='tight')
    plt.savefig(latest_pdf, bbox_inches='tight')
    plt.close()
    
    print(f"   Latest: {latest_png}")
    
    return output_png, output_pdf

def save_metadata(output_dir='map_results'):
    """Save mapping metadata"""
    ensure_dir(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    meta_file = os.path.join(output_dir, f'metadata_{timestamp}.txt')
    
    with open(meta_file, 'w') as f:
        f.write("="*50 + "\n")
        f.write("Mapping Metadata\n")
        f.write("="*50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Trajectory info
        if os.path.exists('map_data.txt'):
            traj = np.loadtxt('map_data.txt', delimiter=',')
            f.write(f"Trajectory points: {len(traj)}\n")
            f.write(f"Start: ({traj[0,0]:.4f}, {traj[0,1]:.4f})\n")
            f.write(f"End: ({traj[-1,0]:.4f}, {traj[-1,1]:.4f})\n")
            total_dist = np.sum(np.sqrt(np.diff(traj[:,0])**2 + np.diff(traj[:,1])**2))
            f.write(f"Total distance: {total_dist:.4f} m\n")
            
            start = traj[0]
            end = traj[-1]
            loop_error = np.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
            f.write(f"Loop closure error: {loop_error:.4f} m\n")
        
        # Map info
        if os.path.exists('my_map.txt'):
            points = np.loadtxt('my_map.txt', delimiter=',')
            f.write(f"\nMap points: {len(points)}\n")
            f.write(f"X range: [{points[:,0].min():.4f}, {points[:,0].max():.4f}]\n")
            f.write(f"Y range: [{points[:,1].min():.4f}, {points[:,1].max():.4f}]\n")
    
    print(f"📝 Metadata saved: {meta_file}")

def analyze_and_save(output_dir='map_results'):
    """Analyze and save map quality report"""
    ensure_dir(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(output_dir, f'quality_report_{timestamp}.txt')
    
    with open(report_file, 'w') as f:
        f.write("="*50 + "\n")
        f.write("Map Quality Report\n")
        f.write("="*50 + "\n\n")
        
        if not os.path.exists('map_data.txt'):
            f.write("❌ No trajectory data\n")
            return
        
        traj = np.loadtxt('map_data.txt', delimiter=',')
        start = traj[0]
        end = traj[-1]
        loop_error = np.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
        
        f.write(f"Loop closure error: {loop_error:.4f} m\n")
        
        if loop_error < 0.1:
            f.write("Evaluation: ✅ Excellent - Good loop closure\n")
        elif loop_error < 0.3:
            f.write("Evaluation: ⚠️ Acceptable - Some drift\n")
        else:
            f.write("Evaluation: ❌ Poor - Significant drift\n")
        
        if os.path.exists('my_map.txt'):
            points = np.loadtxt('my_map.txt', delimiter=',')
            if len(points) > 0:
                x_range = points[:,0].max() - points[:,0].min()
                y_range = points[:,1].max() - points[:,1].min()
                f.write(f"\nMap size: {x_range:.4f} m × {y_range:.4f} m\n")
                f.write(f"Map points: {len(points)}\n")
                if x_range > 0 and y_range > 0:
                    f.write(f"Point density: {len(points)/(x_range*y_range):.2f} points/m²\n")
    
    print(f"📊 Quality report: {report_file}")

if __name__ == "__main__":
    print("="*50)
    print("Generating mapping results...")
    print("="*50)
    
    # Create output folder and generate map
    output_dir = 'map_results'
    
    # Generate map image
    png_file, pdf_file = plot_map(output_dir=output_dir)
    
    # Save metadata
    save_metadata(output_dir)
    
    # Generate quality report
    analyze_and_save(output_dir)
    
    print("\n" + "="*50)
    print(f"✅ All files saved to: {output_dir}/")
    print("="*50)
    
    # List all generated files
    print("\n📁 Generated files:")
    for f in sorted(os.listdir(output_dir)):
        fpath = os.path.join(output_dir, f)
        size = os.path.getsize(fpath)
        print(f"   - {f} ({size} bytes)")