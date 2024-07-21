import os
import importlib
import typing

def get_all_models(formatted: bool = False) -> list:
    """Returns a list of all available models by dinamically importing all providers."""

    models = []

    for _, _, files in os.walk(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "providers"))):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module = importlib.import_module(f"api.providers.{file[:-3]}")
                for _, obj in module.__dict__.items():
                    if hasattr(obj, "ai_models"):
                        if formatted:
                            for model in obj.ai_models:
                                models.append({
                                    "id": model["id"],
                                    "type": model["type"],
                                    "owned_by": obj.provider_name,
                                    "created": 0,
                                    "endpoint": f"/v1/{model['type'].replace('.', '/')}",
                                    "premium": model["premium"]
                                })
                        else:
                            for model in obj.ai_models:
                                models.append(model["id"])

    return models

def get_provider_class(model: str) -> typing.Optional[typing.Any]:
    """Returns the provider class based on the model."""

    for _, _, files in os.walk(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "providers"))):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module = importlib.import_module(f"api.providers.{file[:-3]}")
                for _, obj in module.__dict__.items():
                    if hasattr(obj, "ai_models"):
                        if any(model in model_["id"] for model_ in obj.ai_models):
                            return obj
                        
    return None