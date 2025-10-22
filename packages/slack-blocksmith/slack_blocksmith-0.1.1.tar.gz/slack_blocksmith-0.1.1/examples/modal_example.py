"""Modal example using slack-block-kit-builder."""

from slack_block_kit_builder import Button, ConfirmationDialog, Modal
from slack_block_kit_builder.elements import (
    Checkboxes,
    DatePicker,
    EmailInput,
    MultiStaticSelect,
    NumberInput,
    Option,
    PlainTextInput,
    RadioButtons,
    StaticSelect,
    TimePicker,
)


def create_user_registration_modal():
    """Create a user registration modal with various input types."""
    # Create options for select menus
    department_options = [
        Option.create("Engineering", "engineering"),
        Option.create("Marketing", "marketing"),
        Option.create("Sales", "sales"),
        Option.create("HR", "hr"),
        Option.create("Finance", "finance"),
    ]

    role_options = [
        Option.create("Manager", "manager"),
        Option.create("Senior", "senior"),
        Option.create("Mid-level", "mid"),
        Option.create("Junior", "junior"),
        Option.create("Intern", "intern"),
    ]

    skill_options = [
        Option.create("Python", "python"),
        Option.create("JavaScript", "javascript"),
        Option.create("Go", "go"),
        Option.create("Java", "java"),
        Option.create("C++", "cpp"),
        Option.create("React", "react"),
        Option.create("Vue.js", "vue"),
        Option.create("Angular", "angular"),
    ]

    experience_options = [
        Option.create("0-1 years", "0-1"),
        Option.create("2-3 years", "2-3"),
        Option.create("4-5 years", "4-5"),
        Option.create("6-10 years", "6-10"),
        Option.create("10+ years", "10+"),
    ]

    modal = (
        Modal.create("User Registration")
        .add_header("👤 New User Registration")
        .add_section("Please fill out the form below to register a new user.")
        .add_divider()
        .add_section("**Personal Information**")
        .add_input(
            "Full Name *",
            PlainTextInput.create("full_name")
            .placeholder("Enter full name")
            .max_length(100),
        )
        .add_input(
            "Email Address *",
            EmailInput.create("email").placeholder("user@company.com"),
        )
        .add_input(
            "Phone Number",
            PlainTextInput.create("phone").placeholder("+1 (555) 123-4567"),
        )
        .add_input(
            "Date of Birth", DatePicker.create("birth_date").placeholder("Select date")
        )
        .add_divider()
        .add_section("**Work Information**")
        .add_input(
            "Department *",
            StaticSelect.create("department", "Select department", department_options),
        )
        .add_input("Role *", StaticSelect.create("role", "Select role", role_options))
        .add_input(
            "Employee ID", PlainTextInput.create("employee_id").placeholder("EMP-12345")
        )
        .add_input(
            "Start Date *",
            DatePicker.create("start_date").placeholder("Select start date"),
        )
        .add_input(
            "Salary (optional)",
            NumberInput.create("salary")
            .placeholder("Enter annual salary")
            .is_decimal_allowed(True),
        )
        .add_divider()
        .add_section("**Skills & Experience**")
        .add_input(
            "Technical Skills",
            MultiStaticSelect.create("skills", "Select skills", skill_options),
        )
        .add_input(
            "Years of Experience *",
            RadioButtons.create("experience", experience_options),
        )
        .add_input(
            "Additional Notes",
            PlainTextInput.create("notes")
            .placeholder("Any additional information...")
            .multiline(True)
            .max_length(500),
        )
        .add_divider()
        .add_section("**Preferences**")
        .add_input(
            "Preferred working hours",
            TimePicker.create("start_time").placeholder("Start time"),
        )
        .add_input("End time", TimePicker.create("end_time").placeholder("End time"))
        .add_input(
            "Notification preferences",
            Checkboxes.create(
                "notifications",
                [
                    Option.create("Email notifications", "email"),
                    Option.create("Slack notifications", "slack"),
                    Option.create("SMS notifications", "sms"),
                ],
            ),
        )
        .submit("Register User")
        .close("Cancel")
        .private_metadata("user_registration_form")
        .callback_id("user_registration_callback")
        .clear_on_close(True)
        .notify_on_close(True)
    )

    return modal.build()


def create_project_creation_modal():
    """Create a project creation modal with complex form elements."""
    # Create options for project types
    project_type_options = [
        Option.create("Web Application", "web_app"),
        Option.create("Mobile App", "mobile_app"),
        Option.create("API Development", "api"),
        Option.create("Data Analysis", "data_analysis"),
        Option.create("Machine Learning", "ml"),
        Option.create("DevOps", "devops"),
    ]

    priority_options = [
        Option.create("🔴 Critical", "critical"),
        Option.create("🟡 High", "high"),
        Option.create("🟢 Medium", "medium"),
        Option.create("⚪ Low", "low"),
    ]

    team_member_options = [
        Option.create("Alice Johnson", "alice"),
        Option.create("Bob Smith", "bob"),
        Option.create("Charlie Brown", "charlie"),
        Option.create("Diana Prince", "diana"),
        Option.create("Eve Wilson", "eve"),
    ]

    technology_options = [
        Option.create("Python", "python"),
        Option.create("JavaScript", "javascript"),
        Option.create("TypeScript", "typescript"),
        Option.create("React", "react"),
        Option.create("Vue.js", "vue"),
        Option.create("Node.js", "nodejs"),
        Option.create("Django", "django"),
        Option.create("Flask", "flask"),
        Option.create("FastAPI", "fastapi"),
        Option.create("PostgreSQL", "postgresql"),
        Option.create("MongoDB", "mongodb"),
        Option.create("Redis", "redis"),
        Option.create("Docker", "docker"),
        Option.create("Kubernetes", "kubernetes"),
    ]

    modal = (
        Modal.create("Create New Project")
        .add_header("🚀 New Project Setup")
        .add_section("Create a new project with the details below.")
        .add_divider()
        .add_section("**Project Details**")
        .add_input(
            "Project Name *",
            PlainTextInput.create("project_name")
            .placeholder("Enter project name")
            .max_length(100),
        )
        .add_input(
            "Project Description *",
            PlainTextInput.create("project_description")
            .placeholder("Describe the project goals and requirements...")
            .multiline(True)
            .max_length(1000),
        )
        .add_input(
            "Project Type *",
            StaticSelect.create(
                "project_type", "Select project type", project_type_options
            ),
        )
        .add_input(
            "Priority *",
            StaticSelect.create("priority", "Select priority", priority_options),
        )
        .add_divider()
        .add_section("**Timeline & Resources**")
        .add_input(
            "Start Date *",
            DatePicker.create("start_date").placeholder("Select start date"),
        )
        .add_input(
            "Target End Date *",
            DatePicker.create("end_date").placeholder("Select target end date"),
        )
        .add_input(
            "Estimated Hours",
            NumberInput.create("estimated_hours")
            .placeholder("Enter estimated hours")
            .min_value("1")
            .max_value("10000"),
        )
        .add_input(
            "Budget (optional)",
            NumberInput.create("budget")
            .placeholder("Enter budget in USD")
            .is_decimal_allowed(True),
        )
        .add_divider()
        .add_section("**Team & Technology**")
        .add_input(
            "Team Members *",
            MultiStaticSelect.create(
                "team_members", "Select team members", team_member_options
            ),
        )
        .add_input(
            "Technologies *",
            MultiStaticSelect.create(
                "technologies", "Select technologies", technology_options
            ),
        )
        .add_input(
            "Project Manager",
            StaticSelect.create(
                "project_manager", "Select project manager", team_member_options
            ),
        )
        .add_divider()
        .add_section("**Additional Information**")
        .add_input(
            "Client/Stakeholder",
            PlainTextInput.create("client").placeholder(
                "Enter client or stakeholder name"
            ),
        )
        .add_input(
            "Special Requirements",
            PlainTextInput.create("requirements")
            .placeholder("Any special requirements or constraints...")
            .multiline(True)
            .max_length(500),
        )
        .add_input(
            "Risk Assessment",
            RadioButtons.create(
                "risk_level",
                [
                    Option.create("Low Risk", "low"),
                    Option.create("Medium Risk", "medium"),
                    Option.create("High Risk", "high"),
                    Option.create("Critical Risk", "critical"),
                ],
            ),
        )
        .add_input(
            "Documentation Required",
            Checkboxes.create(
                "documentation",
                [
                    Option.create("Technical Documentation", "technical"),
                    Option.create("User Manual", "user_manual"),
                    Option.create("API Documentation", "api_docs"),
                    Option.create("Deployment Guide", "deployment"),
                    Option.create("Testing Documentation", "testing"),
                ],
            ),
        )
        .submit("Create Project")
        .close("Cancel")
        .private_metadata("project_creation_form")
        .callback_id("project_creation_callback")
        .clear_on_close(True)
        .notify_on_close(True)
    )

    return modal.build()


def create_settings_modal():
    """Create a settings modal with various configuration options."""
    # Create confirmation dialog for reset action
    reset_confirm = ConfirmationDialog.create(
        "Reset Settings",
        "Are you sure you want to reset all settings to default values? This action cannot be undone.",
        "Reset",
        "Cancel",
    ).style("danger")

    modal = (
        Modal.create("Application Settings")
        .add_header("⚙️ Configure Application Settings")
        .add_section("Customize your application preferences below.")
        .add_divider()
        .add_section("**General Settings**")
        .add_input(
            "Application Name",
            PlainTextInput.create("app_name")
            .placeholder("Enter application name")
            .initial_value("My Application"),
        )
        .add_input(
            "Default Language",
            StaticSelect.create(
                "language",
                "Select language",
                [
                    Option.create("English", "en"),
                    Option.create("Spanish", "es"),
                    Option.create("French", "fr"),
                    Option.create("German", "de"),
                    Option.create("Chinese", "zh"),
                ],
            ),
        )
        .add_input(
            "Timezone",
            StaticSelect.create(
                "timezone",
                "Select timezone",
                [
                    Option.create("UTC", "UTC"),
                    Option.create("EST (UTC-5)", "EST"),
                    Option.create("PST (UTC-8)", "PST"),
                    Option.create("CET (UTC+1)", "CET"),
                    Option.create("JST (UTC+9)", "JST"),
                ],
            ),
        )
        .add_divider()
        .add_section("**Notification Settings**")
        .add_input(
            "Email Notifications",
            Checkboxes.create(
                "email_notifications",
                [
                    Option.create("System Alerts", "system"),
                    Option.create("User Activity", "activity"),
                    Option.create("Security Events", "security"),
                    Option.create("Weekly Reports", "reports"),
                ],
            ),
        )
        .add_input(
            "Notification Frequency",
            RadioButtons.create(
                "notification_frequency",
                [
                    Option.create("Immediate", "immediate"),
                    Option.create("Hourly", "hourly"),
                    Option.create("Daily", "daily"),
                    Option.create("Weekly", "weekly"),
                ],
            ),
        )
        .add_divider()
        .add_section("**Security Settings**")
        .add_input(
            "Session Timeout (minutes)",
            NumberInput.create("session_timeout")
            .placeholder("Enter timeout in minutes")
            .initial_value("30")
            .min_value("5")
            .max_value("480"),
        )
        .add_input(
            "Require Two-Factor Authentication",
            Checkboxes.create(
                "2fa_required",
                [Option.create("Enable 2FA for all users", "enable_2fa")],
            ),
        )
        .add_input(
            "Password Policy",
            StaticSelect.create(
                "password_policy",
                "Select password policy",
                [
                    Option.create("Basic (8+ characters)", "basic"),
                    Option.create("Strong (12+ characters, mixed case)", "strong"),
                    Option.create(
                        "Very Strong (16+ characters, special chars)", "very_strong"
                    ),
                ],
            ),
        )
        .add_divider()
        .add_section("**Actions**")
        .add_actions(
            [
                Button.create("💾 Save Settings", "btn_save").style("primary"),
                Button.create("🔄 Reset to Default", "btn_reset")
                .style("danger")
                .confirm(reset_confirm),
                Button.create("📤 Export Settings", "btn_export"),
            ]
        )
        .submit("Save Changes")
        .close("Cancel")
        .private_metadata("settings_form")
        .callback_id("settings_callback")
        .clear_on_close(False)
        .notify_on_close(True)
    )

    return modal.build()


if __name__ == "__main__":
    print("=== User Registration Modal ===")
    print(create_user_registration_modal())
    print("\n=== Project Creation Modal ===")
    print(create_project_creation_modal())
    print("\n=== Settings Modal ===")
    print(create_settings_modal())
