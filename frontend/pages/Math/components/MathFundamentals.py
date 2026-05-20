import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from .DataStructures import DataStructures
from .MatrixOperations import MatrixOperations
from .LinearAlgebraComponents import LinearAlgebraComponents
from .Calculus import Calculus
from .Probability import Probability

def MathFundamentals():
    """
    Component displaying fundamental mathematical operations and concepts
    including linear algebra, calculus, and probability.
    """
    
    st.markdown("# Mathematical Fundamentals")
    
    # Tab navigation for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Data Structures", 
        "🔄 Matrix Operations", 
        "🔢 Linear Algebra", 
        "📈 Calculus", 
        "🎲 Probability"
    ])
    
    with tab1:
        data_structures = DataStructures()
        data_structures.render()
    
    with tab2:
        matrix_ops = MatrixOperations()
        matrix_ops.render()
    
    with tab3:
        linear_algebra = LinearAlgebraComponents()
        linear_algebra.render()
    
    with tab4:
        calculus = Calculus()
        calculus.render()
    
    with tab5:
        probability = Probability()
        probability.render()
            
            
