import json
from pathlib import Path
from nicegui import ui, app
import asyncio
from importlib import resources as importlib_resources
from typing import Dict, Any, Optional

from nemo_library_etl.adapter._utils.config import _deep_merge
from nemo_library_etl.adapter.migman.migmanutils import MigManUtils
from nemo_library_etl.adapter.migman.symbols import MIGMAN_PROJECT_POSTFIX_SEPARATOR


class MigManUI:
    """NiceGUI-based configuration UI for MigMan without hardcoded colors."""

    def load_configurations(self) -> tuple[dict, dict, dict]:
        """Load default and local configuration files and merge them."""
        resource_rel = "adapter/migman/config/default_config_migman.json"
        with importlib_resources.as_file(
            importlib_resources.files("nemo_library_etl").joinpath(resource_rel)
        ) as p:
            with p.open("r", encoding="utf-8") as f:
                global_config = json.load(f)

        local_config_file = Path("./config") / "migman.json"
        if local_config_file.exists():
            with local_config_file.open("r", encoding="utf-8") as f:
                local_config = json.load(f)
        else:
            local_config = {}

        merged_config = _deep_merge(global_config, local_config)
        return global_config, local_config, merged_config

    def _get_config_differences(
        self, current_config: Dict[str, Any], default_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get only the values that differ from default configuration."""
        differences = {}

        for key, value in current_config.items():
            if key not in default_config:
                # New key not in defaults, include it
                differences[key] = value
            elif isinstance(value, dict) and isinstance(default_config[key], dict):
                # Recursively check nested dictionaries
                nested_diff = self._get_config_differences(value, default_config[key])
                if nested_diff:  # Only include if there are differences
                    differences[key] = nested_diff
            elif value != default_config[key]:
                # Value differs from default
                differences[key] = value

        return differences

    def save_configuration(self, config_data: Dict[str, Any]) -> bool:
        """Save only non-default configuration values to local config file."""
        try:
            # Load the current default configuration
            resource_rel = "adapter/migman/config/default_config_migman.json"
            with importlib_resources.as_file(
                importlib_resources.files("nemo_library_etl").joinpath(resource_rel)
            ) as p:
                with p.open("r", encoding="utf-8") as f:
                    default_config = json.load(f)

            # Get only the differences from default configuration
            config_to_save = self._get_config_differences(config_data, default_config)

            local_config_file = Path("./config") / "migman.json"
            local_config_file.parent.mkdir(exist_ok=True)

            with local_config_file.open("w", encoding="utf-8") as f:
                json.dump(config_to_save, f, indent=4, ensure_ascii=False)

            ui.notify("Configuration saved successfully!", type="positive")
            return True
        except Exception as e:
            ui.notify(f"Error saving configuration: {str(e)}", type="negative")
            return False

    def reset_configuration(self) -> bool:
        """Reset configuration to defaults by deleting local config file."""
        try:
            local_config_file = Path("./config") / "migman.json"
            if local_config_file.exists():
                local_config_file.unlink()
                ui.notify("Configuration reset successfully!", type="positive")
            else:
                ui.notify("No local configuration found to reset.", type="info")
            return True
        except Exception as e:
            ui.notify(f"Error resetting configuration: {str(e)}", type="negative")
            return False

    def run_ui(self, *, open_browser: bool = True) -> None:
        """Start the NiceGUI interface for MigMan configuration.

        Args:
            open_browser: whether to open the browser automatically
        """

        connected_clients = set()
        global_config, local_config, merged_config = self.load_configurations()

        # Load dark mode setting from configuration
        dark_mode_enabled = merged_config.get("ui_dark_model", True)

        migmandatabase = MigManUtils.MigManDatabaseLoad()
        migmanprojects = sorted(
            [
                project_name
                for project_name in [
                    (
                        (f"{m.project} {MIGMAN_PROJECT_POSTFIX_SEPARATOR} {m.postfix}")
                        if m.postfix and m.project
                        else m.project
                    )
                    for m in migmandatabase
                ]
                if project_name is not None
            ]
        )
        migmanprojects = sorted(list(set(migmanprojects)))

        # State to track changes and form data
        form_state = {
            "has_changes": False,
            "data": merged_config.copy(),
        }

        # Ensure ui_dark_model is set in form data
        if "ui_dark_model" not in form_state["data"]:
            form_state["data"]["ui_dark_model"] = dark_mode_enabled

        @app.on_connect
        def on_connect(client):
            connected_clients.add(client.id)

        @app.on_disconnect
        async def on_disconnect(client):
            connected_clients.discard(client.id)
            if not connected_clients:
                await asyncio.sleep(0.3)
                app.shutdown()

        @ui.page("/")
        def index():
            # Keep a small reactive state for dark mode so we can toggle it at runtime.
            state = {"dark": dark_mode_enabled}

            # Apply initial theme
            if state["dark"]:
                ui.dark_mode().enable()
            else:
                ui.dark_mode().disable()

            # UI component references
            content_container: Optional[ui.column] = None
            save_button: Optional[ui.button] = None
            nav_buttons = {}
            active = {"value": "Global"}

            def mark_changed():
                """Mark form as changed and enable save button."""
                form_state["has_changes"] = True
                if save_button:
                    save_button.props(remove="disable")

            def mark_saved():
                """Mark form as saved and disable save button."""
                form_state["has_changes"] = False
                if save_button:
                    save_button.props("disable")

            def set_active(name: str):
                """Update the active navigation button appearance using theme props."""
                active["value"] = name
                for key, btn in nav_buttons.items():
                    btn.props(remove="color unelevated")
                    btn.props("flat")
                    if key == name:
                        btn.props(remove="flat")
                        btn.props("color=primary unelevated")

            def save_config():
                """Save current configuration to file."""
                if self.save_configuration(form_state["data"]):
                    mark_saved()

            def reset_config():
                """Reset configuration to defaults."""
                if self.reset_configuration():
                    # Reload configurations
                    nonlocal global_config, local_config, merged_config
                    global_config, local_config, merged_config = (
                        self.load_configurations()
                    )

                    # Update form state with the new merged config
                    form_state["data"] = merged_config.copy()
                    form_state["has_changes"] = False

                    # Update dark mode from reset config and apply it
                    new_dark_mode = merged_config.get("ui_dark_model", True)
                    state["dark"] = new_dark_mode
                    if new_dark_mode:
                        ui.dark_mode().enable()
                    else:
                        ui.dark_mode().disable()

                    # Mark as saved (since we're back to defaults)
                    mark_saved()

                    # Re-render the current active section to reflect changes
                    current_active = active["value"]
                    if current_active == "Global":
                        render_global()
                    elif current_active == "Setup":
                        render_setup()
                    elif current_active == "Extract":
                        render_extract()
                    elif current_active == "Transform":
                        render_transform()
                    elif current_active == "Load":
                        render_load()

            # ---------- GLOBAL TOP BAR WITH SAVE BUTTON, RESET BUTTON AND DARK-MODE TOGGLE ----------
            with ui.element("div").classes("fixed top-2 right-4 z-50"):
                with ui.row().classes("items-center gap-3"):
                    # Reset button (with confirmation dialog)
                    def confirm_reset():
                        """Show confirmation dialog before resetting."""

                        async def on_confirm():
                            reset_config()
                            dialog.close()

                        async def on_cancel():
                            dialog.close()

                        with ui.dialog() as dialog, ui.card():
                            ui.label("Reset Configuration").classes(
                                "text-lg font-semibold"
                            )
                            ui.label(
                                "Do you really want to delete all individual configurations and reset to default values?"
                            ).classes("mb-4")

                            with ui.row().classes("gap-2 justify-end"):
                                ui.button("Cancel", on_click=on_cancel).props("flat")
                                ui.button("Reset", on_click=on_confirm).props(
                                    "color=negative"
                                )

                        dialog.open()

                    ui.button(
                        "Reset", icon="restart_alt", on_click=confirm_reset
                    ).props("color=negative outline")

                    # Save button (initially disabled)
                    save_button = ui.button(
                        "Save", icon="save", on_click=save_config
                    ).props("disable")

                    ui.separator().props("vertical")

                    ui.label("Dark mode")

                    def on_toggle(e):
                        """Enable/disable dark mode globally at runtime."""
                        state["dark"] = e.value
                        form_state["data"]["ui_dark_model"] = e.value
                        mark_changed()
                        if state["dark"]:
                            ui.dark_mode().enable()
                        else:
                            ui.dark_mode().disable()

                    ui.switch(value=state["dark"], on_change=on_toggle)

            # -------------------- Renderers --------------------
            def render_global():
                if not content_container:
                    return

                content_container.clear()
                with content_container:
                    ui.label("Global Settings").classes("text-2xl font-semibold")
                    ui.separator()
                    ui.label("Configure global settings for the MigMan ETL process.")

                    current_etl_directory = form_state["data"].get(
                        "etl_directory", "./etl/migman"
                    )

                    # --- ETL Directory (editable) ---
                    with ui.card().classes(""):
                        ui.label("ETL directory").classes("text-lg font-semibold mb-2")

                        def on_etl_dir_change(e):
                            form_state["data"]["etl_directory"] = e.value
                            mark_changed()

                        etl_dir_input = (
                            ui.input(
                                label="Path to ETL folder",
                                value=current_etl_directory,
                                placeholder="e.g. /Users/me/projects/migman/etl",
                                on_change=on_etl_dir_change,
                                validation={
                                    "Required": lambda v: bool(v and v.strip())
                                },
                            )
                            .props("dense")
                            .classes("w-[36rem]")
                        )
                        ui.label(
                            "Enter an absolute or relative path to a local folder."
                        ).classes("text-sm")

            def render_setup():
                if not content_container:
                    return

                content_container.clear()
                with content_container:
                    ui.label("Setup").classes("text-2xl font-semibold")
                    ui.separator()
                    ui.label("Configure system setup and connection parameters.")

                    # Setup configuration
                    setup_config = form_state["data"].setdefault("setup", {})

                    # --- Project Status File ---
                    with ui.card().classes("mt-4"):
                        ui.label("Project Status File").classes(
                            "text-lg font-semibold mb-2"
                        )

                        def on_project_status_file_change(e):
                            setup_config["project_status_file"] = (
                                e.value if e.value.strip() else None
                            )
                            mark_changed()

                        current_project_status_file = setup_config.get(
                            "project_status_file", ""
                        )
                        if current_project_status_file is None:
                            current_project_status_file = ""

                        with ui.row().classes("gap-2 items-end"):
                            project_status_file_input = (
                                ui.input(
                                    label="Path to project status file",
                                    value=current_project_status_file,
                                    placeholder="e.g. ./etl/migman/status/project_status.xlsx",
                                    on_change=on_project_status_file_change,
                                )
                                .props("dense")
                                .classes("w-[36rem]")
                            )

                            def import_projects_from_file():
                                """Import projects from the specified Excel file."""
                                file_path = project_status_file_input.value
                                if not file_path or not file_path.strip():
                                    ui.notify(
                                        "Please enter a file path first.",
                                        type="warning",
                                    )
                                    return

                                try:
                                    # Check if file exists
                                    import os

                                    if not os.path.exists(file_path):
                                        ui.notify(
                                            f"File not found: {file_path}",
                                            type="negative",
                                        )
                                        return

                                    imported_projects = (
                                        MigManUtils.get_migman_projects_from_excel(
                                            file_path
                                        )
                                    )

                                    # Filter imported projects to only include those that exist in migmanprojects
                                    valid_projects = [
                                        p
                                        for p in imported_projects
                                        if p in migmanprojects
                                    ]
                                    invalid_projects = [
                                        p
                                        for p in imported_projects
                                        if p not in migmanprojects
                                    ]

                                    if valid_projects:
                                        # Update the projects selection
                                        setup_config["projects"] = valid_projects
                                        projects_select.value = valid_projects
                                        mark_changed()
                                        update_selection_count()

                                        message = f"Imported {len(valid_projects)} projects successfully!"
                                        if invalid_projects:
                                            message += f" ({len(invalid_projects)} projects not found in database)"
                                        ui.notify(message, type="positive")
                                    else:
                                        ui.notify(
                                            "No valid projects found in the file.",
                                            type="warning",
                                        )
                                        if invalid_projects:
                                            ui.notify(
                                                f"Invalid projects: {', '.join(invalid_projects[:5])}",
                                                type="info",
                                            )

                                except Exception as e:
                                    ui.notify(
                                        f"Error importing file: {str(e)}",
                                        type="negative",
                                    )

                            ui.button(
                                "Import",
                                icon="upload_file",
                                on_click=import_projects_from_file,
                            ).props("size=sm outline").classes("mb-1")

                        ui.label(
                            "Optional file path to track project status and progress. Use the Import button to load projects from this Excel file."
                        ).classes("text-sm")

                    # --- Projects Selection ---
                    with ui.card().classes("mt-4"):
                        ui.label("Projects").classes("text-lg font-semibold mb-2")

                        current_projects = setup_config.get("projects", [])

                        # Display selection count (will be updated via function)
                        selection_count = ui.label(
                            f"Selected: {len(current_projects)}"
                        ).classes("text-sm font-medium")

                        def update_selection_count():
                            current_selection = setup_config.get("projects", [])
                            selection_count.text = f"Selected: {len(current_selection)}"

                        def on_projects_change(e):
                            setup_config["projects"] = e.value if e.value else []
                            mark_changed()
                            update_selection_count()

                        projects_select = (
                            ui.select(
                                options=migmanprojects,
                                value=current_projects,
                                multiple=True,
                                label="Select projects",
                                on_change=on_projects_change,
                            )
                            .props("use-chips clearable use-input input-debounce=0")
                            .classes("w-[48rem]")
                        )

                        # Add helper text
                        ui.label(
                            f"Select one or more projects from the list. Search functionality is available."
                        ).classes("text-sm mt-2")

                        # Add buttons for quick selection
                        with ui.row().classes("gap-2 mt-3"):

                            def select_all():
                                setup_config["projects"] = migmanprojects.copy()
                                projects_select.value = migmanprojects.copy()
                                mark_changed()
                                update_selection_count()

                            def select_none():
                                setup_config["projects"] = []
                                projects_select.value = []
                                mark_changed()
                                update_selection_count()

                            ui.button("Select All", on_click=select_all).props(
                                "size=sm outline"
                            )
                            ui.button("Select None", on_click=select_none).props(
                                "size=sm outline"
                            )

                    # --- Multi-Project List for Feature Assignments ---
                    with ui.card().classes("mt-4"):
                        ui.label("Multi-Project List for Feature Assignments").classes(
                            "text-lg font-semibold mb-2"
                        )

                        current_feature_assignments = setup_config.get("mult_project_list_feature_assignments", [])

                        # Display selection count for feature assignments
                        feature_assignments_count = ui.label(
                            f"Keys: {len(current_feature_assignments)}"
                        ).classes("text-sm font-medium")

                        def update_feature_assignments_count():
                            current_selection = setup_config.get("mult_project_list_feature_assignments", [])
                            feature_assignments_count.text = f"Keys: {len(current_selection)}"

                        def on_feature_assignments_change(e):
                            # Split by comma, strip whitespace, and filter out empty strings
                            keys = [key.strip() for key in (e.value or "").split(",") if key.strip()]
                            setup_config["mult_project_list_feature_assignments"] = keys
                            mark_changed()
                            update_feature_assignments_count()

                        feature_assignments_input = (
                            ui.input(
                                label="Feature assignment keys (comma-separated)",
                                value=", ".join(current_feature_assignments),
                                placeholder="key1, key2, key3",
                                on_change=on_feature_assignments_change,
                            )
                            .props("dense")
                            .classes("w-[48rem]")
                        )

                        ui.label(
                            "Enter comma-separated keys for feature assignments. Each key should be a single word."
                        ).classes("text-sm mt-2")

                    # --- Multi-Project List for Texts ---
                    with ui.card().classes("mt-4"):
                        ui.label("Multi-Project List for Texts").classes(
                            "text-lg font-semibold mb-2"
                        )

                        current_texts = setup_config.get("mult_project_list_texts", [])

                        # Display selection count for texts
                        texts_count = ui.label(
                            f"Keys: {len(current_texts)}"
                        ).classes("text-sm font-medium")

                        def update_texts_count():
                            current_selection = setup_config.get("mult_project_list_texts", [])
                            texts_count.text = f"Keys: {len(current_selection)}"

                        def on_texts_change(e):
                            # Split by comma, strip whitespace, and filter out empty strings
                            keys = [key.strip() for key in (e.value or "").split(",") if key.strip()]
                            setup_config["mult_project_list_texts"] = keys
                            mark_changed()
                            update_texts_count()

                        texts_input = (
                            ui.input(
                                label="Text keys (comma-separated)",
                                value=", ".join(current_texts),
                                placeholder="text1, text2, text3",
                                on_change=on_texts_change,
                            )
                            .props("dense")
                            .classes("w-[48rem]")
                        )

                        ui.label(
                            "Enter comma-separated keys for texts. Each key should be a single word."
                        ).classes("text-sm mt-2")

            def render_extract():
                if not content_container:
                    return

                content_container.clear()
                with content_container:
                    ui.label("Extract").classes("text-2xl font-semibold")
                    ui.separator()
                    ui.label("Configure data sources and extraction parameters.")

                    # Extract configuration
                    extract_config = form_state["data"].setdefault("extract", {})

                    # General Extract Settings Card
                    with ui.card().classes("mt-4"):
                        ui.label("General Extract Settings").classes(
                            "text-lg font-semibold mb-2"
                        )

                        def on_extract_active_change(e):
                            extract_config["active"] = e.value
                            mark_changed()
                            # Re-render the extract section to update UI state
                            render_extract()

                        extract_active = extract_config.get("active", True)

                        ui.switch(
                            "Extract active",
                            value=extract_active,
                            on_change=on_extract_active_change,
                        )

                        def on_load_to_nemo_change(e):
                            extract_config["load_to_nemo"] = e.value
                            mark_changed()

                        load_to_nemo_switch = ui.switch(
                            "Load to NEMO",
                            value=extract_config.get("load_to_nemo", True),
                            on_change=on_load_to_nemo_change,
                        )
                        if not extract_active:
                            load_to_nemo_switch.props("disable")

                        def on_delete_temp_files_change(e):
                            extract_config["delete_temp_files"] = e.value
                            mark_changed()

                        delete_temp_files_switch = ui.switch(
                            "Delete temp files",
                            value=extract_config.get("delete_temp_files", True),
                            on_change=on_delete_temp_files_change,
                        )
                        if not extract_active:
                            delete_temp_files_switch.props("disable")

                        def on_nemo_project_prefix_change(e):
                            extract_config["nemo_project_prefix"] = e.value
                            mark_changed()

                        nemo_project_prefix_input = (
                            ui.input(
                                label="NEMO project prefix",
                                value=extract_config.get(
                                    "nemo_project_prefix", "migman_extract_"
                                ),
                                placeholder="migman_extract_",
                                on_change=on_nemo_project_prefix_change,
                            )
                            .props("dense")
                            .classes("w-[36rem] mt-3")
                        )
                        if not extract_active:
                            nemo_project_prefix_input.props("disable")

                    # Adapter Selection
                    with ui.card().classes("mt-4"):
                        ui.label("Data Source Adapter").classes(
                            "text-lg font-semibold mb-2"
                        )
                        ui.label(
                            "Select which data source adapter to use for extraction."
                        ).classes("text-sm mb-4")

                        def on_adapter_change(e):
                            extract_config["adapter"] = e.value
                            mark_changed()
                            # Re-render the extract section to update adapter configuration
                            render_extract()

                        current_adapter = extract_config.get("adapter", "inforcom")

                        adapter_select = (
                            ui.select(
                                label="Adapter",
                                options=[
                                    "genericodbc",
                                    "inforcom",
                                    "sapecc",
                                ],
                                value=current_adapter,
                                on_change=on_adapter_change,
                            )
                            .props("dense")
                            .classes("w-48")
                        )
                        if not extract_active:
                            adapter_select.props("disable")

                    # Adapter Configuration
                    with ui.card().classes("mt-4") as adapters_card:
                        ui.label(f"{current_adapter.upper()} Configuration").classes(
                            "text-lg font-semibold mb-2"
                        )

                        if not extract_active:
                            # Show disabled message when extract is not active
                            ui.label(
                                "Extract must be active to configure the data source adapter."
                            ).classes("text-sm text-gray-500 italic mb-4")
                            adapters_card.props("disable")
                        else:
                            if current_adapter == "inforcom":
                                render_inforcom_config(extract_config)
                            elif current_adapter == "sapecc":
                                render_sapecc_config(extract_config)
                            else:  # generic_odbc
                                render_generic_odbc_config(extract_config)

            def render_inforcom_config(extract_config):
                """Render INFORCOM adapter configuration."""
                inforcom_config = extract_config.setdefault("inforcom", {})

                ui.label("INFORCOM Configuration").classes("text-lg font-semibold mb-3")
                ui.label(
                    "ODBC-based extraction from INFORCOM (INFOR.* tables)"
                ).classes("text-sm mb-4")

                with ui.column().classes("gap-4"):
                    # ODBC Connection String
                    def on_odbc_connstr_change(e):
                        inforcom_config["odbc_connstr"] = e.value
                        mark_changed()

                    ui.input(
                        label="ODBC Connection String",
                        value=inforcom_config.get(
                            "odbc_connstr",
                            "Driver={SQL Server};Server=your_server;Database=your_database;UID=your_username;PWD=your_password;",
                        ),
                        placeholder="Driver={SQL Server};Server=your_server;Database=your_database;UID=your_username;PWD=your_password;",
                        on_change=on_odbc_connstr_change,
                    ).props("dense").classes("w-full")

                    # Chunk Size
                    def on_chunk_size_change(e):
                        try:
                            inforcom_config["chunk_size"] = (
                                int(e.value) if e.value else 10000
                            )
                            mark_changed()
                        except ValueError:
                            pass

                    ui.number(
                        label="Chunk Size",
                        value=inforcom_config.get("chunk_size", 10000),
                        min=1,
                        on_change=on_chunk_size_change,
                    ).props("dense").classes("w-48")

                    # Timeout
                    def on_timeout_change(e):
                        try:
                            inforcom_config["timeout"] = (
                                int(e.value) if e.value else 300
                            )
                            mark_changed()
                        except ValueError:
                            pass

                    ui.number(
                        label="Timeout (seconds)",
                        value=inforcom_config.get("timeout", 300),
                        min=1,
                        on_change=on_timeout_change,
                    ).props("dense").classes("w-48")

                    # Table Prefix
                    def on_table_prefix_change(e):
                        inforcom_config["table_prefix"] = e.value
                        mark_changed()

                    ui.input(
                        label="Table Prefix",
                        value=inforcom_config.get("table_prefix", "INFOR."),
                        placeholder="INFOR.",
                        on_change=on_table_prefix_change,
                    ).props("dense").classes("w-48")

                    # Table Selector
                    def on_table_selector_change(e):
                        inforcom_config["table_selector"] = e.value
                        mark_changed()
                        # Show/hide tables list based on selection
                        if e.value == "all":
                            tables_container.set_visibility(True)
                        else:
                            tables_container.set_visibility(False)

                    table_selector = (
                        ui.select(
                            label="Table Selector",
                            options=["all", "join_parser"],
                            value=inforcom_config.get("table_selector", "join_parser"),
                            on_change=on_table_selector_change,
                        )
                        .props("dense")
                        .classes("w-48")
                    )

                    # Tables List (conditionally visible)
                    current_tables = inforcom_config.get("tables", [])

                    with ui.column().classes("w-full") as tables_container:
                        ui.label("Tables").classes("text-base font-medium mt-2")

                        def on_tables_change(e):
                            inforcom_config["tables"] = e.value if e.value else []
                            mark_changed()

                        default_inforcom_tables = (
                            global_config.get("extract", {})
                            .get("inforcom", {})
                            .get("tables", [])
                        )

                        # Combine default tables with any custom tables that might be in current config
                        all_available_tables = list(
                            set(default_inforcom_tables + current_tables)
                        )
                        all_available_tables.sort()

                        tables_select = (
                            ui.select(
                                options=all_available_tables,
                                value=current_tables,
                                multiple=True,
                                label="Select tables to extract",
                                on_change=on_tables_change,
                            )
                            .props("use-chips clearable use-input input-debounce=0")
                            .classes("w-full")
                        )

                        # Add custom table functionality
                        with ui.row().classes("gap-2 items-end mt-3"):
                            new_table_input = (
                                ui.input(
                                    label="Add custom table",
                                    placeholder="Enter table name (e.g. INFOR.CUSTOM_TABLE)",
                                )
                                .props("dense")
                                .classes("flex-1")
                            )

                            def add_custom_table():
                                table_name = new_table_input.value.strip()
                                if (
                                    table_name
                                    and table_name not in all_available_tables
                                ):
                                    # Add to available options
                                    all_available_tables.append(table_name)
                                    all_available_tables.sort()
                                    tables_select.options = all_available_tables

                                    # Add to current selection
                                    current_selection = inforcom_config.get(
                                        "tables", []
                                    )
                                    if table_name not in current_selection:
                                        current_selection.append(table_name)
                                        inforcom_config["tables"] = current_selection
                                        tables_select.value = current_selection
                                        mark_changed()

                                    # Clear input
                                    new_table_input.value = ""
                                    ui.notify(
                                        f"Added table: {table_name}", type="positive"
                                    )
                                elif table_name in all_available_tables:
                                    ui.notify(
                                        f"Table '{table_name}' already exists",
                                        type="warning",
                                    )
                                else:
                                    ui.notify(
                                        "Please enter a table name", type="warning"
                                    )

                            ui.button(
                                "Add Table", icon="add", on_click=add_custom_table
                            ).props("size=sm color=primary")

                        ui.label(
                            "You can add custom tables not in the default list above."
                        ).classes("text-sm text-gray-600 mt-2")

                    # Set initial visibility based on current selection
                    if inforcom_config.get("table_selector", "join_parser") != "all":
                        tables_container.set_visibility(False)

            def render_sapecc_config(extract_config):
                """Render SAP ECC adapter configuration."""
                sapecc_config = extract_config.setdefault("sapecc", {})

                ui.label("SAP ECC Configuration").classes("text-lg font-semibold mb-3")
                ui.label("HANA DB-based extraction from SAP ECC").classes(
                    "text-sm mb-4"
                )

                with ui.column().classes("gap-4"):
                    # Connection parameters row
                    with ui.row().classes("gap-4 w-full"):
                        # Address
                        def on_address_change(e):
                            sapecc_config["address"] = e.value
                            mark_changed()

                        ui.input(
                            label="Server Address",
                            value=sapecc_config.get("address", "your_sap_hana_server"),
                            placeholder="your_sap_hana_server",
                            on_change=on_address_change,
                        ).props("dense").classes("flex-grow")

                        # Port
                        def on_port_change(e):
                            try:
                                port = int(e.value) if e.value else 30015
                                if 1 <= port <= 65535:
                                    sapecc_config["port"] = port
                                    mark_changed()
                            except ValueError:
                                pass

                        ui.number(
                            label="Port",
                            value=sapecc_config.get("port", 30015),
                            min=1,
                            max=65535,
                            on_change=on_port_change,
                        ).props("dense").classes("w-32")

                    # Credentials row
                    with ui.row().classes("gap-4 w-full"):
                        # Username
                        def on_user_change(e):
                            sapecc_config["user"] = e.value
                            mark_changed()

                        ui.input(
                            label="Username",
                            value=sapecc_config.get("user", "your_username"),
                            placeholder="your_username",
                            on_change=on_user_change,
                        ).props("dense").classes("flex-1")

                        # Password
                        def on_password_change(e):
                            sapecc_config["password"] = e.value
                            mark_changed()

                        ui.input(
                            label="Password",
                            value=sapecc_config.get("password", "your_password"),
                            placeholder="your_password",
                            password=True,
                            password_toggle_button=True,
                            on_change=on_password_change,
                        ).props("dense").classes("flex-1")

                    # Settings row
                    with ui.row().classes("gap-4 items-center"):
                        # Autocommit
                        def on_autocommit_change(e):
                            sapecc_config["autocommit"] = e.value
                            mark_changed()

                        ui.switch(
                            "Autocommit",
                            value=sapecc_config.get("autocommit", True),
                            on_change=on_autocommit_change,
                        )

                        # Chunk Size
                        def on_chunk_size_change(e):
                            try:
                                sapecc_config["chunk_size"] = (
                                    int(e.value) if e.value else 10000
                                )
                                mark_changed()
                            except ValueError:
                                pass

                        ui.number(
                            label="Chunk Size",
                            value=sapecc_config.get("chunk_size", 10000),
                            min=1,
                            on_change=on_chunk_size_change,
                        ).props("dense").classes("w-48")

                    # Table Selector
                    def on_table_selector_change(e):
                        sapecc_config["table_selector"] = e.value
                        mark_changed()
                        # Show/hide tables list based on selection
                        if e.value == "all":
                            tables_container.set_visibility(True)
                        else:
                            tables_container.set_visibility(False)

                    table_selector = (
                        ui.select(
                            label="Table Selector",
                            options=["all", "join_parser"],
                            value=sapecc_config.get("table_selector", "join_parser"),
                            on_change=on_table_selector_change,
                        )
                        .props("dense")
                        .classes("w-48")
                    )

                    # Tables List (conditionally visible)
                    current_tables = sapecc_config.get("tables", [])

                    with ui.column().classes("w-full") as tables_container:
                        ui.label("Tables").classes("text-base font-medium mt-2")

                        def on_tables_change(e):
                            sapecc_config["tables"] = e.value if e.value else []
                            mark_changed()

                        default_sapecc_tables = (
                            global_config.get("extract", {})
                            .get("sapecc", {})
                            .get("tables", [])
                        )

                        # Combine default tables with any custom tables that might be in current config
                        all_available_tables = list(
                            set(default_sapecc_tables + current_tables)
                        )
                        all_available_tables.sort()

                        tables_select = (
                            ui.select(
                                options=all_available_tables,
                                value=current_tables,
                                multiple=True,
                                label="Select tables to extract",
                                on_change=on_tables_change,
                            )
                            .props("use-chips clearable use-input input-debounce=0")
                            .classes("w-full")
                        )

                        # Add custom table functionality
                        with ui.row().classes("gap-2 items-end mt-3"):
                            new_table_input = (
                                ui.input(
                                    label="Add custom table",
                                    placeholder="Enter table name (e.g. SAPSR3.CUSTOM_TABLE)",
                                )
                                .props("dense")
                                .classes("flex-1")
                            )

                            def add_custom_table():
                                table_name = new_table_input.value.strip()
                                if (
                                    table_name
                                    and table_name not in all_available_tables
                                ):
                                    # Add to available options
                                    all_available_tables.append(table_name)
                                    all_available_tables.sort()
                                    tables_select.options = all_available_tables

                                    # Add to current selection
                                    current_selection = sapecc_config.get("tables", [])
                                    if table_name not in current_selection:
                                        current_selection.append(table_name)
                                        sapecc_config["tables"] = current_selection
                                        tables_select.value = current_selection
                                        mark_changed()

                                    # Clear input
                                    new_table_input.value = ""
                                    ui.notify(
                                        f"Added table: {table_name}", type="positive"
                                    )
                                elif table_name in all_available_tables:
                                    ui.notify(
                                        f"Table '{table_name}' already exists",
                                        type="warning",
                                    )
                                else:
                                    ui.notify(
                                        "Please enter a table name", type="warning"
                                    )

                            ui.button(
                                "Add Table", icon="add", on_click=add_custom_table
                            ).props("size=sm color=primary")

                        ui.label(
                            "You can add custom tables not in the default list above."
                        ).classes("text-sm text-gray-600 mt-2")

                    # Set initial visibility based on current selection
                    if sapecc_config.get("table_selector", "join_parser") != "all":
                        tables_container.set_visibility(False)

            def render_generic_odbc_config(extract_config):
                """Render Generic ODBC adapter configuration."""
                generic_odbc_config = extract_config.setdefault("genericodbc", {})

                ui.label("Generic ODBC Configuration").classes(
                    "text-lg font-semibold mb-3"
                )
                ui.label(
                    "Generic ODBC-based extraction from any ODBC-compatible database"
                ).classes("text-sm mb-4")

                with ui.column().classes("gap-4"):
                    # ODBC Connection String
                    def on_odbc_connstr_change(e):
                        generic_odbc_config["odbc_connstr"] = e.value
                        mark_changed()

                    ui.input(
                        label="ODBC Connection String",
                        value=generic_odbc_config.get(
                            "odbc_connstr",
                            "Driver={SQL Server};Server=your_server;Database=your_database;UID=your_username;PWD=your_password;",
                        ),
                        placeholder="Driver={SQL Server};Server=your_server;Database=your_database;UID=your_username;PWD=your_password;",
                        on_change=on_odbc_connstr_change,
                    ).props("dense").classes("w-full")

                    # Chunk Size
                    def on_chunk_size_change(e):
                        try:
                            generic_odbc_config["chunk_size"] = (
                                int(e.value) if e.value else 10000
                            )
                            mark_changed()
                        except ValueError:
                            pass

                    ui.number(
                        label="Chunk Size",
                        value=generic_odbc_config.get("chunk_size", 10000),
                        min=1,
                        on_change=on_chunk_size_change,
                    ).props("dense").classes("w-48")

                    # Timeout
                    def on_timeout_change(e):
                        try:
                            generic_odbc_config["timeout"] = (
                                int(e.value) if e.value else 300
                            )
                            mark_changed()
                        except ValueError:
                            pass

                    ui.number(
                        label="Timeout (seconds)",
                        value=generic_odbc_config.get("timeout", 300),
                        min=1,
                        on_change=on_timeout_change,
                    ).props("dense").classes("w-48")

                    # Table Prefix (optional for generic ODBC)
                    def on_table_prefix_change(e):
                        generic_odbc_config["table_prefix"] = e.value
                        mark_changed()

                    ui.input(
                        label="Table Prefix (optional)",
                        value=generic_odbc_config.get("table_prefix", ""),
                        placeholder="e.g. schema_name.",
                        on_change=on_table_prefix_change,
                    ).props("dense").classes("w-48")

                    # Table Selector
                    def on_table_selector_change(e):
                        generic_odbc_config["table_selector"] = e.value
                        mark_changed()
                        # Show/hide tables list based on selection
                        if e.value == "all":
                            tables_container.set_visibility(True)
                        else:
                            tables_container.set_visibility(False)

                    table_selector = (
                        ui.select(
                            label="Table Selector",
                            options=["all", "join_parser"],
                            value=generic_odbc_config.get(
                                "table_selector", "join_parser"
                            ),
                            on_change=on_table_selector_change,
                        )
                        .props("dense")
                        .classes("w-48")
                    )

                    # Tables List (conditionally visible)
                    current_tables = generic_odbc_config.get("tables", [])

                    with ui.column().classes("w-full") as tables_container:
                        ui.label("Tables").classes("text-base font-medium mt-2")

                        def on_tables_change(e):
                            generic_odbc_config["tables"] = e.value if e.value else []
                            mark_changed()

                        default_generic_odbc_tables = (
                            global_config.get("extract", {})
                            .get("genericodbc", {})
                            .get("tables", [])
                        )

                        # Combine default tables with any custom tables that might be in current config
                        all_available_tables = list(
                            set(default_generic_odbc_tables + current_tables)
                        )
                        all_available_tables.sort()

                        tables_select = (
                            ui.select(
                                options=all_available_tables,
                                value=current_tables,
                                multiple=True,
                                label="Select tables to extract",
                                on_change=on_tables_change,
                            )
                            .props("use-chips clearable use-input input-debounce=0")
                            .classes("w-full")
                        )

                        # Add custom table functionality
                        with ui.row().classes("gap-2 items-end mt-3"):
                            new_table_input = (
                                ui.input(
                                    label="Add custom table",
                                    placeholder="Enter table name (e.g. schema.table_name)",
                                )
                                .props("dense")
                                .classes("flex-1")
                            )

                            def add_custom_table():
                                table_name = new_table_input.value.strip()
                                if (
                                    table_name
                                    and table_name not in all_available_tables
                                ):
                                    # Add to available options
                                    all_available_tables.append(table_name)
                                    all_available_tables.sort()
                                    tables_select.options = all_available_tables

                                    # Add to current selection
                                    current_selection = generic_odbc_config.get(
                                        "tables", []
                                    )
                                    if table_name not in current_selection:
                                        current_selection.append(table_name)
                                        generic_odbc_config["tables"] = (
                                            current_selection
                                        )
                                        tables_select.value = current_selection
                                        mark_changed()

                                    # Clear input
                                    new_table_input.value = ""
                                    ui.notify(
                                        f"Added table: {table_name}", type="positive"
                                    )
                                elif table_name in all_available_tables:
                                    ui.notify(
                                        f"Table '{table_name}' already exists",
                                        type="warning",
                                    )
                                else:
                                    ui.notify(
                                        "Please enter a table name", type="warning"
                                    )

                            ui.button(
                                "Add Table", icon="add", on_click=add_custom_table
                            ).props("size=sm color=primary")

                        ui.label(
                            "You can add custom tables not in the default list above."
                        ).classes("text-sm text-gray-600 mt-2")

                    # Set initial visibility based on current selection
                    if (
                        generic_odbc_config.get("table_selector", "join_parser")
                        != "all"
                    ):
                        tables_container.set_visibility(False)

            def render_transform():
                if not content_container:
                    return

                content_container.clear()
                with content_container:
                    ui.label("Transform").classes("text-2xl font-semibold")
                    ui.separator()
                    ui.label("Define transformations, mappings and validations.")

                    # Transform configuration
                    transform_config = form_state["data"].setdefault("transform", {})

                    # General Transform Settings Card
                    with ui.card().classes("mt-4"):
                        ui.label("General Transform Settings").classes(
                            "text-lg font-semibold mb-3"
                        )

                        with ui.column().classes("gap-3"):
                            # Transform active toggle
                            def on_transform_active_change(e):
                                transform_config["active"] = e.value
                                mark_changed()
                                # Re-render the transform section to update disabled states
                                render_transform()

                            transform_active = transform_config.get(
                                "active", True
                            )

                            ui.switch(
                                "Transform active",
                                value=transform_active,
                                on_change=on_transform_active_change,
                            )

                            # Load to Nemo toggle
                            def on_load_to_nemo_change(e):
                                transform_config["load_to_nemo"] = e.value
                                mark_changed()
                                # Re-render the transform section to update disabled states
                                render_transform()

                            load_to_nemo_switch = ui.switch(
                                "Load to Nemo",
                                value=transform_config.get("load_to_nemo", True),
                                on_change=on_load_to_nemo_change,
                            )
                            if not transform_active:
                                load_to_nemo_switch.props("disable")

                            # Delete temp files toggle
                            def on_delete_temp_files_change(e):
                                transform_config["delete_temp_files"] = e.value
                                mark_changed()

                            load_to_nemo = transform_config.get("load_to_nemo", True)
                            delete_temp_files_switch = ui.switch(
                                "Delete temporary files",
                                value=transform_config.get("delete_temp_files", True),
                                on_change=on_delete_temp_files_change,
                            )
                            if not transform_active or not load_to_nemo:
                                delete_temp_files_switch.props("disable")

                            # Dump files toggle
                            def on_dump_files_change(e):
                                transform_config["dump_files"] = e.value
                                mark_changed()

                            dump_files_switch = ui.switch(
                                "Dump files",
                                value=transform_config.get("dump_files", True),
                                on_change=on_dump_files_change,
                            )
                            if not transform_active:
                                dump_files_switch.props("disable")

                            # Nemo project prefix
                            def on_nemo_project_prefix_change(e):
                                transform_config["nemo_project_prefix"] = e.value
                                mark_changed()

                            nemo_prefix_input = (
                                ui.input(
                                    label="Nemo Project Prefix",
                                    value=transform_config.get(
                                        "nemo_project_prefix", "migman_transform_"
                                    ),
                                    on_change=on_nemo_project_prefix_change,
                                )
                                .props("dense")
                                .classes("w-80")
                            )
                            if not transform_active:
                                nemo_prefix_input.props("disable")

                    # Transform Components with Tabs
                    with ui.card().classes("mt-4"):
                        ui.label("Transform Components").classes(
                            "text-lg font-semibold mb-3"
                        )

                        transform_components_container = ui.column().classes("w-full")

                        if transform_active:
                            with transform_components_container:
                                with ui.tabs().classes("w-full") as tabs:
                                    join_tab = ui.tab("Join")
                                    nonempty_tab = ui.tab("Non-Empty")
                                    duplicate_tab = ui.tab("Duplicate")

                                with ui.tab_panels(tabs, value=join_tab).classes(
                                    "w-full"
                                ):
                                    with ui.tab_panel(join_tab):
                                        render_transform_join_config(transform_config)

                                    with ui.tab_panel(nonempty_tab):
                                        render_transform_nonempty_config(
                                            transform_config
                                        )

                                    with ui.tab_panel(duplicate_tab):
                                        render_transform_duplicate_config(
                                            transform_config
                                        )
                        else:
                            with transform_components_container:
                                ui.label(
                                    "Transform components are disabled because Transform is not active."
                                ).classes("text-sm text-gray-500 italic p-4")

            def render_transform_join_config(transform_config):
                """Render join transformation configuration."""
                join_config = transform_config.setdefault("join", {})

                ui.label("Join Configuration").classes("text-lg font-semibold mb-3")
                ui.label("Configure table joins and relationships").classes(
                    "text-sm mb-4"
                )

                with ui.column().classes("gap-4"):
                    # Join active toggle
                    def on_join_active_change(e):
                        join_config["active"] = e.value
                        mark_changed()
                        # Re-render the transform section to update disabled states
                        render_transform()

                    join_active = join_config.get("active", True)

                    ui.switch(
                        "Join active",
                        value=join_active,
                        on_change=on_join_active_change,
                    )

                    # Joins configuration
                    joins_config_label = ui.label("Join Configurations").classes(
                        "text-md font-medium mt-4"
                    )
                    if not join_active:
                        joins_config_label.classes("text-gray-500")

                    joins_config = join_config.setdefault("joins", {})

                    # Display existing joins
                    for join_name, join_settings in joins_config.items():
                        with ui.card().classes("mt-2 p-3"):
                            with ui.row().classes(
                                "items-center justify-between w-full"
                            ):
                                join_label = ui.label(f"Join: {join_name}").classes(
                                    "font-medium"
                                )
                                if not join_active:
                                    join_label.classes("text-gray-500")

                                delete_button = ui.button(
                                    icon="delete",
                                    on_click=lambda name=join_name: remove_join(name),
                                ).props("flat round color=negative size=sm")
                                if not join_active:
                                    delete_button.props("disable")

                            def on_join_item_active_change(e, name=join_name):
                                joins_config[name]["active"] = e.value
                                mark_changed()

                            def on_join_item_file_change(e, name=join_name):
                                joins_config[name]["file"] = e.value
                                mark_changed()

                            join_item_switch = ui.switch(
                                "Active",
                                value=join_settings.get("active", True),
                                on_change=lambda e, name=join_name: on_join_item_active_change(
                                    e, name
                                ),
                            )
                            if not join_active:
                                join_item_switch.props("disable")

                            join_file_input = (
                                ui.input(
                                    label="File",
                                    value=join_settings.get("file", ""),
                                    placeholder="Path to join configuration file",
                                    on_change=lambda e, name=join_name: on_join_item_file_change(
                                        e, name
                                    ),
                                )
                                .props("dense")
                                .classes("w-full")
                            )
                            if not join_active:
                                join_file_input.props("disable")

                    def remove_join(join_name):
                        if join_name in joins_config:
                            del joins_config[join_name]
                            mark_changed()
                            render_transform()

                    # Add new join
                    if join_active:
                        with ui.card().classes("mt-2 p-3 border-dashed"):
                            ui.label("Add New Join").classes("font-medium mb-2")

                            new_join_name = {"value": ""}
                            new_join_file = {"value": ""}

                            def on_new_join_name_change(e):
                                new_join_name["value"] = e.value

                            def on_new_join_file_change(e):
                                new_join_file["value"] = e.value

                            def add_join():
                                if new_join_name["value"] and new_join_file["value"]:
                                    joins_config[new_join_name["value"]] = {
                                        "active": True,
                                        "file": new_join_file["value"],
                                    }
                                    mark_changed()
                                    render_transform()

                            with ui.row().classes("gap-2 items-end w-full"):
                                ui.input(
                                    label="Join Name",
                                    placeholder="Enter join name",
                                    on_change=on_new_join_name_change,
                                ).props("dense").classes("flex-1")

                                ui.input(
                                    label="File Path",
                                    placeholder="Path to join configuration file",
                                    on_change=on_new_join_file_change,
                                ).props("dense").classes("flex-1")

                                ui.button(
                                    "Add Join", icon="add", on_click=add_join
                                ).props("color=primary")
                    else:
                        # Show disabled state message when joins is not active
                        with ui.card().classes("mt-2 p-3 bg-gray-100"):
                            ui.label(
                                "Join configurations are disabled because Join is not active."
                            ).classes("text-sm text-gray-500 italic")

            def render_transform_nonempty_config(transform_config):
                """Render non-empty transformation configuration."""
                nonempty_config = transform_config.setdefault("nonempty", {})

                ui.label("Non-Empty Configuration").classes(
                    "text-lg font-semibold mb-3"
                )
                ui.label("Filter out empty records during transformation").classes(
                    "text-sm mb-4"
                )

                with ui.column().classes("gap-4"):
                    # Non-empty active toggle
                    def on_nonempty_active_change(e):
                        nonempty_config["active"] = e.value
                        mark_changed()

                    ui.switch(
                        "Non-empty filter active",
                        value=nonempty_config.get("active", True),
                        on_change=on_nonempty_active_change,
                    )

                    ui.label(
                        "This transformation will remove records with empty or null values in key fields."
                    ).classes("text-sm text-gray-600")

            def render_transform_duplicate_config(transform_config):
                """Render duplicate transformation configuration."""
                duplicate_config = transform_config.setdefault("duplicate", {})

                ui.label("Duplicate Configuration").classes(
                    "text-lg font-semibold mb-3"
                )
                ui.label("Configure duplicate detection and handling").classes(
                    "text-sm mb-4"
                )

                with ui.column().classes("gap-4"):
                    # Duplicate active toggle
                    def on_duplicate_active_change(e):
                        duplicate_config["active"] = e.value
                        mark_changed()
                        # Re-render the transform section to update disabled states
                        render_transform()

                    duplicate_active = duplicate_config.get("active", True)

                    ui.switch(
                        "Duplicate detection active",
                        value=duplicate_active,
                        on_change=on_duplicate_active_change,
                    )

                    # Duplicates configuration
                    duplicates_config_label = ui.label(
                        "Duplicate Configurations"
                    ).classes("text-md font-medium mt-4")
                    if not duplicate_active:
                        duplicates_config_label.classes("text-gray-500")

                    duplicates_config = duplicate_config.setdefault("duplicates", {})

                    # Display existing duplicate configurations
                    for object_name, duplicate_settings in duplicates_config.items():
                        with ui.card().classes("mt-2 p-3"):
                            with ui.row().classes(
                                "items-center justify-between w-full"
                            ):
                                object_label = ui.label(
                                    f"Object: {object_name}"
                                ).classes("font-medium")
                                if not duplicate_active:
                                    object_label.classes("text-gray-500")

                                delete_button = ui.button(
                                    icon="delete",
                                    on_click=lambda name=object_name: remove_duplicate_config(
                                        name
                                    ),
                                ).props("flat round color=negative size=sm")
                                if not duplicate_active:
                                    delete_button.props("disable")

                            def on_duplicate_obj_active_change(e, name=object_name):
                                duplicates_config[name]["active"] = e.value
                                mark_changed()

                            def on_threshold_change(e, name=object_name):
                                try:
                                    threshold = int(e.value)
                                    if 0 <= threshold <= 100:
                                        duplicates_config[name]["threshold"] = threshold
                                        mark_changed()
                                except (ValueError, TypeError):
                                    pass

                            def on_primary_key_change(e, name=object_name):
                                duplicates_config[name]["primary_key"] = e.value
                                mark_changed()

                            def on_fields_change(e, name=object_name):
                                # Split by comma and clean up
                                fields = [
                                    field.strip()
                                    for field in e.value.split(",")
                                    if field.strip()
                                ]
                                duplicates_config[name]["fields"] = fields
                                mark_changed()

                            duplicate_obj_switch = ui.switch(
                                "Active",
                                value=duplicate_settings.get("active", True),
                                on_change=lambda e, name=object_name: on_duplicate_obj_active_change(
                                    e, name
                                ),
                            )
                            if not duplicate_active:
                                duplicate_obj_switch.props("disable")

                            with ui.row().classes("gap-2 w-full"):
                                threshold_input = (
                                    ui.number(
                                        label="Similarity Threshold (%)",
                                        value=duplicate_settings.get("threshold", 90),
                                        min=0,
                                        max=100,
                                        on_change=lambda e, name=object_name: on_threshold_change(
                                            e, name
                                        ),
                                    )
                                    .props("dense")
                                    .classes("w-48")
                                )
                                if not duplicate_active:
                                    threshold_input.props("disable")

                                primary_key_input = (
                                    ui.input(
                                        label="Primary Key",
                                        value=duplicate_settings.get("primary_key", ""),
                                        placeholder="Enter primary key field",
                                        on_change=lambda e, name=object_name: on_primary_key_change(
                                            e, name
                                        ),
                                    )
                                    .props("dense")
                                    .classes("flex-1")
                                )
                                if not duplicate_active:
                                    primary_key_input.props("disable")

                            fields_input = (
                                ui.input(
                                    label="Fields (comma-separated)",
                                    value=", ".join(
                                        duplicate_settings.get("fields", [])
                                    ),
                                    placeholder="field1, field2, field3",
                                    on_change=lambda e, name=object_name: on_fields_change(
                                        e, name
                                    ),
                                )
                                .props("dense")
                                .classes("w-full")
                            )
                            if not duplicate_active:
                                fields_input.props("disable")

                    def remove_duplicate_config(object_name):
                        if object_name in duplicates_config:
                            del duplicates_config[object_name]
                            mark_changed()
                            render_transform()

                    # Add new duplicate configuration
                    if duplicate_active:
                        with ui.card().classes("mt-2 p-3 border-dashed"):
                            ui.label("Add New Duplicate Configuration").classes(
                                "font-medium mb-2"
                            )

                            new_object_name = {"value": ""}
                            new_primary_key = {"value": ""}
                            new_threshold = {"value": 90}
                            new_fields = {"value": ""}

                            def on_new_object_name_change(e):
                                new_object_name["value"] = e.value

                            def on_new_primary_key_change(e):
                                new_primary_key["value"] = e.value

                            def on_new_threshold_change(e):
                                try:
                                    threshold = int(e.value)
                                    if 0 <= threshold <= 100:
                                        new_threshold["value"] = threshold
                                except (ValueError, TypeError):
                                    pass

                            def on_new_fields_change(e):
                                new_fields["value"] = e.value

                            def add_duplicate_config():
                                if (
                                    new_object_name["value"]
                                    and new_primary_key["value"]
                                ):
                                    fields = [
                                        field.strip()
                                        for field in new_fields["value"].split(",")
                                        if field.strip()
                                    ]
                                    duplicates_config[new_object_name["value"]] = {
                                        "active": True,
                                        "threshold": new_threshold["value"],
                                        "primary_key": new_primary_key["value"],
                                        "fields": fields,
                                    }
                                    mark_changed()
                                    render_transform()

                            with ui.column().classes("gap-2 w-full"):
                                with ui.row().classes("gap-2 w-full"):
                                    ui.input(
                                        label="Object Name",
                                        placeholder="Enter object name",
                                        on_change=on_new_object_name_change,
                                    ).props("dense").classes("flex-1")

                                    ui.number(
                                        label="Threshold (%)",
                                        value=90,
                                        min=0,
                                        max=100,
                                        on_change=on_new_threshold_change,
                                    ).props("dense").classes("w-32")

                                with ui.row().classes("gap-2 w-full"):
                                    ui.input(
                                        label="Primary Key",
                                        placeholder="Enter primary key field",
                                        on_change=on_new_primary_key_change,
                                    ).props("dense").classes("flex-1")

                                    ui.input(
                                        label="Fields (comma-separated)",
                                        placeholder="field1, field2, field3",
                                        on_change=on_new_fields_change,
                                    ).props("dense").classes("flex-1")

                                ui.button(
                                    "Add Configuration",
                                    icon="add",
                                    on_click=add_duplicate_config,
                                ).props("color=primary")
                    else:
                        # Show disabled state message when duplicate detection is not active
                        with ui.card().classes("mt-2 p-3 bg-gray-100"):
                            ui.label(
                                "Duplicate configurations are disabled because Duplicate detection is not active."
                            ).classes("text-sm text-gray-500 italic")

            def render_load():
                if not content_container:
                    return

                content_container.clear()
                with content_container:
                    ui.label("Load").classes("text-2xl font-semibold")
                    ui.separator()
                    ui.label("Load data into target system.")

                    # Load active toggle
                    load_config = form_state["data"].setdefault("load", {})

                    with ui.card().classes("mt-4"):
                        ui.label("Load Settings").classes("text-lg font-semibold mb-2")

                        def on_load_active_change(e):
                            load_config["active"] = e.value
                            mark_changed()
                            # Re-render the load section to update disabled states
                            render_load()

                        load_active = load_config.get("active", True)

                        ui.switch(
                            "Load active",
                            value=load_active,
                            on_change=on_load_active_change,
                        )

                        def on_delete_temp_files_change(e):
                            load_config["delete_temp_files"] = e.value
                            mark_changed()

                        delete_temp_files_switch = ui.switch(
                            "Delete temp files",
                            value=load_config.get("delete_temp_files", True),
                            on_change=on_delete_temp_files_change,
                        )
                        if not load_active:
                            delete_temp_files_switch.props("disable")

                        def on_nemo_project_prefix_change(e):
                            load_config["nemo_project_prefix"] = e.value
                            mark_changed()

                        nemo_project_prefix_input = (
                            ui.input(
                                label="NEMO project prefix",
                                value=load_config.get(
                                    "nemo_project_prefix", "migman_load_"
                                ),
                                placeholder="migman_load_",
                                on_change=on_nemo_project_prefix_change,
                            )
                            .props("dense")
                            .classes("w-[36rem] mt-3")
                        )
                        if not load_active:
                            nemo_project_prefix_input.props("disable")

            # ---------- LEFT DRAWER ----------
            with ui.left_drawer(value=True, fixed=True).classes("w-64 p-4"):
                ui.label("MigMan UI").classes("text-lg font-semibold mb-4")

                def make_nav_button(name: str, cb):
                    b = (
                        ui.button(name, on_click=cb)
                        .props("flat")
                        .classes("w-full justify-start mb-2")
                    )
                    nav_buttons[name] = b
                    return b

                make_nav_button(
                    "Global", lambda: (set_active("Global"), render_global())
                )
                make_nav_button("Setup", lambda: (set_active("Setup"), render_setup()))
                make_nav_button(
                    "Extract", lambda: (set_active("Extract"), render_extract())
                )
                make_nav_button(
                    "Transform", lambda: (set_active("Transform"), render_transform())
                )
                make_nav_button("Load", lambda: (set_active("Load"), render_load()))

            # ---------- MAIN CONTENT ----------
            with ui.element("div"):
                with ui.column() as content:
                    content_container = content
                    set_active("Global")
                    render_global()

        ui.run(reload=False, show=open_browser)
