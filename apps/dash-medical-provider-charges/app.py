from dash import Dash, dcc, html, dash_table, no_update, callback_context
import plotly.graph_objs as go
from dash.dependencies import State, Input, Output
from dash.exceptions import PreventUpdate

import pandas as pd
import numpy as np

# Load and prepare the shark attack data
file_path = 'data/Australian Shark-Incident Database Public Version.xlsx'
df_shark = pd.read_excel(file_path, index_col=0)



app = Dash(
    __name__,
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1, maximum-scale=1.0, user-scalable=no",
        }
    ],
)
app.title = "Australian Shark Incident Analysis"
server = app.server

app.config["suppress_callback_exceptions"] = True

def build_upper_left_panel():
    return html.Div(
        id="upper-left",
        className="two columns",
        children=[
            html.P(
                className="section-title",
                children="Choose filters to see shark incident data",
            ),
            html.Div(
                className="control-row-1",
                children=[
                    html.Div(
                        id="state-select-outer",
                        children=[
                            html.Label("Select a State"),
                            dcc.Dropdown(
                                id="state-select",
                                options=[{"label": i, "value": i} for i in df_shark['State'].unique()],
                                value=df_shark['State'].unique()[0],
                            ),
                        ],
                    ),
                    html.Div(
                        id="select-metric-outer",
                        children=[
                            html.Label("Choose a Metric"),
                            dcc.Dropdown(
                                id="metric-select",
                                options=[
                                    {"label": "Victim Age", "value": "Victim.age"},
                                    {"label": "Shark Length", "value": "Shark.length.m"},
                                ],
                                value="Victim.age",
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                id="region-select-outer",
                className="control-row-2",
                children=[
                    html.Label("Pick a Region"),
                    html.Div(
                        id="checklist-container",
                        children=dcc.Checklist(
                            id="region-select-all",
                            options=[{"label": "Select All Regions", "value": "All"}],
                            value=[],
                        ),
                    ),
                    html.Div(
                        id="region-select-dropdown-outer",
                        children=dcc.Dropdown(
                            id="region-select", multi=True, searchable=True,
                        ),
                    ),
                ],
            ),
            html.Div(
                id="table-container",
                className="table-container",
                children=[
                    html.Div(
                        id="table-upper",
                        children=[
                            html.P("Incident Summary"),
                            dcc.Loading(children=html.Div(id="cost-stats-container")),
                        ],
                    ),
                    html.Div(
                        id="table-lower",
                        children=[
                            html.P("Detailed Incident Summary"),
                            dcc.Loading(
                                children=html.Div(id="procedure-stats-container")
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

def generate_procedure_plot(raw_data, cost_select, region_select, provider_select):
    # Filter data based on region
    procedure_data = raw_data[raw_data['State'].isin(region_select)].reset_index()

    traces = []
    selected_index = procedure_data[
        procedure_data['Location'].isin(provider_select)
    ].index

    text = (
        procedure_data['Location']
        + "<br>"
        + "<b>"
        + procedure_data['Shark.common.name'].map(str)
        + "/<b> <br>"
        + "Incident Year: "
        + procedure_data['Incident.year'].map(str)
    )

    provider_trace = go.Box(
        y=procedure_data['Shark.common.name'],
        x=procedure_data[cost_select],
        name="",
        customdata=procedure_data['Location'],
        boxpoints="all",
        jitter=0,
        pointpos=0,
        hoveron="points",
        fillcolor="rgba(0,0,0,0)",
        line=dict(color="rgba(0,0,0,0)"),
        hoverinfo="text",
        hovertext=text,
        selectedpoints=selected_index,
        selected=dict(marker={"color": "#FFFF00", "size": 13}),
        unselected=dict(marker={"opacity": 0.2}),
        marker=dict(
            line=dict(width=1, color="#000000"),
            color="#21c7ef",
            opacity=0.7,
            symbol="square",
            size=12,
        ),
    )

    traces.append(provider_trace)

    layout = go.Layout(
        showlegend=False,
        hovermode="closest",
        dragmode="select",
        clickmode="event+select",
        xaxis=dict(
            zeroline=False,
            automargin=True,
            showticklabels=True,
            title=dict(text="Metric", font=dict(color="#737a8d")),
            linecolor="#737a8d",
            tickfont=dict(color="#737a8d"),
            type="log",
        ),
        yaxis=dict(
            automargin=True,
            showticklabels=True,
            tickfont=dict(color="#737a8d"),
            gridcolor="#171b26",
        ),
        plot_bgcolor="#171b26",
        paper_bgcolor="#171b26",
    )
    return {"data": traces, "layout": layout}

def create_parallel_coordinates():
    # Select numerical columns for parallel coordinates
    numerical_cols = ['Victim.age', 'Shark.length.m', 'Latitude', 'Longitude', 'Incident.year']
    
    dimensions = []    
    # Create dimensions for each numerical column

    numerical_cols_with = [
        # 'Victim.age', 
        # 'Shark.length.m', 
        'Latitude'
        'Longitude', 
        'Incident.year'
    ]
    for col in numerical_cols_with:
        print(col)
        print(type(df_shark[col]))
        print(df_shark[col])
        print(type(df_shark[col].iloc[0]))  # Use iloc to access by integer position
        print(df_shark[col].iloc[0])        # Print first value
        print(df_shark[col].values)         # Print all values as numpy array
        
        print(len(df_shark[col].values))
        # Convert to numeric, handling any non-numeric values
        numeric_series = pd.to_numeric(df_shark[col], errors='coerce')
        print(numeric_series.min(), numeric_series.max())
        
        
    for col in numerical_cols:
        dimensions.append(
            dict(
                range=[df_shark[col].min(), df_shark[col].max()],
                label=col.replace('.', ' '),
                values=df_shark[col],
                ticktext=None,
                tickvals=None
            )
        )
    
    # Add categorical dimension for Shark Species
    dimensions.append(
        dict(
            range=[0, len(df_shark['Shark.common.name'].unique())],
            ticktext=df_shark['Shark.common.name'].unique(),
            tickvals=list(range(len(df_shark['Shark.common.name'].unique()))),
            label='Shark Species',
            values=[list(df_shark['Shark.common.name'].unique()).index(x) for x in df_shark['Shark.common.name']]
        )
    )
    
    # Create parallel coordinates plot
    fig = go.Figure(data=
        go.Parcoords(
            line=dict(
                color=df_shark['Incident.year'],
                colorscale='Viridis'
            ),
            dimensions=dimensions,
        )
    )
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='#171b26',
        paper_bgcolor='#171b26',
        font=dict(color='#737a8d'),
        margin=dict(l=80, r=80, t=30, b=30),
    )
    
    return fig

# Add this to app layout in the lower container


# Define the layout
app.layout = html.Div(
    className="container scalable",
    children=[
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.H6("Australian Shark attack"),
                html.Img(src=app.get_asset_url("plotly_logo_white.png")),
            ],
        ),
        html.Div(
            id="upper-container",
            className="row",
            children=[
                build_upper_left_panel(),
                html.Div(
                    id="geo-map-outer",
                    className="six columns",
                    children=[
                        html.P(
                            id="map-title",
                            children="Shark Incidents in Australia",
                        ),
                        html.Div(
                            id="geo-map-loading-outer",
                            children=[
                                dcc.Loading(
                                    id="loading",
                                    children=dcc.Graph(
                                        id="geo-map",
                                        figure={
                                            "data": [],
                                            "layout": dict(
                                                plot_bgcolor="#171b26",
                                                paper_bgcolor="#171b26",
                                            ),
                                        },
                                    ),
                                )
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            id="lower-container",
            children=[
                dcc.Graph(
                    id="procedure-plot",
                    figure=generate_procedure_plot(
                        df_shark, 'Victim.age', df_shark['State'].unique(), []
                    ),
                )
            ],
        ),
        html.Div(
        className="container scalable",
        children=[
            # ... (previous layout elements) ...
            html.Div(
                id="lower-container",
                children=[
                    dcc.Graph(
                        id="procedure-plot",
                        figure=generate_procedure_plot(
                            df_shark, 'Victim.age', df_shark['State'].unique(), []
                        ),
                    ),
                    # Add parallel coordinates plot
                    html.Div(
                        className="twelve columns",
                        children=[
                            html.P(
                                className="section-title",
                                children="Parallel Coordinates View of Shark Incident Data",
                            ),
                            dcc.Graph(
                                id='parallel-coords-plot',
                                figure=create_parallel_coordinates()
                            )
                        ]
                    )
                ],
            ),
        ],
    )
],
)

@app.callback(
    [
        Output("region-select", "value"),
        Output("region-select", "options"),
        Output("map-title", "children"),
    ],
    [Input("region-select-all", "value"), Input("state-select", "value"),],
)
def update_region_dropdown(select_all, state_select):
    # Filter the data for the selected state
    state_raw_data = df_shark[df_shark['State'] == state_select]
    
    # Get unique regions
    regions = state_raw_data['Location'].unique() if not state_raw_data.empty else []
    latitude = state_raw_data['Latitude'].unique() if not state_raw_data.empty else []
    long = state_raw_data['Latitude'].unique() if not state_raw_data.empty else []


    
    # Create options for the dropdown
    options = [{"labelSSS": i, "value": i} for i in regions if i]

    # Debugging: Print the options to verify their structure
    print("Dropdown options:", options[0])

    ctx = callback_context
    if ctx.triggered[0]["prop_id"].split(".")[0] == "region-select-all":
        if select_all == ["All"]:
            value = [i["value"] for i in options]
        else:
            value = no_update
    else:
        value = regions[:4] if len(regions) >= 4 else regions

    return (
        value,
        options,
        "Shark Incidents in {}".format(state_select),
    )

@app.callback(
    Output("checklist-container", "children"),
    [Input("region-select", "value")],
    [State("region-select", "options"), State("region-select-all", "value")],
)
def update_checklist(selected, select_options, checked):
    if len(selected) < len(select_options) and len(checked) == 0:
        raise PreventUpdate()

    elif len(selected) < len(select_options) and len(checked) == 1:
        return dcc.Checklist(
            id="region-select-all",
            options=[{"label": "Select All Regions", "value": "All"}],
            value=[],
        )

    elif len(selected) == len(select_options) and len(checked) == 1:
        raise PreventUpdate()

    return dcc.Checklist(
        id="region-select-all",
        options=[{"label": "Select All Regions", "value": "All"}],
        value=["All"],
    )

@app.callback(
    Output("cost-stats-container", "children"),
    [
        Input("geo-map", "selectedData"),
        Input("procedure-plot", "selectedData"),
        Input("metric-select", "value"),
        Input("state-select", "value"),
    ],
)
def update_hospital_datatable(geo_select, procedure_select, cost_select, state_select):
    state_agg = df_shark[df_shark['State'] == state_select]
    # make table from geo-select
    geo_data_dict = {
        "Location": [],
        "Shark Species": [],
        "Incident Year": [],
        "Maximum Metric": [],
        "Minimum Metric": [],
    }

    ctx = callback_context
    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # make table from procedure-select
        if prop_id == "procedure-plot" and procedure_select is not None:
            for point in procedure_select["points"]:
                location = point["customdata"]
                dff = state_agg[state_agg["Location"] == location]

                if not dff.empty:
                    geo_data_dict["Location"].append(location)
                    shark_species = dff["Shark.common.name"].tolist()[0]
                    geo_data_dict["Shark Species"].append(shark_species)

                    year = dff["Incident.year"].tolist()[0]
                    geo_data_dict["Incident Year"].append(year)

                    geo_data_dict["Maximum Metric"].append(
                        dff[cost_select].max()
                    )
                    geo_data_dict["Minimum Metric"].append(
                        dff[cost_select].min()
                    )

        if prop_id == "geo-map" and geo_select is not None:
            for point in geo_select["points"]:
                location = point["customdata"][0]
                dff = state_agg[state_agg["Location"] == location]

                if not dff.empty:
                    geo_data_dict["Location"].append(location)
                    geo_data_dict["Shark Species"].append(dff["Shark.common.name"].tolist()[0])

                    year = dff["Incident.year"].tolist()[0]
                    geo_data_dict["Incident Year"].append(year)

                    geo_data_dict["Maximum Metric"].append(
                        dff[cost_select].max()
                    )
                    geo_data_dict["Minimum Metric"].append(
                        dff[cost_select].min()
                    )

        geo_data_df = pd.DataFrame(data=geo_data_dict)
        data = geo_data_df.to_dict("records")

    else:
        data = [{}]

    return dash_table.DataTable(
        id="cost-stats-table",
        columns=[{"name": i, "id": i} for i in geo_data_dict.keys()],
        data=data,
        filter_action="native",
        page_size=5,
        style_cell={"background-color": "#242a3b", "color": "#7b7d8d"},
        style_as_list_view=False,
        style_header={"background-color": "#1f2536", "padding": "0px 5px"},
    )

@app.callback(
    Output("procedure-stats-container", "children"),
    [
        Input("procedure-plot", "selectedData"),
        Input("geo-map", "selectedData"),
        Input("metric-select", "value"),
    ],
    [State("state-select", "value")],
)
def update_procedure_stats(procedure_select, geo_select, cost_select, state_select):
    procedure_dict = {
        "Shark Species": [],
        "Location": [],
        "Incident Year": [],
        "Metric Summary": [],
    }

    ctx = callback_context
    prop_id = ""
    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if prop_id == "procedure-plot" and procedure_select is not None:
        for point in procedure_select["points"]:
            procedure_dict["Shark Species"].append(point["y"])
            procedure_dict["Location"].append(point["customdata"])
            procedure_dict["Incident Year"].append(point["x"])
            procedure_dict["Metric Summary"].append(("${:,.2f}".format(point["x"])))

    # Display all procedures at selected location
    location_select = []

    if prop_id == "geo-map" and geo_select is not None:
        for point in geo_select["points"]:
            location = point["customdata"][0]
            location_select.append(location)

        state_raw_data = df_shark[df_shark['State'] == state_select]
        location_filtered = state_raw_data[
            state_raw_data["Location"].isin(location_select)
        ]

        for i in range(len(location_filtered)):
            procedure_dict["Shark Species"].append(
                location_filtered.iloc[i]["Shark.common.name"]
            )
            procedure_dict["Location"].append(
                location_filtered.iloc[i]["Location"]
            )
            procedure_dict["Incident Year"].append(
                location_filtered.iloc[i]["Incident.year"]
            )
            procedure_dict["Metric Summary"].append(
                "${:,.2f}".format(location_filtered.iloc[0][cost_select])
            )

    procedure_data_df = pd.DataFrame(data=procedure_dict)

    return dash_table.DataTable(
        id="procedure-stats-table",
        columns=[{"name": i, "id": i} for i in procedure_dict.keys()],
        data=procedure_data_df.to_dict("records"),
        filter_action="native",
        sort_action="native",
        style_cell={
            "textOverflow": "ellipsis",
            "background-color": "#242a3b",
            "color": "#7b7d8d",
        },
        sort_mode="multi",
        page_size=5,
        style_as_list_view=False,
        style_header={"background-color": "#1f2536", "padding": "2px 12px 0px 12px"},
    )

@app.callback(
    Output("geo-map", "figure"),
    [
        Input("metric-select", "value"),
        Input("region-select", "value"),
        Input("procedure-plot", "selectedData"),
        Input("state-select", "value"),
    ],
)
def update_geo_map(cost_select, region_select, procedure_select, state_select):
    # Ensure region_select is a list
    if region_select is None:
        region_select = []

    # Generate geo map from state-select, procedure-select
    state_agg_data = df_shark[df_shark['State'] == state_select]

    location_data = {"procedure": [], "location": []}
    if procedure_select is not None:
        for point in procedure_select["points"]:
            location_data["procedure"].append(point["y"])
            location_data["location"].append(point["customdata"])

    return generate_geo_map(state_agg_data, cost_select, region_select, location_data)

def generate_geo_map(geo_data, selected_metric, region_select, location_select):
    # Ensure region_select is a list
    if not isinstance(region_select, list):
        region_select = []

    filtered_data = geo_data[geo_data['Location'].isin(region_select)]

    colors = ["#21c7ef", "#76f2ff", "#ff6969", "#ff1717"]

    locations = []

    lat = filtered_data["Latitude"].tolist()
    lon = filtered_data["Longitude"].tolist()
    metric_mean = filtered_data[selected_metric].mean()
    regions = filtered_data["Location"].tolist()
    shark_species = filtered_data["Shark.common.name"].tolist()

    # Metric mapping from aggregated data

    metric_data = {}
    metric_data["min"] = filtered_data[selected_metric].min()
    metric_data["max"] = filtered_data[selected_metric].max()
    metric_data["mid"] = (metric_data["min"] + metric_data["max"]) / 2
    metric_data["low_mid"] = (
        metric_data["min"] + metric_data["mid"]
    ) / 2
    metric_data["high_mid"] = (
        metric_data["mid"] + metric_data["max"]
    ) / 2

    for i in range(len(lat)):
        val = metric_mean
        region = regions[i]
        species = shark_species[i]

        if val <= metric_data["low_mid"]:
            color = colors[0]
        elif metric_data["low_mid"] < val <= metric_data["mid"]:
            color = colors[1]
        elif metric_data["mid"] < val <= metric_data["high_mid"]:
            color = colors[2]
        else:
            color = colors[3]

        selected_index = []
        if region in location_select["location"]:
            selected_index = [0]

        location = go.Scattermapbox(
            lat=[lat[i]],
            lon=[lon[i]],
            mode="markers",
            marker=dict(
                color=color,
                showscale=True,
                colorscale=[
                    [0, "#21c7ef"],
                    [0.33, "#76f2ff"],
                    [0.66, "#ff6969"],
                    [1, "#ff1717"],
                ],
                cmin=metric_data["min"],
                cmax=metric_data["max"],
                size=10
                * (1 + (val + metric_data["min"]) / metric_data["mid"]),
                colorbar=dict(
                    x=0.9,
                    len=0.7,
                    title=dict(
                        text="Average Metric",
                        font={"color": "#737a8d", "family": "Open Sans"},
                    ),
                    titleside="top",
                    tickmode="array",
                    tickvals=[metric_data["min"], metric_data["max"]],
                    ticktext=[
                        "${:,.2f}".format(metric_data["min"]),
                        "${:,.2f}".format(metric_data["max"]),
                    ],
                    ticks="outside",
                    thickness=15,
                    tickfont={"family": "Open Sans", "color": "#737a8d"},
                ),
            ),
            opacity=0.8,
            selectedpoints=selected_index,
            selected=dict(marker={"color": "#ffff00"}),
            customdata=[(region, species)],
            hoverinfo="text",
            text=region
            + "<br>"
            + species
            + "<br>Average Metric:"
            + " ${:,.2f}".format(val),
        )
        locations.append(location)

    layout = go.Layout(
        margin=dict(l=10, r=10, t=20, b=10, pad=5),
        plot_bgcolor="#171b26",
        paper_bgcolor="#171b26",
        clickmode="event+select",
        hovermode="closest",
        showlegend=False,
        mapbox=go.layout.Mapbox(
            accesstoken="pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A",
            bearing=10,
            center=go.layout.mapbox.Center(
                lat=filtered_data.Latitude.mean(), lon=filtered_data.Longitude.mean()
            ),
            pitch=5,
            zoom=5,
            style="carto-darkmatter"
,
        ),
    )

    return {"data": locations, "layout": layout}

if __name__ == "__main__":
    app.run_server(debug=True)