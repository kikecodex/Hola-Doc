
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config
try:
    print("Testing Config validation...")
    Config.validate()
    print("Config OK.")
except Exception as e:
    print(f"Config Error: {e}")

try:
    print("Importing RagEngine...")
    from engine.rag_engine import RagEngine
    print("Initializing RagEngine...")
    rag = RagEngine()
    print("RagEngine Initialized.")
except Exception as e:
    print(f"RagEngine Error: {e}")
    import traceback
    traceback.print_exc()

try:
    print("Importing ConversationEngine...")
    from engine.conversation import ConversationEngine
    print("Initializing ConversationEngine...")
    conv = ConversationEngine()
    print("ConversationEngine Initialized.")
except Exception as e:
    print(f"ConversationEngine Error: {e}")
    import traceback
    traceback.print_exc()
