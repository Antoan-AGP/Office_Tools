from flask import Flask, jsonify, request
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Create Flask app
app = Flask(__name__)

# A data structure to keep track of users' statuses by IP address.
user_statuses = {}
@app.route('/remove', methods=['POST'])
def remove_status():
    data = request.json
    name_to_remove = data['name']

    # Find the user's IP and remove their status
    ip_to_remove = None
    for ip, user_data in user_statuses.items():
        if user_data['name'] == name_to_remove:
            ip_to_remove = ip
            break

    if ip_to_remove:
        del user_statuses[ip_to_remove]
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "user not found"}), 404

def get_client_ip():
    """Extract client IP address from the request."""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        ip = request.environ.get('REMOTE_ADDR')
    return ip

@app.route('/update', methods=['POST'])
def update_status():
    data = request.json
    ip_address = get_client_ip()

    # Update the user's status by their IP address
    user_statuses[ip_address] = {
        "name": data['name'],
        "feeling": data['feeling']
    }

    return jsonify({"status": "success"}), 200
# Initialize Dash app with Flatly theme and custom font
dash_app = dash.Dash(
    __name__, 
    server=app, 
    url_base_pathname='/dashboard/',
    external_stylesheets=[dbc.themes.FLATLY]  # Use Flatly theme
)

# Dash layout with modern font and theme
dash_app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1('Office Temperature Dashboard', style={'font-family': 'Roboto, sans-serif'}))
    ]),

    # Pie chart to show statistics
    dbc.Row([
        dbc.Col(dcc.Graph(id='feeling-pie'))
    ]),

    # Details for individual users
    dbc.Row([
        dbc.Col(html.H2('User Details')),
        dbc.Col(html.Ul(id='user-list'))
    ]),

    # Update graph every 5 seconds
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # in milliseconds
        n_intervals=0
    )
], fluid=True)

@dash_app.callback(
    [Output('feeling-pie', 'figure'),
     Output('user-list', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    cold = len([v for v in user_statuses.values() if v['feeling'] == 'cold'])
    ok = len([v for v in user_statuses.values() if v['feeling'] == 'ok'])
    warm = len([v for v in user_statuses.values() if v['feeling'] == 'warm'])

    # Pie chart with fixed colors
    fig = go.Figure(data=[go.Pie(
        labels=['Cold', 'Ok', 'Warm'],
        values=[cold, ok, warm],
        marker=dict(colors=['#1f77b4', '#2ca02c', '#ff7f0e'])  # Blue, Green, Orange
    )])

    user_list_items = [html.Li(f'{data["name"]}: {data["feeling"]}') for data in user_statuses.values()]

    return fig, user_list_items


# Run Flask app with embedded Dash app
if __name__ == '__main__':
    app.run(host='localhost',port='1129',debug=True)
