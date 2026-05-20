import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

class MatrixOperations:
    """
    Class for demonstrating matrix operations and transformations
    """
    
    def __init__(self):
        pass
    
    def matrix_multiplication_demo(self):
        """Demonstrate matrix multiplication with NumPy vs manual implementation"""
        st.markdown("### Matrix Multiplication")
        st.markdown("For matrices A (m×n) and B (n×p), result C = AB is (m×p)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Matrix A (2×3):**")
            A = np.array([[1,2,3],[4,5,6]])
            st.write(A)
            
            st.markdown("**Matrix B (3×2):**")
            B = np.array([[7,8], [9,10], [11,12]])
            st.write(B)
        
        with col2:
            st.markdown("**Result A @ B:**")
            result = A @ B
            st.write(result)
            
            st.markdown("**Manual Implementation:**")
            st.write(self.mat_mult(A, B))
    
    def mat_mult(self, A, B):
        """Manual matrix multiplication implementation"""
        m, n = A.shape
        n2, p = B.shape
        
        if n != n2:
            raise ValueError("Matrix dims do not match")
        
        C = np.zeros((m, p))
        for i in range(m):
            for j in range(p):
                for k in range(n):
                    C[i,j] += A[i,k] * B[k,j]
        return C
    
    def transformation_2d_demo(self):
        """Demonstrate 2D transformations with rotation"""
        st.markdown("### 2D Transformations")
        st.markdown("Point rotation using transformation matrix")
        
        angle = st.slider("Rotation angle (degrees)", 0, 360, 90)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Transformation Matrix:**")
            angle_rad = np.deg2rad(angle)
            
            R = np.array([
                [np.cos(angle_rad), -np.sin(angle_rad)],
                [np.sin(angle_rad), np.cos(angle_rad)]
            ])
            st.write(R)
            
            st.markdown(f"**Angle:** {angle}° = {angle_rad:.4f} radians")
        
        with col2:
            st.markdown("**Rotation Visualization:**")
            point = np.array([1, 0])
            rotated = self.rotate_point(point, angle)
            
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.quiver(0, 0, point[0], point[1], angles='xy', scale_units='xy', scale=1, color='blue', label='Original')
            ax.quiver(0, 0, rotated[0], rotated[1], angles='xy', scale_units='xy', scale=1, color='red', label=f'Rotated {angle}°')
            ax.set_xlim(-2, 2)
            ax.set_ylim(-2, 2)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax.set_title('2D Rotation Transformation')
            st.pyplot(fig)
            
            st.markdown(f"**Original Point:** [{point[0]}, {point[1]}]")
            st.markdown(f"**Rotated Point:** [{rotated[0]:.2f}, {rotated[1]:.2f}]")
    
    def rotate_point(self, point, angle_degrees):
        """Rotate a 2D point by given angle"""
        angle_rad = np.deg2rad(angle_degrees)
        
        R = np.array([
            [np.cos(angle_rad), -np.sin(angle_rad)],
            [np.sin(angle_rad), np.cos(angle_rad)]
        ])
        
        return R @ point
    
    def matrix_properties_demo(self):
        """Demonstrate important matrix properties"""
        st.markdown("### Matrix Properties")
        
        # Create sample matrices
        identity = np.eye(3)
        diagonal = np.diag([1, 2, 3])
        symmetric = np.array([[2, 1, 3], [1, 4, 5], [3, 5, 6]])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Identity Matrix I₃:**")
            st.write(identity)
            st.code(f"determinant: {np.linalg.det(identity):.2f}")
            st.code(f"rank: {np.linalg.matrix_rank(identity)}")
        
        with col2:
            st.markdown("**Diagonal Matrix:**")
            st.write(diagonal)
            st.code(f"determinant: {np.linalg.det(diagonal):.2f}")
            st.code(f"rank: {np.linalg.matrix_rank(diagonal)}")
        
        with col3:
            st.markdown("**Symmetric Matrix:**")
            st.write(symmetric)
            st.code(f"determinant: {np.linalg.det(symmetric):.2f}")
            st.code(f"rank: {np.linalg.matrix_rank(symmetric)}")
            st.code(f"is symmetric: {np.allclose(symmetric, symmetric.T)}")
        
        st.markdown("### Matrix Properties Explanation")
        st.markdown("""
        **Identity Matrix**: Diagonal elements are 1, others are 0. I × A = A
        **Diagonal Matrix**: Non-diagonal elements are 0
        **Symmetric Matrix**: A = Aᵀ (matrix equals its transpose)
        
        **Determinant**: Scalar value that indicates if matrix is invertible
        **Rank**: Number of linearly independent rows/columns
        """)
    
    def render(self):
        """Render all matrix operations"""
        st.markdown("## Matrix Operations")
        
        self.matrix_multiplication_demo()
        st.markdown("---")
        self.transformation_2d_demo()
        st.markdown("---")
        self.matrix_properties_demo()
