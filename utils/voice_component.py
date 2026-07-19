import streamlit.components.v1 as components
import os

# Define the component path
parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "voice_recorder")

# Declare the component
_voice_recorder = components.declare_component("voice_recorder", path=build_dir)

def voice_recorder_component(key=None):
    """
    Renders the custom premium voice recorder component.
    Returns the base64 audio string when recording stops.
    """
    return _voice_recorder(key=key, default=None)
