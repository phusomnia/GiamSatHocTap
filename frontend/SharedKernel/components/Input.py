# components/ui/Input.py
import streamlit as st
import streamlit.components.v2 as components


def Input(placeholder="", value="", key="input", on_change=None):
    component = components.component(
        name=f"react_input_{key}",
        html=f"""
        <input 
            id="input_{key}" 
            placeholder="{placeholder}" 
            value=""
            class="input"
        />
        """,
        css="""
        .input {
            padding: 10px 14px;
            border-radius: 8px;
            border: 1px solid #ccc;
            outline: none;
            font-size: 14px;
            width: 100%;
        }

        .input:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 2px rgba(79,70,229,0.2);
        }
        """,
        js=f"""
        export default function(component) {{
            const {{ parentElement, data, setStateValue }} = component;
            const input = parentElement.querySelector("#input_{key}");

            // Smooth update: only set value if different to avoid cursor jump
            const newValue = data?.value || "";
            if (input.value !== newValue) {{
                input.value = newValue;
            }}

            // Send state on change
            input.addEventListener("input", (e) => {{
                setStateValue("value", e.target.value);
            }});
        }}
        """
    )

    result = component(
        data={"value": value},
        default={"value": value},
        on_value_change=on_change,
        key=key
    )

    return result