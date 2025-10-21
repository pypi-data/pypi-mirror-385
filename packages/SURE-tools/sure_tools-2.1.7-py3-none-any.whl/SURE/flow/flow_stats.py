import numpy as np
from scipy.spatial.distance import pdist, squareform

def calculate_movement_stats(vectors):
    """
    计算移动矢量的基本统计量
    """
    # 计算每个矢量的模长（移动距离）
    distances = np.linalg.norm(vectors, axis=1)
    
    stats = {
        'total_movement': np.sum(distances),
        'mean_distance': np.mean(distances),
        'median_distance': np.median(distances),
        'std_distance': np.std(distances),
        'max_distance': np.max(distances),
        'min_distance': np.min(distances),
        'total_points': len(vectors)
    }
    
    return stats, distances

def calculate_direction_stats(vectors):
    """
    计算移动方向的一致性
    """
    # 单位向量
    unit_vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    
    # 平均方向向量
    mean_direction = np.mean(unit_vectors, axis=0)
    mean_direction_norm = np.linalg.norm(mean_direction)
    
    # 方向一致性（0-1，1表示完全一致）
    direction_consistency = mean_direction_norm
    
    return {
        'direction_consistency': direction_consistency,
        'mean_direction': mean_direction,
        'direction_variance': 1 - direction_consistency  # 方向分散度
    }

def calculate_movement_energy(vectors, masses=None):
    """
    计算移动的能量（假设每个点有质量）
    """
    if masses is None:
        masses = np.ones(len(vectors))  # 默认单位质量
    
    # 动能 = 0.5 * mass * velocity^2
    speeds_squared = np.sum(vectors**2, axis=1)
    kinetic_energy = 0.5 * masses * speeds_squared
    
    return {
        'total_energy': np.sum(kinetic_energy),
        'mean_energy': np.mean(kinetic_energy),
        'energy_std': np.std(kinetic_energy)
    }

def calculate_movement_divergence(positions, vectors):
    """
    计算移动的散度（衡量扩张/收缩）
    """
    
    # 计算移动前后的位置
    new_positions = positions + vectors
    
    # 计算位置变化的协方差
    orig_cov = np.cov(positions.T)
    new_cov = np.cov(new_positions.T)
    
    # 体积变化（行列式比值）
    volume_ratio = np.linalg.det(new_cov) / np.linalg.det(orig_cov)
    
    return {
        'volume_expansion': volume_ratio,  # >1扩张, <1收缩
        'expansion_factor': volume_ratio**(1/positions.shape[1])
    }