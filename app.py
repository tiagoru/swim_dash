import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dtaidistance import dtw

# Load Dataset
df = pd.read_csv("df_swim_paris.csv")  # Ensure the CSV is correctly loaded

# Extract unique heat numbers for dropdowns
heat_options = df["heat"].unique()

# Initialize Dash App
app = dash.Dash(__name__)

# Dashboard Layout
app.layout = html.Div([
    html.H1("Olympic Swimming Split Times Dashboard", style={'textAlign': 'center'}),

    # Dropdown to select Heat Number
    html.Label("Select Heat Number:"),
    dcc.Dropdown(
        id="heat-dropdown",
        options=[{"label": heat, "value": heat} for heat in heat_options],
        value=heat_options[0] if len(heat_options) > 0 else None,
        multi=False,
        style={'width': "50%"}
    ),

    # Graph to show pacing trends
    dcc.Graph(id="pacing-trend-graph"),

    # Heatmap of split times
    dcc.Graph(id="split-times-heatmap"),

    # Table to show total times of each swimmer
    html.H3("Total Times per Swimmer"),
    dcc.Graph(id="total-times-chart"),  # Horizontal bar chart

    html.Hr(),

    html.H2("Compare Swimmers Using Dynamic Time Warping (DTW)"),

    # Heat and Swimmer selection for DTW
    html.Label("Select Heat for Swimmer 1:"),
    dcc.Dropdown(id="heat1-dropdown", options=[{"label": heat, "value": heat} for heat in heat_options], style={'width': "50%"}),

    html.Label("Select Swimmer 1:"),
    dcc.Dropdown(id="swimmer1-dropdown", style={'width': "50%"}),

    html.Label("Select Heat for Swimmer 2:"),
    dcc.Dropdown(id="heat2-dropdown", options=[{"label": heat, "value": heat} for heat in heat_options], style={'width': "50%"}),

    html.Label("Select Swimmer 2:"),
    dcc.Dropdown(id="swimmer2-dropdown", style={'width': "50%"}),

    html.Button("Compare DTW", id="compare-dtw-button", n_clicks=0),

    # Display DTW Distance
    html.Div(id="dtw-output"),

    # Graph to show swimmer comparison
    dcc.Graph(id="dtw-comparison-graph")
])

# Callback to update pacing trend graph based on selected heat
@app.callback(
    Output("pacing-trend-graph", "figure"),
    Input("heat-dropdown", "value")
)
def update_pacing_trend(selected_heat):
    filtered_df = df[df["heat"] == selected_heat]

    fig = go.Figure()
    for _, row in filtered_df.iterrows():
        split_times = row.iloc[14:44]  # Ensure correct indexing for split times
        fig.add_trace(go.Scatter(x=split_times.index, y=split_times.values, mode='lines+markers', name=row["Athlete"]))

    fig.update_layout(title=f"Pacing Trends - {selected_heat}",
                      xaxis_title="Distance (m)", yaxis_title="Split Time (s)")
    return fig

# Callback to update heatmap of split times
@app.callback(
    Output("split-times-heatmap", "figure"),
    Input("heat-dropdown", "value")
)
def update_split_times_heatmap(selected_heat):
    filtered_df = df[df["heat"] == selected_heat]

    if filtered_df.empty:
        return go.Figure()  # Return empty figure if no data

    heatmap_data = filtered_df.iloc[:, 14:44]  # Extract split times
    swimmers = filtered_df["Athlete"].tolist()

    fig = px.imshow(
        heatmap_data.values,
        labels={"x": "Split Distance", "y": "Swimmers", "color": "Time (s)"},
        x=heatmap_data.columns,
        y=swimmers,
        color_continuous_scale="Blues"
    )

    fig.update_layout(title=f"Split Times Heatmap - {selected_heat}")
    return fig

# Callback to update total times per swimmer (now horizontal bar chart)
@app.callback(
    Output("total-times-chart", "figure"),
    Input("heat-dropdown", "value")
)
def update_total_times(selected_heat):
    filtered_df = df[df["heat"] == selected_heat]

    if filtered_df.empty:
        return go.Figure()  # Return empty figure if no data

    # Compute total time for each swimmer (sum of all split times)
    total_times = filtered_df.iloc[:, 14:44].sum(axis=1)
    swimmers = filtered_df["Athlete"]

    # Create horizontal bar chart
    fig = px.bar(
        y=swimmers, x=total_times,  # Reversed for horizontal bar chart
        labels={'y': 'Swimmer', 'x': 'Total Time (s)'},
        title=f"Total Times - {selected_heat}",
        orientation="h"
    )

    fig.update_layout(yaxis={'categoryorder': 'total ascending'})  # Sort by fastest time
    return fig

# Callback to update swimmer dropdowns based on selected heat
@app.callback(
    [Output("swimmer1-dropdown", "options"), Output("swimmer2-dropdown", "options")],
    [Input("heat1-dropdown", "value"), Input("heat2-dropdown", "value")]
)
def update_swimmer_options(heat1, heat2):
    filtered_df1 = df[df["heat"] == heat1] if heat1 else df
    filtered_df2 = df[df["heat"] == heat2] if heat2 else df

    swimmer1_options = [{"label": athlete, "value": athlete} for athlete in filtered_df1["Athlete"].unique()]
    swimmer2_options = [{"label": athlete, "value": athlete} for athlete in filtered_df2["Athlete"].unique()]

    return swimmer1_options, swimmer2_options

# Callback to compute and display DTW distance
@app.callback(
    [Output("dtw-output", "children"), Output("dtw-comparison-graph", "figure")],
    [Input("compare-dtw-button", "n_clicks")],
    [Input("swimmer1-dropdown", "value"), Input("swimmer2-dropdown", "value"),
     Input("heat1-dropdown", "value"), Input("heat2-dropdown", "value")]
)
def compute_dtw(n_clicks, swimmer1, swimmer2, heat1, heat2):
    if n_clicks > 0 and swimmer1 and swimmer2 and heat1 and heat2:
        filtered_df1 = df[(df["heat"] == heat1) & (df["Athlete"] == swimmer1)]
        filtered_df2 = df[(df["heat"] == heat2) & (df["Athlete"] == swimmer2)]
        
        if not filtered_df1.empty and not filtered_df2.empty:
            swimmer1_data = filtered_df1.iloc[:, 14:44].values.flatten()
            swimmer2_data = filtered_df2.iloc[:, 14:44].values.flatten()

            # Compute DTW distance
            dtw_distance = dtw.distance(swimmer1_data, swimmer2_data)

            # Create a comparison plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=filtered_df1.columns[14:44], y=swimmer1_data, mode='lines+markers', name=f"{swimmer1} - {heat1}"))
            fig.add_trace(go.Scatter(x=filtered_df2.columns[14:44], y=swimmer2_data, mode='lines+markers', name=f"{swimmer2} - {heat2}"))

            fig.update_layout(title=f"DTW Comparison: {swimmer1} ({heat1}) vs {swimmer2} ({heat2}) (DTW={dtw_distance:.2f})",
                              xaxis_title="Distance (m)", yaxis_title="Split Time (s)")

            return f"DTW Distance: {dtw_distance:.2f}", fig
    return "Select valid swimmers and heats", go.Figure()

# Run Server
if __name__ == '__main__':
    app.run_server(debug=True)
from dash import Dash

app = Dash(__name__)  # Create the Dash app
server = app.server  # Expose the Flask server for Gunicorn

if __name__ == "__main__":
    app.run_server(debug=True)
