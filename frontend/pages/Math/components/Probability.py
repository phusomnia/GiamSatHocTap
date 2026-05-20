import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

class Probability:
    """
    Class for demonstrating probability concepts:
    Bayes' theorem, distributions, and statistical inference
    """
    
    def __init__(self):
        pass

    def render(self):
        """Render all probability demonstrations"""
        st.markdown("## Probability")
        
        self.bayes_theorem()
        st.markdown("---")
        self.distributions()
    
    def bayes_theorem(self):
        """Demonstrate Bayes' theorem with cat classifier example"""
        st.markdown("### Bayes' Theorem")
        st.markdown("**P(A|B) = [P(B|A) × P(A)] / P(B)**")
        
        st.markdown("#### Cat Classifier Example")
        st.markdown("""
        Given:
        - P(Cat) = 0.1 (10% of images contain cats)
        - P(Whiskers|Cat) = 0.9 (90% of cat images have whiskers)
        - P(Whiskers|NoCat) = 0.2 (20% of non-cat images still have whisker-like objects)
        
        Question: If we see whiskers, what's the probability it's a cat?
        """)
        
        # Interactive Bayes calculation
        p_cat = st.slider("P(Cat)", 0.0, 1.0, 0.1)
        p_whiskers_given_cat = st.slider("P(Whiskers|Cat)", 0.0, 1.0, 0.9)
        p_whiskers_given_no_cat = st.slider("P(Whiskers|NoCat)", 0.0, 1.0, 0.2)
        
        p_no_cat = 1 - p_cat
        
        # Evidence
        p_whiskers = (p_whiskers_given_cat * p_cat + p_whiskers_given_no_cat * p_no_cat)
        
        # Posterior (Bayes)
        p_cat_given_whiskers = (p_whiskers_given_cat * p_cat) / p_whiskers
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Calculations:**")
            st.code(f"P(Whiskers) = {p_whiskers:.4f}")
            st.code(f"P(Cat | Whiskers) = {p_cat_given_whiskers:.4f}")
            st.code(f"Probability = {p_cat_given_whiskers * 100:.2f}%")
        
        with col2:
            # Visual representation
            fig, ax = plt.subplots(figsize=(6, 4))
            categories = ["Cat", "No Cat"]
            probabilities = [p_cat_given_whiskers, 1 - p_cat_given_whiskers]
            colors = ["lightcoral", "lightblue"]
            
            ax.bar(categories, probabilities, color=colors)
            ax.set_ylabel("Probability")
            ax.set_title("P(Category | Whiskers)")
            ax.set_ylim(0, 1)
            
            # Add percentage labels
            for i, (cat, prob) in enumerate(zip(categories, probabilities)):
                ax.text(i, prob + 0.02, f"{prob*100:.1f}%", ha="center", va="bottom")
            
            st.pyplot(fig)
    
    def distributions(self):
        """Demonstrate common probability distributions"""
        st.markdown("### Probability Distributions")
        
        # Distribution selection
        dist_type = st.selectbox("Select Distribution", [
            "Bernoulli", 
            "Binomial", 
            "Normal (Gaussian)",
            "Poisson"
        ])

        st.markdown("### Probability Concepts")
        self.Bernoulli()
        self.Gaussian()

    def Bernoulli(self):
        st.markdown("""
        Bernoulli (xac xuat roi rac):
        - phep thu co ket qua 1 va 0
        * Ham khoi xac suat (PMF):
        """)
        st.code("P(X=x) = p^x(1-p)^{1-x} với x in {0, 1}")
        st.markdown("""
        * Dinh ly Bernoulli
        """)
        st.code("P_n(k) = C_n^k * p^k * (1-p)^{n-k}")
        st.markdown("""
        * Dac trung: 
            Ky vong 
        Vi du: cho mo phong tung dong xu

        Gaussian (xac xuat lien tuc)
        - Phan phoi chuan (Normal Distribution)\n
        """)
        st.code("Cong thuc: f(x) = (1/(σ√(2π))) × e^(-(x-μ)²/(2σ²))")
        p = 0.5
        n_flips = 10
        n_exp = 10000

        st.markdown("""
        Example code:
        """)

        def PMF(p, x):
            return (p ** x) * ((1 - p) ** (1 - x))

        # Simulate a single coin flip (0 = Tails, 1 = Heads)
        flip_result = np.random.binomial(1, p)
        st.code(f"Result of flip: {'Head' if flip_result == 1 else 'Tail'}")
        
        # Show PMF values for both outcomes
        st.code(f"P(Tails) = PMF({p}, 0) = {PMF(p, 0):.4f}")
        st.code(f"P(Heads) = PMF({p}, 1) = {PMF(p, 1):.4f}")

    def gaussian_f(self, 
        x: float, 
        mu: float, 
        sigma: float
    ): return (1 / (sigma * np.sqrt(2 * math.pi))) * \
           np.exp(-((x - mu) ** 2) / (2 * sigma ** 2)) 

    def Gaussian(self):
        st.markdown("""
        Đặc trưng:
            μ (mu): giá trị trung bình kỳ vọng
            σ (sigma): độ lệch chuẩn
        """)

        x = 2
        mu = 4
        sigma = 2
        result = self.gaussian_f(x, mu, sigma)
        st.code(f"gaussian_f({x}) = {result:.6f}")
        
        # Show the formula
        st.code(f"With μ={mu}, σ={sigma}, x={x}")

t = Probability()
t.gaussian_f(2, 4, 2)