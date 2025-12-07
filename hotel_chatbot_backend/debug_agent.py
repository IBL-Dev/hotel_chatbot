
try:
    from llama_index.core.agent import ReActAgent
    print("ReActAgent imported successfully.")
    print("Attributes:", dir(ReActAgent))
    if hasattr(ReActAgent, 'from_tools'):
        print("from_tools exists.")
    else:
        print("from_tools DOES NOT exist.")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
