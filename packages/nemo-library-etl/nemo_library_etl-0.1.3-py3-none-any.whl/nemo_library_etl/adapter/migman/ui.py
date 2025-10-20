import json
from pathlib import Path
from nicegui import ui, app
import asyncio
from importlib import resources as importlib_resources

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

    def run_ui(self, *, open_browser: bool = True, dark_mode_enabled: bool = True) -> None:
        """Start the NiceGUI interface for MigMan configuration.

        Args:
            open_browser: whether to open the browser automatically
            dark_mode_enabled: initial dark mode state (you can load this from config)
        """

        connected_clients = set()
        global_config, local_config, merged_config = self.load_configurations()

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

            refs = {"content": None}
            nav_buttons = {}
            active = {"value": "Global"}

            def set_active(name: str):
                """Update the active navigation button appearance using theme props."""
                active["value"] = name
                for key, btn in nav_buttons.items():
                    btn.props(remove="color unelevated")
                    btn.props("flat")
                    if key == name:
                        btn.props(remove="flat")
                        btn.props("color=primary unelevated")

            # ---------- GLOBAL TOP BAR WITH DARK-MODE TOGGLE ----------
            # This is a lightweight header pinned to the top right.
            with ui.element("div").classes(
                "fixed top-2 right-4 z-50"
            ):
                with ui.row().classes("items-center gap-3"):
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
                c = refs["content"]
                c.clear()
                with c:
                    ui.label("Global Settings").classes("text-2xl font-semibold")
                    ui.separator()
                    ui.label("Configure global settings for the MigMan ETL process.")

                    etl_default = global_config.get("etl_directory", "./etl/migman")

                    # --- ETL Directory (editable) ---
                    with ui.card().classes("mt-4 p-4 max-w-[900px]"):
                        ui.label("ETL directory").classes("text-lg font-semibold mb-2")
                        etl_dir_input = (
                            ui.input(
                                label="Path to ETL folder",
                                value=etl_default,
                                placeholder="e.g. /Users/me/projects/migman/etl",
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


                    # --- Print button ---
                    def print_current():
                        print("[GLOBAL] etl_directory =", etl_dir_input.value or "")
                        ui.notify("Printed selections to console.", type="positive")

                    ui.button("Print selections", on_click=print_current).classes(
                        "mt-4"
                    )

            def render_extract():
                c = refs["content"]
                c.clear()
                with c:
                    ui.label("Extract").classes("text-2xl font-semibold")
                    ui.separator()
                    ui.label("Configure data sources and extraction parameters.")

            def render_transform():
                c = refs["content"]
                c.clear()
                with c:
                    ui.label("Transform").classes("text-2xl font-semibold")
                    ui.separator()
                    ui.label("Define transformations, mappings and validations.")

            def render_load():
                c = refs["content"]
                c.clear()
                with c:
                    ui.label("Load").classes("text-2xl font-semibold")
                    ui.separator()
                    ui.label("Load data into target system.")

            # ---------- LEFT DRAWER ----------
            with ui.left_drawer(value=True, fixed=True).classes("w-64 p-4"):
                ui.label("MigMan UI").classes("text-lg font-semibold mb-4")

                def make_nav_button(name: str, cb):
                    b = ui.button(name, on_click=cb).props("flat").classes(
                        "w-full justify-start mb-2"
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
                    refs["content"] = content
                    set_active("Global")
                    render_global()

        ui.run(reload=False, show=open_browser)