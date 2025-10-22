import math
import numpy as np
from cv2 import solvePnP, Rodrigues


def __rotation_matrix_to_angles(rotation_matrix):
    """
    从旋转矩阵计算欧拉角。
    :param rotation_matrix: 3x3旋转矩阵。
    :return: 绕每个轴的角度（以度为单位）。
    """
    x = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])  # 计算绕X轴的旋转角度
    y = math.atan2(-rotation_matrix[2, 0],
                   math.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2))  # 计算绕Y轴的旋转角度
    z = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])  # 计算绕Z轴的旋转角度
    return np.array([x, y, z]) * 180. / math.pi  # 将弧度转换为度


def get_head_pose_angles(landmarks, width, height):
    """
    根据面部特征点计算头部姿势角度。
    :param landmarks: Mediapipe面部特征点。
    :param width: 图像宽度。
    :param height: 图像高度。
    :return: 俯仰(pitch)、偏航(yaw)和滚转(roll)角度。
    """
    # 定义面部特征点的坐标
    face_coordination_in_real_world = np.array([
        [285, 528, 200],  # Point 1  右眼内角
        [285, 371, 152],  # Point 9  下巴
        [197, 574, 128],  # Point 57  右嘴角
        [173, 425, 108],  # Point 130  左眼内角
        [360, 574, 128],  # Point 287   左嘴角
        [391, 425, 108]  # Point 359   鼻尖
    ], dtype=np.float64)

    face_coordination_in_image = []

    # 提取所需的特征点坐标
    for idx in [1, 9, 57, 130, 287, 359]:  # 这些索引需要根据实际的landmark索引调整
        landmark = landmarks[idx]
        x, y = int(landmark.x * width), int(landmark.y * height)  # 将归一化坐标转换为图像坐标
        face_coordination_in_image.append([x, y])

    face_coordination_in_image = np.array(face_coordination_in_image, dtype=np.float64)

    # 定义相机矩阵
    focal_length = width
    cam_matrix = np.array([[focal_length, 0, width / 2],
                           [0, focal_length, height / 2],
                           [0, 0, 1]])

    # 假设没有镜头畸变
    dist_matrix = np.zeros((4, 1), dtype=np.float64)

    # 求解姿态
    success, rotation_vec, _ = solvePnP(
        face_coordination_in_real_world, face_coordination_in_image, cam_matrix, dist_matrix)

    if not success:
        return None

    # 将旋转向量转换为旋转矩阵
    rotation_matrix, _ = Rodrigues(rotation_vec)
    # 计算欧拉角
    return __rotation_matrix_to_angles(rotation_matrix)
