import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

class Calculus:
    """
    Class for demonstrating calculus concepts:
    derivatives, gradients, chain rule, and optimization
    """
    
    def __init__(self):
        pass
    
    def derivatives_demo(self):
        """Demonstrate derivatives and gradients"""
        st.markdown("### Derivatives and Gradients")
        st.markdown("Derivative measures rate of change: **f'(x) = lim(h→0) [f(x+h) - f(x)]/h**")
        
        def func_xy(x, y):
            return x**2 + y**2 + x*y
        
        def gradient(f, x, y, h=1e-7):
            df_dx = (f(x + h, y) - f(x, y)) / h
            df_dy = (f(x, y + h) - f(x, y)) / h
            return np.array([df_dx, df_dy])
        
        x_val = st.slider("x value", -5, 5, 2)
        y_val = st.slider("y value", -5, 5, 2)
        
        grad = gradient(func_xy, x_val, y_val)
        st.code(f"∇f({x_val}, {y_val}) = [{grad[0]:.4f}, {grad[1]:.4f}]")
        
        # Visualize gradient
        fig, ax = plt.subplots(figsize=(6, 4))
        x_range = np.linspace(-5, 5, 100)
        y_range = np.linspace(-5, 5, 100)
        X, Y = np.meshgrid(x_range, y_range)
        Z = func_xy(X, Y)
        
        # Plot surface
        contour = ax.contour(X, Y, Z, levels=20, alpha=0.6)
        ax.clabel(contour, inline=True, fontsize=8)
        
        # Plot gradient vector
        ax.quiver(x_val, y_val, grad[0], grad[1], angles='xy', scale_units='xy', scale=1, color='red', width=0.01)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('Gradient Visualization')
        ax.set_aspect('equal')
        st.pyplot(fig)
    
    def chain_rule_demo(self):
        """Demonstrate chain rule"""
        st.markdown("### Chain Rule")
        st.markdown("For y = sin(x²), dy/dx = (dy/du) × (du/dx)")
        
        x_demo = st.slider("Chain rule demo - x value", -3, 3, 2)
        
        def u(x): return x**2
        def du_dx(x): return 2*x
        def y(u): return np.sin(u)
        def df_du(u): return np.cos(u)
        
        dy_dx = du_dx(x_demo) * df_du(u(x_demo))
        st.markdown(f"dy/dx at x={x_demo} = {dy_dx:.4f}")
        
        # Numerical verification
        h = 1e-7
        numerical = (np.sin((x_demo + h)**2) - np.sin(x_demo**2)) / h
        st.code(f"Numerical: {numerical:.4f}")
        
        # Visualization
        fig, ax = plt.subplots(figsize=(8, 4))
        x_vals = np.linspace(-3, 3, 100)
        y_vals = np.sin(x_vals**2)
        ax.plot(x_vals, y_vals, 'b-', label='y = sin(x²)')
        
        # Mark current point
        y_current = np.sin(x_demo**2)
        ax.scatter([x_demo], [y_current], color='red', s=100, zorder=5, label=f'Point at x={x_demo}')
        
        # Show tangent line
        x_tangent = np.linspace(x_demo - 1, x_demo + 1, 50)
        y_tangent = y_current + dy_dx * (x_tangent - x_demo)
        ax.plot(x_tangent, y_tangent, 'r--', label=f'Tangent: dy/dx={dy_dx:.2f}')
        
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('Chain Rule Demonstration')
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    
    def gradient_descent_demo(self):
        """Demonstrate gradient descent optimization"""
        st.markdown("### Gradient Descent")
        st.markdown("Optimization algorithm: **w(new) = w(old) - α×∇L(w)**")
        
        # Simple function minimization
        def f(x): return x**2
        def gradient(x): return 2*x
        
        lr = st.slider("Learning rate", 0.01, 0.5, 0.1)
        epochs = st.slider("Epochs", 10, 100, 20)
        
        x = 10.0
        history = []
        
        for i in range(epochs):
            grad = gradient(x)
            x = x - lr * grad
            history.append((i, x, f(x)))
        
        # Plot gradient descent
        fig, ax = plt.subplots(figsize=(8, 4))
        x_vals = np.linspace(-10, 10, 100)
        y_vals = f(x_vals)
        ax.plot(x_vals, y_vals, 'b-', alpha=0.3, label='f(x) = x²')
        
        # Plot trajectory
        traj_x = [h[1] for h in history]
        traj_y = [h[2] for h in history]
        ax.plot(traj_x, traj_y, 'ro-', markersize=4, label='Gradient descent path')
        ax.scatter([traj_x[-1]], [traj_y[-1]], color='green', s=100, zorder=5, label=f'Final: x≈{traj_x[-1]:.3f}')
        
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')
        ax.set_title('Gradient Descent Optimization')
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        
        st.markdown(f"**Final result:** x ≈ {traj_x[-1]:.3f} (very close to 0)")
    
    def integration_demo(self):
        """Demonstrate numerical integration"""
        st.markdown("### Numerical Integration")
        st.markdown("∫f(x)dx ≈ Σ[f(xᵢ) × Δx]")
        
        def f(x): return x**2
        
        # Integration parameters
        a = st.slider("Lower bound (a)", -5, 0, -1)
        b = st.slider("Upper bound (b)", 0, 5, 1)
        n = st.slider("Number of rectangles", 10, 100, 50)
        
        # Riemann sum
        x = np.linspace(a, b, n+1)
        dx = (b - a) / n
        
        # Left Riemann sum
        left_sum = np.sum(f(x[:-1]) * dx)
        
        # Right Riemann sum
        right_sum = np.sum(f(x[1:]) * dx)
        
        # Trapezoidal rule
        trap_sum = np.sum((f(x[:-1]) + f(x[1:])) * dx / 2)
        
        # Exact solution
        exact = (b**3 - a**3) / 3
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Numerical Results:**")
            st.code(f"Left Riemann: {left_sum:.4f}")
            st.code(f"Right Riemann: {right_sum:.4f}")
            st.code(f"Trapezoidal: {trap_sum:.4f}")
        
        with col2:
            st.markdown("**Exact Solution:**")
            st.code(f"∫x²dx = (b³-a³)/3 = {exact:.4f}")
            st.code(f"Error (trapezoidal): {abs(trap_sum - exact):.6f}")
        
        # Visualization
        fig, ax = plt.subplots(figsize=(8, 4))
        x_vis = np.linspace(a, b, 100)
        y_vis = f(x_vis)
        ax.plot(x_vis, y_vis, 'b-', label='f(x) = x²')
        
        # Show rectangles
        for i in range(n):
            x_rect = x[i:i+2]
            y_rect = f(x[i])
            ax.bar(x_rect[0], y_rect, width=dx, alpha=0.3, color='lightblue', edgecolor='blue')
        
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')
        ax.set_title(f'Numerical Integration: ∫{a}^{b} x² dx')
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    
    def render(self):
        """Render all calculus demonstrations"""
        st.markdown("## Calculus")
        
        self.derivatives_demo()
        st.markdown("---")
        self.chain_rule_demo()
        st.markdown("---")
        self.gradient_descent_demo()
        st.markdown("---")
        self.integration_demo()
        
        st.markdown("### Calculus Concepts")
        st.markdown("""
        **Derivative**: Instantaneous rate of change
        **Gradient**: Vector of partial derivatives for multivariable functions
        **Chain Rule**: (f∘g)'(x) = f'(g(x)) × g'(x)
        **Gradient Descent**: Iterative optimization using negative gradient direction
        **Integration**: Area under the curve using Riemann sums
        """)
