try:
    from llama_index.core.agent import ReActAgent
    print("ReActAgent imported successfully")
    try:
        agent = ReActAgent(tools=[], llm=None)
        print("Instantiated successfully")
    except Exception as e:
        print(f"Instantiation failed: {e}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
