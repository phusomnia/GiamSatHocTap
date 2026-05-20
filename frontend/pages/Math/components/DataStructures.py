import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

class DataStructures:
    """
    Class for visualizing and explaining fundamental data structures:
    vectors, matrices, and tensors
    """
    
    def __init__(self):
        pass
    
    def display_vector_info(self):
        """Display vector information and visualization"""
        st.markdown("### Vector")
        vector = np.array([1, 2, 3, 4])
        st.code(f"shape: {vector.shape}")
        st.code(f"norm: {np.linalg.norm(vector):.2f}")
        st.code(f"dims: {vector.ndim}")
        st.write(vector)
        
        # Vector visualization
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.quiver(0, 0, vector[0], vector[1], angles='xy', scale_units='xy', scale=1, color='blue', label='Vector')
        ax.set_xlim(-1, 5)
        ax.set_ylim(-1, 5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_title('Vector Visualization')
        st.pyplot(fig)
    
    def display_matrix_info(self):
        """Display matrix information and visualization"""
        st.markdown("### Matrix")
        matrix = np.array([[1, 2], [1, 2]])
        st.code(f"shape: {matrix.shape}")
        st.code(f"norm: {np.linalg.norm(matrix):.2f}")
        st.code(f"dims: {matrix.ndim}")
        st.write(matrix)
        
        # Matrix visualization as heatmap
        fig, ax = plt.subplots(figsize=(4, 3))
        im = ax.imshow(matrix, cmap='Blues', aspect='auto')
        ax.set_title('Matrix Visualization')
        
        # Add text annotations
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                ax.text(j, i, f'{matrix[i, j]}', ha='center', va='center', color='red')
        
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        st.pyplot(fig)
    
    def display_tensor_info(self):
        """Display tensor information and visualization"""
        st.markdown("### Tensor")
        tensor = np.array([
            [[1,2], [3,4]],
            [[5,6], [7,8]]
        ])
        st.code(f"shape: {tensor.shape}")
        st.code(f"norm: {np.linalg.norm(tensor):.2f}")
        st.code(f"dims: {tensor.ndim}")
        
        # Display tensor as text to avoid matplotlib issues
        st.text(str(tensor))
        
        # Visualize tensor slices
        st.markdown("**Tensor Slices:**")
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        
        # First slice
        axes[0].imshow(tensor[0], cmap='Blues', aspect='auto')
        axes[0].set_title('Tensor[0]')
        for i in range(tensor.shape[1]):
            for j in range(tensor.shape[2]):
                axes[0].text(j, i, f'{tensor[0, i, j]}', ha='center', va='center', color='red')
        
        # Second slice
        axes[1].imshow(tensor[1], cmap='Blues', aspect='auto')
        axes[1].set_title('Tensor[1]')
        for i in range(tensor.shape[1]):
            for j in range(tensor.shape[2]):
                axes[1].text(j, i, f'{tensor[1, i, j]}', ha='center', va='center', color='red')
        
        plt.tight_layout()
        st.pyplot(fig)
    
    def render(self):
        """Render all data structures"""
        st.markdown("## Data Structures Visualization")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            self.display_vector_info()
        
        with col2:
            self.display_matrix_info()
        
        with col3:
            self.display_tensor_info()
        
        st.markdown("### Data Structure Properties")
        st.markdown("""
        **Vector**: 1D array - represents magnitude and direction\n
        **Matrix**: 2D array - represents linear transformations\n
        **Tensor**: 3D+ array - represents multi-dimensional data
        
        Common operations:
        - **Norm**: L2 norm = √(x₁² + x₂² + ... + xₙ²)
        - **Shape**: Dimensions of the array
        - **Dimensions**: Number of axes (ndim)
        """)
