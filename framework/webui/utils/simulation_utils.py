# Python dependencies
import os
import sys

# Dash dependencies
from dash_extensions.WebSocket import WebSocket
import dash_bootstrap_components as dbc
from dash_extensions.enrich import Input, Output, State, callback, html
from dash.exceptions import PreventUpdate

# WebUI dependencies
from utils.schematic_utils import export_schematic
from utils.common_utils import get_session_dir

# elise library dipendencies
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
))
from batch.submit import execute_simulation

app_progress_report = WebSocket(id="app-progress-report", url="ws://localhost:55500")
progress_finished = dbc.Alert("The simulation has finished", id="execute-simulation-alert", duration=5000, is_open=False)
progress_bar = dbc.Alert([
    html.H2("Simulation Progress"),
    dbc.Progress(id="progress-bar", value=0)
    ],
    id="progress-bar-collapse",
    is_open=False, 
    # style={"position": "fixed", "bottom": "0", "left": "0", "right": "0", "margin": "0", "width": "100%"}
)

@callback(
    Output("progress-bar", "value"),
    Output("progress-bar", "label"),
    Input("app-progress-report", "message"),
    prevent_initial_call=True
)
def update_progress_store(msg):
    data_str = str(msg["data"])
    data_str = data_str.rstrip("\x00")
    progress = int(float(data_str))
    return progress, f"{progress} %"

@callback(
    Output("progress-bar-collapse", "is_open"),
    Output("progress-bar-collapse", "duration"),
    Input("execute-simulation-btn", "n_clicks"),
    prevent_initial_call=True
)
def webui_show_progress(n_clicks):
    return True, None

@callback(
    Output("execute-simulation-alert", "is_open"),
    Output("progress-bar-collapse", "duration", allow_duplicate=True),
    Input("execute-simulation-btn", "n_clicks"),
    State("app-sim-schematic", "data"),
    State("app-session-store", "data"),
    prevent_initial_call=True
)
def webui_execute_simulation(n_clicks, schematic_data, session_data):
    if not n_clicks:
        raise PreventUpdate
    
    filename = export_schematic(schematic_data, session_data)
    cmdline = ["-f", filename, "-p", "mpi", "--webui", "--export_reports", f"{get_session_dir(session_data)}/results"]
    execute_simulation(cmdline)
    return True, 3000