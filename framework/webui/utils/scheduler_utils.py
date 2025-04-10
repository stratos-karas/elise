from dash import dcc, html, ALL
from dash import callback, callback_context, Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

import base64
import tempfile


"""
app-sim-schematic::schedulers

    keyword (str): scheduler-{id}
    value:
        method (str): Defaults or Custom
        name (str): scheduler's name
        value (str): scheduler's name or file path
        default (bool): if it is the default scheduler
        options list(int): list of the options enabled for the scheduler
"""

def scheduler_item_modal_body(data=None, index=None):
    """If data is None then new scheduler item; if data exists then modifying the scheduler
    """
    
    
    if data is None:

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
            dbc.Button("Save Scheduler", id="scheduler-item-save-btn", style=dict(width="100%"))
        ])

    else:
        method = data["method"]
        value = data["name"]
        options_values = data["options"]

        if method == "Custom":
            div = html.Div([
                dbc.InputGroup([dbc.Select(["Defaults", "Custom"], "Custom", id="scheduler-item-select-method"), 
                                dbc.Select(["FIFO Scheduler", "EASY Scheduler"], "FIFO Scheduler", id="scheduler-item-select-scheduler", style={"display": "none"}),
                                dcc.Upload(dbc.Button("Upload file", style=dict(width="100%")), id="scheduler-item-upload-scheduler", style={"display": "block"}),
                ]),
                html.Footer(f"* Uploaded scheduler file: {value}", id="scheduler-item-upload-footer", className="small", style=dict(display="block")),
                dbc.Checklist(
                    id="scheduler-item-options",
                    options=[dict(label="Default", value=1), dict(label="Backfilling", value=2), dict(label="Compact fallback", value=3)],
                    value=options_values,
                    inline=True,
                    switch=True
                ),
                dbc.Button("Save Scheduler", id="scheduler-item-save-btn", style=dict(display="none")),
                dbc.Button("Modify scheduler", id={"modify-item": "scheduler", "index": index}, style=dict(width="100%"))
            ])
        else:
            div = html.Div([
                dbc.InputGroup([dbc.Select(["Defaults", "Custom"], "Defaults", id="scheduler-item-select-method"), 
                                dbc.Select(["FIFO Scheduler", "EASY Scheduler"], value, id="scheduler-item-select-scheduler", style={"display": "block"}),
                                dcc.Upload(dbc.Button("Upload file", style=dict(width="100%")), id="scheduler-item-upload-scheduler", style={"display": "none"}),
                ]),
                html.Footer(id="scheduler-item-upload-footer", className="small", style=dict(display="none")),
                dbc.Checklist(
                    id="scheduler-item-options",
                    options=[dict(label="Default", value=1), dict(label="Backfilling", value=2), dict(label="Compact fallback", value=3)],
                    value=options_values,
                    inline=True,
                    switch=True
                ),
                dbc.Button("Save Scheduler", id="scheduler-item-save-btn", style=dict(display="none")),
                dbc.Button("Modify scheduler", id={"modify-item": "scheduler", "index": index}, style=dict(width="100%"))
            ])
    
    return div
 
schedulers_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Schedulers")),
    dbc.ModalBody(id="schedulers-modal-body")
], id="schedulers-modal", is_open=False)


@callback(
   Output("schedulers-modal", "is_open"),
   Output("schedulers-modal-body", "children"),
   Output("add-schedulers", "n_clicks"),
   Output({"item": "scheduler", "index": ALL}, "n_clicks"),
   Input("add-schedulers", "n_clicks"),
   Input({"item": "scheduler", "index": ALL}, "n_clicks"),
   State("app-sim-schematic", "data"),
   prevent_initial_call=True,
)
def schedulers_modal_open(n_clicks, m_clicks, data):
    
    if not n_clicks and not any(m_clicks):
        raise PreventUpdate

    trigger_id = callback_context.triggered_id
    print(trigger_id)
    if trigger_id == "add-schedulers":
        return True, scheduler_item_modal_body(), None, [None] * len(m_clicks)
    else:
        idx = int(trigger_id["index"])
        return True, scheduler_item_modal_body(data["schedulers"][f"scheduler-{idx}"], idx), None, [None] * len(m_clicks)

@callback(
    Output("scheduler-item-select-scheduler", "style"),
    Output("scheduler-item-upload-scheduler", "style"),
    Output("scheduler-item-upload-footer", "style"),
    Input("scheduler-item-select-method", "value"),
    prevent_initial_call=True
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
    Input("scheduler-item-upload-scheduler", "filename"),
    prevent_initial_call=True
)
def scheduler_item_upload_scheduler_notification(filename):
    return f"* Uploaded scheduler file: {filename}"


def parse_uploaded_scheduler_contents(enc_contents):
    # Decode the contents
    content_type, content_string = enc_contents.split(',')
    
    if "python" not in content_type.lower():
        raise Exception

    decoded = base64.b64decode(content_string)
    return decoded.decode('utf-8')

@callback(
    Output("app-sim-schematic", "data"),
    Output("schedulers-modal", "is_open", allow_duplicate=True),
    Input("scheduler-item-save-btn", "n_clicks"),
    Input({"modify-item": "scheduler", "index": ALL}, "n_clicks"),
    State("scheduler-item-select-method", "value"),
    State("scheduler-item-select-scheduler", "value"),
    State("scheduler-item-upload-scheduler", "filename"),
    State("scheduler-item-upload-scheduler", "contents"),
    State("scheduler-item-options", "value"),
    State("app-sim-schematic", "data"),
    prevent_initial_call=True,
)
def save_scheduler_item(n_clicks,
                        m_clicks,
                        method, 
                        select_scheduler_value, 
                        upload_scheduler_value, 
                        upload_scheduler_contents, 
                        options, 
                        schematic_data):
    if not n_clicks and not any(m_clicks):
        raise PreventUpdate

    # Get the context of the callback
    triggered_id = callback_context.triggered_id
    print(triggered_id)

    modal_remains_open = True

    data = dict()
    data["method"] = method
    data["options"] = options
    if method == "Custom":
        try:
            dec_contents = parse_uploaded_scheduler_contents(upload_scheduler_contents)
            filename = tempfile.mktemp(suffix=".py", prefix=upload_scheduler_value)
            with open(filename, "w") as fd:
                fd.write(dec_contents)
            data["value"] = filename
            # TODO: automatic load schedulers that are created inside the schedulers' directory
            data["name"] = upload_scheduler_value
        except:
            if triggered_id != "scheduler-item-save-btn":
                index = triggered_id["index"]
                data["value"] = schematic_data["schedulers"][f"scheduler-{index}"]["value"]
                data["name"] = schematic_data["schedulers"][f"scheduler-{index}"]["name"]
            else:
                raise PreventUpdate

    else:
        data["value"] = select_scheduler_value
        data["name"] = select_scheduler_value
    
    if triggered_id == "scheduler-item-save-btn":
    
        # Find the new scheduler's id based on the already existing ids
        stored_scheduler_ids = set(
            [int(keyval.split('-')[1]) for keyval in schematic_data["schedulers"].keys()]
        )
        max_val = -1
        if stored_scheduler_ids:
            max_val = max(stored_scheduler_ids)
            possible_scheduler_ids = set(range(0, max_val+1))
            diff = possible_scheduler_ids - stored_scheduler_ids
            # If there are unused ids inside the range of the current 0 and max then use them
            if diff:
                scheduler_id = diff.pop()
            else:
                scheduler_id = max_val + 1
        else:
            scheduler_id = max_val + 1

        
        schematic_data["schedulers"].update({f"scheduler-{scheduler_id}": data})
    
    else:

        index = triggered_id["index"]
        schematic_data["schedulers"][f"scheduler-{index}"] = data
        modal_remains_open = False
    
    return schematic_data, modal_remains_open

@callback(
    Output("app-sim-schematic", "data", allow_duplicate=True),
    Input({"delete-item": "scheduler", "index": ALL}, "n_clicks"),
    State("app-sim-schematic", "data"),
    prevent_initial_call=True,
)
def remove_scheduler_item(n_clicks, schematic_data):
    if not any(n_clicks):
        raise PreventUpdate
    
    triggered_id = callback_context.triggered_id
    index = triggered_id["index"]
    schematic_data["schedulers"].pop(f"scheduler-{index}")
    
    return schematic_data
    