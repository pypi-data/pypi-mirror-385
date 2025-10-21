from typing import Dict, Any


def model_name_from_container_or_model(params: Dict[str, Any]) -> str:
    """
    checks params for container. if its there, uses maniac:container as model name.
    if theres no container, checks for model. if theres a model, uses it.
    if theres no container or model, uses openai/gpt-4.1 (default model) as model name.
    """
    container = params.get("container", None)
    if container and not isinstance(container, str):
        container = container.get("label")
        model_name = f"maniac:{container}"
    model = params.get("model", None)
    if model and not container:
        model_name = model
    if not model_name:
        model_name = "openai/gpt-4.1"
    return model_name
