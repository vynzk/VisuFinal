import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

# Leer datos
# (Nota: Asegúrate de tener el archivo 'Llamados2024.xlsx' en el mismo directorio)
data = pd.read_excel('Llamados2024.xlsx')

# Preparar datos
contacted_counts = data['contactadopor'].value_counts().reset_index()
contacted_counts.columns = ['contactadopor', 'count']
canceled_hours = data[data['estado'] == 'anulada']
finalized_hours = data[data['estado'] == 'finalizada']

# Inicializar app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Estilo CSS
app.index_string = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f7f7f7;
            margin: 0;
            padding: 0;
        }
        .container {
            display: flex;
            flex-direction: column;
            gap: 20px;
            padding: 20px;
        }
        .card {
            background-color: #ffffff;
            border: 1px solid #dddddd;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            padding: 20px;
            border-left: 6px solid #ff5722;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .card-content {
            display: flex;
            gap: 20px;
            align-items: flex-start;
        }
        .graph {
            flex: 2;
        }
        .controls {
            flex: 1;
        }
        .btn {
            background-color: #ff5722;
            color: white;
            border: none;
            padding: 10px 15px;
            cursor: pointer;
            border-radius: 4px;
        }
        .btn:hover {
            background-color: #e64a19;
        }
        .table {
            margin-top: 20px;
            display: none;
            border-collapse: collapse;
            width: 100%;
        }
        .table.show {
            display: table;
        }
        .table th, .table td {
            border: 1px solid #dddddd;
            padding: 8px;
            text-align: left;
        }
        .table th {
            background-color: #ff5722;
            color: white;
        }
        .table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <div id="app">{%app_entry%}</div>
    <footer>
        {%config%}
        {%scripts%}
    </footer>
</body>
</html>
"""

# Layout
app.layout = html.Div(className="container", children=[
    html.Div(className="card", children=[
        html.Div(className="card-header", children=[
            html.H3("Administrativos v/s Cantidad de Pacientes Contactados"),
            html.Button("Ver Datos", id="toggle-table-1", className="btn")
        ]),
        html.Div(className="card-content", children=[
            dcc.Graph(id='bar-graph', className="graph"),
            html.Div(className="controls", children=[
                dcc.Dropdown(
                    id='category-dropdown',
                    options=[
                        {'label': 'Sin filtro', 'value': 'all'},
                        {'label': 'Entre 0 a 4000', 'value': '0-4000'},
                        {'label': 'Entre 4001 a 8000', 'value': '4001-8000'},
                        {'label': 'Entre 8001 en adelante', 'value': '8001+'}
                    ],
                    value='all',
                    placeholder="Filtrar por Categoría"
                ),
                dcc.Dropdown(
                    id='admin-dropdown',
                    options=[{'label': admin, 'value': admin} for admin in contacted_counts['contactadopor']],
                    placeholder="Seleccionar Administrativo"
                )
            ])
        ]),
        html.Div(id="table-1", className="table", children=[
            html.Table([
                html.Thead(html.Tr([html.Th("Administrativo"), html.Th("Cantidad")])),
                html.Tbody([
                    html.Tr([html.Td(row['contactadopor']), html.Td(row['count'])]) for _, row in contacted_counts.iterrows()
                ])
            ])
        ])
    ]),


    html.Div(className="card", children=[
        html.Div(className="card-header", children=[
            html.H3("Médicos v/s Horas Anuladas"),
            html.Button("Ver Datos", id="toggle-table-1", className="btn")
        ]),
        html.Div(className="card-content", children=[
            dcc.Graph(id='canceled-hours-pie', className="graph"),
            html.Div(className="controls", children=[
                dcc.Dropdown(
                    id='medico-dropdown',
                    options=[{'label': 'Todos', 'value': 'all'}] + [{'label': medico, 'value': medico} for medico in canceled_hours_counts['Medico']],
                    value='all',
                    placeholder="Seleccionar Médico"
                ),
                dcc.Dropdown(
                    id='dado-por-dropdown',
                    options=[
                        {'label': 'Web', 'value': 'Web'},
                        {'label': 'Médico', 'value': 'MEDICO'},
                        {'label': 'Administrativo', 'value': 'ADMINISTRATIVO'}
                    ],
                    placeholder="Dado Por"
                ),
                dcc.Dropdown(
                    id='mes-dropdown',
                    options=[{'label': mes, 'value': mes} for mes in data['fecha'].dt.strftime('%Y-%m').unique()],
                    placeholder="Seleccionar Mes"
                )
            ])
        ]),
        html.Div(id="table-1", className="table", children=[
            html.Table([
                html.Thead(html.Tr([html.Th("Médico"), html.Th("Dado Por"), html.Th("Mes")])),
                html.Tbody([
                    html.Tr([html.Td(row['Medico']), html.Td(row['Dado Por']), html.Td(row['Mes'])]) for _, row in canceled_hours_counts.iterrows()
                ])
            ])
        ])
    ])
])




    html.Div(className="card", children=[
        html.Div(className="card-header", children=[
            html.H3("Cantidad de Horas Finalizadas"),
            html.Button("Ver Datos", id="toggle-table-3", className="btn")
        ]),
        html.Div(className="card-content", children=[
            dcc.Graph(
                id='finalized-graph',
                className="graph"
            )
        ])
    ])
])

@app.callback(
    Output('bar-graph', 'figure'),
    [Input('category-dropdown', 'value'),
     Input('admin-dropdown', 'value')]
)
def update_admin_graph(selected_category, selected_admin):
    if selected_category == '0-4000':
        filtered_data = contacted_counts[contacted_counts['count'] <= 4000]
    elif selected_category == '4001-8000':
        filtered_data = contacted_counts[(contacted_counts['count'] > 4000) & (contacted_counts['count'] <= 8000)]
    elif selected_category == '8001+':
        filtered_data = contacted_counts[contacted_counts['count'] > 8000]
    else:
        filtered_data = contacted_counts

    fig = px.bar(filtered_data, x='contactadopor', y='count', title='Cantidad de pacientes contactados')

    if selected_admin:
        selected_admin_data = contacted_counts[contacted_counts['contactadopor'] == selected_admin]
        if not selected_admin_data.empty:
            admin_count = selected_admin_data['count'].values[0]
            avg_count = contacted_counts['count'].mean()
            fig.add_trace(px.bar(x=[selected_admin, 'Promedio'], y=[admin_count, avg_count]).data[0])

    return fig

@app.callback(
    Output('canceled-graph', 'figure'),
    [Input('toggle-table-2', 'n_clicks')]
)
def update_canceled_graph(n_clicks):
    return px.histogram(canceled_hours, x='hora', title='Horas Anuladas')

@app.callback(
    Output('finalized-graph', 'figure'),
    [Input('toggle-table-3', 'n_clicks')]
)
def update_finalized_graph(n_clicks):
    return px.histogram(finalized_hours, x='hora', title='Horas Finalizadas')

@app.callback(
    Output('table-1', 'className'),
    [Input('toggle-table-1', 'n_clicks')],
    [State('table-1', 'className')]
)
def toggle_table_1(n_clicks, current_class):
    if n_clicks:
        return "table show" if "show" not in current_class else "table"
    return current_class

if __name__ == '__main__':
    app.run_server(debug=True)
