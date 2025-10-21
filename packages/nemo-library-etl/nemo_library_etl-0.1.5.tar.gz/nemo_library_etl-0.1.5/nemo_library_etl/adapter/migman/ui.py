import json
from pathlib import Path
from nicegui import ui, app
import asyncio
from importlib import resources as importlib_resources
from typing import Dict, Any, Optional

from nemo_library_etl.adapter._utils.config import _deep_merge


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

    def _get_config_differences(self, current_config: Dict[str, Any], default_config: Dict[str, Any]) -> Dict[str, Any]:
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

    def run_ui(
        self, *, open_browser: bool = True, dark_mode_enabled: bool = True
    ) -> None:
        """Start the NiceGUI interface for MigMan configuration.

        Args:
            open_browser: whether to open the browser automatically
            dark_mode_enabled: initial dark mode state (you can load this from config)
        """

        connected_clients = set()
        global_config, local_config, merged_config = self.load_configurations()

        # State to track changes and form data
        form_state = {
            "has_changes": False,
            "data": merged_config.copy(),
        }

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
                    global_config, local_config, merged_config = self.load_configurations()
                    
                    # Update form state with the new merged config
                    form_state["data"] = merged_config.copy()
                    form_state["has_changes"] = False
                    
                    # Mark as saved (since we're back to defaults)
                    mark_saved()
                    
                    # Re-render the current active section to reflect changes
                    current_active = active["value"]
                    if current_active == "Global":
                        render_global()
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
                            ui.label("Reset Configuration").classes("text-lg font-semibold")
                            ui.label("Do you really want to delete all individual configurations and reset to default values?").classes("mb-4")
                            
                            with ui.row().classes("gap-2 justify-end"):
                                ui.button("Cancel", on_click=on_cancel).props("flat")
                                ui.button("Reset", on_click=on_confirm).props("color=negative")
                        
                        dialog.open()
                    
                    ui.button(
                        "Reset", 
                        icon="restart_alt",
                        on_click=confirm_reset
                    ).classes("text-white").props("color=negative outline")
                    
                    # Save button (initially disabled)
                    save_button = ui.button(
                        "Save", 
                        icon="save",
                        on_click=save_config
                    ).props("disable").classes("text-white")
                    
                    ui.separator().props("vertical")
                    
                    ui.label("Dark mode")

                    def on_toggle(e):
                        """Enable/disable dark mode globally at runtime."""
                        state["dark"] = e.value
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

                    current_etl_directory = form_state["data"].get("etl_directory", "./etl/migman")

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


            def render_extract():
                if not content_container:
                    return
                    
                content_container.clear()
                with content_container:
                    ui.label("Extract").classes("text-2xl font-semibold")
                    ui.separator()
                    ui.label("Configure data sources and extraction parameters.")
                    
                    # Extract active toggle
                    extract_config = form_state["data"].setdefault("extract", {})
                    
                    with ui.card().classes("mt-4"):
                        ui.label("Extract Settings").classes("text-lg font-semibold mb-2")
                        
                        def on_extract_active_change(e):
                            extract_config["extract_active"] = e.value
                            mark_changed()
                        
                        ui.switch(
                            "Extract active",
                            value=extract_config.get("extract_active", True),
                            on_change=on_extract_active_change
                        )
                        
                        def on_load_to_nemo_change(e):
                            extract_config["load_to_nemo"] = e.value
                            mark_changed()
                        
                        ui.switch(
                            "Load to NEMO",
                            value=extract_config.get("load_to_nemo", True),
                            on_change=on_load_to_nemo_change
                        )

            def render_transform():
                if not content_container:
                    return
                    
                content_container.clear()
                with content_container:
                    ui.label("Transform").classes("text-2xl font-semibold")
                    ui.separator()
                    ui.label("Define transformations, mappings and validations.")
                    
                    # Transform active toggle
                    transform_config = form_state["data"].setdefault("transform", {})
                    
                    with ui.card().classes("mt-4"):
                        ui.label("Transform Settings").classes("text-lg font-semibold mb-2")
                        
                        def on_transform_active_change(e):
                            transform_config["transform_active"] = e.value
                            mark_changed()
                        
                        ui.switch(
                            "Transform active",
                            value=transform_config.get("transform_active", True),
                            on_change=on_transform_active_change
                        )

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
                            load_config["load_active"] = e.value
                            mark_changed()
                        
                        ui.switch(
                            "Load active",
                            value=load_config.get("load_active", True),
                            on_change=on_load_active_change
                        )

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
