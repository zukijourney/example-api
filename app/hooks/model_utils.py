from ..providers import PROVIDER_LIST

def get_all_models(type: str = "any") -> list:
    """Return a list of all available models."""

    models = []

    for provider in PROVIDER_LIST:
        for model in provider.ai_models:
            if model["type"] == type or type == "any":
                model_dict = {
                    "id": model["id"],
                    "type": model["type"],
                    "premium_only": model["premium"]
                }

                if model_dict["type"] == "audio.speech":
                    model_dict["voices"] = model["voices"]
                    
                models.append(model_dict)
    
    return models