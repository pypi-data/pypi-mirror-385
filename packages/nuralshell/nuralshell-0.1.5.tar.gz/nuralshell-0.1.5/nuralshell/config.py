import json
import os

# Define the directory where config will be stored (~/.nuralshell/)
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".nuralshell")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def load_config():
    """Loads configuration from the local file."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load config file. {e}")
        return {}

def save_config(config):
    """Saves configuration to the local file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"Error saving configuration: {e}")

def get_config_or_prompt():
    """Loads existing config or prompts the user for new details."""
    config = load_config()

    # 1. Select Provider
    Model_Provider_choice = config.get("provider", "2")
    if not config or input(f"Current provider is {Model_Provider_choice}. \nUse Existing? (Y/N): ").lower() == 'n':
        Model_Provider_choice = input("""Select the Model provider
    1. ChatGPT
    2. Gemini
    Default [2. Gemini]:
    """).strip() or "2"

    if Model_Provider_choice not in ['1', '2']:
        print("Invalid option. Exiting.")
        print("Selecting Default Model Provider Gemini")
        Model_Provider_choice = "2"
        return None, None
    
    provider_key = "gemini_api_key" if Model_Provider_choice == '2' else "openai_api_key"
    
    # 2. Get API Key from config or env
    API_KEY = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    API_KEY = API_KEY or config.get(provider_key, "")

    if not API_KEY or input(f"API Key found for {provider_key}. \nUse Existing? (Y/N): ").lower().strip() == 'n':
        API_KEY = input(f"Enter your API Key (for Provider {Model_Provider_choice}): ").strip()
        if not API_KEY:
            print("API Key is required. Exiting.")
            return None, None

    # 3. Get Model Name
    default_model = "gemini-2.5-flash" if Model_Provider_choice == '2' else "gpt-4o-mini"
    model_name = config.get("model_name", default_model)
    
    if not config or input(f"Current model is {model_name}. \nUse Existing? (Y/N): ").lower() == 'n':
        model_name = input(f"Enter Your Model Name (Default: {default_model}):").strip() or default_model

    # Save new configuration
    new_config = {
        "provider": Model_Provider_choice,
        "model_name": model_name,
        "openai_api_key": API_KEY if Model_Provider_choice == '1' else config.get("openai_api_key", ""),
        "gemini_api_key": API_KEY if Model_Provider_choice == '2' else config.get("gemini_api_key", ""),
    }
    # Only store the active key for ease of use
    new_config[provider_key] = API_KEY
    
    
    save_config(new_config)

    return Model_Provider_choice, API_KEY, model_name
