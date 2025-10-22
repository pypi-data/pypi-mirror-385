"""Tests for blocks."""

import pytest

from slack_block_kit_builder.blocks import (
    Actions,
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
from slack_block_kit_builder.composition import PlainText
from slack_block_kit_builder.elements import Button, PlainTextInput


class TestSection:
    """Test Section block."""

    def test_create_basic(self):
        """Test creating basic section."""
        section = Section.create("Hello World")
        assert section.type == "section"
        assert section.text.text == "Hello World"
        assert section.fields is None
        assert section.accessory is None
        assert section.block_id is None

    def test_create_with_fields(self):
        """Test creating section with fields."""
        fields = ["Field 1", "Field 2"]
        section = Section.create(fields=fields)
        assert section.fields is not None
        assert len(section.fields) == 2
        assert section.fields[0].text == "Field 1"

    def test_create_with_accessory(self):
        """Test creating section with accessory."""
        button = Button.create("Click me", "btn_1")
        section = Section.create(accessory=button)
        assert section.accessory == button

    def test_builder_pattern(self):
        """Test builder pattern for section."""
        section = (
            Section.create("Hello")
            .set_text("Updated text", "mrkdwn")
            .set_block_id("section_1")
        )
        assert section.text.text == "Updated text"
        assert section.text.type == "mrkdwn"
        assert section.block_id == "section_1"

    def test_build(self):
        """Test building section to dict."""
        button = Button.create("Click me", "btn_1")
        section = Section.create("Hello World", accessory=button, block_id="section_1")
        result = section.build()
        expected = {
            "type": "section",
            "block_id": "section_1",
            "text": {"type": "plain_text", "text": "Hello World"},
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "Click me"},
                "action_id": "btn_1",
            },
        }
        assert result == expected


class TestDivider:
    """Test Divider block."""

    def test_create_basic(self):
        """Test creating basic divider."""
        divider = Divider.create()
        assert divider.type == "divider"
        assert divider.block_id is None

    def test_create_with_block_id(self):
        """Test creating divider with block ID."""
        divider = Divider.create(block_id="divider_1")
        assert divider.block_id == "divider_1"

    def test_builder_pattern(self):
        """Test builder pattern for divider."""
        divider = Divider.create().set_block_id("divider_1")
        assert divider.block_id == "divider_1"

    def test_build(self):
        """Test building divider to dict."""
        divider = Divider.create(block_id="divider_1")
        result = divider.build()
        expected = {
            "type": "divider",
            "block_id": "divider_1",
        }
        assert result == expected


class TestImageBlock:
    """Test ImageBlock block."""

    def test_create_basic(self):
        """Test creating basic image block."""
        image = ImageBlock.create("https://example.com/image.png", "Alt text")
        assert image.type == "image"
        assert image.image_url == "https://example.com/image.png"
        assert image.alt_text == "Alt text"
        assert image.title is None

    def test_create_with_title(self):
        """Test creating image block with title."""
        image = ImageBlock.create(
            "https://example.com/image.png", "Alt text", title="Image Title"
        )
        assert image.title.text == "Image Title"

    def test_builder_pattern(self):
        """Test builder pattern for image block."""
        image = (
            ImageBlock.create("https://example.com/image.png", "Alt text")
            .set_title("Image Title")
            .set_block_id("image_1")
        )
        assert image.title.text == "Image Title"
        assert image.block_id == "image_1"

    def test_build(self):
        """Test building image block to dict."""
        image = ImageBlock.create(
            "https://example.com/image.png",
            "Alt text",
            title="Image Title",
            block_id="image_1",
        )
        result = image.build()
        expected = {
            "type": "image",
            "block_id": "image_1",
            "image_url": "https://example.com/image.png",
            "alt_text": "Alt text",
            "title": {"type": "plain_text", "text": "Image Title"},
        }
        assert result == expected


class TestActions:
    """Test Actions block."""

    def test_create_basic(self):
        """Test creating basic actions block."""
        buttons = [
            Button.create("Button 1", "btn_1"),
            Button.create("Button 2", "btn_2"),
        ]
        actions = Actions.create(buttons)
        assert actions.type == "actions"
        assert len(actions.elements) == 2
        assert actions.block_id is None

    def test_builder_pattern(self):
        """Test builder pattern for actions block."""
        buttons = [Button.create("Button 1", "btn_1")]
        actions = Actions.create(buttons)
        new_button = Button.create("Button 2", "btn_2")
        actions.add_element(new_button).set_block_id("actions_1")
        assert len(actions.elements) == 2
        assert actions.block_id == "actions_1"

    def test_build(self):
        """Test building actions block to dict."""
        buttons = [
            Button.create("Button 1", "btn_1"),
            Button.create("Button 2", "btn_2"),
        ]
        actions = Actions.create(buttons, block_id="actions_1")
        result = actions.build()
        expected = {
            "type": "actions",
            "block_id": "actions_1",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Button 1"},
                    "action_id": "btn_1",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Button 2"},
                    "action_id": "btn_2",
                },
            ],
        }
        assert result == expected

    def test_elements_count_validation(self):
        """Test actions elements count validation."""
        buttons = [Button.create(f"Button {i}", f"btn_{i}") for i in range(26)]
        with pytest.raises(
            ValueError, match="Number of elements 26 exceeds maximum of 25"
        ):
            Actions.create(buttons)


class TestContext:
    """Test Context block."""

    def test_create_basic(self):
        """Test creating basic context block."""
        elements = [PlainText.create("Context text"), Button.create("Button", "btn_1")]
        context = Context.create(elements)
        assert context.type == "context"
        assert len(context.elements) == 2
        assert context.block_id is None

    def test_builder_pattern(self):
        """Test builder pattern for context block."""
        elements = [PlainText.create("Context text")]
        context = Context.create(elements)
        context.add_element(Button.create("Button", "btn_1")).add_text(
            "More text"
        ).set_block_id("context_1")
        assert len(context.elements) == 3
        assert context.block_id == "context_1"

    def test_build(self):
        """Test building context block to dict."""
        elements = [PlainText.create("Context text"), Button.create("Button", "btn_1")]
        context = Context.create(elements, block_id="context_1")
        result = context.build()
        expected = {
            "type": "context",
            "block_id": "context_1",
            "elements": [
                {"type": "plain_text", "text": "Context text"},
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Button"},
                    "action_id": "btn_1",
                },
            ],
        }
        assert result == expected

    def test_elements_count_validation(self):
        """Test context elements count validation."""
        elements = [PlainText.create(f"Text {i}") for i in range(11)]
        with pytest.raises(
            ValueError, match="Number of elements 11 exceeds maximum of 10"
        ):
            Context.create(elements)


class TestInput:
    """Test Input block."""

    def test_create_basic(self):
        """Test creating basic input block."""
        text_input = PlainTextInput.create("text_1")
        input_block = Input.create("Label", text_input)
        assert input_block.type == "input"
        assert input_block.label.text == "Label"
        assert input_block.element == text_input
        assert input_block.hint is None
        assert input_block.optional is None
        assert input_block.dispatch_action is None

    def test_create_with_hint(self):
        """Test creating input block with hint."""
        text_input = PlainTextInput.create("text_1")
        input_block = Input.create("Label", text_input, hint="Hint text")
        assert input_block.hint.text == "Hint text"

    def test_builder_pattern(self):
        """Test builder pattern for input block."""
        text_input = PlainTextInput.create("text_1")
        input_block = Input.create("Label", text_input)
        input_block.set_hint("Hint text").set_optional(True).set_dispatch_action(
            True
        ).set_block_id("input_1")
        assert input_block.hint.text == "Hint text"
        assert input_block.optional is True
        assert input_block.dispatch_action is True
        assert input_block.block_id == "input_1"

    def test_build(self):
        """Test building input block to dict."""
        text_input = PlainTextInput.create("text_1")
        input_block = Input.create(
            "Label", text_input, hint="Hint text", optional=True, block_id="input_1"
        )
        result = input_block.build()
        expected = {
            "type": "input",
            "block_id": "input_1",
            "label": {"type": "plain_text", "text": "Label"},
            "element": {
                "type": "plain_text_input",
                "action_id": "text_1",
            },
            "hint": {"type": "plain_text", "text": "Hint text"},
            "optional": True,
        }
        assert result == expected

    def test_label_length_validation(self):
        """Test input label length validation."""
        long_label = "x" * 2001
        text_input = PlainTextInput.create("text_1")
        with pytest.raises(
            ValueError, match="Label length 2001 exceeds maximum of 2000"
        ):
            Input.create(long_label, text_input)

    def test_hint_length_validation(self):
        """Test input hint length validation."""
        long_hint = "x" * 2001
        text_input = PlainTextInput.create("text_1")
        with pytest.raises(
            ValueError, match="Hint length 2001 exceeds maximum of 2000"
        ):
            Input.create("Label", text_input, hint=long_hint)


class TestFile:
    """Test File block."""

    def test_create_basic(self):
        """Test creating basic file block."""
        file_block = File.create("external_123")
        assert file_block.type == "file"
        assert file_block.external_id == "external_123"
        assert file_block.source == "remote"
        assert file_block.block_id is None

    def test_create_with_block_id(self):
        """Test creating file block with block ID."""
        file_block = File.create("external_123", block_id="file_1")
        assert file_block.block_id == "file_1"

    def test_builder_pattern(self):
        """Test builder pattern for file block."""
        file_block = File.create("external_123").set_block_id("file_1")
        assert file_block.block_id == "file_1"

    def test_build(self):
        """Test building file block to dict."""
        file_block = File.create("external_123", block_id="file_1")
        result = file_block.build()
        expected = {
            "type": "file",
            "block_id": "file_1",
            "external_id": "external_123",
            "source": "remote",
        }
        assert result == expected


class TestHeader:
    """Test Header block."""

    def test_create_basic(self):
        """Test creating basic header block."""
        header = Header.create("Header Text")
        assert header.type == "header"
        assert header.text.text == "Header Text"
        assert header.block_id is None

    def test_create_with_block_id(self):
        """Test creating header block with block ID."""
        header = Header.create("Header Text", block_id="header_1")
        assert header.block_id == "header_1"

    def test_builder_pattern(self):
        """Test builder pattern for header block."""
        header = Header.create("Header Text").set_block_id("header_1")
        assert header.block_id == "header_1"

    def test_build(self):
        """Test building header block to dict."""
        header = Header.create("Header Text", block_id="header_1")
        result = header.build()
        expected = {
            "type": "header",
            "block_id": "header_1",
            "text": {"type": "plain_text", "text": "Header Text"},
        }
        assert result == expected


class TestVideo:
    """Test Video block."""

    def test_create_basic(self):
        """Test creating basic video block."""
        video = Video.create("Video Title", "https://example.com/video.mp4")
        assert video.type == "video"
        assert video.title.text == "Video Title"
        assert video.video_url == "https://example.com/video.mp4"
        assert video.title_url is None
        assert video.description is None

    def test_create_with_properties(self):
        """Test creating video block with properties."""
        video = Video.create(
            "Video Title",
            "https://example.com/video.mp4",
            title_url="https://example.com",
            description="Video description",
            thumbnail_url="https://example.com/thumb.jpg",
            alt_text="Video thumbnail",
            author_name="Author",
            provider_name="Provider",
            provider_icon_url="https://example.com/icon.png",
        )
        assert video.title_url == "https://example.com"
        assert video.description.text == "Video description"
        assert video.thumbnail_url == "https://example.com/thumb.jpg"
        assert video.alt_text == "Video thumbnail"
        assert video.author_name == "Author"
        assert video.provider_name == "Provider"
        assert video.provider_icon_url == "https://example.com/icon.png"

    def test_builder_pattern(self):
        """Test builder pattern for video block."""
        video = (
            Video.create("Video Title", "https://example.com/video.mp4")
            .set_title_url("https://example.com")
            .set_description("Video description")
            .set_thumbnail_url("https://example.com/thumb.jpg")
            .set_alt_text("Video thumbnail")
            .set_author_name("Author")
            .set_provider_name("Provider")
            .set_provider_icon_url("https://example.com/icon.png")
            .set_block_id("video_1")
        )
        assert video.title_url == "https://example.com"
        assert video.description.text == "Video description"
        assert video.thumbnail_url == "https://example.com/thumb.jpg"
        assert video.alt_text == "Video thumbnail"
        assert video.author_name == "Author"
        assert video.provider_name == "Provider"
        assert video.provider_icon_url == "https://example.com/icon.png"
        assert video.block_id == "video_1"

    def test_build(self):
        """Test building video block to dict."""
        video = Video.create(
            "Video Title",
            "https://example.com/video.mp4",
            title_url="https://example.com",
            description="Video description",
            thumbnail_url="https://example.com/thumb.jpg",
            alt_text="Video thumbnail",
            author_name="Author",
            provider_name="Provider",
            provider_icon_url="https://example.com/icon.png",
            block_id="video_1",
        )
        result = video.build()
        expected = {
            "type": "video",
            "block_id": "video_1",
            "title": {"type": "plain_text", "text": "Video Title"},
            "video_url": "https://example.com/video.mp4",
            "title_url": "https://example.com",
            "description": {"type": "plain_text", "text": "Video description"},
            "thumbnail_url": "https://example.com/thumb.jpg",
            "alt_text": "Video thumbnail",
            "author_name": "Author",
            "provider_name": "Provider",
            "provider_icon_url": "https://example.com/icon.png",
        }
        assert result == expected

    def test_video_url_validation(self):
        """Test video URL validation."""
        long_url = "https://example.com/" + "x" * 3000
        with pytest.raises(ValueError, match="URL length 3020 exceeds maximum of 3000"):
            Video.create("Video Title", long_url)


class TestRichText:
    """Test RichText block."""

    def test_create_basic(self):
        """Test creating basic rich text block."""
        elements = [{"type": "text", "text": "Hello World"}]
        rich_text = RichText.create(elements)
        assert rich_text.type == "rich_text"
        assert rich_text.elements == elements
        assert rich_text.block_id is None

    def test_create_with_block_id(self):
        """Test creating rich text block with block ID."""
        elements = [{"type": "text", "text": "Hello World"}]
        rich_text = RichText.create(elements, block_id="rich_text_1")
        assert rich_text.block_id == "rich_text_1"

    def test_builder_pattern(self):
        """Test builder pattern for rich text block."""
        elements = [{"type": "text", "text": "Hello World"}]
        rich_text = RichText.create(elements)
        new_element = {"type": "text", "text": "More text"}
        rich_text.add_element(new_element).set_block_id("rich_text_1")
        assert len(rich_text.elements) == 2
        assert rich_text.block_id == "rich_text_1"

    def test_build(self):
        """Test building rich text block to dict."""
        elements = [{"type": "text", "text": "Hello World"}]
        rich_text = RichText.create(elements, block_id="rich_text_1")
        result = rich_text.build()
        expected = {
            "type": "rich_text",
            "block_id": "rich_text_1",
            "elements": [{"type": "text", "text": "Hello World"}],
        }
        assert result == expected
