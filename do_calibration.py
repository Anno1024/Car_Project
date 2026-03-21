#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import glob
import os

# ==================== 配置参数 ====================
# 棋盘格内部角点数量
CHESSBOARD_SIZE = (9, 6)  # 9列6行内部角点

# 格子实际尺寸 (单位：米)
SQUARE_SIZE = 0.024  # 24mm = 0.024m

# 图片路径
IMAGE_PATH = './camera_calibration_pictures/*.jpg'

# 结果保存
CALIB_RESULT_PATH = './calibration_result/camera_calibration_result.npz'
# =================================================

# 设置亚像素角点参数
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# 准备世界坐标点 (单位：米)
objp = np.zeros((CHESSBOARD_SIZE[0] * CHESSBOARD_SIZE[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHESSBOARD_SIZE[0], 0:CHESSBOARD_SIZE[1]].T.reshape(-1, 2)
objp = objp * SQUARE_SIZE  # 现在单位是米

# 储存角点坐标
objpoints = []  # 世界坐标系3D点
imgpoints = []  # 图像坐标系2D点

# 加载图片
images = glob.glob(IMAGE_PATH)
print(f"找到 {len(images)} 张图片")

if len(images) == 0:
    print("错误：没有找到图片！请检查路径")
    exit()

# ==================== 找角点 ====================
success_count = 0
failed_images = []

for i, fname in enumerate(images):
    print(f"\r处理图片 {i+1}/{len(images)}，成功: {success_count}", end="", flush=True)
    
    img = cv2.imread(fname)
    if img is None:
        print(f"\n无法读取图片: {fname}")
        failed_images.append(fname)
        continue
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 找棋盘格角点
    ret, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE, None)
    
    if ret:
        success_count += 1
        # 亚像素角点
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        
        objpoints.append(objp)
        imgpoints.append(corners2)
    else:
        failed_images.append(fname)

print(f"\n成功检测到角点的图片: {success_count}/{len(images)}")

if len(failed_images) > 0:
    print(f"\n失败的图片 ({len(failed_images)} 张):")
    for f in failed_images[:5]:  # 只显示前5张
        print(f"  - {os.path.basename(f)}")
    if len(failed_images) > 5:
        print(f"  ... 还有 {len(failed_images)-5} 张")

if success_count < 5:
    print("错误：成功检测的图片太少，请重新拍照")
    print("可能原因：")
    print("  1. 棋盘格太远/太模糊")
    print("  2. 光照不均匀")
    print("  3. 棋盘格被遮挡")
    print("  4. 棋盘格规格不是9x6内部角点")
    exit()

# ==================== 执行标定 ====================
print("\n正在计算相机参数...")

# 获取图像尺寸（用第一张成功的图）
test_img = cv2.imread(images[0])
h, w = test_img.shape[:2]

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, (w, h), None, None
)

# ==================== 输出结果 ====================
print("\n" + "="*60)
print("标定结果")
print("="*60)
print(f"\n【重投影误差】: {ret:.6f} 像素")
print("  (小于0.5表示标定质量很好，小于1.0也可用)")

print("\n【相机内参矩阵】")
print("  ┌─────────────┐")
print(f"  │ {mtx[0,0]:8.3f}  {mtx[0,1]:8.3f}  {mtx[0,2]:8.3f} │")
print(f"  │ {mtx[1,0]:8.3f}  {mtx[1,1]:8.3f}  {mtx[1,2]:8.3f} │")
print(f"  │ {mtx[2,0]:8.3f}  {mtx[2,1]:8.3f}  {mtx[2,2]:8.3f} │")
print("  └─────────────┘")

print("\n【畸变系数】")
print(f"  k1, k2, p1, p2, k3:")
print(f"  {dist.flatten()}")

# ==================== 保存结果 ====================
np.savez(CALIB_RESULT_PATH, 
         camera_matrix=mtx, 
         dist_coeffs=dist,
         ret_error=ret)
print(f"\n结果已保存到: {CALIB_RESULT_PATH}")

# ==================== 生成验证图片 ====================
print("\n生成验证图片...")

# 选一张图展示校正效果
test_img = cv2.imread(images[0])
h, w = test_img.shape[:2]

# 校正
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
dst = cv2.undistort(test_img, mtx, dist, None, newcameramtx)

# 裁剪黑边
x, y, w_roi, h_roi = roi
dst_cropped = dst[y:y+h_roi, x:x+w_roi]

# 保存对比图（不显示，直接保存）
cv2.imwrite('./calibration_result/calibration_original.jpg', test_img)
cv2.imwrite('./calibration_result/calibration_undistorted.jpg', dst)
cv2.imwrite('./calibration_result/calibration_cropped.jpg', dst_cropped)

print("已生成对比图片：")
print("  - calibration_original.jpg   (原始图像)")
print("  - calibration_undistorted.jpg (校正后图像)")
print("  - calibration_cropped.jpg     (裁剪黑边后的图像)")

# ==================== 生成ROS YAML文件 ====================
yaml_content = f"""# 相机标定参数 (自动生成)
image_width: {w}
image_height: {h}
camera_name: camera
camera_matrix:
  rows: 3
  cols: 3
  data: [{mtx[0,0]}, {mtx[0,1]}, {mtx[0,2]},
         {mtx[1,0]}, {mtx[1,1]}, {mtx[1,2]},
         {mtx[2,0]}, {mtx[2,1]}, {mtx[2,2]}]
distortion_model: plumb_bob
distortion_coefficients:
  rows: 1
  cols: 5
  data: [{dist[0,0]}, {dist[0,1]}, {dist[0,2]}, {dist[0,3]}, {dist[0,4]}]
rectification_matrix:
  rows: 3
  cols: 3
  data: [1, 0, 0, 0, 1, 0, 0, 0, 1]
projection_matrix:
  rows: 3
  cols: 4
  data: [{mtx[0,0]}, 0, {mtx[0,2]}, 0,
         0, {mtx[1,1]}, {mtx[1,2]}, 0,
         0, 0, 1, 0]
"""

with open('./camera_calibration.yaml', 'w') as f:
    f.write(yaml_content)
print("\n已生成ROS格式参数文件: camera_calibration.yaml")

# ==================== 简单统计 ====================
print("\n" + "="*60)
print("标定完成！")
print("="*60)
print(f"使用图片: {success_count}/{len(images)} 张")
print(f"重投影误差: {ret:.6f} 像素")
print(f"\n下一步可以在代码中加载标定结果：")
print("  import numpy as np")
print("  calib = np.load('calibration_result/camera_calibration_result.npz')")
print("  mtx = calib['camera_matrix']")
print("  dist = calib['dist_coeffs']")