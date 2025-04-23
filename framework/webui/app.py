from dash_extensions.enrich import DashProxy, Input, Output, dcc, html, callback
import dash_bootstrap_components as dbc
from flask import Flask, request, jsonify
from layouts.main import main_layout
import os
import subprocess
import sys
from uuid import uuid4

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
))

from common import utils as cutils
from utils.action_utils import action_item_name, action_items_names

# Store session information
app_session_store = dcc.Store(
        id="app-session-store",
        storage_type="session",
        data=dict(
            sid=str(uuid4())
            )
        )

actions_data = {
    action_item_name(name):{"inputs": [], "schedulers": []}
    for name in action_items_names
}

# Store schematic data
app_schematic_store = dcc.Store(
        id="app-sim-schematic",
        storage_type="session",
        data=dict(
            name="",
            description="",
            inputs=dict(),
            schedulers=dict(),
            actions=actions_data
        )
)

# Store simulation progress
app_progress_store = dcc.Store(
    id="app-progress-store",
    storage_type="memory",
    data=dict(
        progress=0
    ) 
)

app_results_store = dcc.Store(
    id="app-results-store",
    storage_type="memory",
    data=list()
)

# Defining the application
app = DashProxy(__name__,
                compress=True,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                external_stylesheets=["assets/css/bootstrap.min.css", "assets/css/bootstrap-icons.css", "assets/css/schematic_components.css"])

# Application configuration
# app.config.suppress_callback_exceptions = True

# Defining the layout
app.layout = dbc.Container([

    app_session_store,
    app_schematic_store,
    app_progress_store,
    app_results_store,
    main_layout

], fluid=True, class_name="mh-100", style={"height": "100vh"}, id="layout")

app.title = "ELiSE"
app.config.update_title = None

if __name__ == "__main__":
    gui_debug = cutils.envvar_bool_val("ELiSE_GUI_DEBUG")
    ws_server_process = subprocess.Popen(["python", "ws_server.py"])
    # Start application
    app.run(host="0.0.0.0", port=8050, debug=gui_debug)
    ws_server_process.wait()
