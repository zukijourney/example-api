import typing
from ..providers import PROVIDER_LIST

def get_all_models(formatted: bool = False, type: str = "any") -> list:
    """Return a list of all available models."""

    if formatted:
        models = []
        for provider in PROVIDER_LIST:
            for model in provider.ai_models:
                if model["type"] == type or type == "any":
                    model_dict = {
                        "id": model["id"],
                        "type": model["type"],
                        "owned_by": model["owner"],
                        "endpoint": f"/v1/{model['type'].replace('.', '/')}",
                        "premium_only": model["premium"],
                        "pricing": {
                            "amount": model.get("cost", 100),
                            "multiplier": model.get("cost_multiplier", 1)
                        }
                    }

                    if model_dict["type"] == "audio.speech":
                        model_dict["voices"] = model["voices"]
                    
                    models.append(model_dict)
    else:
        models = [
            model["id"]
            for provider in PROVIDER_LIST
            for model in provider.ai_models
            if model["type"] == type or type == "any"
        ]

    return models

def get_provider_class(model: str) -> typing.Optional[typing.Any]:
    """Return the provider class based on the model."""

    for provider in PROVIDER_LIST:
        if any(model == provider_model["id"] for provider_model in provider.ai_models):
            return provider

    return None