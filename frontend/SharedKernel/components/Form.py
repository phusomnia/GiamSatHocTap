import streamlit as st
import streamlit.components.v2 as components


def Option(label: str, value: str) -> dict:
    return {"label": label, "value": value}


def Select(options: list, value: list, key: str, on_change=None, placeholder="Select..."):
    options_html = "".join([
        f'<option value="{opt.get("value", "")}">{opt.get("label", "")}</option>'
        for opt in options
    ])

    component = components.component(
        name=f"react_select_{key}",
        html=f"""
        <select
            id="select_{key}"
            multiple
            class="select"
            placeholder="{placeholder}"
        >
            {options_html}
        </select>
        """,
        css="""
        .select {
            padding: 10px 14px;
            border-radius: 8px;
            border: 1px solid #ccc;
            outline: none;
            font-size: 14px;
            width: 100%;
            min-height: 42px;
            background-color: white;
            cursor: pointer;
        }

        .select:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 2px rgba(79,70,229,0.2);
        }

        .select option {
            padding: 8px;
        }
        """,
        js=f"""
        export default function(component) {{
            const {{ parentElement, data, setStateValue }} = component;
            const select = parentElement.querySelector("#select_{key}");

            // Smooth update: only sync if different
            const selectedValues = data?.value || [];
            const currentSelected = Array.from(select.selectedOptions).map(o => o.value);
            
            if (JSON.stringify(selectedValues) !== JSON.stringify(currentSelected)) {{
                Array.from(select.options).forEach(opt => {{
                    opt.selected = selectedValues.includes(opt.value);
                }});
            }}

            // Send state on change
            select.addEventListener("change", (e) => {{
                const selected = Array.from(e.target.selectedOptions).map(opt => opt.value);
                setStateValue("value", selected);
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


def Date(value: str, key: str, on_change=None, format: str = "%Y-%m-%d"):
    input_type = "date"
    if "%H" in format or "%M" in format or "%S" in format:
        input_type = "datetime-local"
    elif "%H" in format or "%M" in format:
        input_type = "time"

    component = components.component(
        name=f"react_date_{key}",
        html=f"""
        <input
            id="date_{key}"
            type="{input_type}"
            value=""
            class="date-input"
        />
        """,
        css="""
        .date-input {
            padding: 10px 14px;
            border-radius: 8px;
            border: 1px solid #ccc;
            outline: none;
            font-size: 14px;
            width: 100%;
            font-family: inherit;
        }

        .date-input:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 2px rgba(79,70,229,0.2);
        }
        """,
        js=f"""
        export default function(component) {{
            const {{ parentElement, data, setStateValue }} = component;
            const input = parentElement.querySelector("#date_{key}");

            // Initialize from data
            if (data?.value) {{
                input.value = data.value;
            }}

            // Send state on change
            input.addEventListener("change", (e) => {{
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


def Checkbox(label: str, value: bool, key: str, on_change=None):
    component = components.component(
        name=f"react_checkbox_{key}",
        html=f"""
        <div class="checkbox-wrapper" id="wrapper_{key}">
            <input type="checkbox" id="checkbox_{key}" class="checkbox" />
            <label for="checkbox_{key}" class="checkbox-label">{label}</label>
        </div>
        """,
        css="""
        .checkbox-wrapper {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 0;
        }

        .checkbox {
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: #4f46e5;
        }

        .checkbox-label {
            font-size: 14px;
            cursor: pointer;
            user-select: none;
        }
        """,
        js=f"""
        export default function(component) {{
            const {{ parentElement, data, setStateValue }} = component;
            const checkbox = parentElement.querySelector("#checkbox_{key}");

            // Smooth update: only set if different
            const newValue = !!data?.value;
            if (checkbox.checked !== newValue) {{
                checkbox.checked = newValue;
            }}

            // Send state on change
            checkbox.addEventListener("change", (e) => {{
                setStateValue("value", e.target.checked);
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


def Radio(options: list, value: str, key: str, on_change=None):
    options_html = "".join([
        f'''
        <div class="radio-option">
            <input type="radio" id="radio_{key}_{opt.get("value", "")}" name="radio_{key}" value="{opt.get("value", "")}" class="radio" />
            <label for="radio_{key}_{opt.get("value", "")}" class="radio-label">{opt.get("label", "")}</label>
        </div>
        '''
        for opt in options
    ])

    component = components.component(
        name=f"react_radio_{key}",
        html=f"""
        <div class="radio-group" id="group_{key}">
            {options_html}
        </div>
        """,
        css="""
        .radio-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 8px 0;
        }

        .radio-option {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .radio {
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: #4f46e5;
        }

        .radio-label {
            font-size: 14px;
            cursor: pointer;
            user-select: none;
        }
        """,
        js=f"""
        export default function(component) {{
            const {{ parentElement, data, setStateValue }} = component;
            const radios = parentElement.querySelectorAll(".radio");
            const currentValue = data?.value || "";

            // Smooth update: only update if different
            radios.forEach(radio => {{
                const shouldBeChecked = radio.value === currentValue;
                if (radio.checked !== shouldBeChecked) {{
                    radio.checked = shouldBeChecked;
                }}
            }});

            // Send state on change
            radios.forEach(radio => {{
                radio.addEventListener("change", (e) => {{
                    if (e.target.checked) {{
                        setStateValue("value", e.target.value);
                    }}
                }});
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


def TextArea(value: str, key: str, on_change=None, placeholder: str = "", rows: int = 4):
    component = components.component(
        name=f"react_textarea_{key}",
        html=f"""
        <textarea
            id="textarea_{key}"
            class="textarea"
            placeholder="{placeholder}"
            rows="{rows}"
        ></textarea>
        """,
        css="""
        .textarea {
            padding: 10px 14px;
            border-radius: 8px;
            border: 1px solid #ccc;
            outline: none;
            font-size: 14px;
            width: 100%;
            font-family: inherit;
            resize: vertical;
            min-height: 100px;
        }

        .textarea:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 2px rgba(79,70,229,0.2);
        }
        """,
        js=f"""
        export default function(component) {{
            const {{ parentElement, data, setStateValue }} = component;
            const textarea = parentElement.querySelector("#textarea_{key}");

            // Smooth update: only set if different to avoid cursor jump
            const newValue = data?.value || "";
            if (textarea.value !== newValue) {{
                textarea.value = newValue;
            }}

            // Send state on change
            textarea.addEventListener("input", (e) => {{
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