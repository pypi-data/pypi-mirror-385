"""Message builders for Slack Block Kit."""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator

from .blocks import (
    Actions,
    Block,
    Context,
    Divider,
    File,
    Header,
    ImageBlock,
    Input,
    RichText,
    Section,
    Video,
)
from .composition import MrkdwnText, PlainText
from .elements import Element
from .validators import SlackConstraints


class Message(BaseModel):
    """Message builder for Slack Block Kit."""

    blocks: List[Block] = Field(default_factory=list)
    response_type: Optional[Literal["in_channel", "ephemeral"]] = None
    replace_original: Optional[bool] = None
    delete_original: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("blocks")
    @classmethod
    def validate_blocks(cls, v: List[Block]) -> List[Block]:
        """Validate number of blocks."""
        if len(v) > SlackConstraints.MAX_BLOCKS_PER_MESSAGE:
            raise ValueError(
                f"Number of blocks {len(v)} exceeds maximum of {SlackConstraints.MAX_BLOCKS_PER_MESSAGE}"
            )
        return v

    def build(self) -> Dict[str, Any]:
        """Build the message as a dictionary."""
        # Validate block count before building
        if len(self.blocks) > SlackConstraints.MAX_BLOCKS_PER_MESSAGE:
            raise ValueError(
                f"Number of blocks {len(self.blocks)} exceeds maximum of {SlackConstraints.MAX_BLOCKS_PER_MESSAGE}"
            )
        result = {"blocks": [block.build() for block in self.blocks]}
        if self.response_type is not None:
            result["response_type"] = self.response_type  # type: ignore[assignment]
        if self.replace_original is not None:
            result["replace_original"] = self.replace_original  # type: ignore[assignment]
        if self.delete_original is not None:
            result["delete_original"] = self.delete_original  # type: ignore[assignment]
        if self.metadata is not None:
            result["metadata"] = self.metadata  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls) -> "Message":
        """Create a message with builder pattern."""
        return cls()

    def add_block(self, block: Block) -> "Message":
        """Add a block and return self for chaining."""
        self.blocks.append(block)
        return self

    def add_section(
        self,
        text: Optional[Union[str, PlainText, MrkdwnText]] = None,
        fields: Optional[List[Union[str, PlainText, MrkdwnText]]] = None,
        accessory: Optional[Element] = None,
        block_id: Optional[str] = None,
    ) -> "Message":
        """Add a section block and return self for chaining."""
        section = Section.create(
            text=text, fields=fields, accessory=accessory, block_id=block_id
        )
        self.blocks.append(section)
        return self

    def add_divider(self, block_id: Optional[str] = None) -> "Message":
        """Add a divider block and return self for chaining."""
        divider = Divider.create(block_id=block_id)
        self.blocks.append(divider)
        return self

    def add_image(
        self,
        image_url: str,
        alt_text: str,
        title: Optional[str] = None,
        block_id: Optional[str] = None,
    ) -> "Message":
        """Add an image block and return self for chaining."""
        image = ImageBlock.create(
            image_url=image_url,
            alt_text=alt_text,
            title=title,
            block_id=block_id,
        )
        self.blocks.append(image)
        return self

    def add_actions(
        self, elements: List[Element], block_id: Optional[str] = None
    ) -> "Message":
        """Add an actions block and return self for chaining."""
        actions = Actions.create(elements=elements, block_id=block_id)
        self.blocks.append(actions)
        return self

    def add_context(
        self,
        elements: List[Union[Element, str]],
        block_id: Optional[str] = None,
    ) -> "Message":
        """Add a context block and return self for chaining."""
        context_elements: List[Union[PlainText, MrkdwnText, Element]] = []
        for element in elements:
            if isinstance(element, str):
                context_elements.append(PlainText.create(element))
            else:
                context_elements.append(element)

        context = Context.create(elements=context_elements, block_id=block_id)
        self.blocks.append(context)
        return self

    def add_input(
        self,
        label: str,
        element: Element,
        hint: Optional[str] = None,
        optional: Optional[bool] = None,
        dispatch_action: Optional[bool] = None,
        block_id: Optional[str] = None,
    ) -> "Message":
        """Add an input block and return self for chaining."""
        input_block = Input.create(
            label=label,
            element=element,
            hint=hint,
            optional=optional,
            dispatch_action=dispatch_action,
            block_id=block_id,
        )
        self.blocks.append(input_block)
        return self

    def add_file(self, external_id: str, block_id: Optional[str] = None) -> "Message":
        """Add a file block and return self for chaining."""
        file_block = File.create(external_id=external_id, block_id=block_id)
        self.blocks.append(file_block)
        return self

    def add_header(self, text: str, block_id: Optional[str] = None) -> "Message":
        """Add a header block and return self for chaining."""
        header = Header.create(text=text, block_id=block_id)
        self.blocks.append(header)
        return self

    def add_video(
        self,
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
    ) -> "Message":
        """Add a video block and return self for chaining."""
        video = Video.create(
            title=title,
            video_url=video_url,
            title_url=title_url,
            description=description,
            thumbnail_url=thumbnail_url,
            alt_text=alt_text,
            author_name=author_name,
            provider_name=provider_name,
            provider_icon_url=provider_icon_url,
            block_id=block_id,
        )
        self.blocks.append(video)
        return self

    def add_rich_text(
        self, elements: List[Dict[str, Any]], block_id: Optional[str] = None
    ) -> "Message":
        """Add a rich text block and return self for chaining."""
        rich_text = RichText.create(elements=elements, block_id=block_id)
        self.blocks.append(rich_text)
        return self

    def set_response_type(
        self, response_type: Literal["in_channel", "ephemeral"]
    ) -> "Message":
        """Set response type and return self for chaining."""
        self.response_type = response_type
        return self

    def set_replace_original(self, replace: bool) -> "Message":
        """Set replace original and return self for chaining."""
        self.replace_original = replace
        return self

    def set_delete_original(self, delete: bool) -> "Message":
        """Set delete original and return self for chaining."""
        self.delete_original = delete
        return self

    def set_metadata(self, metadata: Dict[str, Any]) -> "Message":
        """Set metadata and return self for chaining."""
        self.metadata = metadata
        return self


class Modal(BaseModel):
    """Modal builder for Slack Block Kit."""

    type: Literal["modal"] = "modal"
    title: str
    blocks: List[Block] = Field(default_factory=list)
    submit: Optional[str] = None
    close: Optional[str] = None
    private_metadata: Optional[str] = None
    callback_id: Optional[str] = None
    clear_on_close: Optional[bool] = None
    notify_on_close: Optional[bool] = None
    external_id: Optional[str] = None

    @field_validator("blocks")
    @classmethod
    def validate_blocks(cls, v: List[Block]) -> List[Block]:
        """Validate number of blocks."""
        if len(v) > SlackConstraints.MAX_BLOCKS_PER_MODAL:
            raise ValueError(
                f"Number of blocks {len(v)} exceeds maximum of {SlackConstraints.MAX_BLOCKS_PER_MODAL}"
            )
        return v

    def build(self) -> Dict[str, Any]:
        """Build the modal as a dictionary."""
        # Validate block count before building
        if len(self.blocks) > SlackConstraints.MAX_BLOCKS_PER_MODAL:
            raise ValueError(
                f"Number of blocks {len(self.blocks)} exceeds maximum of {SlackConstraints.MAX_BLOCKS_PER_MODAL}"
            )
        result = {
            "type": self.type,
            "title": {"type": "plain_text", "text": self.title},
            "blocks": [block.build() for block in self.blocks],
        }
        if self.submit is not None:
            result["submit"] = {"type": "plain_text", "text": self.submit}
        if self.close is not None:
            result["close"] = {"type": "plain_text", "text": self.close}
        if self.private_metadata is not None:
            result["private_metadata"] = self.private_metadata
        if self.callback_id is not None:
            result["callback_id"] = self.callback_id
        if self.clear_on_close is not None:
            result["clear_on_close"] = self.clear_on_close  # type: ignore[assignment]
        if self.notify_on_close is not None:
            result["notify_on_close"] = self.notify_on_close  # type: ignore[assignment]
        if self.external_id is not None:
            result["external_id"] = self.external_id
        return result

    @classmethod
    def create(
        cls,
        title: str,
        submit: Optional[str] = None,
        close: Optional[str] = None,
        private_metadata: Optional[str] = None,
        callback_id: Optional[str] = None,
        clear_on_close: Optional[bool] = None,
        notify_on_close: Optional[bool] = None,
        external_id: Optional[str] = None,
    ) -> "Modal":
        """Create a modal with builder pattern."""
        return cls(
            title=title,
            submit=submit,
            close=close,
            private_metadata=private_metadata,
            callback_id=callback_id,
            clear_on_close=clear_on_close,
            notify_on_close=notify_on_close,
            external_id=external_id,
        )

    def add_block(self, block: Block) -> "Modal":
        """Add a block and return self for chaining."""
        self.blocks.append(block)
        return self

    def add_section(
        self,
        text: Optional[str] = None,
        fields: Optional[List[str]] = None,
        accessory: Optional[Element] = None,
        block_id: Optional[str] = None,
    ) -> "Modal":
        """Add a section block and return self for chaining."""
        section = Section.create(
            text=text, fields=fields, accessory=accessory, block_id=block_id
        )
        self.blocks.append(section)
        return self

    def add_divider(self, block_id: Optional[str] = None) -> "Modal":
        """Add a divider block and return self for chaining."""
        divider = Divider.create(block_id=block_id)
        self.blocks.append(divider)
        return self

    def add_image(
        self,
        image_url: str,
        alt_text: str,
        title: Optional[str] = None,
        block_id: Optional[str] = None,
    ) -> "Modal":
        """Add an image block and return self for chaining."""
        image = ImageBlock.create(
            image_url=image_url,
            alt_text=alt_text,
            title=title,
            block_id=block_id,
        )
        self.blocks.append(image)
        return self

    def add_actions(
        self, elements: List[Element], block_id: Optional[str] = None
    ) -> "Modal":
        """Add an actions block and return self for chaining."""
        actions = Actions.create(elements=elements, block_id=block_id)
        self.blocks.append(actions)
        return self

    def add_context(
        self,
        elements: List[Union[Element, str]],
        block_id: Optional[str] = None,
    ) -> "Modal":
        """Add a context block and return self for chaining."""
        context_elements: List[Union[PlainText, MrkdwnText, Element]] = []
        for element in elements:
            if isinstance(element, str):
                context_elements.append(PlainText.create(element))
            else:
                context_elements.append(element)

        context = Context.create(elements=context_elements, block_id=block_id)
        self.blocks.append(context)
        return self

    def add_input(
        self,
        label: str,
        element: Element,
        hint: Optional[str] = None,
        optional: Optional[bool] = None,
        dispatch_action: Optional[bool] = None,
        block_id: Optional[str] = None,
    ) -> "Modal":
        """Add an input block and return self for chaining."""
        input_block = Input.create(
            label=label,
            element=element,
            hint=hint,
            optional=optional,
            dispatch_action=dispatch_action,
            block_id=block_id,
        )
        self.blocks.append(input_block)
        return self

    def add_file(self, external_id: str, block_id: Optional[str] = None) -> "Modal":
        """Add a file block and return self for chaining."""
        file_block = File.create(external_id=external_id, block_id=block_id)
        self.blocks.append(file_block)
        return self

    def add_header(self, text: str, block_id: Optional[str] = None) -> "Modal":
        """Add a header block and return self for chaining."""
        header = Header.create(text=text, block_id=block_id)
        self.blocks.append(header)
        return self

    def add_video(
        self,
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
    ) -> "Modal":
        """Add a video block and return self for chaining."""
        video = Video.create(
            title=title,
            video_url=video_url,
            title_url=title_url,
            description=description,
            thumbnail_url=thumbnail_url,
            alt_text=alt_text,
            author_name=author_name,
            provider_name=provider_name,
            provider_icon_url=provider_icon_url,
            block_id=block_id,
        )
        self.blocks.append(video)
        return self

    def add_rich_text(
        self, elements: List[Dict[str, Any]], block_id: Optional[str] = None
    ) -> "Modal":
        """Add a rich text block and return self for chaining."""
        rich_text = RichText.create(elements=elements, block_id=block_id)
        self.blocks.append(rich_text)
        return self

    def set_submit(self, text: str) -> "Modal":
        """Set submit button text and return self for chaining."""
        self.submit = text
        return self

    def set_close(self, text: str) -> "Modal":
        """Set close button text and return self for chaining."""
        self.close = text
        return self

    def set_private_metadata(self, metadata: str) -> "Modal":
        """Set private metadata and return self for chaining."""
        self.private_metadata = metadata
        return self

    def set_callback_id(self, callback_id: str) -> "Modal":
        """Set callback ID and return self for chaining."""
        self.callback_id = callback_id
        return self

    def set_clear_on_close(self, clear: bool) -> "Modal":
        """Set clear on close and return self for chaining."""
        self.clear_on_close = clear
        return self

    def set_notify_on_close(self, notify: bool) -> "Modal":
        """Set notify on close and return self for chaining."""
        self.notify_on_close = notify
        return self

    def set_external_id(self, external_id: str) -> "Modal":
        """Set external ID and return self for chaining."""
        self.external_id = external_id
        return self


class HomeTab(BaseModel):
    """Home tab builder for Slack Block Kit."""

    type: Literal["home"] = "home"
    blocks: List[Block] = Field(default_factory=list)
    private_metadata: Optional[str] = None
    callback_id: Optional[str] = None
    external_id: Optional[str] = None

    @field_validator("blocks")
    @classmethod
    def validate_blocks(cls, v: List[Block]) -> List[Block]:
        """Validate number of blocks."""
        if len(v) > SlackConstraints.MAX_BLOCKS_PER_HOME_TAB:
            raise ValueError(
                f"Number of blocks {len(v)} exceeds maximum of {SlackConstraints.MAX_BLOCKS_PER_HOME_TAB}"
            )
        return v

    def build(self) -> Dict[str, Any]:
        """Build the home tab as a dictionary."""
        # Validate block count before building
        if len(self.blocks) > SlackConstraints.MAX_BLOCKS_PER_HOME_TAB:
            raise ValueError(
                f"Number of blocks {len(self.blocks)} exceeds maximum of {SlackConstraints.MAX_BLOCKS_PER_HOME_TAB}"
            )
        result = {
            "type": self.type,
            "blocks": [block.build() for block in self.blocks],
        }
        if self.private_metadata is not None:
            result["private_metadata"] = self.private_metadata
        if self.callback_id is not None:
            result["callback_id"] = self.callback_id
        if self.external_id is not None:
            result["external_id"] = self.external_id
        return result

    @classmethod
    def create(
        cls,
        private_metadata: Optional[str] = None,
        callback_id: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> "HomeTab":
        """Create a home tab with builder pattern."""
        return cls(
            private_metadata=private_metadata,
            callback_id=callback_id,
            external_id=external_id,
        )

    def add_block(self, block: Block) -> "HomeTab":
        """Add a block and return self for chaining."""
        self.blocks.append(block)
        return self

    def add_section(
        self,
        text: Optional[Union[str, PlainText, MrkdwnText]] = None,
        fields: Optional[List[Union[str, PlainText, MrkdwnText]]] = None,
        accessory: Optional[Element] = None,
        block_id: Optional[str] = None,
    ) -> "HomeTab":
        """Add a section block and return self for chaining."""
        section = Section.create(
            text=text, fields=fields, accessory=accessory, block_id=block_id
        )
        self.blocks.append(section)
        return self

    def add_divider(self, block_id: Optional[str] = None) -> "HomeTab":
        """Add a divider block and return self for chaining."""
        divider = Divider.create(block_id=block_id)
        self.blocks.append(divider)
        return self

    def add_image(
        self,
        image_url: str,
        alt_text: str,
        title: Optional[str] = None,
        block_id: Optional[str] = None,
    ) -> "HomeTab":
        """Add an image block and return self for chaining."""
        image = ImageBlock.create(
            image_url=image_url,
            alt_text=alt_text,
            title=title,
            block_id=block_id,
        )
        self.blocks.append(image)
        return self

    def add_actions(
        self, elements: List[Element], block_id: Optional[str] = None
    ) -> "HomeTab":
        """Add an actions block and return self for chaining."""
        actions = Actions.create(elements=elements, block_id=block_id)
        self.blocks.append(actions)
        return self

    def add_context(
        self,
        elements: List[Union[Element, str]],
        block_id: Optional[str] = None,
    ) -> "HomeTab":
        """Add a context block and return self for chaining."""
        context_elements: List[Union[PlainText, MrkdwnText, Element]] = []
        for element in elements:
            if isinstance(element, str):
                context_elements.append(PlainText.create(element))
            else:
                context_elements.append(element)

        context = Context.create(elements=context_elements, block_id=block_id)
        self.blocks.append(context)
        return self

    def add_input(
        self,
        label: str,
        element: Element,
        hint: Optional[str] = None,
        optional: Optional[bool] = None,
        dispatch_action: Optional[bool] = None,
        block_id: Optional[str] = None,
    ) -> "HomeTab":
        """Add an input block and return self for chaining."""
        input_block = Input.create(
            label=label,
            element=element,
            hint=hint,
            optional=optional,
            dispatch_action=dispatch_action,
            block_id=block_id,
        )
        self.blocks.append(input_block)
        return self

    def add_file(self, external_id: str, block_id: Optional[str] = None) -> "HomeTab":
        """Add a file block and return self for chaining."""
        file_block = File.create(external_id=external_id, block_id=block_id)
        self.blocks.append(file_block)
        return self

    def add_header(self, text: str, block_id: Optional[str] = None) -> "HomeTab":
        """Add a header block and return self for chaining."""
        header = Header.create(text=text, block_id=block_id)
        self.blocks.append(header)
        return self

    def add_video(
        self,
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
    ) -> "HomeTab":
        """Add a video block and return self for chaining."""
        video = Video.create(
            title=title,
            video_url=video_url,
            title_url=title_url,
            description=description,
            thumbnail_url=thumbnail_url,
            alt_text=alt_text,
            author_name=author_name,
            provider_name=provider_name,
            provider_icon_url=provider_icon_url,
            block_id=block_id,
        )
        self.blocks.append(video)
        return self

    def add_rich_text(
        self, elements: List[Dict[str, Any]], block_id: Optional[str] = None
    ) -> "HomeTab":
        """Add a rich text block and return self for chaining."""
        rich_text = RichText.create(elements=elements, block_id=block_id)
        self.blocks.append(rich_text)
        return self

    def set_private_metadata(self, metadata: str) -> "HomeTab":
        """Set private metadata and return self for chaining."""
        self.private_metadata = metadata
        return self

    def set_callback_id(self, callback_id: str) -> "HomeTab":
        """Set callback ID and return self for chaining."""
        self.callback_id = callback_id
        return self

    def set_external_id(self, external_id: str) -> "HomeTab":
        """Set external ID and return self for chaining."""
        self.external_id = external_id
        return self
