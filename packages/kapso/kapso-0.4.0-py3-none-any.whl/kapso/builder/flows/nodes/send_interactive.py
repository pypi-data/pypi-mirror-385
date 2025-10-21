"""SendInteractiveNode for sending interactive WhatsApp messages in flows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Union

from .base import Node
from kapso.builder.ai.field import AIField


@dataclass
class InteractiveButton:
    """Helper representing a reply button."""

    id: str
    title: str

    def to_dict(self) -> Dict[str, str]:
        """Convert the button to the backend format."""
        return {"id": self.id, "title": self.title}


@dataclass
class ListRow:
    """Helper representing a row within an interactive list section."""

    id: str
    title: str
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        """Convert the row to the backend format."""
        data = {"id": self.id, "title": self.title}
        if self.description is not None:
            data["description"] = self.description
        return data


@dataclass
class ListSection:
    """Helper representing an interactive list section."""

    title: Optional[str]
    rows: Sequence[Union[ListRow, Dict[str, Any]]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the section (and nested rows) to backend format."""
        data: Dict[str, Any] = {}
        if self.title is not None:
            data["title"] = self.title
        data["rows"] = [
            row.to_dict() if isinstance(row, ListRow) else row for row in self.rows
        ]
        return data


InteractiveBody = Union[str, AIField]


def _normalise_buttons(
    buttons: Sequence[Union[InteractiveButton, Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """Normalise button inputs to plain dictionaries."""

    normalised: List[Dict[str, Any]] = []
    for button in buttons:
        if isinstance(button, InteractiveButton):
            normalised.append(button.to_dict())
        elif isinstance(button, dict):
            normalised.append(button)
        else:
            raise TypeError("Buttons must be InteractiveButton or dict instances")
    return normalised


def _normalise_sections(
    sections: Sequence[Union[ListSection, Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """Normalise list section inputs to plain dictionaries."""

    normalised: List[Dict[str, Any]] = []
    for section in sections:
        if isinstance(section, ListSection):
            normalised.append(section.to_dict())
        elif isinstance(section, dict):
            normalised.append(section)
        else:
            raise TypeError("List sections must be ListSection or dict instances")
    return normalised


class SendInteractiveNode(Node):
    """Node for sending interactive WhatsApp messages (lists, buttons, CTAs)."""

    def __init__(
        self,
        id: str,
        whatsapp_config_id: Optional[str] = None,
        interactive_type: Optional[str] = None,
        body_text: Optional[InteractiveBody] = None,
        *,
        header_type: Optional[str] = None,
        header_text: Optional[InteractiveBody] = None,
        header_media_url: Optional[str] = None,
        footer_text: Optional[InteractiveBody] = None,
        buttons: Optional[Sequence[Union[InteractiveButton, Dict[str, Any]]]] = None,
        list_button_text: Optional[str] = None,
        list_sections: Optional[Sequence[Union[ListSection, Dict[str, Any]]]] = None,
        cta_display_text: Optional[str] = None,
        cta_url: Optional[str] = None,
        flow_id: Optional[str] = None,
        flow_cta: Optional[str] = None,
        flow_token: Optional[str] = None,
        provider_model_name: Optional[str] = None,
    ) -> None:
        if interactive_type is None:
            raise ValueError("interactive_type is required for SendInteractiveNode")
        if body_text is None:
            raise ValueError("body_text is required for SendInteractiveNode")

        config: Dict[str, Any] = {
            "interactive_type": interactive_type,
            "body_text": body_text.to_dict() if isinstance(body_text, AIField) else body_text,
        }
        if whatsapp_config_id is not None:
            config["whatsapp_config_id"] = whatsapp_config_id

        ai_config: Dict[str, Dict[str, Any]] = {}
        has_ai_fields = False

        if isinstance(body_text, AIField):
            ai_config["body_text"] = body_text.to_config()
            has_ai_fields = True

        if header_type:
            config["header_type"] = header_type

        if header_text is not None:
            config["header_text"] = (
                header_text.to_dict() if isinstance(header_text, AIField) else header_text
            )
            if isinstance(header_text, AIField):
                ai_config["header_text"] = header_text.to_config()
                has_ai_fields = True

        if header_media_url:
            config["header_media_url"] = header_media_url

        if footer_text is not None:
            config["footer_text"] = (
                footer_text.to_dict() if isinstance(footer_text, AIField) else footer_text
            )
            if isinstance(footer_text, AIField):
                ai_config["footer_text"] = footer_text.to_config()
                has_ai_fields = True

        if buttons is not None:
            config["buttons"] = _normalise_buttons(buttons)

        if list_button_text is not None:
            config["list_button_text"] = list_button_text

        if list_sections is not None:
            config["list_sections"] = _normalise_sections(list_sections)

        if cta_display_text is not None:
            config["cta_display_text"] = cta_display_text

        if cta_url is not None:
            config["cta_url"] = cta_url

        if flow_id is not None:
            config["flow_id"] = flow_id

        if flow_cta is not None:
            config["flow_cta"] = flow_cta

        if flow_token is not None:
            config["flow_token"] = flow_token

        if has_ai_fields:
            config["ai_field_config"] = ai_config
            if not provider_model_name:
                raise ValueError("provider_model_name required when using AIField")

        if provider_model_name:
            config["provider_model_name"] = provider_model_name

        # Store originals for property access
        self._body_text = body_text
        self._header_type = header_type
        self._header_text = header_text
        self._header_media_url = header_media_url
        self._footer_text = footer_text
        self._buttons = list(buttons) if buttons is not None else None
        self._list_button_text = list_button_text
        self._list_sections = list(list_sections) if list_sections is not None else None
        self._cta_display_text = cta_display_text
        self._cta_url = cta_url
        self._flow_id = flow_id
        self._flow_cta = flow_cta
        self._flow_token = flow_token

        super().__init__(
            id=id,
            node_type="send_interactive",
            config=config,
        )

    @property
    def whatsapp_config_id(self) -> Optional[str]:
        """Get the WhatsApp config ID if explicitly set."""
        return self.config.get("whatsapp_config_id")

    @property
    def interactive_type(self) -> str:
        """Get the interactive type."""
        return self.config["interactive_type"]

    @property
    def body_text(self) -> InteractiveBody:
        """Get the body text."""
        return self._body_text

    @property
    def header_type(self) -> Optional[str]:
        """Get the header type."""
        return self._header_type

    @property
    def header_text(self) -> Optional[InteractiveBody]:
        """Get the header text."""
        return self._header_text

    @property
    def header_media_url(self) -> Optional[str]:
        """Get the header media URL."""
        return self._header_media_url

    @property
    def footer_text(self) -> Optional[InteractiveBody]:
        """Get the footer text."""
        return self._footer_text

    @property
    def buttons(self) -> Optional[Sequence[Union[InteractiveButton, Dict[str, Any]]]]:
        """Get the button configuration."""
        return self._buttons

    @property
    def list_button_text(self) -> Optional[str]:
        """Get the list button text."""
        return self._list_button_text

    @property
    def list_sections(self) -> Optional[Sequence[Union[ListSection, Dict[str, Any]]]]:
        """Get the list sections."""
        return self._list_sections

    @property
    def cta_display_text(self) -> Optional[str]:
        """Get the CTA button display text."""
        return self._cta_display_text

    @property
    def cta_url(self) -> Optional[str]:
        """Get the CTA url."""
        return self._cta_url

    @property
    def flow_id(self) -> Optional[str]:
        """Get the WhatsApp Flow ID."""
        return self._flow_id

    @property
    def flow_cta(self) -> Optional[str]:
        """Get the WhatsApp Flow CTA label."""
        return self._flow_cta

    @property
    def flow_token(self) -> Optional[str]:
        """Get the WhatsApp Flow token."""
        return self._flow_token

    @property
    def provider_model_name(self) -> Optional[str]:
        """Get the provider model name."""
        return self.config.get("provider_model_name")

    @property
    def ai_field_config(self) -> Optional[Dict[str, Any]]:
        """Get the AI field configuration."""
        return self.config.get("ai_field_config")


__all__ = [
    "SendInteractiveNode",
    "InteractiveButton",
    "ListRow",
    "ListSection",
]
