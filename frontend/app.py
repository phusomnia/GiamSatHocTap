import streamlit as st
import importlib
from pathlib import Path

st.set_page_config(
    page_title="Hello",
    page_icon="👋"
)

st.write("# Welcome to Streamlit! 👋")


PAGES_DIR = Path(__file__).parent / "pages"

def discover_pages():
    pages = []
    root_page = None

    # First, check for root index.py (pages/index.py)
    root_file = PAGES_DIR / "index.py"
    if root_file.exists():
        print(f"Found root file: {root_file}")  # Debug
        module_path = "pages.index"
        module = importlib.import_module(module_path)
        print(f"Root module imported: {module}")  # Debug
        
        root_page = st.Page(
            getattr(module, "render"),
            title="/"
        )
        pages.append(root_page)

    # Then find other index.py files in subdirectories
    for file in PAGES_DIR.rglob("index.py"):
        # Skip the root index.py since we already handled it
        if file == root_file:
            continue
            
        print(f"Found file: {file}")  # Debug
        relative_path = file.relative_to(PAGES_DIR.parent)
        module_path = (
            str(relative_path.with_suffix(""))
            .replace("/", ".")
            .replace("\\", ".")
        )

        print(f"Module path: {module_path}")  # Debug
        module = importlib.import_module(module_path)
        print(f"Module imported: {module}")  # Debug

        relative = file.relative_to(PAGES_DIR)
        print(f"Relative path: {relative}")  # Debug

        # Admin/Users/index.py
        # -> Admin / Users
        title = " / ".join(relative.parts[:-1])
        print(f"Title: {title}")  # Debug
        
        # Generate URL path
        url_path = str(relative.parent).lower().replace("\\", "/")
        print(f"Full URL: http://127.0.0.1:3000/{url_path}")  # Debug

        pages.append(
            st.Page(
                getattr(module, "render"),
                title=title,
                url_path=url_path
            )
        )

    # Sort non-root pages by title to ensure consistent order
    non_root_pages = [p for p in pages if p != root_page]
    non_root_pages.sort(key=lambda p: p.title)
    
    # Final order: root page first, then sorted other pages
    final_pages = []
    if root_page:
        final_pages.append(root_page)
    final_pages.extend(non_root_pages)

    print(f"Found {len(final_pages)} pages")  # Debug
    return final_pages


pg = st.navigation(
    discover_pages(),
    position="hidden"
)

pg.run()