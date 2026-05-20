import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
# from frontend.SharedKernel.math.LinearAlgebra import (
#     EigenDecomposition, 
#     SingularValueDecomposition, 
#     MatrixDecompositions
# )

class LinearAlgebraComponents:
    """
    Class for demonstrating linear algebra concepts:
    eigenvectors, eigenvalues, SVD, and matrix decompositions
    """
    
    def __init__(self):
        pass
    
    def eigenvector_demo(self):
        """Demonstrate eigenvectors and eigenvalues"""
        st.markdown("### Eigenvectors and Eigenvalues")
        st.markdown("For matrix A, eigenvectors satisfy: **Av = λv**")
        
        A = np.array([[1,2], [3,4]])
        eigen_decomp = EigenDecomposition(A)
        values = eigen_decomp.get_eigenvalues()
        vectors = eigen_decomp.get_eigenvectors()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Matrix A:**")
            st.write(A)
            
            st.markdown("**Eigenvalues:**")
            for i, val in enumerate(values):
                st.code(f"λ{i+1} = {val:.4f}")
        
        with col2:
            st.markdown("**Eigenvectors:**")
            for i, vec in enumerate(vectors.T):
                st.code(f"v{i+1} = [{vec[0]:.4f}, {vec[1]:.4f}]")
                
                # Verify Av = λv using the extracted math core
                Av, λv = eigen_decomp.verify_eigenvector(i)
                st.code(f"Av = [{Av[0]:.4f}, {Av[1]:.4f}]")
                st.code(f"λv = [{λv[0]:.4f}, {λv[1]:.4f}]")
        
        st.markdown("**Verification:** Av ≈ λv (should be equal)")
    
    def svd_demo(self):
        """Demonstrate Singular Value Decomposition"""
        st.markdown("### Singular Value Decomposition (SVD)")
        st.markdown("**A = UΣV^T**")
        st.markdown("Applications: PCA, image compression, recommendation systems")
        
        # Generate a sample image for SVD demo
        img_arr = np.random.randint(0, 256, (20, 20, 3), dtype=np.uint8)
        # Create a gradient pattern instead of cumsum to avoid potential issues
        for i in range(20):
            for j in range(20):
                img_arr[i, j] = (i * 12 + j * 12) % 256
        
        def compress_img_svd(img, k):
            compressed = np.zeros_like(img, dtype=float)
            for c in range(3):
                svd = SingularValueDecomposition(img[:,:, c])
                compressed[:, :, c] = svd.compress(k)
            return compressed
        
        k = st.slider("Number of singular values (k)", 1, 20, 10)
        
        compressed = compress_img_svd(img_arr, k)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Image**")
            # Ensure proper format for st.image
            if img_arr.dtype != np.uint8:
                img_display = np.clip(img_arr, 0, 255).astype(np.uint8)
            else:
                img_display = img_arr
            st.image(img_display, clamp=True, width=200)
        
        with col2:
            st.markdown(f"**Compressed (k={k})**")
            # Normalize and convert to uint8 for display
            compressed_display = np.clip(compressed, 0, 255).astype(np.uint8)
            st.image(compressed_display, clamp=True, width=200)
        
        # Show singular values using extracted math core
        st.markdown("**Singular Values:**")
        svd = SingularValueDecomposition(img_arr[:,:, 0])
        S = svd.get_singular_values()
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(S, 'bo-')
        ax.set_xlabel('Index')
        ax.set_ylabel('Value')
        ax.set_title('Singular Values')
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    
    def matrix_decomposition_demo(self):
        """Demonstrate various matrix decompositions"""
        st.markdown("### Matrix Decompositions")
        
        # Sample matrix
        A = np.array([[4, 3], [6, 5]])
        decomp = MatrixDecompositions(A)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**LU Decomposition:**")
            P, L, U = decomp.lu_decomposition()
            st.code(f"P = {P}")
            st.code(f"L = {L}")
            st.code(f"U = {U}")
            st.code(f"PA = LU")
        
        with col2:
            st.markdown("**QR Decomposition:**")
            Q, R = decomp.qr_decomposition()
            st.code(f"Q = {Q}")
            st.code(f"R = {R}")
            st.code(f"A = QR")
        
        with col3:
            st.markdown("**Cholesky Decomposition:**")
            try:
                L_chol = decomp.cholesky_decomposition()
                st.code(f"L = {L_chol}")
                st.code(f"A = LL^T")
            except ValueError as e:
                st.warning(str(e))
    
    def render(self):
        """Render all linear algebra demonstrations"""
        st.markdown("## Linear Algebra")
        
        self.eigenvector_demo()
        st.markdown("---")
        self.svd_demo()
        st.markdown("---")
        self.matrix_decomposition_demo()
        
        st.markdown("### Linear Algebra Concepts")
        st.markdown("""
        **Eigendecomposition**: A = PDP⁻¹ where D contains eigenvalues
        **SVD**: A = UΣV^T for any rectangular matrix
        **LU**: PA = LU for square matrices
        **QR**: A = QR where Q is orthogonal, R is upper triangular
        **Cholesky**: A = LL^T for positive definite matrices
        """)
