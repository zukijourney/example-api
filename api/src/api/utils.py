from typing import Dict, List, Any, Set
from dataclasses import dataclass
from ..providers import BaseProvider

@dataclass
class ModelMetadata:
    free_models: Set[str]
    pricing: Dict[str, Any]
    multipliers: Dict[str, float]

class ModelListGenerator:
    @staticmethod
    def _collect_model_metadata() -> ModelMetadata:
        providers = BaseProvider.__subclasses__()
        
        return ModelMetadata(
            free_models={
                model 
                for provider in providers 
                for model in provider.config.free_models
            },
            pricing={
                model: pricing 
                for provider in providers 
                for model, pricing in provider.config.model_prices.items()
            },
            multipliers={
                model: multiplier 
                for provider in providers 
                for model, multiplier in provider.config.model_multipliers.items()
            }
        )

    @staticmethod
    def _create_model_entry(
        model: str,
        metadata: ModelMetadata
    ) -> Dict[str, Any]:
        return {
            'id': model,
            'object': 'model',
            'owned_by': 'zukijourney',
            'is_free': model in metadata.free_models,
            'pricing': {
                'credits': metadata.pricing.get(model, 'per_token'),
                'multiplier': metadata.multipliers.get(model, 1)
            }
        }

    @classmethod
    def generate(cls) -> List[Dict[str, Any]]:
        metadata = cls._collect_model_metadata()
        
        return [
            cls._create_model_entry(model, metadata)
            for model in BaseProvider.get_all_models()
        ]