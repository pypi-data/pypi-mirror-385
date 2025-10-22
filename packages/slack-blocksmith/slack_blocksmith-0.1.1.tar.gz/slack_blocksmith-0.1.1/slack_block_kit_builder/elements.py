"""Elements for Slack Block Kit."""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, field_validator

from .composition import (
    ConfirmationDialog,
    DispatchActionConfiguration,
    Filter,
    MrkdwnText,
    Option,
    OptionGroup,
    PlainText,
)
from .validators import (
    SlackConstraints,
    validate_action_id,
    validate_options_count,
    validate_url,
)


class Element(BaseModel):
    """Base class for elements."""

    type: str

    def build(self) -> Dict[str, Any]:
        """Build the element as a dictionary."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


class Button(Element):
    """Button element."""

    type: Literal["button"] = "button"
    text: Union[PlainText, MrkdwnText]
    action_id: str
    url: Optional[str] = None
    value: Optional[str] = None
    style: Optional[Literal["primary", "danger"]] = None
    confirm: Optional[ConfirmationDialog] = None
    accessibility_label: Optional[str] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL length."""
        if v is not None:
            return validate_url(v)
        return v

    def build(self) -> Dict[str, Any]:
        """Build the button as a dictionary."""
        result = {
            "type": self.type,
            "text": self.text.build(),
            "action_id": self.action_id,
        }
        if self.url is not None:
            result["url"] = self.url
        if self.value is not None:
            result["value"] = self.value
        if self.style is not None:
            result["style"] = self.style
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()
        if self.accessibility_label is not None:
            result["accessibility_label"] = self.accessibility_label
        return result

    @classmethod
    def create(
        cls,
        text: str,
        action_id: str,
        url: Optional[str] = None,
        value: Optional[str] = None,
        style: Optional[Literal["primary", "danger"]] = None,
    ) -> "Button":
        """Create a button with builder pattern."""
        return cls(
            text=PlainText.create(text),
            action_id=action_id,
            url=url,
            value=value,
            style=style,
        )

    def set_url(self, url: str) -> "Button":
        """Set URL and return self for chaining."""
        self.url = url
        return self

    def set_value(self, value: str) -> "Button":
        """Set value and return self for chaining."""
        self.value = value
        return self

    def set_style(self, style: Literal["primary", "danger"]) -> "Button":
        """Set style and return self for chaining."""
        self.style = style
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "Button":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_accessibility_label(self, label: str) -> "Button":
        """Set accessibility label and return self for chaining."""
        self.accessibility_label = label
        return self


class Checkboxes(Element):
    """Checkboxes element."""

    type: Literal["checkboxes"] = "checkboxes"
    action_id: str
    options: List[Option]
    initial_options: Optional[List[Option]] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: List[Option]) -> List[Option]:
        """Validate number of options."""
        return validate_options_count(v, SlackConstraints.MAX_OPTIONS_PER_SELECT)

    def build(self) -> Dict[str, Any]:
        """Build the checkboxes as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
            "options": [option.build() for option in self.options],
        }
        if self.initial_options is not None:
            result["initial_options"] = [
                option.build() for option in self.initial_options
            ]
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()  # type: ignore[assignment]
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str, options: List[Option]) -> "Checkboxes":
        """Create checkboxes with builder pattern."""
        return cls(action_id=action_id, options=options)

    def set_initial_options(self, options: List[Option]) -> "Checkboxes":
        """Set initial options and return self for chaining."""
        self.initial_options = options
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "Checkboxes":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "Checkboxes":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class DatePicker(Element):
    """Date picker element."""

    type: Literal["datepicker"] = "datepicker"
    action_id: str
    placeholder: Optional[Union[PlainText, MrkdwnText]] = None
    initial_date: Optional[str] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the date picker as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
        }
        if self.placeholder is not None:
            result["placeholder"] = self.placeholder.build()  # type: ignore[assignment]
        if self.initial_date is not None:
            result["initial_date"] = self.initial_date
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()  # type: ignore[assignment]
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str) -> "DatePicker":
        """Create a date picker with builder pattern."""
        return cls(action_id=action_id)

    def set_placeholder(self, text: str) -> "DatePicker":
        """Set placeholder and return self for chaining."""
        self.placeholder = PlainText.create(text)
        return self

    def set_initial_date(self, date: str) -> "DatePicker":
        """Set initial date and return self for chaining."""
        self.initial_date = date
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "DatePicker":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "DatePicker":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class TimePicker(Element):
    """Time picker element."""

    type: Literal["timepicker"] = "timepicker"
    action_id: str
    placeholder: Optional[Union[PlainText, MrkdwnText]] = None
    initial_time: Optional[str] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the time picker as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
        }
        if self.placeholder is not None:
            result["placeholder"] = self.placeholder.build()  # type: ignore[assignment]
        if self.initial_time is not None:
            result["initial_time"] = self.initial_time
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()  # type: ignore[assignment]
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str) -> "TimePicker":
        """Create a time picker with builder pattern."""
        return cls(action_id=action_id)

    def set_placeholder(self, text: str) -> "TimePicker":
        """Set placeholder and return self for chaining."""
        self.placeholder = PlainText.create(text)
        return self

    def set_initial_time(self, time: str) -> "TimePicker":
        """Set initial time and return self for chaining."""
        self.initial_time = time
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "TimePicker":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "TimePicker":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class DatetimePicker(Element):
    """Datetime picker element."""

    type: Literal["datetimepicker"] = "datetimepicker"
    action_id: str
    initial_date_time: Optional[int] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the datetime picker as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
        }
        if self.initial_date_time is not None:
            result["initial_date_time"] = self.initial_date_time  # type: ignore[assignment]
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()  # type: ignore[assignment]
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str) -> "DatetimePicker":
        """Create a datetime picker with builder pattern."""
        return cls(action_id=action_id)

    def set_initial_date_time(self, timestamp: int) -> "DatetimePicker":
        """Set initial datetime and return self for chaining."""
        self.initial_date_time = timestamp
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "DatetimePicker":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "DatetimePicker":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class EmailInput(Element):
    """Email input element."""

    type: Literal["email_text_input"] = "email_text_input"
    action_id: str
    placeholder: Optional[Union[PlainText, MrkdwnText]] = None
    initial_value: Optional[str] = None
    dispatch_action_config: Optional[DispatchActionConfiguration] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the email input as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
        }
        if self.placeholder is not None:
            result["placeholder"] = self.placeholder.build()  # type: ignore[assignment]
        if self.initial_value is not None:
            result["initial_value"] = self.initial_value
        if self.dispatch_action_config is not None:
            result["dispatch_action_config"] = self.dispatch_action_config.build()  # type: ignore[assignment]
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str) -> "EmailInput":
        """Create an email input with builder pattern."""
        return cls(action_id=action_id)

    def set_placeholder(self, text: str) -> "EmailInput":
        """Set placeholder and return self for chaining."""
        self.placeholder = PlainText.create(text)
        return self

    def set_initial_value(self, value: str) -> "EmailInput":
        """Set initial value and return self for chaining."""
        self.initial_value = value
        return self

    def set_dispatch_action_config(
        self, config: DispatchActionConfiguration
    ) -> "EmailInput":
        """Set dispatch action config and return self for chaining."""
        self.dispatch_action_config = config
        return self

    def set_focus_on_load(self, focus: bool) -> "EmailInput":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class NumberInput(Element):
    """Number input element."""

    type: Literal["number_input"] = "number_input"
    action_id: str
    is_decimal_allowed: Optional[bool] = None
    initial_value: Optional[str] = None
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    dispatch_action_config: Optional[DispatchActionConfiguration] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the number input as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
        }
        if self.is_decimal_allowed is not None:
            result["is_decimal_allowed"] = self.is_decimal_allowed  # type: ignore[assignment]
        if self.initial_value is not None:
            result["initial_value"] = self.initial_value
        if self.min_value is not None:
            result["min_value"] = self.min_value
        if self.max_value is not None:
            result["max_value"] = self.max_value
        if self.dispatch_action_config is not None:
            result["dispatch_action_config"] = self.dispatch_action_config.build()  # type: ignore[assignment]
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str) -> "NumberInput":
        """Create a number input with builder pattern."""
        return cls(action_id=action_id)

    def set_is_decimal_allowed(self, allowed: bool) -> "NumberInput":
        """Set decimal allowed and return self for chaining."""
        self.is_decimal_allowed = allowed
        return self

    def set_initial_value(self, value: str) -> "NumberInput":
        """Set initial value and return self for chaining."""
        self.initial_value = value
        return self

    def set_min_value(self, value: str) -> "NumberInput":
        """Set min value and return self for chaining."""
        self.min_value = value
        return self

    def set_max_value(self, value: str) -> "NumberInput":
        """Set max value and return self for chaining."""
        self.max_value = value
        return self

    def set_dispatch_action_config(
        self, config: DispatchActionConfiguration
    ) -> "NumberInput":
        """Set dispatch action config and return self for chaining."""
        self.dispatch_action_config = config
        return self

    def set_focus_on_load(self, focus: bool) -> "NumberInput":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class PlainTextInput(Element):
    """Plain text input element."""

    type: Literal["plain_text_input"] = "plain_text_input"
    action_id: str
    placeholder: Optional[Union[PlainText, MrkdwnText]] = None
    initial_value: Optional[str] = None
    multiline: Optional[bool] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    dispatch_action_config: Optional[DispatchActionConfiguration] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the plain text input as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
        }
        if self.placeholder is not None:
            result["placeholder"] = self.placeholder.build()  # type: ignore[assignment]
        if self.initial_value is not None:
            result["initial_value"] = self.initial_value
        if self.multiline is not None:
            result["multiline"] = self.multiline  # type: ignore[assignment]
        if self.min_length is not None:
            result["min_length"] = self.min_length  # type: ignore[assignment]
        if self.max_length is not None:
            result["max_length"] = self.max_length  # type: ignore[assignment]
        if self.dispatch_action_config is not None:
            result["dispatch_action_config"] = self.dispatch_action_config.build()  # type: ignore[assignment]
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str) -> "PlainTextInput":
        """Create a plain text input with builder pattern."""
        return cls(action_id=action_id)

    def set_placeholder(self, text: str) -> "PlainTextInput":
        """Set placeholder and return self for chaining."""
        self.placeholder = PlainText.create(text)
        return self

    def set_initial_value(self, value: str) -> "PlainTextInput":
        """Set initial value and return self for chaining."""
        self.initial_value = value
        return self

    def set_multiline(self, multiline: bool) -> "PlainTextInput":
        """Set multiline and return self for chaining."""
        self.multiline = multiline
        return self

    def set_min_length(self, length: int) -> "PlainTextInput":
        """Set min length and return self for chaining."""
        self.min_length = length
        return self

    def set_max_length(self, length: int) -> "PlainTextInput":
        """Set max length and return self for chaining."""
        self.max_length = length
        return self

    def set_dispatch_action_config(
        self, config: DispatchActionConfiguration
    ) -> "PlainTextInput":
        """Set dispatch action config and return self for chaining."""
        self.dispatch_action_config = config
        return self

    def set_focus_on_load(self, focus: bool) -> "PlainTextInput":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class URLInput(Element):
    """URL input element."""

    type: Literal["url_text_input"] = "url_text_input"
    action_id: str
    placeholder: Optional[Union[PlainText, MrkdwnText]] = None
    initial_value: Optional[str] = None
    dispatch_action_config: Optional[DispatchActionConfiguration] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the URL input as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
        }
        if self.placeholder is not None:
            result["placeholder"] = self.placeholder.build()  # type: ignore[assignment]
        if self.initial_value is not None:
            result["initial_value"] = self.initial_value
        if self.dispatch_action_config is not None:
            result["dispatch_action_config"] = self.dispatch_action_config.build()  # type: ignore[assignment]
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str) -> "URLInput":
        """Create a URL input with builder pattern."""
        return cls(action_id=action_id)

    def set_placeholder(self, text: str) -> "URLInput":
        """Set placeholder and return self for chaining."""
        self.placeholder = PlainText.create(text)
        return self

    def set_initial_value(self, value: str) -> "URLInput":
        """Set initial value and return self for chaining."""
        self.initial_value = value
        return self

    def set_dispatch_action_config(
        self, config: DispatchActionConfiguration
    ) -> "URLInput":
        """Set dispatch action config and return self for chaining."""
        self.dispatch_action_config = config
        return self

    def set_focus_on_load(self, focus: bool) -> "URLInput":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class RadioButtons(Element):
    """Radio buttons element."""

    type: Literal["radio_buttons"] = "radio_buttons"
    action_id: str
    options: List[Option]
    initial_option: Optional[Option] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: List[Option]) -> List[Option]:
        """Validate number of options."""
        return validate_options_count(v, SlackConstraints.MAX_OPTIONS_PER_SELECT)

    def build(self) -> Dict[str, Any]:
        """Build the radio buttons as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
            "options": [option.build() for option in self.options],
        }
        if self.initial_option is not None:
            result["initial_option"] = self.initial_option.build()  # type: ignore[assignment]
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()  # type: ignore[assignment]
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str, options: List[Option]) -> "RadioButtons":
        """Create radio buttons with builder pattern."""
        return cls(action_id=action_id, options=options)

    def set_initial_option(self, option: Option) -> "RadioButtons":
        """Set initial option and return self for chaining."""
        self.initial_option = option
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "RadioButtons":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "RadioButtons":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class StaticSelect(Element):
    """Static select element."""

    type: Literal["static_select"] = "static_select"
    action_id: str
    placeholder: Union[PlainText, MrkdwnText]
    options: Optional[List[Option]] = None
    option_groups: Optional[List[OptionGroup]] = None
    initial_option: Optional[Option] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: Optional[List[Option]]) -> Optional[List[Option]]:
        """Validate number of options."""
        if v is not None:
            return validate_options_count(v, SlackConstraints.MAX_OPTIONS_PER_SELECT)
        return v

    def build(self) -> Dict[str, Any]:
        """Build the static select as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
            "placeholder": self.placeholder.build(),
        }
        if self.options is not None:
            result["options"] = [option.build() for option in self.options]  # type: ignore[misc]
        if self.option_groups is not None:
            result["option_groups"] = [group.build() for group in self.option_groups]  # type: ignore[misc]
        if self.initial_option is not None:
            result["initial_option"] = self.initial_option.build()
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(
        cls,
        action_id: str,
        placeholder: str,
        options: Optional[List[Option]] = None,
        option_groups: Optional[List[OptionGroup]] = None,
    ) -> "StaticSelect":
        """Create a static select with builder pattern."""
        return cls(
            action_id=action_id,
            placeholder=PlainText.create(placeholder),
            options=options,
            option_groups=option_groups,
        )

    def set_initial_option(self, option: Option) -> "StaticSelect":
        """Set initial option and return self for chaining."""
        self.initial_option = option
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "StaticSelect":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "StaticSelect":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class ExternalSelect(Element):
    """External select element."""

    type: Literal["external_select"] = "external_select"
    action_id: str
    placeholder: Union[PlainText, MrkdwnText]
    initial_option: Optional[Option] = None
    min_query_length: Optional[int] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the external select as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
            "placeholder": self.placeholder.build(),
        }
        if self.initial_option is not None:
            result["initial_option"] = self.initial_option.build()
        if self.min_query_length is not None:
            result["min_query_length"] = self.min_query_length  # type: ignore[assignment]
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str, placeholder: str) -> "ExternalSelect":
        """Create an external select with builder pattern."""
        return cls(action_id=action_id, placeholder=PlainText.create(placeholder))

    def set_initial_option(self, option: Option) -> "ExternalSelect":
        """Set initial option and return self for chaining."""
        self.initial_option = option
        return self

    def set_min_query_length(self, length: int) -> "ExternalSelect":
        """Set min query length and return self for chaining."""
        self.min_query_length = length
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "ExternalSelect":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "ExternalSelect":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class UsersSelect(Element):
    """Users select element."""

    type: Literal["users_select"] = "users_select"
    action_id: str
    placeholder: Union[PlainText, MrkdwnText]
    initial_user: Optional[str] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the users select as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
            "placeholder": self.placeholder.build(),
        }
        if self.initial_user is not None:
            result["initial_user"] = self.initial_user
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str, placeholder: str) -> "UsersSelect":
        """Create a users select with builder pattern."""
        return cls(action_id=action_id, placeholder=PlainText.create(placeholder))

    def set_initial_user(self, user: str) -> "UsersSelect":
        """Set initial user and return self for chaining."""
        self.initial_user = user
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "UsersSelect":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "UsersSelect":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class ConversationsSelect(Element):
    """Conversations select element."""

    type: Literal["conversations_select"] = "conversations_select"
    action_id: str
    placeholder: Union[PlainText, MrkdwnText]
    initial_conversation: Optional[str] = None
    default_to_current_conversation: Optional[bool] = None
    filter: Optional[Filter] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the conversations select as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
            "placeholder": self.placeholder.build(),
        }
        if self.initial_conversation is not None:
            result["initial_conversation"] = self.initial_conversation
        if self.default_to_current_conversation is not None:
            result["default_to_current_conversation"] = (
                self.default_to_current_conversation
            )  # type: ignore[assignment]
        if self.filter is not None:
            result["filter"] = self.filter.build()
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str, placeholder: str) -> "ConversationsSelect":
        """Create a conversations select with builder pattern."""
        return cls(action_id=action_id, placeholder=PlainText.create(placeholder))

    def set_initial_conversation(self, conversation: str) -> "ConversationsSelect":
        """Set initial conversation and return self for chaining."""
        self.initial_conversation = conversation
        return self

    def set_default_to_current_conversation(
        self, default: bool
    ) -> "ConversationsSelect":
        """Set default to current conversation and return self for chaining."""
        self.default_to_current_conversation = default
        return self

    def set_filter(self, filter_obj: Filter) -> "ConversationsSelect":
        """Set filter and return self for chaining."""
        self.filter = filter_obj
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "ConversationsSelect":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "ConversationsSelect":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class ChannelsSelect(Element):
    """Channels select element."""

    type: Literal["channels_select"] = "channels_select"
    action_id: str
    placeholder: Union[PlainText, MrkdwnText]
    initial_channel: Optional[str] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the channels select as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
            "placeholder": self.placeholder.build(),
        }
        if self.initial_channel is not None:
            result["initial_channel"] = self.initial_channel
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str, placeholder: str) -> "ChannelsSelect":
        """Create a channels select with builder pattern."""
        return cls(action_id=action_id, placeholder=PlainText.create(placeholder))

    def set_initial_channel(self, channel: str) -> "ChannelsSelect":
        """Set initial channel and return self for chaining."""
        self.initial_channel = channel
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "ChannelsSelect":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "ChannelsSelect":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


# Multi-select elements follow the same pattern but with different type names
class MultiStaticSelect(Element):
    """Multi static select element."""

    type: Literal["multi_static_select"] = "multi_static_select"
    action_id: str
    placeholder: Union[PlainText, MrkdwnText]
    options: Optional[List[Option]] = None
    option_groups: Optional[List[OptionGroup]] = None
    initial_options: Optional[List[Option]] = None
    max_selected_items: Optional[int] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: Optional[List[Option]]) -> Optional[List[Option]]:
        """Validate number of options."""
        if v is not None:
            return validate_options_count(v, SlackConstraints.MAX_OPTIONS_PER_SELECT)
        return v

    def build(self) -> Dict[str, Any]:
        """Build the multi static select as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
            "placeholder": self.placeholder.build(),
        }
        if self.options is not None:
            result["options"] = [option.build() for option in self.options]  # type: ignore[misc]
        if self.option_groups is not None:
            result["option_groups"] = [group.build() for group in self.option_groups]  # type: ignore[misc]
        if self.initial_options is not None:
            result["initial_options"] = [
                option.build() for option in self.initial_options
            ]  # type: ignore[misc]
        if self.max_selected_items is not None:
            result["max_selected_items"] = self.max_selected_items  # type: ignore[assignment]
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(
        cls,
        action_id: str,
        placeholder: str,
        options: Optional[List[Option]] = None,
        option_groups: Optional[List[OptionGroup]] = None,
    ) -> "MultiStaticSelect":
        """Create a multi static select with builder pattern."""
        return cls(
            action_id=action_id,
            placeholder=PlainText.create(placeholder),
            options=options,
            option_groups=option_groups,
        )

    def set_initial_options(self, options: List[Option]) -> "MultiStaticSelect":
        """Set initial options and return self for chaining."""
        self.initial_options = options
        return self

    def set_max_selected_items(self, max_items: int) -> "MultiStaticSelect":
        """Set max selected items and return self for chaining."""
        self.max_selected_items = max_items
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "MultiStaticSelect":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "MultiStaticSelect":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


# Additional multi-select elements would follow the same pattern...
# For brevity, I'll include a few more key ones:


class MultiExternalSelect(Element):
    """Multi external select element."""

    type: Literal["multi_external_select"] = "multi_external_select"
    action_id: str
    placeholder: Union[PlainText, MrkdwnText]
    initial_options: Optional[List[Option]] = None
    min_query_length: Optional[int] = None
    max_selected_items: Optional[int] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the multi external select as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
            "placeholder": self.placeholder.build(),
        }
        if self.initial_options is not None:
            result["initial_options"] = [
                option.build() for option in self.initial_options
            ]  # type: ignore[misc]
        if self.min_query_length is not None:
            result["min_query_length"] = self.min_query_length  # type: ignore[assignment]
        if self.max_selected_items is not None:
            result["max_selected_items"] = self.max_selected_items  # type: ignore[assignment]
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str, placeholder: str) -> "MultiExternalSelect":
        """Create a multi external select with builder pattern."""
        return cls(action_id=action_id, placeholder=PlainText.create(placeholder))

    def set_initial_options(self, options: List[Option]) -> "MultiExternalSelect":
        """Set initial options and return self for chaining."""
        self.initial_options = options
        return self

    def set_min_query_length(self, length: int) -> "MultiExternalSelect":
        """Set min query length and return self for chaining."""
        self.min_query_length = length
        return self

    def set_max_selected_items(self, max_items: int) -> "MultiExternalSelect":
        """Set max selected items and return self for chaining."""
        self.max_selected_items = max_items
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "MultiExternalSelect":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "MultiExternalSelect":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class OverflowMenu(Element):
    """Overflow menu element."""

    type: Literal["overflow"] = "overflow"
    action_id: str
    options: List[Option]
    confirm: Optional[ConfirmationDialog] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: List[Option]) -> List[Option]:
        """Validate number of options."""
        return validate_options_count(v, SlackConstraints.MAX_OPTIONS_PER_OVERFLOW)

    def set_confirm(self, confirm: ConfirmationDialog) -> "OverflowMenu":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def build(self) -> Dict[str, Any]:
        """Build the overflow menu as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
            "options": [option.build() for option in self.options],
        }
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str, options: List[Option]) -> "OverflowMenu":
        """Create an overflow menu with builder pattern."""
        return cls(action_id=action_id, options=options)


class FileInput(Element):
    """File input element."""

    type: Literal["file_input"] = "file_input"
    action_id: str
    filetypes: Optional[List[str]] = None
    max_files: Optional[int] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the file input as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
        }
        if self.filetypes is not None:
            result["filetypes"] = self.filetypes  # type: ignore[assignment]
        if self.max_files is not None:
            result["max_files"] = self.max_files  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str) -> "FileInput":
        """Create a file input with builder pattern."""
        return cls(action_id=action_id)

    def set_filetypes(self, types: List[str]) -> "FileInput":
        """Set file types and return self for chaining."""
        self.filetypes = types
        return self

    def set_max_files(self, max_files: int) -> "FileInput":
        """Set max files and return self for chaining."""
        self.max_files = max_files
        return self


class RichTextInput(Element):
    """Rich text input element."""

    type: Literal["rich_text_input"] = "rich_text_input"
    action_id: str
    placeholder: Optional[Union[PlainText, MrkdwnText]] = None
    initial_value: Optional[str] = None
    dispatch_action_config: Optional[DispatchActionConfiguration] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def set_placeholder(
        self, placeholder: Union[str, PlainText, MrkdwnText]
    ) -> "RichTextInput":
        """Set placeholder and return self for chaining."""
        if isinstance(placeholder, str):
            self.placeholder = PlainText.create(placeholder)
        else:
            self.placeholder = placeholder
        return self

    def set_initial_value(self, initial_value: str) -> "RichTextInput":
        """Set initial value and return self for chaining."""
        self.initial_value = initial_value
        return self

    def build(self) -> Dict[str, Any]:
        """Build the rich text input as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
        }
        if self.placeholder is not None:
            result["placeholder"] = self.placeholder.build()  # type: ignore[assignment]
        if self.initial_value is not None:
            result["initial_value"] = self.initial_value
        if self.dispatch_action_config is not None:
            result["dispatch_action_config"] = self.dispatch_action_config.build()  # type: ignore[assignment]
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str) -> "RichTextInput":
        """Create a rich text input with builder pattern."""
        return cls(action_id=action_id)

    def set_dispatch_action_config(
        self, config: DispatchActionConfiguration
    ) -> "RichTextInput":
        """Set dispatch action config and return self for chaining."""
        self.dispatch_action_config = config
        return self

    def set_focus_on_load(self, focus: bool) -> "RichTextInput":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class Image(Element):
    """Image element."""

    type: Literal["image"] = "image"
    image_url: str
    alt_text: str

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, v: str) -> str:
        """Validate image URL length."""
        return validate_url(v)

    def build(self) -> Dict[str, Any]:
        """Build the image as a dictionary."""
        return {
            "type": self.type,
            "image_url": self.image_url,
            "alt_text": self.alt_text,
        }

    @classmethod
    def create(cls, image_url: str, alt_text: str) -> "Image":
        """Create an image with builder pattern."""
        return cls(image_url=image_url, alt_text=alt_text)


# Additional multi-select elements for completeness
class MultiUsersSelect(Element):
    """Multi users select element."""

    type: Literal["multi_users_select"] = "multi_users_select"
    action_id: str
    placeholder: Union[PlainText, MrkdwnText]
    initial_users: Optional[List[str]] = None
    max_selected_items: Optional[int] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the multi users select as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
            "placeholder": self.placeholder.build(),
        }
        if self.initial_users is not None:
            result["initial_users"] = self.initial_users
        if self.max_selected_items is not None:
            result["max_selected_items"] = self.max_selected_items  # type: ignore[assignment]
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str, placeholder: str) -> "MultiUsersSelect":
        """Create a multi users select with builder pattern."""
        return cls(action_id=action_id, placeholder=PlainText.create(placeholder))

    def set_initial_users(self, users: List[str]) -> "MultiUsersSelect":
        """Set initial users and return self for chaining."""
        self.initial_users = users
        return self

    def set_max_selected_items(self, max_items: int) -> "MultiUsersSelect":
        """Set max selected items and return self for chaining."""
        self.max_selected_items = max_items
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "MultiUsersSelect":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "MultiUsersSelect":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class MultiConversationsSelect(Element):
    """Multi conversations select element."""

    type: Literal["multi_conversations_select"] = "multi_conversations_select"
    action_id: str
    placeholder: Union[PlainText, MrkdwnText]
    initial_conversations: Optional[List[str]] = None
    default_to_current_conversation: Optional[bool] = None
    filter: Optional[Filter] = None
    max_selected_items: Optional[int] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the multi conversations select as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
            "placeholder": self.placeholder.build(),
        }
        if self.initial_conversations is not None:
            result["initial_conversations"] = self.initial_conversations
        if self.default_to_current_conversation is not None:
            result["default_to_current_conversation"] = (
                self.default_to_current_conversation
            )  # type: ignore[assignment]
        if self.filter is not None:
            result["filter"] = self.filter.build()
        if self.max_selected_items is not None:
            result["max_selected_items"] = self.max_selected_items  # type: ignore[assignment]
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str, placeholder: str) -> "MultiConversationsSelect":
        """Create a multi conversations select with builder pattern."""
        return cls(action_id=action_id, placeholder=PlainText.create(placeholder))

    def set_initial_conversations(
        self, conversations: List[str]
    ) -> "MultiConversationsSelect":
        """Set initial conversations and return self for chaining."""
        self.initial_conversations = conversations
        return self

    def set_default_to_current_conversation(
        self, default: bool
    ) -> "MultiConversationsSelect":
        """Set default to current conversation and return self for chaining."""
        self.default_to_current_conversation = default
        return self

    def set_filter(self, filter_obj: Filter) -> "MultiConversationsSelect":
        """Set filter and return self for chaining."""
        self.filter = filter_obj
        return self

    def set_max_selected_items(self, max_items: int) -> "MultiConversationsSelect":
        """Set max selected items and return self for chaining."""
        self.max_selected_items = max_items
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "MultiConversationsSelect":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "MultiConversationsSelect":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self


class MultiChannelsSelect(Element):
    """Multi channels select element."""

    type: Literal["multi_channels_select"] = "multi_channels_select"
    action_id: str
    placeholder: Union[PlainText, MrkdwnText]
    initial_channels: Optional[List[str]] = None
    max_selected_items: Optional[int] = None
    confirm: Optional[ConfirmationDialog] = None
    focus_on_load: Optional[bool] = None

    @field_validator("action_id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        """Validate action ID length."""
        return validate_action_id(v)

    def build(self) -> Dict[str, Any]:
        """Build the multi channels select as a dictionary."""
        result = {
            "type": self.type,
            "action_id": self.action_id,
            "placeholder": self.placeholder.build(),
        }
        if self.initial_channels is not None:
            result["initial_channels"] = self.initial_channels
        if self.max_selected_items is not None:
            result["max_selected_items"] = self.max_selected_items  # type: ignore[assignment]
        if self.confirm is not None:
            result["confirm"] = self.confirm.build()
        if self.focus_on_load is not None:
            result["focus_on_load"] = self.focus_on_load  # type: ignore[assignment]
        return result

    @classmethod
    def create(cls, action_id: str, placeholder: str) -> "MultiChannelsSelect":
        """Create a multi channels select with builder pattern."""
        return cls(action_id=action_id, placeholder=PlainText.create(placeholder))

    def set_initial_channels(self, channels: List[str]) -> "MultiChannelsSelect":
        """Set initial channels and return self for chaining."""
        self.initial_channels = channels
        return self

    def set_max_selected_items(self, max_items: int) -> "MultiChannelsSelect":
        """Set max selected items and return self for chaining."""
        self.max_selected_items = max_items
        return self

    def set_confirm(self, confirm: ConfirmationDialog) -> "MultiChannelsSelect":
        """Set confirmation dialog and return self for chaining."""
        self.confirm = confirm
        return self

    def set_focus_on_load(self, focus: bool) -> "MultiChannelsSelect":
        """Set focus on load and return self for chaining."""
        self.focus_on_load = focus
        return self
