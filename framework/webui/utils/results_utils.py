# Python dependencies
import json
import plotly.graph_objects as go
from plotly.io import from_json
import os
from datetime import timedelta

# Dash dependencies
from dash_extensions.WebSocket import WebSocket
import dash_bootstrap_components as dbc
from dash_extensions.enrich import Input, Output, State, callback, html, ALL, clientside_callback, MATCH, callback_context, dcc, dash_table
from dash.exceptions import PreventUpdate

# WebUI dependencies
from utils.common_utils import get_session_dir

def import_results(path: str):
    # If it exists and is a file return the contents
    # else return None
    contents = None
    if os.path.exists(path) and os.path.isfile(path):
        with open(path, "r") as fd:
            contents = fd.read()
    return contents
            
def files_in_directory(path: str):
    if os.path.isdir(path):
        return os.listdir(path)
    else:
        return []

def fork_results(action_args, path: str):
    
    res = dict()

    # If one of them is an empty list
    inputs = action_args["inputs"]
    schedulers = action_args["schedulers"]
    if not inputs or not schedulers:
        return res

    # If the directory does not exist
    if not os.path.isdir(path):
        return res
    
    files = os.listdir(path)

    for inp_idx in inputs:
        input_key = f"input-{inp_idx-1}"
        res[input_key] = dict()
        for sched_idx in schedulers:
            scheduler_key = f"scheduler-{sched_idx-1}"
            file_prefix = f"input_{inp_idx-1}_scheduler_{sched_idx-1}."

            filename = ""
            for file in files:
                if file_prefix in file:
                    filename = file
                    break
            
            if not filename:
                pass
            
            print(input_key, scheduler_key)
            res[input_key][scheduler_key] = import_results(f"{path}/{filename}")

        res[input_key] = {key: res[input_key][key] for key in sorted(res[input_key])}
    
    return res

def get_experiment_results(schematic_data, session_data):
    # Get results directory
    session_dir = get_session_dir(session_data)
    results_dir = f"{session_dir}/results"

    # Define basic experiment structure
    results = dict()
    results["time-reports"] = import_results(f"{results_dir}/time_reports.csv")

    def conditional_action(action: str, out_dir: str):
        if action in schematic_data["actions"]:
            fork_res = fork_results(schematic_data["actions"][action], f"{results_dir}/{out_dir}")
            if fork_res:
                results[action] = fork_res

    conditional_action("get-workloads", "workloads")
    conditional_action("get-gantt-diagrams", "gantt")
    conditional_action("get-waiting-queue-diagrams", "waiting_queue")
    conditional_action("get-jobs-throughput-diagrams", "jobs_throughput")
    conditional_action("get-unused-cores-diagrams", "unused_cores")
    conditional_action("get-animated-clusters", "animated_cluster")
    
    return results

def get_action_name(action: str):
    match action:
        case "time-reports":
            return "Report"
        case "get-workloads":
            return "Workloads"
        case "get-gantt-diagrams":
            return "Gantt Diagrams"
        case "get-waiting-queue-diagrams":
            return "Waiting Queue Diagrams"
        case "get-jobs-throughput-diagrams":
            return "Jobs Throughput Diagrams"
        case "get-unused-cores-diagrams":
            return "Unused Cores Diagrams"
        case "get-animated-clusters":
            return "Animated Clusters"

def get_input_name(input_id: str):
    return input_id.replace("input-", "Input ")

def get_scheduler_name(sched_id: str, schematic_data: dict):
    scheduler_name = schematic_data["schedulers"][sched_id]["name"]
    return f"{sched_id.replace('scheduler-', '')}. {scheduler_name}"

def is_general_diagram(action: str):
    match action:
        case "get-gantt-diagrams":
            return False
        case "get-workloads":
            return False
        case "get-animated-clusters":
            return False
        case _:
            return True


@callback(
    Output("results-component-items", "children"),
    Input("app-results-store", "data"),
    State("app-sim-schematic", "data"),
    # prevent_initial_call=True
)
def create_results_tree(results_data, schematic_data):
    results_component_children = []
    for exp_id, exp in enumerate(results_data):
        exp_btn = dbc.Button(html.H6(f"Experiment {exp_id}"), id={"experiment": exp_id}, size="sm", outline=True, style={"textAlign": "left", "border": "none"})
        exp_children = []

        for action, action_val in exp.items():
            action_btn = dbc.Button(get_action_name(action), id={"experiment": exp_id, "action": action}, size="sm", outline=True, style={"textAlign": "left", "border": "none"})
            # exp_children.append(action_btn)

            if type(action_val) == dict:
                action_children = []
                for input_id, input_val in action_val.items():
                    general_diagram = is_general_diagram(action)
                    input_btn = dbc.Button(get_input_name(input_id), id={"experiment": exp_id, "action": action, "input": input_id, "general": general_diagram}, size="sm", outline=True, style={"textAlign": "left", "border": "none"})
                    
                    # Check if we want a general diagram or a per scheduler diagram
                    if not general_diagram:
                    
                        input_children = []
                        for sched_id in input_val.keys():
                            sched_btn = dbc.Button(get_scheduler_name(sched_id, schematic_data), id={"experiment": exp_id, "action": action, "input": input_id, "scheduler": sched_id}, size="sm", outline=True, style={"textAlign": "left", "border": "none"}) 
                            input_children.append(sched_btn)
                        
                        input_collapse = dbc.Collapse(dbc.Stack(input_children), id={"type": "experiment-action-input-collapse", "experiment": exp_id, "action": action, "input": input_id}, style={"paddingLeft": "10%"}, is_open=True)

                        action_children.append(dbc.Stack([input_btn, input_collapse]))
                    
                    else:
                        action_children.append(input_btn)
                    
                action_collapse = dbc.Collapse(dbc.Stack(action_children), id={"type": "experiment-action-collapse", "experiment": exp_id, "action": action}, style={"paddingLeft": "10%"}, is_open=True)
                
                exp_children.append(dbc.Stack([action_btn, action_collapse]))

            else:
                exp_children.append(action_btn)
        
        exp_collapse = dbc.Collapse(dbc.Stack(exp_children), id={"type": "experiment-collapse", "experiment": exp_id}, style={"paddingLeft": "10%"})
        results_component_children.append(dbc.Stack([exp_btn, exp_collapse]))
        
    return results_component_children             

@callback(
    Output({"type": "experiment-collapse", "experiment": MATCH}, "is_open"),
    Input({"experiment": MATCH}, "n_clicks"),
    State({"type": "experiment-collapse", "experiment": MATCH}, "is_open"),
    prevent_initial_call=True
)
def experiment_collapses(n_clicks, is_open):
    return not is_open

@callback(
    Output({"type": "experiment-action-collapse", "experiment": MATCH, "action": MATCH}, "is_open"),
    Input({"experiment": MATCH, "action": MATCH}, "n_clicks"),
    State({"type": "experiment-action-collapse", "experiment": MATCH, "action": MATCH}, "is_open"),
    prevent_initial_call=True
)
def experiment_action_collapses(n_clicks, is_open):
    return not is_open

@callback(
    Output({"type": "experiment-action-input-collapse", "experiment": MATCH, "action": MATCH, "input": MATCH}, "is_open"),
    Input({"experiment": MATCH, "action": MATCH, "input": MATCH, "general": False}, "n_clicks"),
    State({"type": "experiment-action-input-collapse", "experiment": MATCH, "action": MATCH, "input": MATCH}, "is_open"),
    prevent_initial_call=True
)
def experiment_input_collapses(n_clicks, is_open):
    print(False)
    return not is_open

@callback(
    Output("main-canvas", "children", allow_duplicate=True),
    Input({"experiment": ALL, "action": ALL, "input": ALL, "general": True}, "n_clicks"),
    State("app-results-store", "data"),
    State("app-sim-schematic", "data"),
    prevent_initial_call=True
)
def draw_canvas_general_diagram(n_clicks, results_data, schematic_data):
    if not any(n_clicks):
        raise PreventUpdate

    triggered_id = callback_context.triggered_id
    exp_id = triggered_id["experiment"]
    action = triggered_id["action"]
    input_id = triggered_id["input"]

    result = results_data[exp_id][action][input_id]
    data = []

    max_x = -1
    for sched_id, sched_val in result.items():
        sched_data = from_json(json.loads(sched_val)).data[0]
        if max(sched_data.x) > max_x:
            max_x = max(sched_data.x)
        sched_name = schematic_data["schedulers"][sched_id]["name"]
        sched_data.update({"name": sched_name})
        data.append(sched_data)
    
    fig = go.Figure(data=data)

    match action:
        case "get-waiting-queue-diagrams":
            layout = {
                "title": f"<b>Number of jobs in waiting queues</b><br>{get_input_name(input_id)}",
                "title_x": 0.5,
                "xaxis": {"title": "<b>Time</b>"},
                "yaxis": {"title": "<b>Number of waiting jobs</b>"},
            }
        case "get-jobs-throughput-diagrams":
            layout = {
                "title": f"<b>Number of finished jobs per scheduler</b><br>{get_input_name(input_id)}",
                "title_x": 0.5,
                "xaxis": {"title": "<b>Time</b>"},
                "yaxis": {"title": "<b>Number of finished jobs</b>"},
            }
        case "get-unused-cores-diagrams":
            layout = {
                "title": f"<b>Cluster utilization per scheduler</b><br>{get_input_name(input_id)}",
                "title_x": 0.5,
                "xaxis": {"title": "<b>Time</b>"},
                "yaxis": {"title": "<b>Number of unused cores</b>"},
            }
        case _:
            layout = {}
    
    fig.update_layout(layout)

    xaxis_tickvals = [i * (max_x / 10) for i in range(0, 11)]
    xaxis_ticktext = [str(timedelta(seconds=i)).split('.')[0] for i in xaxis_tickvals]
    fig.update_xaxes(range=[0, max_x])
    
    fig["layout"]["xaxis"]["tickvals"] = xaxis_tickvals
    fig["layout"]["xaxis"]["ticktext"] = xaxis_ticktext

    return dcc.Graph(figure=fig, style={"height": "100vh"})
    

@callback(
    Output("main-canvas", "children", allow_duplicate=True),
    Input({"experiment": ALL, "action": ALL, "input": ALL, "scheduler": ALL}, "n_clicks"),
    State("app-results-store", "data"),
    State("app-sim-schematic", "data"),
    prevent_initial_call=True
)
def draw_canvas_scheduler(n_clicks, results_data, schematic_data):
    
    if not any(n_clicks):
        raise PreventUpdate

    triggered_id = callback_context.triggered_id
    exp_id = triggered_id["experiment"]
    action = triggered_id["action"]
    input_id = triggered_id["input"]
    sched_id = triggered_id["scheduler"]
    
    result = results_data[exp_id][action][input_id][sched_id]
    
    match action:
        case "get-workloads":
            def create_table(inp):
                data = inp.split("\n")
                table_data = [] 
                head = data[0].strip().split(",")
                for line in data[1:]:
                    values = line.strip().split(",")
                    table_data.append(dict(zip(head, values)))
                return head, table_data
            
            head, table_data = create_table(result)
            for row in table_data:
                for key, val in row.items():
                    if "time" in key.lower() and val != "":
                        row[key] = float(val)
            
            # Create tooltips from the other schedulers
            others = dict()
            for other_sched_id in schematic_data["schedulers"].keys():
                if other_sched_id != sched_id:
                    _, other_tdata = create_table(results_data[exp_id][action][input_id][other_sched_id])
                    others[other_sched_id] = other_tdata
            
            tooltip = []
            for i, row in enumerate(table_data):
                row_dict = dict()
                for key in row.keys():
                    values = []
                    for other_sched_id, other_tdata in others.items():
                        values.append(f"{schematic_data["schedulers"][other_sched_id]["name"]}: {other_tdata[i][key]}")
                    row_dict[key] = "\n".join(values)
                tooltip.append(row_dict)
            
            
            def create_columns():
                columns = []
                for head_col in head:
                    if "time" in head_col.lower():
                        columns.append({"name": head_col, "id": head_col, "type": "numeric", "format": {"specifier": ".3f"}})
                    else:
                        columns.append({"name": head_col, "id": head_col})
                return columns
            
            return dash_table.DataTable(data=table_data, 
                                        columns=create_columns(), 
                                        style_table={"height": "100vh", "overflowY": "scroll"},
                                        style_header={"whiteSpace": "normal", "height": "auto", "fontWeight": "bold", "textAlign": "center", "position": "sticky", "top": 0},
                                        style_cell={"textAlign": "center"},
                                        tooltip_data=tooltip,
                                        tooltip_delay=1000,
                                        tooltip_duration=None)
        
        case _:
            # For Plotly graphs
            data = json.loads(result)
            diagram = from_json(data)
            print(type(diagram))
            return dcc.Graph(figure=diagram, style={"height": "100vh"})