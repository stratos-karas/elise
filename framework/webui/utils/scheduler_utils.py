from dash import html
from dash import callback, callback_context, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_core_components as dcc


"""
app-sim-schematic::schedulers

    keyword (str): scheduler-{id}
    value:
        method (str): Defaults or Custom
        value (str): scheduler name or file path
        default (bool): if it is the default scheduler
        options list(int): list of the options enabled for the scheduler
"""

def scheduler_item_modal_body(data=None):
    """If data is None then new scheduler item; if data exists then modifying the scheduler
    """
    
    
    # if data is None:

    div = html.Div([
        dbc.InputGroup([dbc.Select(["Defaults", "Custom"], "Defaults", id="scheduler-item-select-method"), 
                        dbc.Select(["FIFO Scheduler", "EASY Scheduler"], "FIFO Scheduler", id="scheduler-item-select-scheduler", style={"display": "block"}),
                        dcc.Upload(dbc.Button("Upload file", style=dict(width="100%")), id="scheduler-item-upload-scheduler", style={"display": "none"}),
        ]),
        html.Footer(id="scheduler-item-upload-footer", className="small", style=dict(display="none")),
        dbc.Checklist(
            id="scheduler-item-options",
            options=[dict(label="Default", value=1), dict(label="Backfilling", value=2), dict(label="Compact fallback", value=3)],
            value=[],
            inline=True,
            switch=True
        ),
        dbc.Button("Save Scheduler", id="scheduler-item-save-btn")
    ])
    
    return div
    # else:
    #     method, value = list(data["method"].items())
    #     match method:
    #         case "file":
    #             select_scheduler_element = dbc.Select(["FIFO Scheduler", "EASY Scheduler"], "FIFO Scheduler", style=hidden_style)
    #             upload_scheduler_element = dbc.Button("Upload file", style=displayed_style)
    #         case _:
    #             select_scheduler_element = dbc.Select(["FIFO Scheduler", "EASY Scheduler"], "FIFO Scheduler", style=displayed_style)
    #             upload_scheduler_element = dbc.Button("Upload file", style=hidden_style)

    #     options_enabled = data["options"]

    #     div = html.Div([
    #         dbc.InputGroup(
    #             [
    #                 dbc.Select(["Defaults", "Custom"], "Defaults", id="scheduler-item-select-method"), 
    #                 dbc.Select(["FIFO Scheduler", "EASY Scheduler"], "FIFO Scheduler"), 
    #                 dbc.Button("Upload file")
    #             ], id="scheduler-item-methodinput"
    #         ),
    #         dbc.Checklist(
    #             options=[dict(label="Backfilling", value=1), dict(label="Compact fallback", value=2)],
    #             value=options_enabled,
    #             inline=True,
    #             switch=True
    #         ),
    #         dbc.Button("Save")
    #     ])

# @callback(
#     Output("app-sim-schematic", "data")
#     Input("schedulers-modal-save-btn", "n_clicks")
# )
# def schedulers_modal_save_button(n_clicks):
#     pass
    
schedulers_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Schedulers")),
    dbc.ModalBody(id="schedulers-modal-body")
], id="schedulers-modal", is_open=False)


@callback(
   Output("schedulers-modal", "is_open"),
   Output("schedulers-modal-body", "children"),
   Input("add-schedulers", "n_clicks"),
)
def schedulers_modal_open(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    return True, scheduler_item_modal_body()

@callback(
    Output("scheduler-item-select-scheduler", "style"),
    Output("scheduler-item-upload-scheduler", "style"),
    Output("scheduler-item-upload-footer", "style"),
    Input("scheduler-item-select-method", "value"),
)
def scheduler_item_select_method(value):
    if not value:
        raise PreventUpdate
    display = {"display": "block"}
    hidden = {"display": "none"}
    print(value)
    if value == "Custom":
        return hidden, display, display
    else:
        return display, hidden, hidden

@callback(
    Output("scheduler-item-upload-footer", "children"),
    Input("scheduler-item-upload-scheduler", "filename")
)
def scheduler_item_upload_scheduler(filename):
    if not filename:
        raise PreventUpdate
    return f"* Uploaded scheduler file: {filename}"

@callback(
    Output("app-sim-schematic", "data"),
    Input("scheduler-item-save-btn", "n_clicks"),
    State("scheduler-item-select-method", "value"),
    State("scheduler-item-select-scheduler", "value"),
    State("scheduler-item-upload-scheduler", "filename"),
    State("scheduler-item-options", "value"),
    State("app-sim-schematic", "data")
)
def save_scheduler_item(n_clicks, method, select_scheduler_value, upload_scheduler_value, options, schematic_data):
    if not n_clicks:
        raise PreventUpdate

    data = dict()
    data["method"] = method
    data["options"] = options
    if method == "Custom":
        data["value"] = upload_scheduler_value
    else:
        data["value"] = select_scheduler_value
    
    scheduler_id = len(list(schematic_data["schedulers"].keys())) - 1
    schematic_data["schedulers"].update({scheduler_id: data})
    
    return schematic_data