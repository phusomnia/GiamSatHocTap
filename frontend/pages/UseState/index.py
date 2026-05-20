import streamlit as st
from SharedKernel.hooks.hooks import use_state
from SharedKernel.components.Button import Button
from SharedKernel.components.Input import Input
from SharedKernel.components.Form import Select, Option, Date, Checkbox, Radio, TextArea

def render():
    st.title("UseState Demo")

    # Counter section
    st.subheader("Counter")
    count, set_count = use_state("count", 0)
    st.write("Count:", count)

    def handle_incre():
        set_count(lambda c: c + 1)

    Button("+", key="counter_btn", on_click=handle_incre)

    st.divider()

    # Input section
    st.subheader("Input")
    text, set_text = use_state("text", "")

    def handle_input_change():
        val = st.session_state.get("chat_input", {}).get("value", "")
        st.session_state["text"] = val

    Input(
        placeholder="Type something...",
        value=text,
        key="chat_input",
        on_change=handle_input_change
    )

    st.write("You typed:", text)

    st.divider()

    # Select (Multi-select) section
    st.subheader("Select (Multi-select)")
    selected, set_selected = use_state("selected", [])

    options = [
        Option("Option 1", "opt1"),
        Option("Option 2", "opt2"),
        Option("Option 3", "opt3"),
        Option("Option 4", "opt4"),
        Option("Option 5", "opt5"),
    ]

    def handle_select_change():
        val = st.session_state.get("my_select", {}).get("value", [])
        st.session_state["selected"] = val

    Select(
        options=options,
        value=selected,
        key="my_select",
        on_change=handle_select_change,
        placeholder="Choose options..."
    )

    st.write("Selected:", selected)

    st.divider()

    # Date section
    st.subheader("Date")
    date_val, set_date = use_state("date_val", "")

    def handle_date_change():
        val = st.session_state.get("my_date", {}).get("value", "")
        st.session_state["date_val"] = val

    Date(
        value=date_val,
        key="my_date",
        on_change=handle_date_change,
        format="%Y-%m-%d"
    )

    st.write("Date:", date_val)

    st.divider()

    # Checkbox section
    st.subheader("Checkbox")
    checked, set_checked = use_state("checked", False)

    def handle_checkbox_change():
        val = st.session_state.get("terms", {}).get("value", False)
        st.session_state["checked"] = val

    Checkbox(
        label="I agree to the terms and conditions",
        value=checked,
        key="terms",
        on_change=handle_checkbox_change
    )

    st.write("Checked:", checked)

    st.divider()

    # Radio section
    st.subheader("Radio")
    radio_opts = [
        Option("Option A", "a"),
        Option("Option B", "b"),
        Option("Option C", "c"),
    ]
    selected_radio, set_radio = use_state("radio", "")

    def handle_radio_change():
        val = st.session_state.get("my_radio", {}).get("value", "")
        st.session_state["radio"] = val

    Radio(
        options=radio_opts,
        value=selected_radio,
        key="my_radio",
        on_change=handle_radio_change
    )

    st.write("Selected:", selected_radio)

    st.divider()

    # TextArea section
    st.subheader("TextArea")
    content, set_content = use_state("content", "")

    def handle_textarea_change():
        val = st.session_state.get("my_textarea", {}).get("value", "")
        st.session_state["content"] = val

    TextArea(
        value=content,
        key="my_textarea",
        on_change=handle_textarea_change,
        placeholder="Enter your message here...",
        rows=6
    )

    st.write("Content:", content)