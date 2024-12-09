import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

data = pd.read_excel('Llamados2024.xlsx')

# Filter data to get the count of patients contacted by each administrative
contacted_counts = data['contactadopor'].value_counts().reset_index()
contacted_counts.columns = ['contactadopor', 'count']
contacted_counts = contacted_counts.sort_values(by='count')


# Filter data to get the count of canceled hours by each doctor
canceled_hours = data[data['estado'] == 'anulada']
canceled_hours_counts = canceled_hours['Medico'].value_counts().reset_index()
canceled_hours_counts.columns = ['Medico', 'count']
canceled_hours_counts = canceled_hours_counts.sort_values(by='count')

avg_canceled_hours = canceled_hours_counts['count'].mean()

# Calculate the count of finalized hours by type of consultation
finalized_hours = data[data['estado'] == 'finalizada']
finalized_hours_counts = finalized_hours['tipoconsulta'].value_counts().reset_index()
finalized_hours_counts.columns = ['tipoconsulta', 'count']

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard"),
    html.Div([
        html.H2("Administrativos v/s Cantidad de pacientes contactados"),
        dcc.Dropdown(
            id='category-dropdown',
            options=[
                {'label': 'Sin filtro', 'value': 'all'},
                {'label': 'Entre 0 a 4000', 'value': '0-4000'},
                {'label': 'Entre 4001 a 8000', 'value': '4001-8000'},
                {'label': 'Entre 8001 en adelante', 'value': '8001+'}
            ],
            value='all'
        ),
        dcc.Dropdown(
            id='admin-dropdown',
            options=[{'label': admin, 'value': admin} for admin in contacted_counts['contactadopor']],
            placeholder="Select an administrative"
        ),
        dcc.Graph(id='bar-graph')
    ]),
    html.Div([
        html.H2("Médicos v/s Horas Anuladas"),
        dcc.Dropdown(
            id='medico-dropdown',
            options=[{'label': 'Todos', 'value': 'all'}] + [{'label': medico, 'value': medico} for medico in canceled_hours_counts['Medico']],
            value='all'
        ),
        dcc.Dropdown(
            id='dado-por-dropdown',
            options=[
                {'label': 'Web', 'value': 'Web'},
                {'label': 'Médico', 'value': 'MEDICO'},
                {'label': 'Administrativo', 'value': 'ADMINISTRATIVO'}
            ],
            placeholder="Select Dado Por"
        ),
        dcc.Dropdown(
            id='mes-dropdown',
            options=[{'label': mes, 'value': mes} for mes in data['fecha'].dt.strftime('%Y-%m').unique()],
            placeholder="Select a month"
        ),
        dcc.Graph(id='canceled-hours-graph')
    ]),
    html.Div([
        html.H2("Horas Finalizadas v/s Tipo Consulta"),
        dcc.Dropdown(
            id='tipo-consulta-dropdown',
            options=[{'label': tipo, 'value': tipo} for tipo in finalized_hours_counts['tipoconsulta']],
            placeholder="Select Tipo Consulta"
        ),
        dcc.Dropdown(
            id='mes-finalizada-dropdown',
            options=[{'label': mes, 'value': mes} for mes in data['fecha'].dt.strftime('%Y-%m').unique()],
            placeholder="Select a month"
        ),
        dcc.Graph(id='finalized-hours-graph')
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
        admin_count = contacted_counts[contacted_counts['contactadopor'] == selected_admin]['count'].values[0]
        avg_count = contacted_counts['count'].mean()
        fig.add_trace(px.bar(x=[selected_admin, 'Promedio'], y=[admin_count, avg_count], title='Comparación con el promedio').data[0])

    return fig

@app.callback(
    Output('canceled-hours-graph', 'figure'),
    [Input('medico-dropdown', 'value'),
     Input('dado-por-dropdown', 'value'),
     Input('mes-dropdown', 'value')]
)
def update_canceled_hours_graph(selected_medico, selected_dado_por, selected_mes):
    filtered_data = canceled_hours
    if selected_medico != 'all':
        filtered_data = filtered_data[filtered_data['Medico'] == selected_medico]
    if selected_dado_por:
        filtered_data = filtered_data[filtered_data['dadoporperfil'] == selected_dado_por]
    if selected_mes:
        filtered_data = filtered_data[filtered_data['fecha'].dt.strftime('%Y-%m') == selected_mes]

    canceled_hours_counts = filtered_data['Medico'].value_counts().reset_index()
    canceled_hours_counts.columns = ['Medico', 'count']
    canceled_hours_counts = canceled_hours_counts.sort_values(by='count')

    fig = px.bar(canceled_hours_counts, x='Medico', y='count', title='Horas Anuladas por Médico')

    return fig

@app.callback(
    Output('finalized-hours-graph', 'figure'),
    [Input('tipo-consulta-dropdown', 'value'),
     Input('mes-finalizada-dropdown', 'value')]
)
def update_finalized_hours_graph(selected_tipo_consulta, selected_mes):
    filtered_data = finalized_hours
    if selected_tipo_consulta:
        filtered_data = filtered_data[filtered_data['tipoconsulta'] == selected_tipo_consulta]
    if selected_mes:
        filtered_data = filtered_data[filtered_data['fecha'].dt.strftime('%Y-%m') == selected_mes]

    finalized_hours_counts = filtered_data['tipoconsulta'].value_counts().reset_index()
    finalized_hours_counts.columns = ['tipoconsulta', 'count']

    fig = px.bar(finalized_hours_counts, x='tipoconsulta', y='count', title='Horas Finalizadas por Tipo de Consulta')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)