import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import scanpy as sc
from matplotlib.colors import ListedColormap

def plot_quiver(z_points, delta_z, method='pca', figsize=(6,4), dpi=200, 
                subsample=None, color_by=None, colormap='viridis', 
                arrow_scale=1.0, arrow_width=0.005, alpha=0.8):
    """
    优化后的quiver可视化函数
    
    Args:
        z_points: 原始潜在空间点 [n_samples, n_dims]
        delta_z: 移动向量 [n_samples, n_dims]
        method: 降维方法 ('pca', 'variance', 'manual', 'umap')
        figsize: 图像大小
        dpi: 分辨率
        subsample: 随机采样的数据点数量 (None表示不采样)
        color_by: 颜色标签数组 [n_samples]
        colormap: 颜色映射名称或ListedColormap对象
        arrow_scale: 箭头缩放因子
        arrow_width: 箭头宽度
        alpha: 透明度
    """
    # 数据采样
    if subsample is not None and len(z_points) > subsample:
        idx = np.random.choice(len(z_points), subsample, replace=False)
        z_points = z_points[idx]
        delta_z = delta_z[idx]
        if color_by is not None:
            color_by = color_by[idx]
    
    # 降维投影
    if method == 'variance':
        variances = np.var(z_points, axis=0)
        dims = np.argsort(variances)[-2:]
        z_2d = z_points[:, dims]
        delta_z_2d = delta_z[:, dims]
        dim_names = [f'z[{d}]' for d in dims]
        
    elif method == 'pca':
        pca = PCA(n_components=2)
        z_2d = pca.fit_transform(z_points)
        delta_z_2d = pca.transform(z_points + delta_z) - z_2d
        dim_names = ['PC1', 'PC2']
        
    elif method == 'manual':
        dims = [0, 1]
        z_2d = z_points[:, dims]
        delta_z_2d = delta_z[:, dims]
        dim_names = [f'z[{d}]' for d in dims]
        
    elif method == 'umap':
        ad = sc.AnnData(np.vstack([z_points, z_points+delta_z]))
        sc.pp.neighbors(ad)
        sc.tl.umap(ad)
        z_2d = ad[:z_points.shape[0]].obsm['X_umap']
        delta_z_2d = ad[z_points.shape[0]:].obsm['X_umap'] - z_2d
        dim_names = ['UMAP1', 'UMAP2']
    
    # 颜色处理
    if color_by is not None:
        if isinstance(colormap, str):
            cmap = plt.get_cmap(colormap)
        else:
            cmap = colormap
        
        if color_by.dtype.kind in ['i', 'f']:  # 数值型标签
            colors = cmap(color_by / max(color_by.max(), 1e-8))
            cbar_label = 'Numeric Label'
        else:  # 类别型标签
            unique_labels = np.unique(color_by)
            color_map = {label: cmap(i/len(unique_labels)) 
                        for i, label in enumerate(unique_labels)}
            colors = [color_map[label] for label in color_by]
            cbar_label = 'Class Label'
    else:
        colors = 'blue'
    
    # 绘制
    plt.figure(figsize=figsize, dpi=dpi)
    
    # 绘制quiver（分颜色组绘制以获得正确图例）
    if color_by is not None and isinstance(color_by[0], str):
        for label in np.unique(color_by):
            mask = color_by == label
            plt.quiver(z_2d[mask, 0], z_2d[mask, 1],
                      delta_z_2d[mask, 0], delta_z_2d[mask, 1],
                      angles='xy', scale_units='xy', scale=1.0/arrow_scale,
                      color=colors[mask], width=arrow_width, alpha=alpha,
                      label=str(label))
        plt.legend()
    else:
        q = plt.quiver(z_2d[:, 0], z_2d[:, 1],
                      delta_z_2d[:, 0], delta_z_2d[:, 1],
                      angles='xy', scale_units='xy', scale=1.0/arrow_scale,
                      color=colors, width=arrow_width, alpha=alpha)
        
        # 添加颜色条（数值型标签）
        if color_by is not None and color_by.dtype.kind in ['i', 'f']:
            plt.colorbar(plt.cm.ScalarMappable(
                norm=plt.Normalize(color_by.min(), color_by.max()),
                cmap=cmap), label=cbar_label)
    
    # 美化图形
    plt.scatter(z_2d[:, 0], z_2d[:, 1], c='gray', alpha=0.3, s=5)
    plt.xlabel(dim_names[0])
    plt.ylabel(dim_names[1])
    plt.title(f"Latent Space Movement ({method} projection)")
    plt.grid(alpha=0.2)
    plt.tight_layout()
    plt.show()
    
    return z_2d, delta_z_2d

def plot_quiver_old(z_points, delta_z, method='pca', figsize=(6,4), dpi=200):
    """
    从高维潜在空间选择2个维度进行quiver可视化
    """
    if method == 'variance':
        # 方法1: 选择方差最大的2个维度
        variances = np.var(z_points, axis=0)
        dims = np.argsort(variances)[-2:]  # 选择方差最大的两个维度
        dim_names = [f'z[{d}]' for d in dims]
        
    elif method == 'pca':
        # 方法2: 使用PCA的前两个主成分
        pca = PCA(n_components=2)
        z_2d = pca.fit_transform(z_points)
        delta_z_2d = pca.transform(z_points + delta_z) - z_2d
        dim_names = ['PC1', 'PC2']
        
    elif method == 'manual':
        # 方法3: 手动选择感兴趣的维度
        dims = [0, 1]  # 选择前两个维度
        z_2d = z_points[:, dims]
        delta_z_2d = delta_z[:, dims]
        dim_names = [f'z[{d}]' for d in dims]
        
    elif method == 'umap':
        ad = sc.AnnData(np.vstack([z_points, z_points+delta_z]))
        sc.pp.neighbors(ad)
        sc.tl.umap(ad)
        z_2d = ad[:z_points.shape[0]].obsm['X_umap']
        delta_z_2d = ad[z_points.shape[0]:].obsm['X_umap'] - z_2d
        dim_names = ['UMAP1', 'UMAP2']
    
    # 绘制quiver图
    plt.figure(figsize=figsize, dpi=dpi)
    plt.quiver(z_2d[:, 0], z_2d[:, 1], 
               delta_z_2d[:, 0], delta_z_2d[:, 1],
               angles='xy', scale_units='xy', scale=1,
               color='blue', alpha=0.6, width=0.005)
    
    plt.scatter(z_2d[:, 0], z_2d[:, 1], c='gray', alpha=0.5, s=10)
    plt.xlabel(dim_names[0])
    plt.ylabel(dim_names[1])
    plt.title(f"Latent Space Movement ({method} projection)")
    plt.grid(alpha=0.3)
    plt.show()
    
    return z_2d, delta_z_2d