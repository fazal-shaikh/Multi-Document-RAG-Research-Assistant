import re

app_path = r"c:\Users\Lenovo\OneDrive\Desktop\Multi-Document RAG Research Assistant\app.py"

with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update the CSS class name
content = content.replace(".word-anim {", ".letter-anim {")
content = content.replace("wordPulse", "letterPulse")

# Generate the new HTML
base_delay = 0.05

def generate_spans(text, start_delay, add_class=""):
    html = ""
    delay = start_delay
    for char in text:
        if char == " ":
            html += " "
            delay += base_delay
            continue
        classes = f"letter-anim {add_class}".strip()
        html += f'<span class="{classes}" style="animation-delay: {delay:.2f}s;">{char}</span>'
        delay += base_delay
    return html, delay

part1, delay = generate_spans("Welcome to ", 0.0)
part2, delay = generate_spans("AI Workspace!", delay, "gradient-text")

new_html = f'<h1 class="hero-title">\n{part1}\n{part2}\n</h1>'

# Find the old HTML
start_marker = '<h1 class="hero-title">'
end_marker = '</h1>'
start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx) + len(end_marker)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_html + content[end_idx:]

with open(app_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated title to letter-by-letter animation!")
