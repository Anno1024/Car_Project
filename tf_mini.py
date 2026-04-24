import numpy as np
data = np.load('calibration_result/camera_calibration_result.npz')
print(data.files) # 看看输出是不是 ['mtx', 'dist']