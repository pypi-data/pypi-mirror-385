"""SendTemplateNode for sending WhatsApp templates in flows."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from .base import Node
from kapso.builder.ai.field import AIField

TemplateParameters = Optional[Union[Dict[str, Any], List[Any], AIField]]


def _convert_parameters(
    parameters: Union[Dict[str, Any], List[Any]],
    path_prefix: str,
    ai_field_config: Dict[str, Dict[str, Any]],
) -> Union[Dict[str, Any], List[Any]]:
    """Convert nested parameters, capturing AIField markers for backend config."""

    def _set_ai_config(path: str, config_value: Dict[str, Any]) -> None:
        ai_field_config[path] = config_value
        if path.startswith("parameters"):
            alias_path = path.replace("parameters", "template_params", 1)
            ai_field_config[alias_path] = config_value

    def _transform(value: Any, path: str) -> Any:
        if isinstance(value, AIField):
            _set_ai_config(path, value.to_config())
            return value.to_dict()
        if isinstance(value, list):
            return [
                _transform(item, f"{path}.{index}" if path else str(index))
                for index, item in enumerate(value)
            ]
        if isinstance(value, dict):
            return {
                key: _transform(item, f"{path}.{key}" if path else key)
                for key, item in value.items()
            }
        return value

    return _transform(parameters, path_prefix)


class SendTemplateNode(Node):
    """Node for sending WhatsApp message templates."""

    def __init__(
        self,
        id: str,
        whatsapp_config_id: Optional[str] = None,
        template_id: Optional[str] = None,
        template_params: TemplateParameters = None,
        provider_model_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        # Support new keyword `parameters` while keeping backwards compatibility with
        # the legacy `template_params` argument.
        if "parameters" in kwargs:
            if template_params is not None:
                raise ValueError("Use either template_params or parameters, not both")
            template_params = kwargs.pop("parameters")

        if kwargs:
            unexpected = ", ".join(kwargs.keys())
            raise TypeError(f"Unexpected keyword arguments: {unexpected}")

        if template_id is None:
            raise ValueError("template_id is required for SendTemplateNode")

        config: Dict[str, Any] = {
            "template_id": template_id,
        }
        if whatsapp_config_id is not None:
            config["whatsapp_config_id"] = whatsapp_config_id

        ai_config: Dict[str, Dict[str, Any]] = {}
        has_ai_fields = False

        processed_parameters: TemplateParameters = template_params

        if template_params is not None:
            if isinstance(template_params, AIField):
                config["parameters"] = template_params.to_dict()
                config["template_params"] = config["parameters"]
                ai_config["parameters"] = template_params.to_config()
                ai_config["template_params"] = ai_config["parameters"]
                has_ai_fields = True
            elif isinstance(template_params, (dict, list)):
                processed_parameters = template_params
                converted = _convert_parameters(template_params, "parameters", ai_config)
                config["parameters"] = converted
                config["template_params"] = converted
                has_ai_fields = bool(ai_config)
            else:
                raise TypeError(
                    "template parameters must be a dict, list, or AIField"
                )

        if has_ai_fields:
            config["ai_field_config"] = ai_config
            if not provider_model_name:
                raise ValueError("provider_model_name required when using AIField")

        if provider_model_name:
            config["provider_model_name"] = provider_model_name

        # Keep original parameters for property access (avoid mutation of user input).
        self._parameters = processed_parameters

        super().__init__(
            id=id,
            node_type="send_template",
            config=config,
        )

    @property
    def whatsapp_config_id(self) -> Optional[str]:
        """Get the WhatsApp config ID if explicitly set."""
        return self.config.get("whatsapp_config_id")

    @property
    def template_id(self) -> str:
        """Get the template ID."""
        return self.config["template_id"]

    @property
    def parameters(self) -> TemplateParameters:
        """Get the template parameters."""
        return self._parameters

    @property
    def template_params(self) -> TemplateParameters:
        """Backwards-compatible alias for template parameters."""
        return self.parameters

    @property
    def provider_model_name(self) -> Optional[str]:
        """Get the provider model name."""
        return self.config.get("provider_model_name")
