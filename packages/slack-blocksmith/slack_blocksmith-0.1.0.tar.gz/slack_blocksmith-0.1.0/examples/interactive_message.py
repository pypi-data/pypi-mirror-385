"""Interactive message example using slack-block-kit-builder."""

from slack_block_kit_builder import (
    Button,
    ConfirmationDialog,
    Message,
    Option,
    OverflowMenu,
)
from slack_block_kit_builder.elements import (
    DatePicker,
    MultiStaticSelect,
    NumberInput,
    PlainTextInput,
    RadioButtons,
    StaticSelect,
)


def create_task_management_message():
    """Create a task management message with various interactive elements."""
    # Create options for select menus
    priority_options = [
        Option.create("🔥 High", "high"),
        Option.create("🟡 Medium", "medium"),
        Option.create("🟢 Low", "low"),
    ]

    status_options = [
        Option.create("📋 Todo", "todo"),
        Option.create("🔄 In Progress", "in_progress"),
        Option.create("✅ Done", "done"),
    ]

    assignee_options = [
        Option.create("Alice", "alice"),
        Option.create("Bob", "bob"),
        Option.create("Charlie", "charlie"),
    ]

    # Create confirmation dialog for delete action
    ConfirmationDialog.create(
        "Delete Task", "Are you sure you want to delete this task?", "Delete", "Cancel"
    ).set_style("danger")

    # Create overflow menu for additional actions
    overflow_options = [
        Option.create("Edit Task", "edit"),
        Option.create("Add Comment", "comment"),
        Option.create("Set Reminder", "reminder"),
    ]

    message = (
        Message.create()
        .add_header("Task Management Dashboard")
        .add_section(
            text="*Create New Task*",
            accessory=Button.create("+ New Task", "btn_new_task").style("primary"),
        )
        .add_divider()
        .add_section("**Task Filters:**")
        .add_actions(
            [
                StaticSelect.create("priority_filter", "Priority", priority_options),
                StaticSelect.create("status_filter", "Status", status_options),
                MultiStaticSelect.create(
                    "assignee_filter", "Assignees", [], assignee_options
                ),
            ]
        )
        .add_divider()
        .add_section("**Quick Actions:**")
        .add_actions(
            [
                Button.create("📊 View Reports", "btn_reports"),
                Button.create("📅 Calendar", "btn_calendar"),
                Button.create("⚙️ Settings", "btn_settings"),
                OverflowMenu.create("more_actions", overflow_options),
            ]
        )
        .add_context(["Last updated: 2 minutes ago", "Total tasks: 15", "Overdue: 3"])
    )

    return message.build()


def create_survey_message():
    """Create a survey message with various input types."""
    # Create rating options
    rating_options = [
        Option.create("⭐ 1", "1"),
        Option.create("⭐⭐ 2", "2"),
        Option.create("⭐⭐⭐ 3", "3"),
        Option.create("⭐⭐⭐⭐ 4", "4"),
        Option.create("⭐⭐⭐⭐⭐ 5", "5"),
    ]

    # Create feedback categories
    feedback_options = [
        Option.create("🐛 Bug Report", "bug"),
        Option.create("💡 Feature Request", "feature"),
        Option.create("📝 General Feedback", "general"),
        Option.create("❓ Question", "question"),
    ]

    message = (
        Message.create()
        .add_header("Customer Feedback Survey")
        .add_section("Help us improve our service by sharing your feedback!")
        .add_divider()
        .add_section("**Rate your experience:**")
        .add_actions([RadioButtons.create("rating_radio", rating_options)])
        .add_section("**What type of feedback is this?**")
        .add_actions(
            [StaticSelect.create("feedback_type", "Select category", feedback_options)]
        )
        .add_section("**Tell us more:**")
        .add_input(
            "Your feedback",
            PlainTextInput.create("feedback_text")
            .placeholder("Please share your thoughts...")
            .multiline(True)
            .min_length(10)
            .max_length(500),
        )
        .add_input(
            "Contact email (optional)",
            PlainTextInput.create("contact_email").placeholder(
                "your.email@example.com"
            ),
        )
        .add_input(
            "How likely are you to recommend us?",
            NumberInput.create("recommendation_score")
            .min_value("0")
            .max_value("10")
            .placeholder("Enter a number from 0-10"),
        )
        .add_input(
            "When did you last use our service?",
            DatePicker.create("last_used_date").placeholder("Select date"),
        )
        .add_actions(
            [
                Button.create("Submit Feedback", "btn_submit").style("primary"),
                Button.create("Save Draft", "btn_save_draft"),
            ]
        )
        .add_context(
            [
                "Your feedback is anonymous and will help us improve our service.",
                "Response time: 2-3 business days",
            ]
        )
    )

    return message.build()


def create_approval_workflow_message():
    """Create an approval workflow message with confirmation dialogs."""
    # Create confirmation dialogs
    approve_confirm = ConfirmationDialog.create(
        "Approve Request",
        "Are you sure you want to approve this request?",
        "Approve",
        "Cancel",
    ).style("primary")

    reject_confirm = ConfirmationDialog.create(
        "Reject Request",
        "Are you sure you want to reject this request? This action cannot be undone.",
        "Reject",
        "Cancel",
    ).style("danger")

    # Create options for rejection reason
    rejection_reasons = [
        Option.create("Incomplete information", "incomplete"),
        Option.create("Does not meet requirements", "requirements"),
        Option.create("Budget constraints", "budget"),
        Option.create("Timeline issues", "timeline"),
        Option.create("Other", "other"),
    ]

    message = (
        Message.create()
        .add_header("📋 Purchase Request Approval")
        .add_section(
            text='*Request Details:*\n• Item: MacBook Pro 16"\n• Amount: $2,499.00\n• Requested by: John Doe\n• Department: Engineering',
            accessory=Button.create("View Details", "btn_view_details"),
        )
        .add_divider()
        .add_section("**Approval Actions:**")
        .add_actions(
            [
                Button.create("✅ Approve", "btn_approve")
                .style("primary")
                .confirm(approve_confirm),
                Button.create("❌ Reject", "btn_reject")
                .style("danger")
                .confirm(reject_confirm),
            ]
        )
        .add_section("**If rejecting, please provide a reason:**")
        .add_actions(
            [
                StaticSelect.create(
                    "rejection_reason", "Select reason", rejection_reasons
                )
            ]
        )
        .add_input(
            "Additional comments",
            PlainTextInput.create("rejection_comments")
            .placeholder("Optional: Provide additional details...")
            .multiline(True),
        )
        .add_divider()
        .add_context(
            [
                "Request ID: REQ-2024-001",
                "Submitted: 2 hours ago",
                "Approval deadline: 24 hours",
            ]
        )
    )

    return message.build()


if __name__ == "__main__":
    print("=== Task Management Message ===")
    print(create_task_management_message())
    print("\n=== Survey Message ===")
    print(create_survey_message())
    print("\n=== Approval Workflow Message ===")
    print(create_approval_workflow_message())
