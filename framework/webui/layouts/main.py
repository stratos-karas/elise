from dash import dcc, html
from dash import callback, callback_context, Output, Input, State
from dash.exceptions import PreventUpdate
# import dash_blueprint_components as dpc
import dash_bootstrap_components as dbc

from utils import schematic_utils
from utils.input_utils import inputs_modal
from utils.scheduler_utils import schedulers_modal, schedulers_hierarchy_modal, schedulers_timer
from utils.action_utils import action_items_ctn, actions_modal
from utils.simulation_utils import progress_bar, app_progress_report, progress_finished

# SCHEMATIC TOOL
def schematic_component(name: str, description = None, items: list[dbc.ListGroupItem] = list(), add_button_enabled: bool = True):
    """Create an element for each schematic component
    + name: name of the component
    + description: description of the component
    + items: items of the component
    """

    # Title/name of the component
    title = html.H6(name)

    # Add button
    add_btn_label = html.I(className="bi bi-plus-square")
    add_btn_id = "add-" + name.lower()
    add_btn = dbc.Button(add_btn_label, id=add_btn_id,size="sm", outline=True)
    
    # Collapse button
    collapse_btn_label_icon_id = "collapse-" + name.lower() + "-btn-icon"
    collapse_btn_label = html.I(className="bi bi-caret-down-fill", id=collapse_btn_label_icon_id)
    collapse_btn_id = "collapse-" + name.lower() + '-btn'
    collapse_btn = dbc.Button(collapse_btn_label, id=collapse_btn_id, size="sm", outline=True)
    
    # Control buttons
    control_buttons_children = list()
    if add_button_enabled:
        control_buttons_children.append(add_btn)
    control_buttons_children.append(collapse_btn)
    control_buttons = dbc.ButtonGroup(control_buttons_children, className="ml-auto")

    title_div = html.Div([title, control_buttons], id=f"tooltip-{name.lower()}-target", className="d-flex align-items-center justify-content-between")
    
    if description:
        title_div.children.append(dbc.Tooltip(description, delay=dict(show=1000, hide=0), target=f"tooltip-{name.lower()}-target"))

    collapse_id = "collapse-" + name.lower()
    component_id = "component-" + name.lower()
    component_items_id = "component-" + name.lower() + "-items"
    
    # TODO: Add a button in the title div element and make the listgroup collapsable
    return dbc.ListGroupItem([
        title_div, 
        dbc.Collapse(dbc.Stack(items, id=component_items_id, style={"width": "100%"}), is_open=True, id=collapse_id),
        ], id=component_id, style={"width": "100%"})
    
schematic_components = [
    schematic_component(name="Inputs", description="Declares a schematic input: source, heatmap, generator, cluster", items=[]),
    schematic_component(name="Schedulers", description="Declares a schematic scheduler: known or custom", items=[]),
    schematic_component(name="Actions", description="Declares a schematic action: preprocessing and postprocessing", items=action_items_ctn, add_button_enabled=False),
    inputs_modal,
    schedulers_modal,
    schedulers_hierarchy_modal,
    schedulers_timer,
    actions_modal
]
schematic_components_ctn = dbc.Collapse(children=dbc.Stack(schematic_components, gap=3), id="schematic-components-collapse", is_open=True, style=dict(width="100%"))
schematic_header = dbc.Button(html.H5("Schematic", style={"alignSelf": "center", "textAlign": "left"}), size="sm", id="schematic-components-collapse-btn", style={"width": "100%"})
schematic_ctn = dbc.Stack([schematic_header, schematic_components_ctn])

# MAIN ACTIONS TOOL
main_actions_components = [
    dbc.InputGroup([
        dbc.InputGroupText("Provider", style={"width": "30%"}),
        dbc.Select(["MPI", "Python"], "MPI", id="main-action-multiprocessing-provider")
    ], style={"width": "100%"}),
    # dbc.Button("Export schematic", style={"width": "100%"}),
    # dbc.Button("Expand schematic", style={"width": "100%"}),
    dbc.Button("Execute simulation", id="execute-simulation-btn", style={"width": "100%"}),
]
main_actions_components_ctn = dbc.Collapse(children=dbc.Stack(main_actions_components), id="main-actions-components-collapse", is_open=True, style={"width": "100%"})
main_actions_header = dbc.Button(html.H5("Main Actions", style={"alignSelf": "center", "textAlign": "left"}), size="sm", id="main-actions-components-collapse-btn", style={"width": "100%"})
main_actions_ctn = dbc.Stack([main_actions_header, main_actions_components_ctn])

# RESULTS TOOL
results_components = []
results_components_ctn = dbc.Collapse(children=dbc.Stack(results_components, id="results-component-items"), id="results-components-collapse", is_open=True, style={"width": "100%"})
results_header = dbc.Button(html.H5("Results", style={"alignSelf": "center", "textAlign": "left"}), size="sm", id="results-components-collapse-btn", style={"width": "100%"})
results_ctn = dbc.Stack([results_header, results_components_ctn])

# FLOATING ALERTS
floating_div = dbc.Col([app_progress_report, progress_bar, progress_finished], style={"position": "fixed", "top": "0", "zIndex": 1, "backdrop-filter": "blur(5px)", "margin": 0, "padding": 0}, md=12, lg=10)

# ELiSE Logo
elise_logo = html.Div(
    html.Img(src="assets/imgs/elise-logo-horizontal.png", style={"width": "100%", "height": "auto"})
    , style={"flex": 1}
)

main_layout = dbc.Container([
    dbc.Row([
        dbc.Col(dbc.Stack([elise_logo, main_actions_ctn, schematic_ctn, results_ctn], gap=1), md=12, lg=2, class_name="toolarea", style={"overflowY": "scroll"}),
        dbc.Col([floating_div, dbc.Spinner(dbc.Container(id="main-canvas", fluid=True))], md=12, lg=10, class_name="workarea")
    ], class_name="g-0", style={"height": "100vh"})
], fluid=True, style={"width": "100%", "height": "100vh", "margin": 0, "padding": 0})

@callback(
    Output("main-actions-components-collapse", "is_open"),
    Output("schematic-components-collapse", "is_open"),
    Output("results-components-collapse", "is_open"),
    Input("main-actions-components-collapse-btn", "n_clicks"),
    Input("schematic-components-collapse-btn", "n_clicks"),
    Input("results-components-collapse-btn", "n_clicks"),
    State("main-actions-components-collapse", "is_open"),
    State("schematic-components-collapse", "is_open"),
    State("results-components-collapse", "is_open"),
    prevent_initial_call=True
)
def handle_tool_collapses(n, m, l, main_actions_open, schematic_open, results_open):
    triggered_id = callback_context.triggered_id
    if triggered_id == "main-actions-components-collapse-btn":
        return not main_actions_open, schematic_open, results_open
    elif triggered_id == "schematic-components-collapse-btn":
        return main_actions_open, not schematic_open, results_open
    elif triggered_id == "results-components-collapse-btn":
        return main_actions_open, schematic_open, not results_open
    else:
        raise PreventUpdate

@callback(
    Output("collapse-inputs", "is_open"),
    Output("collapse-schedulers", "is_open"),
    Output("collapse-actions", "is_open"),
    Output("collapse-inputs-btn-icon", "className"),
    Output("collapse-schedulers-btn-icon", "className"),
    Output("collapse-actions-btn-icon", "className"),
    Input("collapse-inputs-btn", "n_clicks"),
    Input("collapse-schedulers-btn", "n_clicks"),
    Input("collapse-actions-btn", "n_clicks"),
    State("collapse-inputs", "is_open"),
    State("collapse-schedulers", "is_open"),
    State("collapse-actions", "is_open"),
    prevent_initial_call=True
)
def handle_collapses(n,m,l, inp_open, sched_open, act_open):
    def icon_class(open: bool):
        if open:
            return "bi bi-caret-down-fill"
        else:
            return "bi bi-caret-right-fill"
    triggered_id = callback_context.triggered_id
    match triggered_id:
        case "collapse-inputs-btn":
            return not inp_open, sched_open, act_open, icon_class(not inp_open), icon_class(sched_open), icon_class(act_open)
        case "collapse-schedulers-btn":
            return inp_open, not sched_open, act_open, icon_class(inp_open), icon_class(not sched_open), icon_class(act_open)
        case "collapse-actions-btn":
            return inp_open, sched_open, not act_open, icon_class(inp_open), icon_class(sched_open), icon_class(not act_open)
        case _:
            raise PreventUpdate


# component_names = ["Inputs", "Schedulers", "Actions"]
component_names = ["Inputs", "Schedulers"]
component_ouput = [Output("component-"+name.lower()+"-items", "children") for name in component_names]
component_input = [Input("add-"+name.lower(), "n_clicks") for name in component_names]
component_state = [State("component-"+name.lower()+"-items", "children") for name in component_names]

def input_item_icon(case):
    if case.lower() == "database":
        return "bi bi-database"
    elif case.lower() == "json":
        return "bi bi-filetype-json"
    elif case.lower() == "path":
        return "bi bi-folder"
    else:
        return "bi bi-file-binary"


@callback(
    component_ouput,
    Input("app-sim-schematic", "data"),
    component_state
)
def modify_component_items(data, inputs_children, schedulers_children):

    if not data:
        raise PreventUpdate

    new_inputs_children = list()
    for key, val in data["inputs"].items():
        item, index = key.split('-')
        id = {"item": item, "index": index}
        del_id = {"delete-item": item, "index": index}
        child_exists = False
        
        for item in inputs_children:
            btn = item["props"]["children"][1]
            btn_id = btn["props"]["id"]
            btn_label = btn["props"]["children"]

            # Check if they share the same id and name==label
            if id == btn_id and val["name"] == btn_label:
                new_inputs_children.append(item)
                child_exists = True
                break
        
        if not child_exists:
            new_inputs_children.append(
                # dbc.ListGroupItem(
                    dbc.ButtonGroup([
                        html.I(className=input_item_icon(data["inputs"][key]["logs-source"]), style={"alignSelf": "center"}),
                        dbc.Button(data["inputs"][key]["name"], id=id, color="secondary", outline=True, size="sm", style={"flex": 1, "border": "none", "margin": 0, "textAlign": "left"}),
                        dbc.Button(html.I(className="bi bi-x"), id=del_id, size="sm", outline=True, style={"flex": 0})
                    ], style={"paddingLeft": "10%"}, class_name="d-flex"))
                # , style=dict(margin=0, padding=0, border="none", display="flex")),
                # , style={"paddingLeft": "10%", "border": "none", "width": "100%"}),
            # )

    
    new_schedulers_children = list()
    for key, val in data["schedulers"].items():
        item, index = key.split('-')
        id = {"item": item, "index": index}
        del_id = {"delete-item": item, "index": index}
        child_exists = False
        
        for item in schedulers_children:
            btn = item["props"]["children"][0]
            btn_id = btn["props"]["id"]
            btn_label = btn["props"]["children"]

            # Check if they share the same id and name==label
            if id == btn_id and val["name"] == btn_label:
                new_schedulers_children.append(item)
                child_exists = True
                break
        
        if not child_exists:
            new_schedulers_children.append(
                # dbc.ListGroupItem(
                    dbc.ButtonGroup([
                        dbc.Button(data["schedulers"][key]["name"], id=id, color="secondary", outline=True, size="sm", style={"flex": 1, "border": "none", "margin": 0, "textAlign": "left"}),
                        dbc.Button(html.I(className="bi bi-x"), id=del_id, size="sm", outline=True, style={"flex": 0})
                    ], style={"paddingLeft": "10%"})
            )
                # , style=dict(margin=0, padding=0)),
                # , style={"paddingLeft": "10%", "border": "none", "width": "100%"}),
            # )

    return new_inputs_children, new_schedulers_children
