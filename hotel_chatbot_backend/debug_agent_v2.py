
try:
    from llama_index.core.agent import ReActAgent
    print("Direct Import: Success")
except ImportError:
    print("Direct Import: Failed")

try:
    from llama_index.core.agent.workflow import ReActAgent as NewReActAgent
    print("Workflow Import: Success")
    if hasattr(NewReActAgent, 'from_tools'):
        print("NewReActAgent.from_tools: Exists")
    else:
        print("NewReActAgent.from_tools: DOES NOT interact")
except ImportError:
    print("Workflow Import: Failed")
