import os
import importlib
import typing

def get_all_models(formatted: bool = False, type: str = "any") -> typing.Union[list, tuple]:
    """Returns a list of all available models by dinamically importing all providers."""

    models = []
    providers_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "providers"))

    for _, _, files in os.walk(providers_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module = importlib.import_module(f"app.providers.{file[:-3]}")
                for _, obj in module.__dict__.items():
                    if hasattr(obj, "ai_models"):
                        if formatted:
                            for model in obj.ai_models:
                                if model["type"] == type or type == "any":
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
                                if model["type"] == type or type == "any":
                                    models.append(model["id"])

    return models

def get_all_provider_classes() -> list:
    """Returns a list of all available providers classes."""

    providers = []
    providers_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "providers"))

    for _, _, files in os.walk(providers_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module = importlib.import_module(f"app.providers.{file[:-3]}")
                for _, obj in module.__dict__.items():
                    if hasattr(obj, "ai_models"):
                        providers.append(obj)
                        
    return providers

def get_provider_class(model: str) -> typing.Optional[typing.Any]:
    """Returns the provider class based on the model."""

    providers = get_all_provider_classes()

    for provider in providers:
        for provider_model in provider.__dict__["ai_models"]:
            if model == provider_model["id"]:
                return provider

    return None