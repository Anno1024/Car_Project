#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 文件名: plot_map.py

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

def ensure_dir(directory):
    """确保文件夹存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📁 创建文件夹: {directory}")

def plot_map(traj_file='map_data.txt', map_file='my_map.txt', output_dir='map_results'):
    """
    读取里程计轨迹和红线地图点，生成地图图片到指定文件夹
    """
    
    # 创建输出文件夹
    ensure_dir(output_dir)
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    plt.figure(figsize=(12, 10))
    
    # 1. 读取并绘制小车轨迹
    if not os.path.exists(traj_file):
        print(f"❌ 未找到文件: {traj_file}")
        return None, None
    
    traj = np.loadtxt(traj_file, delimiter=',')
    plt.plot(traj[:,0], traj[:,1], 'b-', linewidth=2, label='小车轨迹', alpha=0.7)
    plt.scatter(traj[0,0], traj[0,1], c='green', s=150, marker='o', 
               edgecolors='darkgreen', linewidth=2, label='起点', zorder=5)
    plt.scatter(traj[-1,0], traj[-1,1], c='red', s=150, marker='s', 
               edgecolors='darkred', linewidth=2, label='终点', zorder=5)
    
    print(f"✅ 轨迹数据: {len(traj)} 个点")
    print(f"   起点: ({traj[0,0]:.3f}, {traj[0,1]:.3f})")
    print(f"   终点: ({traj[-1,0]:.3f}, {traj[-1,1]:.3f})")
    total_dist = np.sum(np.sqrt(np.diff(traj[:,0])**2 + np.diff(traj[:,1])**2))
    print(f"   总行程: {total_dist:.3f} 米")
    
    # 2. 读取并绘制红线地图点
    map_point_count = 0
    if os.path.exists(map_file):
        points = np.loadtxt(map_file, delimiter=',')
        map_point_count = len(points)
        plt.scatter(points[:,0], points[:,1], c='red', s=8, alpha=0.6, 
                   label=f'红线地图 ({map_point_count} 个点)', marker='.')
        
        print(f"✅ 红线地图: {map_point_count} 个特征点")
        print(f"   X范围: [{points[:,0].min():.3f}, {points[:,0].max():.3f}]")
        print(f"   Y范围: [{points[:,1].min():.3f}, {points[:,1].max():.3f}]")
    
    # 3. 设置图形属性
    plt.xlabel('X (米)', fontsize=12)
    plt.ylabel('Y (米)', fontsize=12)
    plt.title(f'巡线建图结果\n总行程: {total_dist:.2f}m | 地图点: {map_point_count}', 
              fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.tight_layout()
    
    # 4. 保存图片到文件夹（多种格式）
    output_png = os.path.join(output_dir, f'map_{timestamp}.png')
    output_pdf = os.path.join(output_dir, f'map_{timestamp}.pdf')
    
    plt.savefig(output_png, dpi=150, bbox_inches='tight')
    plt.savefig(output_pdf, bbox_inches='tight')
    plt.close()
    
    print(f"\n📸 地图已保存:")
    print(f"   PNG: {output_png}")
    print(f"   PDF: {output_pdf}")
    
    # 同时保存一份最新的（覆盖）
    latest_png = os.path.join(output_dir, 'latest_map.png')
    latest_pdf = os.path.join(output_dir, 'latest_map.pdf')
    
    # 重新生成一份作为latest
    plt.figure(figsize=(12, 10))
    plt.plot(traj[:,0], traj[:,1], 'b-', linewidth=2, alpha=0.7)
    plt.scatter(traj[0,0], traj[0,1], c='green', s=150, marker='o', edgecolors='darkgreen', linewidth=2)
    plt.scatter(traj[-1,0], traj[-1,1], c='red', s=150, marker='s', edgecolors='darkred', linewidth=2)
    if os.path.exists(map_file):
        points = np.loadtxt(map_file, delimiter=',')
        plt.scatter(points[:,0], points[:,1], c='red', s=8, alpha=0.6, marker='.')
    plt.xlabel('X (米)', fontsize=12)
    plt.ylabel('Y (米)', fontsize=12)
    plt.title('最新建图结果')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(latest_png, dpi=150, bbox_inches='tight')
    plt.savefig(latest_pdf, bbox_inches='tight')
    plt.close()
    
    print(f"   最新版: {latest_png}")
    
    return output_png, output_pdf

def save_metadata(output_dir='map_results'):
    """保存建图元数据"""
    ensure_dir(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    meta_file = os.path.join(output_dir, f'metadata_{timestamp}.txt')
    
    with open(meta_file, 'w') as f:
        f.write("="*50 + "\n")
        f.write("建图元数据\n")
        f.write("="*50 + "\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 轨迹信息
        if os.path.exists('map_data.txt'):
            traj = np.loadtxt('map_data.txt', delimiter=',')
            f.write(f"轨迹点数: {len(traj)}\n")
            f.write(f"起点: ({traj[0,0]:.4f}, {traj[0,1]:.4f})\n")
            f.write(f"终点: ({traj[-1,0]:.4f}, {traj[-1,1]:.4f})\n")
            total_dist = np.sum(np.sqrt(np.diff(traj[:,0])**2 + np.diff(traj[:,1])**2))
            f.write(f"总行程: {total_dist:.4f} 米\n")
            
            start = traj[0]
            end = traj[-1]
            loop_error = np.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
            f.write(f"闭环误差: {loop_error:.4f} 米\n")
        
        # 地图信息
        if os.path.exists('my_map.txt'):
            points = np.loadtxt('my_map.txt', delimiter=',')
            f.write(f"\n地图点数: {len(points)}\n")
            f.write(f"X范围: [{points[:,0].min():.4f}, {points[:,0].max():.4f}]\n")
            f.write(f"Y范围: [{points[:,1].min():.4f}, {points[:,1].max():.4f}]\n")
    
    print(f"📝 元数据已保存: {meta_file}")

def analyze_and_save(output_dir='map_results'):
    """分析并保存地图质量报告"""
    ensure_dir(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(output_dir, f'quality_report_{timestamp}.txt')
    
    with open(report_file, 'w') as f:
        f.write("="*50 + "\n")
        f.write("地图质量报告\n")
        f.write("="*50 + "\n\n")
        
        if not os.path.exists('map_data.txt'):
            f.write("❌ 没有轨迹数据\n")
            return
        
        traj = np.loadtxt('map_data.txt', delimiter=',')
        start = traj[0]
        end = traj[-1]
        loop_error = np.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
        
        f.write(f"闭环误差: {loop_error:.4f} 米\n")
        
        if loop_error < 0.1:
            f.write("评价: ✅ 优秀 - 轨迹闭合良好\n")
        elif loop_error < 0.3:
            f.write("评价: ⚠️  可接受 - 有一定漂移\n")
        else:
            f.write("评价: ❌ 较差 - 漂移较大，建议缩短建图距离\n")
        
        if os.path.exists('my_map.txt'):
            points = np.loadtxt('my_map.txt', delimiter=',')
            if len(points) > 0:
                x_range = points[:,0].max() - points[:,0].min()
                y_range = points[:,1].max() - points[:,1].min()
                f.write(f"\n地图尺寸: {x_range:.4f} m × {y_range:.4f} m\n")
                f.write(f"地图点数: {len(points)}\n")
                f.write(f"点云密度: {len(points)/(x_range*y_range):.2f} 点/平方米\n")
    
    print(f"📊 质量报告: {report_file}")

if __name__ == "__main__":
    print("="*50)
    print("开始生成建图结果...")
    print("="*50)
    
    # 创建输出文件夹并生成地图
    output_dir = 'map_results'
    
    # 生成地图图片
    png_file, pdf_file = plot_map(output_dir=output_dir)
    
    # 保存元数据
    save_metadata(output_dir)
    
    # 生成质量报告
    analyze_and_save(output_dir)
    
    print("\n" + "="*50)
    print(f"✅ 所有文件已保存到: {output_dir}/")
    print("="*50)
    
    # 列出所有生成的文件
    print("\n📁 生成的文件列表:")
    for f in sorted(os.listdir(output_dir)):
        fpath = os.path.join(output_dir, f)
        size = os.path.getsize(fpath)
        print(f"   - {f} ({size} bytes)")