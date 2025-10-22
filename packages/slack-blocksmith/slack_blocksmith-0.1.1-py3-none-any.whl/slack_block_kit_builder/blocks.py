"""Blocks for Slack Block Kit."""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, field_validator

from .composition import MrkdwnText, PlainText
from .elements import Element
from .validators import (
    SlackConstraints,
    validate_block_id,
    validate_url,
)


class Block(BaseModel):
    """Base class for blocks."""

    type: str
    block_id: Optional[str] = None

    @field_validator("block_id")
    @classmethod
    def validate_block_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate block ID length."""
        return validate_block_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the block as a dictionary."""
        result = {"type": self.type}
        if self.block_id is not None:
            result["block_id"] = self.block_id
        return result


class Section(Block):
    """Section block."""

    type: Literal["section"] = "section"
    text: Optional[Union[PlainText, MrkdwnText]] = None
    fields: Optional[List[Union[PlainText, MrkdwnText]]] = None
    accessory: Optional[Element] = None

    def build(self) -> Dict[str, Any]:
        """Build the section block as a dictionary."""
        result = super().build()
        if self.text is not None:
            result["text"] = self.text.build()
        if self.fields is not None:
            result["fields"] = [field.build() for field in self.fields]
        if self.accessory is not None:
            result["accessory"] = self.accessory.build()
        return result

    @classmethod
    def create(
        cls,
        text: Optional[Union[str, PlainText, MrkdwnText]] = None,
        fields: Optional[List[Union[str, PlainText, MrkdwnText]]] = None,
        accessory: Optional[Element] = None,
        block_id: Optional[str] = None,
    ) -> "Section":
        """Create a section block with builder pattern."""
        # Handle text parameter - if it's already a text object, use it; if it's a string, create PlainText
        if text is None:
            text_obj = None
        elif isinstance(text, (PlainText, MrkdwnText)):
            text_obj = text
        else:
            text_obj = PlainText.create(text)

        # Handle fields parameter - convert strings to PlainText, keep text objects as-is
        if fields is None:
            field_objs = None
        else:
            field_objs = []
            for field in fields:
                if isinstance(field, (PlainText, MrkdwnText)):
                    field_objs.append(field)
                else:
                    field_objs.append(PlainText.create(field))

        return cls(
            text=text_obj,
            fields=field_objs,
            accessory=accessory,
            block_id=block_id,
        )

    def set_text(
        self, text: str, text_type: Literal["plain_text", "mrkdwn"] = "plain_text"
    ) -> "Section":
        """Set text and return self for chaining."""
        if text_type == "plain_text":
            self.text = PlainText.create(text)
        else:
            self.text = MrkdwnText.create(text)
        return self

    def set_fields(
        self,
        fields: List[str],
        text_type: Literal["plain_text", "mrkdwn"] = "plain_text",
    ) -> "Section":
        """Set fields and return self for chaining."""
        if text_type == "plain_text":
            self.fields = [PlainText.create(field) for field in fields]
        else:
            self.fields = [MrkdwnText.create(field) for field in fields]
        return self

    def set_accessory(self, element: Element) -> "Section":
        """Set accessory and return self for chaining."""
        self.accessory = element
        return self

    def set_block_id(self, block_id: str) -> "Section":
        """Set block ID and return self for chaining."""
        self.block_id = block_id
        return self


class Divider(Block):
    """Divider block."""

    type: Literal["divider"] = "divider"

    def set_block_id(self, block_id: str) -> "Divider":
        """Set block ID and return self for chaining."""
        self.block_id = block_id
        return self

    @classmethod
    def create(cls, block_id: Optional[str] = None) -> "Divider":
        """Create a divider block with builder pattern."""
        return cls(block_id=block_id)


class ImageBlock(Block):
    """Image block."""

    type: Literal["image"] = "image"
    image_url: str
    alt_text: str
    title: Optional[Union[PlainText, MrkdwnText]] = None

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, v: str) -> str:
        """Validate image URL length."""
        return validate_url(v)

    def build(self) -> Dict[str, Any]:
        """Build the image block as a dictionary."""
        result = super().build()
        result.update(
            {
                "image_url": self.image_url,
                "alt_text": self.alt_text,
            }
        )
        if self.title is not None:
            result["title"] = self.title.build()
        return result

    @classmethod
    def create(
        cls,
        image_url: str,
        alt_text: str,
        title: Optional[str] = None,
        block_id: Optional[str] = None,
    ) -> "ImageBlock":
        """Create an image block with builder pattern."""
        title_obj = PlainText.create(title) if title else None
        return cls(
            image_url=image_url,
            alt_text=alt_text,
            title=title_obj,
            block_id=block_id,
        )

    def set_title(self, title: str) -> "ImageBlock":
        """Set title and return self for chaining."""
        self.title = PlainText.create(title)
        return self

    def set_block_id(self, block_id: str) -> "ImageBlock":
        """Set block ID and return self for chaining."""
        self.block_id = block_id
        return self


class Actions(Block):
    """Actions block."""

    type: Literal["actions"] = "actions"
    elements: List[Element]

    def set_block_id(self, block_id: str) -> "Actions":
        """Set block ID and return self for chaining."""
        self.block_id = block_id
        return self

    @field_validator("elements")
    @classmethod
    def validate_elements(cls, v: List[Element]) -> List[Element]:
        """Validate number of elements."""
        if len(v) > SlackConstraints.MAX_ELEMENTS_PER_ACTIONS:
            raise ValueError(
                f"Number of elements {len(v)} exceeds maximum of {SlackConstraints.MAX_ELEMENTS_PER_ACTIONS}"
            )
        return v

    def build(self) -> Dict[str, Any]:
        """Build the actions block as a dictionary."""
        result = super().build()
        result["elements"] = [element.build() for element in self.elements]
        return result

    @classmethod
    def create(
        cls, elements: List[Element], block_id: Optional[str] = None
    ) -> "Actions":
        """Create an actions block with builder pattern."""
        return cls(elements=elements, block_id=block_id)

    def add_element(self, element: Element) -> "Actions":
        """Add an element and return self for chaining."""
        self.elements.append(element)
        return self


class Context(Block):
    """Context block."""

    type: Literal["context"] = "context"
    elements: List[Union[Element, PlainText, MrkdwnText]]

    def set_block_id(self, block_id: str) -> "Context":
        """Set block ID and return self for chaining."""
        self.block_id = block_id
        return self

    @field_validator("elements")
    @classmethod
    def validate_elements(
        cls, v: List[Union[Element, PlainText, MrkdwnText]]
    ) -> List[Union[Element, PlainText, MrkdwnText]]:
        """Validate number of elements."""
        if len(v) > SlackConstraints.MAX_ELEMENTS_PER_CONTEXT:
            raise ValueError(
                f"Number of elements {len(v)} exceeds maximum of {SlackConstraints.MAX_ELEMENTS_PER_CONTEXT}"
            )
        return v

    def build(self) -> Dict[str, Any]:
        """Build the context block as a dictionary."""
        result = super().build()
        result["elements"] = [element.build() for element in self.elements]
        return result

    @classmethod
    def create(
        cls,
        elements: List[Union[Element, PlainText, MrkdwnText]],
        block_id: Optional[str] = None,
    ) -> "Context":
        """Create a context block with builder pattern."""
        return cls(elements=elements, block_id=block_id)

    def add_element(self, element: Union[Element, PlainText, MrkdwnText]) -> "Context":
        """Add an element and return self for chaining."""
        self.elements.append(element)
        return self

    def add_text(
        self, text: str, text_type: Literal["plain_text", "mrkdwn"] = "plain_text"
    ) -> "Context":
        """Add text element and return self for chaining."""
        if text_type == "plain_text":
            self.elements.append(PlainText.create(text))
        else:
            self.elements.append(MrkdwnText.create(text))
        return self


class Input(Block):
    """Input block."""

    type: Literal["input"] = "input"
    label: Union[PlainText, MrkdwnText]
    element: Element
    hint: Optional[Union[PlainText, MrkdwnText]] = None
    optional: Optional[bool] = None
    dispatch_action: Optional[bool] = None

    @field_validator("label")
    @classmethod
    def validate_label(
        cls, v: Union[PlainText, MrkdwnText]
    ) -> Union[PlainText, MrkdwnText]:
        """Validate label length."""
        if len(v.text) > SlackConstraints.MAX_INPUT_LABEL_LENGTH:
            raise ValueError(
                f"Label length {len(v.text)} exceeds maximum of {SlackConstraints.MAX_INPUT_LABEL_LENGTH}"
            )
        return v

    @field_validator("hint")
    @classmethod
    def validate_hint(
        cls, v: Optional[Union[PlainText, MrkdwnText]]
    ) -> Optional[Union[PlainText, MrkdwnText]]:
        """Validate hint length."""
        if v is not None and len(v.text) > SlackConstraints.MAX_INPUT_HINT_LENGTH:
            raise ValueError(
                f"Hint length {len(v.text)} exceeds maximum of {SlackConstraints.MAX_INPUT_HINT_LENGTH}"
            )
        return v

    def build(self) -> Dict[str, Any]:
        """Build the input block as a dictionary."""
        result = super().build()
        result.update(
            {
                "label": self.label.build(),
                "element": self.element.build(),
            }
        )
        if self.hint is not None:
            result["hint"] = self.hint.build()
        if self.optional is not None:
            result["optional"] = self.optional
        if self.dispatch_action is not None:
            result["dispatch_action"] = self.dispatch_action
        return result

    @classmethod
    def create(
        cls,
        label: str,
        element: Element,
        hint: Optional[str] = None,
        optional: Optional[bool] = None,
        dispatch_action: Optional[bool] = None,
        block_id: Optional[str] = None,
    ) -> "Input":
        """Create an input block with builder pattern."""
        label_obj = PlainText.create(label)
        hint_obj = PlainText.create(hint) if hint else None
        return cls(
            label=label_obj,
            element=element,
            hint=hint_obj,
            optional=optional,
            dispatch_action=dispatch_action,
            block_id=block_id,
        )

    def set_hint(self, hint: str) -> "Input":
        """Set hint and return self for chaining."""
        self.hint = PlainText.create(hint)
        return self

    def set_optional(self, optional: bool) -> "Input":
        """Set optional and return self for chaining."""
        self.optional = optional
        return self

    def set_dispatch_action(self, dispatch_action: bool) -> "Input":
        """Set dispatch action and return self for chaining."""
        self.dispatch_action = dispatch_action
        return self

    def set_block_id(self, block_id: str) -> "Input":
        """Set block ID and return self for chaining."""
        self.block_id = block_id
        return self


class File(Block):
    """File block."""

    type: Literal["file"] = "file"
    external_id: str
    source: Literal["remote"] = "remote"

    def set_block_id(self, block_id: str) -> "File":
        """Set block ID and return self for chaining."""
        self.block_id = block_id
        return self

    def build(self) -> Dict[str, Any]:
        """Build the file block as a dictionary."""
        result = super().build()
        result.update(
            {
                "external_id": self.external_id,
                "source": self.source,
            }
        )
        return result

    @classmethod
    def create(cls, external_id: str, block_id: Optional[str] = None) -> "File":
        """Create a file block with builder pattern."""
        return cls(external_id=external_id, block_id=block_id)


class Header(Block):
    """Header block."""

    type: Literal["header"] = "header"
    text: Union[PlainText, MrkdwnText]

    def set_block_id(self, block_id: str) -> "Header":
        """Set block ID and return self for chaining."""
        self.block_id = block_id
        return self

    def build(self) -> Dict[str, Any]:
        """Build the header block as a dictionary."""
        result = super().build()
        result["text"] = self.text.build()
        return result

    @classmethod
    def create(cls, text: str, block_id: Optional[str] = None) -> "Header":
        """Create a header block with builder pattern."""
        return cls(text=PlainText.create(text), block_id=block_id)


class Video(Block):
    """Video block."""

    type: Literal["video"] = "video"
    title: Union[PlainText, MrkdwnText]
    title_url: Optional[str] = None
    description: Optional[Union[PlainText, MrkdwnText]] = None
    video_url: str
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    author_name: Optional[str] = None
    provider_name: Optional[str] = None
    provider_icon_url: Optional[str] = None

    @field_validator("video_url")
    @classmethod
    def validate_video_url(cls, v: str) -> str:
        """Validate video URL length."""
        return validate_url(v, SlackConstraints.MAX_VIDEO_URL_LENGTH)

    @field_validator("thumbnail_url")
    @classmethod
    def validate_thumbnail_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate thumbnail URL length."""
        if v is not None:
            return validate_url(v)
        return v

    @field_validator("title_url")
    @classmethod
    def validate_title_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate title URL length."""
        if v is not None:
            return validate_url(v)
        return v

    @field_validator("provider_icon_url")
    @classmethod
    def validate_provider_icon_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate provider icon URL length."""
        if v is not None:
            return validate_url(v)
        return v

    def build(self) -> Dict[str, Any]:
        """Build the video block as a dictionary."""
        result = super().build()
        result.update(
            {
                "title": self.title.build(),
                "video_url": self.video_url,
            }
        )
        if self.title_url is not None:
            result["title_url"] = self.title_url
        if self.description is not None:
            result["description"] = self.description.build()
        if self.thumbnail_url is not None:
            result["thumbnail_url"] = self.thumbnail_url
        if self.alt_text is not None:
            result["alt_text"] = self.alt_text
        if self.author_name is not None:
            result["author_name"] = self.author_name
        if self.provider_name is not None:
            result["provider_name"] = self.provider_name
        if self.provider_icon_url is not None:
            result["provider_icon_url"] = self.provider_icon_url
        return result

    @classmethod
    def create(
        cls,
        title: str,
        video_url: str,
        title_url: Optional[str] = None,
        description: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        alt_text: Optional[str] = None,
        author_name: Optional[str] = None,
        provider_name: Optional[str] = None,
        provider_icon_url: Optional[str] = None,
        block_id: Optional[str] = None,
    ) -> "Video":
        """Create a video block with builder pattern."""
        title_obj = PlainText.create(title)
        description_obj = PlainText.create(description) if description else None
        return cls(
            title=title_obj,
            video_url=video_url,
            title_url=title_url,
            description=description_obj,
            thumbnail_url=thumbnail_url,
            alt_text=alt_text,
            author_name=author_name,
            provider_name=provider_name,
            provider_icon_url=provider_icon_url,
            block_id=block_id,
        )

    def set_title_url(self, url: str) -> "Video":
        """Set title URL and return self for chaining."""
        self.title_url = url
        return self

    def set_description(self, description: str) -> "Video":
        """Set description and return self for chaining."""
        self.description = PlainText.create(description)
        return self

    def set_thumbnail_url(self, url: str) -> "Video":
        """Set thumbnail URL and return self for chaining."""
        self.thumbnail_url = url
        return self

    def set_alt_text(self, text: str) -> "Video":
        """Set alt text and return self for chaining."""
        self.alt_text = text
        return self

    def set_author_name(self, name: str) -> "Video":
        """Set author name and return self for chaining."""
        self.author_name = name
        return self

    def set_provider_name(self, name: str) -> "Video":
        """Set provider name and return self for chaining."""
        self.provider_name = name
        return self

    def set_provider_icon_url(self, url: str) -> "Video":
        """Set provider icon URL and return self for chaining."""
        self.provider_icon_url = url
        return self

    def set_block_id(self, block_id: str) -> "Video":
        """Set block ID and return self for chaining."""
        self.block_id = block_id
        return self


class RichText(Block):
    """Rich text block."""

    type: Literal["rich_text"] = "rich_text"
    elements: List[Dict[str, Any]]  # Rich text elements are complex, using Dict for now

    def set_block_id(self, block_id: str) -> "RichText":
        """Set block ID and return self for chaining."""
        self.block_id = block_id
        return self

    def build(self) -> Dict[str, Any]:
        """Build the rich text block as a dictionary."""
        result = super().build()
        result["elements"] = self.elements
        return result

    @classmethod
    def create(
        cls, elements: List[Dict[str, Any]], block_id: Optional[str] = None
    ) -> "RichText":
        """Create a rich text block with builder pattern."""
        return cls(elements=elements, block_id=block_id)

    def add_element(self, element: Dict[str, Any]) -> "RichText":
        """Add an element and return self for chaining."""
        self.elements.append(element)
        return self
