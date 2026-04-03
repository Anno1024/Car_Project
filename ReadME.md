相机标定请：
调节相机角度，运行test_roi.py 看到前面20到30厘米

运行 take_pictures.py ,图片将会储存在camera_calibration_pictures文件夹中
然后运行do_calibration.py 进行相机标定 并生成相应配置文件

色带阈值请参考：
hsv_tuner.py 请对比图片找到最适合的值域


小车键盘控制：
1 在树莓派上运行car_server.py
2 在电脑上运行car_client.py

里程计测试信息
listen_serial.py  可以成功监听。


driver.py       协议
osometry.py     里程计信息
vision.py       视觉
main.py         主控，但是没写好，因该加入比例控制


