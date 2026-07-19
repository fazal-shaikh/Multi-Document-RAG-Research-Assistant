import re
with open("c:\\Users\\Lenovo\\OneDrive\\Desktop\\Multi-Document RAG Research Assistant\\app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the start of the Session Controls in sidebar
start_idx = content.find("    if st.session_state.vector_db is not None:\n        st.markdown('<div class=\"sidebar-header\">⚙️ Session Controls</div>', unsafe_allow_html=True)")
if start_idx == -1:
    print("Could not find start_idx")

# Find the end of the Export section
end_idx = content.find("                st.info(\"No chat history to export yet.\")") + len("                st.info(\"No chat history to export yet.\")") + 1

if start_idx != -1 and end_idx != -1:
    sidebar_controls = content[start_idx:end_idx]
    
    # Remove it from its current position
    new_content = content[:start_idx] + content[end_idx:]
    
    # Append it at the end of the file, wrapped in `with st.sidebar:` just in case it's no longer in the sidebar context
    # Wait, the block currently expects to be indented by 4 spaces inside `with st.sidebar:`
    # Let's unindent it by 4 spaces, and wrap it
    
    # Actually, it's easier to just do:
    sidebar_controls_unindented = "\n".join([line[4:] if line.startswith("    ") else line for line in sidebar_controls.split("\n")])
    
    append_content = "\n\n# Post-Processing Sidebar Updates\nwith st.sidebar:\n" + "\n".join(["    " + line for line in sidebar_controls_unindented.split("\n")])
    
    new_content = new_content + append_content
    
    with open("c:\\Users\\Lenovo\\OneDrive\\Desktop\\Multi-Document RAG Research Assistant\\app.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully moved sidebar controls to bottom of file")
else:
    print("Failed to find boundaries")
