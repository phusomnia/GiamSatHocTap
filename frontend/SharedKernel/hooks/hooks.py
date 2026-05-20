import streamlit as st
import hashlib
import json
from typing import Callable, TypeVar

T = TypeVar("T")

def use_state(key: str, initial: T):

    if key not in st.session_state:
        st.session_state[key] = initial

    def set_state(value: T | Callable[[T], T]):
        current = st.session_state[key]

        # React-style: setState(prev => newValue)
        if callable(value):
            st.session_state[key] = value(current)
        else:
            st.session_state[key] = value

        # Don't call rerun if we're already in a callback (component on_change)
        # The component's setStateValue already triggered a rerun
        if not st.session_state.get("_in_callback", False):
            st.rerun()

    return st.session_state[key], set_state

def _hash(deps):
    return hashlib.md5(json.dumps(deps, default=str).encode()).hexdigest()

def use_effect(fn, deps=None):
    deps = deps or []
    key = f"effect_{_hash(deps)}"

    if key not in st.session_state:
        st.session_state[key] = True
        fn()