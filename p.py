import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go

# Initialize the Dash app
app = dash.Dash(__name__)

# Set the coordinates for the center of the map
maldives_coordinates = [4.2083205, 73.4914555]

# Define the font size for the banner
banner_style = {'background-color': '#0C356A', 'color': 'white', 'text-align': 'left', 'padding': '22px', 'font-size': '24px', 'font-family': 'Arial, sans-serif'}

# Create a sidebar with a slider to select the CSV file
app.layout = html.Div([
    html.Div("Energy Eye", style=banner_style),
    dcc.Loading(
        dcc.Graph(
            id='heatmap-graph',
            config={'scrollZoom': True, 'displayModeBar': False},
            style={'width': '100%', 'height': '600px', 'display': 'block', 'margin': '1px auto 0 auto'},  # Center and stretch
        ),
        type="default"
    ),
    html.Div([
        dcc.Slider(
            id='csv-slider',
            min=1,
            max=12,
            step=1,
            value=1,
            marks={i: str(i) for i in range(1, 13)},
        ),
        dcc.Dropdown(
            id='parameter-dropdown',
            options=[
                {'label': 'Insolation', 'value': 'insolation'},
                {'label': 'Windspeed', 'value': 'windspeed'}
            ],
            value='insolation'
        ),
        html.Div(id='selected-coordinates', style={'padding': '10px'}),
        dcc.Graph(id='insolation-graph', style={'width': '50%', 'height': '450px', 'display': 'block', 'float': 'left'})
    ])
])

def generate_insolation_graph(selected_coordinates, selected_parameter):
    lat, lon = selected_coordinates['lat'], selected_coordinates['lon']
    parameter_changes = []

    for i in range(1, 13):
        csv_filename = f'temp{i}.csv'
        data = pd.read_csv(csv_filename)
        parameter = data[(data['latitude'] == lat) & (data['longitude'] == lon)][selected_parameter].values
        if len(parameter) > 0:
            parameter_changes.append(parameter[0])
        else:
            parameter_changes.append(None)

    return parameter_changes

@app.callback(
    [Output('selected-coordinates', 'children'),
     Output('insolation-graph', 'figure')],
    [Input('heatmap-graph', 'hoverData'),
     Input('parameter-dropdown', 'value')]  # Add this Input
)
def display_coordinates(hoverData, selected_parameter):
    if hoverData:
        lat = hoverData['points'][0]['lat']
        lon = hoverData['points'][0]['lon']
        z_value = hoverData['points'][0]['z']
        selected_coordinates = {'lat': lat, 'lon': lon, selected_parameter: z_value}  # Use selected_parameter

        parameter_changes = generate_insolation_graph(selected_coordinates, selected_parameter)

        parameter_graph = go.Figure(go.Scatter(x=list(range(1, 13)), y=parameter_changes, mode='lines+markers'))
        parameter_graph.update_layout(title=f'{selected_parameter.capitalize()} Change Over 12 Months',
                                       xaxis_title='Month', yaxis_title=selected_parameter.capitalize())

        return f'Selected Coordinates: Lat {lat}, Lon {lon}, {selected_parameter} {z_value}', parameter_graph

    return '', go.Figure()


@app.callback(
    Output('heatmap-graph', 'figure'),
    [Input('csv-slider', 'value'),
     Input('parameter-dropdown', 'value')]
)
def update_heatmap(selected_csv, selected_parameter):
    csv_filename = f'temp{selected_csv}.csv'
    data = pd.read_csv(csv_filename)
    
    heat_data = data[['latitude', 'longitude', selected_parameter]].values.tolist()

    figure = go.Figure(go.Densitymapbox(
        lat=[coord[0] for coord in heat_data],
        lon=[coord[1] for coord in heat_data],
        z=[coord[2] for coord in heat_data],
        radius=50,
        opacity=0.4,
        hoverinfo="lat+lon+z",
    ))
    figure.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": maldives_coordinates[0], "lon": maldives_coordinates[1]},
        mapbox_zoom=12,
    )

    return figure

if __name__ == '__main__':
    app.run_server(debug=True)

