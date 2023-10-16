import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go

# Initialize the Dash app
app = dash.Dash(__name__)

# Set the coordinates for the center of the map
maldives_coordinates = [4.2083205, 73.4914555]

# Create a sidebar with a slider to select the CSV file
app.layout = html.Div([
    html.Div(className='header',
             children=[
                 html.Div(
                     html.Button('Solar', id='solar-button', n_clicks=0, className='button'),
                     style={'display': 'inline-block', 'margin': '0 10px', 'text-align': 'center'}
                 ),
                 html.Div(
                     html.Button('Wind', id='wind-button', n_clicks=0, className='button'),
                     style={'display': 'inline-block', 'margin': '0 10px', 'text-align': 'center'}
                 ),
                 html.Div(
                     html.Button('Current', id='current-button', n_clicks=0, className='button'),
                     style={'display': 'inline-block', 'margin': '0 10px', 'text-align': 'center'}
                 ),
             ]),
    html.Div(className='sidebar',
             children=[
                 dcc.Slider(
                     id='csv-slider',
                     min=1,
                     max=30,
                     step=1,
                     value=1,
                     marks={i: str(i) for i in range(1, 31)},
                 ),
                 dcc.Location(id='selected-area', refresh=False)  # Location component to store selected area
             ]),
    dcc.Graph(
        id='heatmap-graph',
        config={'scrollZoom': True},
        style={'width': '100%', 'height': '80vh'},  # Adjust map height
    ),
    dcc.Store(id='selected-coordinates', data=[]),  # Store clicked coordinates
    html.Div(id='coordinate-info', style={'text-align': 'center', 'font-size': '20px'}),  # Coordinate info
    dcc.Graph(id='line-chart'),  # Line chart
])

@app.callback(
    Output('selected-area', 'search'),
    Input('heatmap-graph', 'clickData'),
    State('selected-area', 'search'),
    prevent_initial_call=True
)
def update_selected_area_coordinates(click_data, current_search):
    if click_data:
        # Capture the clicked area coordinates
        return click_data
    return current_search

@app.callback(
    Output('heatmap-graph', 'figure'),
    Output('selected-coordinates', 'data'),
    Output('coordinate-info', 'children'),
    Input('csv-slider', 'value'),
    Input('solar-button', 'n_clicks'),
    Input('wind-button', 'n_clicks'),
    Input('current-button', 'n_clicks'),
    Input('selected-area', 'search'),
    State('heatmap-graph', 'figure'),
    State('selected-coordinates', 'data')
)
def update_heatmap(selected_csv, solar_clicks, wind_clicks, current_clicks, selected_area, heatmap_figure, current_coordinates):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    
    if 'solar-button' in changed_id:
        pass  # Handle Solar button click
    
    if 'wind-button' in changed_id:
        pass  # Handle Wind button click
    
    if 'current-button' in changed_id:
        pass  # Handle Current button click
    
    # Load temperature data from the selected CSV file
    csv_filename = f'temp{selected_csv}.csv'
    data = pd.read_csv(csv_filename)

    # Create a list of lists with latitude, longitude, and temperature
    heat_data = data[['latitude', 'longitude', 'temperature']].values.tolist()

    # Create a heatmap using Plotly with adjusted opacity
    figure = go.Figure(go.Densitymapbox(
        lat=[coord[0] for coord in heat_data],
        lon=[coord[1] for coord in heat_data],
        z=[coord[2] for coord in heat_data],
        radius=30,
        opacity=0.5  # Adjust opacity here (0.0 to 1.0)
    ))
    figure.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": maldives_coordinates[0], "lon": maldives_coordinates[1]},
        mapbox_zoom=12,
    )

    # Check if a location on the map is clicked
    if selected_area:
        coordinates = selected_area['points'][0]
        selected_latitude = coordinates['lat']
        selected_longitude = coordinates['lon']
        
        figure.add_trace(go.Scattermapbox(
            lat=[selected_latitude],
            lon=[selected_longitude],
            mode='markers',
            marker={'size': 10, 'color': 'red', 'symbol': 'cross'},
            name='Selected Point'
        ))
        
        coordinate_info = f"Selected Coordinate: Latitude {selected_latitude}, Longitude {selected_longitude}"
    else:
        coordinate_info = ""
        
    return figure, current_coordinates, coordinate_info

@app.callback(
    Output('line-chart', 'figure'),
    Input('csv-slider', 'value'),
)
def update_line_chart(selected_csv):
    # Load temperature data from the selected CSV file
    csv_filename = f'temp{selected_csv}.csv'
    data = pd.read_csv(csv_filename)

    # Create a line chart for temperature data
    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=data['day'],
        y=data['temperature'],
        mode='lines+markers',
    ))
    figure.update_layout(
        xaxis=dict(title='Days', range=[1, 30]),
        yaxis=dict(title='Temperature', range=[20, 40]),
        title="Temperature Trend Over 30 Days",
    )

    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
