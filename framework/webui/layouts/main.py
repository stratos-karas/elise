from dash import html
from dash import callback, callback_context, Output, Input, State
from dash.exceptions import PreventUpdate
# import dash_blueprint_components as dpc
import dash_bootstrap_components as dbc
import dash_core_components as dcc

from utils.scheduler_utils import schedulers_modal

def create_schem_component(name: str, description: str = "", items: list[dbc.ListGroupItem] = list()):
    """Create an element for each schematic component
    + name: name of the component
    + description: description of the component
    + items: items of the component
    """
    title = html.H3(name)
    title_div = html.Div([title], id=f"tooltip-{name.lower()}-target")
    
    if description:
        title_div.children.append(dbc.Tooltip(description, delay=dict(show=1000, hide=0), target=f"tooltip-{name.lower()}-target"))
    
    btn_label = "Add " + name
    btn_id = "add-" + name.lower()
    title_div.children.append(
        dbc.ListGroupItem(
            dbc.Button(btn_label, id=btn_id, style=dict(margin=0, padding=0, width="100%")),
            style=dict(margin=0, padding=0))
        
    )
    # items.append(
    #     )

    component_id = "component-" + name.lower()
    component_items_id = "component-" + name.lower() + "-items"
    
    # TODO: Add a button in the title div element and make the listgroup collapsable
    return dbc.ListGroupItem([title_div, dbc.ListGroup(items, id=component_items_id)], id=component_id, action=True)
    

tools = [
    create_schem_component(name="Workloads", description="Add workloads: source, heatmap, generator, cluster", items=[]),
    create_schem_component(name="Schedulers", description="Add schedulers: known or custom", items=[]),
    create_schem_component(name="Actions", description="Add actions: preprocessing and postprocessing", items=[]),
    schedulers_modal
]
tools_ctn = dbc.ListGroup(children=tools, id="tools-container", key="tools-container", style=dict(width="100%"))

main_layout = dbc.Container([
    dbc.Row([
        dbc.Col(tools_ctn, width=2, style={"background-color": "gray", "height": "100%"}),
        dbc.Col(width=10, style={"height": "100%"})
    ], align="stretch")
], fluid=True, style={"height": "100%"})



component_names = ["Workloads", "Schedulers", "Actions"]
component_ouput = [Output("component-"+name.lower()+"-items", "children") for name in component_names]

component_input = [Input("add-"+name.lower(), "n_clicks") for name in component_names]

component_state = [State("component-"+name.lower()+"-items", "children") for name in component_names]

def get_item_id():
    pass

@callback(
    component_ouput,
    Input("app-sim-schematic", "data"),
    component_state
)
def modify_component_items(data, workloads_children, schedulers_children, actions_children):

    if not data:
        raise PreventUpdate

    # new_workloads_children = [dbc.ListGroupItem(f"workload-{idx}") for idx, _ in enumerate(data["workloads"].keys())]
    # new_workloads_children = list()
    # for i, key in enumerate(data["workloads"].keys()):
    #     new_workloads_children.append(
    #         dbc.ListGroupItem(dbc.Button(key, id=dict(item="workload", index=i), style=dict(margin=0, padding=0, width="100%")),
    #                           style=dict(margin=0, padding=0))
    #     )

    
    new_schedulers_children = list()
    for key in data["schedulers"].keys():
        item, index = key.split('-')
        id = {"item": item, "index": index}
        del_id = {"delete-item": item, "index": index}
        child_exists = False
        
        for item in schedulers_children:
            btn = item["props"]["children"]["props"]["children"][0]
            btn_id = btn["props"]["id"]

            try:
                if id == btn_id:
                    new_schedulers_children.append(item)
                    child_exists = True
                    break
            except:
                continue
        
        if not child_exists:
            new_schedulers_children.append(
                dbc.ListGroupItem(
                    dbc.InputGroup([
                        dbc.Button(data["schedulers"][key]["name"], id=id, color="secondary", outline=True, size="sm", style=dict(margin=0, padding=0, width="80%")),
                        dbc.Button(html.I(className="bi bi-x"), id=del_id, size="sm", style=dict(width="20%"))
                    ])
                , style=dict(margin=0, padding=0)),
            )

    # new_actions_children = list()
    # for i, key in enumerate(data["actions"].keys()):
    #     new_actions_children.append(
    #         dbc.ListGroupItem(dbc.Button(key, id=dict(item="action", index=i), style=dict(margin=0, padding=0, width="100%")),
    #                           style=dict(margin=0, padding=0))
    #     )

    return workloads_children, new_schedulers_children, actions_children
