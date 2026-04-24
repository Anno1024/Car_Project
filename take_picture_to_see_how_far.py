import cv2
import os
import time

def capture_single_photo():
    # 创建保存目录
    save_dir = 'calib_images'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 初始化摄像头 (通常树莓派上是 0 或 1)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return

    # 设置分辨率 (建议与你 main.py 运行的分辨率一致)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("📸 正在热身摄像头...")
    # 摄像头预热，跳过前几帧以保证曝光正常
    for _ in range(30):
        cap.read()

    # 读取一帧
    ret, frame = cap.read()

    if ret:
        # 生成文件名：calib_20240422_183005.jpg
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file_name = f"calib_{timestamp}.jpg"
        file_path = os.path.join(save_dir, file_name)
        
        # 保存图片
        cv2.imwrite(file_path, frame)
        print(f"✅ 照片已成功保存至: {file_path}")
        print(f"📏 现在你可以去文件夹里查看这张图，并测量物理距离了。")
    else:
        print("❌ 拍照失败")

    # 释放资源
    cap.release()

if __name__ == "__main__":
    capture_single_photo()
