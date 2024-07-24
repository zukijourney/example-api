import os
import importlib

def get_all_models() -> list:
    """Returns a list of all available models by dinamically importing all providers."""

    models = []

    for _, _, files in os.walk(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "providers"))):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module = importlib.import_module(f"api.providers.{file[:-3]}")
                for _, obj in module.__dict__.items():
                    if hasattr(obj, "ai_models"):
                        for model in obj.ai_models:
                            models.append({
                                "id": model["id"],
                                "type": model["type"],
                                "owned_by": obj.provider_name,
                                "created": 0,
                                "endpoint": f"/v1/{model['type'].replace('.', '/')}",
                                "premium": model["premium"]
                            })

    return models