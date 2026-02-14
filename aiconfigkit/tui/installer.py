"""Textual TUI for installing instructions from library."""

from typing import Optional

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
)

from aiconfigkit.ai_tools.detector import get_detector
from aiconfigkit.core.models import InstallationScope
from aiconfigkit.storage.library import LibraryManager
from aiconfigkit.utils.project import find_project_root


class InstructionInstallerScreen(Screen):
    """Main screen for selecting and installing instructions."""

    CSS = """
    Screen {
        background: $background;
    }

    #title-container {
        height: 3;
        background: $boost;
        padding: 1;
        border-bottom: solid $primary;
    }

    #app-title {
        text-align: center;
        text-style: bold;
    }

    #search-container {
        height: 3;
        padding: 0 1;
        margin-top: 1;
    }

    #filter-container {
        height: 3;
        padding: 0 1;
    }

    #instructions-table {
        height: 1fr;
    }

    #installation-settings {
        height: auto;
        padding: 1;
        background: $panel;
        border-top: solid $primary;
    }

    #tools-container {
        height: auto;
        padding: 0 1;
    }

    #scope-container {
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
    }

    #status-bar {
        height: auto;
        padding: 1;
        background: $surface;
    }

    #actions-container {
        height: 3;
        padding: 0 1;
    }

    Button {
        margin: 0 1;
    }

    Checkbox {
        margin: 0 2;
    }

    .selected-row {
        background: $accent;
    }

    .setting-label {
        text-style: bold;
        color: $primary;
    }

    .help-text {
        color: $text-muted;
    }
    """

    BINDINGS = [
        ("escape", "quit", "Quit"),
        ("space", "toggle_selection", "Toggle Selection"),
        ("enter", "toggle_selection", "Toggle Selection"),
        ("ctrl+a", "select_all", "Select All"),
        ("ctrl+d", "deselect_all", "Deselect All"),
        ("ctrl+l", "clear_search", "Clear Search"),
        ("/", "focus_search", "Search"),
    ]

    def __init__(
        self,
        library: LibraryManager,
        tool: Optional[str] = None,
    ):
        """
        Initialize installer screen.

        Args:
            library: Library manager instance
            tool: AI tool to install to (ignored - user must select)
        """
        super().__init__()
        self.library = library
        # Always use project scope
        self.scope = InstallationScope.PROJECT
        self.instructions = library.list_instructions()
        self.filtered_instructions = self.instructions.copy()
        self.selected_ids: set[str] = set()

        # Get current directory info for display
        from pathlib import Path

        self.current_dir = Path.cwd()
        self.project_root = find_project_root()

        # Detect available AI tools
        detector = get_detector()
        self.available_tools = detector.detect_installed_tools()

        # No default tool selection - user must explicitly select
        self.selected_tools: set[str] = set()

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header(show_clock=True)

        # Branded title section
        with Container(id="title-container"):
            yield Static(
                "🎯 [bold cyan]DevSync[/bold cyan] [dim]│[/dim] " "Browse & Install Instructions",
                id="app-title",
            )

        # Search container
        with Container(id="search-container"):
            yield Input(placeholder="🔍 Search instructions by name or description...", id="search-input")

        # Filter container
        with Horizontal(id="filter-container"):
            # Repository filter
            repo_options = [("All Repositories", "")]
            repos = {inst.repo_namespace: inst.repo_name for inst in self.instructions}
            repo_options.extend([(name, namespace) for namespace, name in repos.items()])

            yield Label("Filter by Repo:")
            yield Select(
                options=repo_options,
                value="",
                id="repo-filter",
            )

        # Instructions table
        yield DataTable(id="instructions-table")

        # Installation Settings Section
        with Container(id="installation-settings"):
            yield Label("⚙️  Installation Settings (REQUIRED)", classes="setting-label")

            # Show installation location info
            with Vertical(id="scope-container"):
                yield Label("Installation location:")

                # Display where files will be installed
                if self.project_root:
                    help_text = f"Files will be installed to: {self.project_root}/<tool-specific-dir>/rules/"
                else:
                    help_text = f"Files will be installed to: {self.current_dir}/<tool-specific-dir>/rules/"
                yield Static(help_text, id="scope-help", classes="help-text")

            # Target tools selection
            with Vertical(id="tools-container"):
                yield Label("Install to which AI tools: *")
                if self.available_tools:
                    for tool in self.available_tools:
                        tool_id = tool.tool_type.value
                        # Start with nothing checked - user must select
                        yield Checkbox(
                            f"{tool.tool_name}",
                            value=False,
                            id=f"tool-{tool_id}",
                        )
                else:
                    yield Static("⚠️  No AI coding tools detected!", classes="help-text")

        # Status bar
        with Container(id="status-bar"):
            yield Static("", id="status-text")

        # Action buttons
        with Horizontal(id="actions-container"):
            yield Button("Cancel", variant="default", id="cancel-btn")
            yield Button("Select All", variant="primary", id="select-all-btn")
            yield Button("Clear Selection", variant="default", id="deselect-all-btn")
            yield Button("📦 Install Selected", variant="success", id="install-btn")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the table when mounted."""
        table = self.query_one("#instructions-table", DataTable)

        # Add columns
        table.add_column("☑", key="selected", width=3)
        table.add_column("Name", key="name", width=25)
        table.add_column("Description", key="description", width=40)
        table.add_column("Repository", key="repo", width=20)
        table.add_column("Author", key="author", width=15)
        table.add_column("Ver", key="version", width=8)
        table.add_column("Tags", key="tags", width=20)

        # Populate table
        self.refresh_table()
        self.update_status()

        # Set focus to the table instead of search input
        table.focus()

    def refresh_table(self) -> None:
        """Refresh the table with filtered instructions."""
        table = self.query_one("#instructions-table", DataTable)
        table.clear()

        for inst in self.filtered_instructions:
            is_selected = inst.id in self.selected_ids
            checkbox = "[✓]" if is_selected else "[ ]"

            # Truncate long text
            name = inst.name[:23] + "..." if len(inst.name) > 23 else inst.name
            desc = inst.description[:38] + "..." if len(inst.description) > 38 else inst.description
            repo = inst.repo_name[:18] + "..." if len(inst.repo_name) > 18 else inst.repo_name
            author = inst.author[:13] + "..." if len(inst.author) > 13 else inst.author
            tags = ", ".join(inst.tags[:2]) if inst.tags else "-"
            if len(inst.tags) > 2:
                tags += f" +{len(inst.tags) - 2}"

            table.add_row(
                checkbox,
                name,
                desc,
                repo,
                author,
                inst.version,
                tags,
                key=inst.id,
            )

    def update_status(self) -> None:
        """Update the status bar."""
        status = self.query_one("#status-text", Static)
        total = len(self.filtered_instructions)
        selected_instructions = len(self.selected_ids)
        selected_tools_count = len(self.selected_tools)

        # Tools text
        if selected_tools_count == 0:
            tools_text = "⚠️  None selected"
        elif selected_tools_count == len(self.available_tools):
            tools_text = f"All {selected_tools_count} tools"
        else:
            tools_text = f"{selected_tools_count} tool(s)"

        status.update(
            f"Instructions: {selected_instructions} selected | {total} shown | "
            f"Target: {tools_text} | Install to: Project"
        )

    def filter_instructions(
        self,
        search: str = "",
        repo_namespace: str = "",
    ) -> None:
        """
        Filter instructions based on criteria.

        Args:
            search: Search query
            repo_namespace: Repository namespace filter
        """
        self.filtered_instructions = self.instructions.copy()

        # Apply search filter
        if search:
            query = search.lower()
            self.filtered_instructions = [
                inst
                for inst in self.filtered_instructions
                if query in inst.name.lower() or query in inst.description.lower()
            ]

        # Apply repo filter
        if repo_namespace:
            self.filtered_instructions = [
                inst for inst in self.filtered_instructions if inst.repo_namespace == repo_namespace
            ]

        self.refresh_table()
        self.update_status()

    @on(Input.Changed, "#search-input")
    def on_search_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        repo_filter = self.query_one("#repo-filter", Select).value
        # Convert to string, handling NoSelection or other non-string values
        repo_filter_str = str(repo_filter) if repo_filter is not None else ""
        self.filter_instructions(search=event.value, repo_namespace=repo_filter_str)

    @on(Select.Changed, "#repo-filter")
    def on_repo_filter_changed(self, event: Select.Changed) -> None:
        """Handle repository filter changes."""
        search = self.query_one("#search-input", Input).value
        self.filter_instructions(search=search, repo_namespace=str(event.value))

    @on(Checkbox.Changed)
    def on_tool_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle tool checkbox changes."""
        # Extract tool name from checkbox ID (format: "tool-cursor")
        checkbox_id = event.checkbox.id
        if checkbox_id and checkbox_id.startswith("tool-"):
            tool_name = checkbox_id[5:]  # Remove "tool-" prefix

            if event.value:
                self.selected_tools.add(tool_name)
            else:
                self.selected_tools.discard(tool_name)

            self.update_status()

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Toggle selection when row is clicked."""
        if event.row_key:
            instruction_id = str(event.row_key.value)

            if instruction_id in self.selected_ids:
                self.selected_ids.remove(instruction_id)
            else:
                self.selected_ids.add(instruction_id)

            self.refresh_table()
            self.update_status()

    @on(Button.Pressed, "#select-all-btn")
    def action_select_all(self) -> None:
        """Select all filtered instructions."""
        self.selected_ids.update(inst.id for inst in self.filtered_instructions)
        self.refresh_table()
        self.update_status()

    @on(Button.Pressed, "#deselect-all-btn")
    def action_deselect_all(self) -> None:
        """Deselect all instructions."""
        self.selected_ids.clear()
        self.refresh_table()
        self.update_status()

    def action_toggle_selection(self) -> None:
        """Toggle selection of the currently highlighted row."""
        table = self.query_one("#instructions-table", DataTable)

        # Get the currently highlighted row
        if table.cursor_row is not None and table.cursor_row >= 0:
            # Get all row keys as a list
            row_keys = list(table.rows.keys())
            if table.cursor_row < len(row_keys):
                row_key = row_keys[table.cursor_row]
                # Access the .value property of the RowKey to get the actual instruction ID
                instruction_id = str(row_key.value)

                # Toggle selection
                if instruction_id in self.selected_ids:
                    self.selected_ids.remove(instruction_id)
                else:
                    self.selected_ids.add(instruction_id)

                self.refresh_table()
                self.update_status()

    def action_clear_search(self) -> None:
        """Clear search input."""
        search_input = self.query_one("#search-input", Input)
        search_input.value = ""
        search_input.focus()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one("#search-input", Input).focus()

    @on(Button.Pressed, "#cancel-btn")
    def action_quit(self) -> None:
        """Cancel and exit."""
        self.dismiss(None)

    @on(Button.Pressed, "#install-btn")
    def on_install_pressed(self) -> None:
        """Handle install button press."""
        # Validate all required selections
        errors = []

        if not self.selected_ids:
            errors.append("Please select at least one instruction")

        if not self.selected_tools:
            errors.append("Please select at least one AI tool")

        # Show all errors
        if errors:
            for error in errors:
                self.app.notify(error, severity="error", timeout=4)
            return

        # Get selected instructions
        selected_instructions = [inst for inst in self.instructions if inst.id in self.selected_ids]

        # Return result with selected tools as a list
        self.dismiss(
            {
                "instructions": selected_instructions,
                "tools": list(self.selected_tools),  # Return as list
            }
        )


class InstructionInstallerApp(App):
    """Application for installing instructions."""

    TITLE = "DevSync Installer"
    SUB_TITLE = "Browse, Select & Install Instructions"

    def __init__(
        self,
        library: LibraryManager,
        tool: Optional[str] = None,
    ):
        """
        Initialize installer app.

        Args:
            library: Library manager instance
            tool: AI tool to install to (None = all)
        """
        super().__init__()
        self.library = library
        self.tool = tool
        self.result: Optional[dict] = None

    def on_mount(self) -> None:
        """Push the installer screen when app mounts."""
        screen = InstructionInstallerScreen(
            library=self.library,
            tool=self.tool,
        )
        self.push_screen(screen, self.handle_result)

    def handle_result(self, result: Optional[dict]) -> None:
        """Handle result from installer screen."""
        self.result = result
        self.exit()


def show_installer_tui(
    library: LibraryManager,
    tool: Optional[str] = None,
) -> Optional[dict]:
    """
    Show the instruction installer TUI.

    All installations are at project level.

    Args:
        library: Library manager instance
        tool: AI tool to install to (None = all)

    Returns:
        Dictionary with selected instructions and settings, or None if cancelled
    """
    app = InstructionInstallerApp(library=library, tool=tool)
    app.run()
    return app.result
