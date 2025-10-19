import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import scanpy as sc

def plot_quiver_high_dim(z_points, delta_z, method='umap', figsize=(6,4), dpi=200):
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
        delta_z_2d = ad[z_points.shape[0]:] - z_2d
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