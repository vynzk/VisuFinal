import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# Leer los datos desde el archivo
data = pd.read_excel('Llamados2024.xlsx')
data['fecha'] = pd.to_datetime(data['fecha'])

# Configurar los datos iniciales
contacted_counts = data['contactadopor'].value_counts().reset_index()
contacted_counts.columns = ['contactadopor', 'count']

canceled_hours = data[data['estado'] == 'anulada']
canceled_hours_counts = canceled_hours['Medico'].value_counts().reset_index()
canceled_hours_counts.columns = ['Medico', 'count']

canceled_hours['count'] = 1

finalized_hours = data[data['estado'] == 'finalizada']
finalized_hours_counts = finalized_hours.groupby(['tipoconsulta'])['estado'].count().reset_index()
finalized_hours_counts.columns = ['tipoconsulta', 'count']

finalized_hours['count'] = 1

# Crear la app Dash
app = Dash(__name__)

# Paleta de colores moderna
colors = {
    'background': '#F9F9F9',
    'text': '#333333',
    'primary': '#2A9D8F',
    'secondary': '#E76F51',
    'accent': '#F4A261'
}

app.layout = html.Div(style={'backgroundColor': colors['background'], 'fontFamily': 'Arial'}, children=[
    html.H1("Dashboard de Gestión", style={'color': colors['text'], 'textAlign': 'center'}),
    
    # Administrativos v/s Cantidad de pacientes contactados
    html.Div([
        html.H2("Administrativos v/s Cantidad de Pacientes Contactados", style={'color': colors['primary']}),
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
            placeholder="Selecciona un Administrativo"
        ),
        dcc.Graph(id='bar-graph')
    ], style={'marginBottom': '50px'}),
    
    # Médicos v/s Horas Anuladas
    html.Div([
        html.H2("Médicos v/s Horas Anuladas", style={'color': colors['secondary']}),
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
            placeholder="Dado Por"
        ),
        dcc.Dropdown(
            id='mes-dropdown',
            options=[{'label': mes, 'value': mes} for mes in data['fecha'].dt.strftime('%Y-%m').unique()],
            placeholder="Selecciona un Mes"
        ),
        dcc.Graph(id='canceled-hours-pie')
    ], style={'marginBottom': '50px'}),
    
    # Horas Finalizadas v/s Tipo Consulta
    html.Div([
        html.H2("Horas Finalizadas v/s Tipo Consulta", style={'color': colors['accent']}),
        dcc.Dropdown(
            id='tipo-consulta-dropdown',
            options=[{'label': tipo, 'value': tipo} for tipo in finalized_hours_counts['tipoconsulta']],
            placeholder="Selecciona un Tipo de Consulta"
        ),
        dcc.Dropdown(
            id='mes-finalizada-dropdown',
            options=[{'label': mes, 'value': mes} for mes in data['fecha'].dt.strftime('%Y-%m').unique()],
            placeholder="Selecciona un Mes"
        ),
        dcc.Graph(id='finalized-hours-area')
    ])
])

# Callbacks para actualizar gráficos
@app.callback(
    Output('bar-graph', 'figure'),
    [Input('category-dropdown', 'value'),
     Input('admin-dropdown', 'value')]
)
def update_admin_graph(selected_category, selected_admin):
    filtered_data = contacted_counts.copy()
    if selected_category == '0-4000':
        filtered_data = filtered_data[filtered_data['count'] <= 4000]
    elif selected_category == '4001-8000':
        filtered_data = filtered_data[(filtered_data['count'] > 4000) & (filtered_data['count'] <= 8000)]
    elif selected_category == '8001+':
        filtered_data = filtered_data[filtered_data['count'] > 8000]

    fig = px.bar(
        filtered_data, x='count', y='contactadopor', orientation='h',
        title='Pacientes Contactados por Administrativo',
        color='count', color_continuous_scale='Blues'
    )

    if selected_admin:
        admin_data = contacted_counts[contacted_counts['contactadopor'] == selected_admin]
        if not admin_data.empty:
            fig.add_trace(
                go.Bar(
                    x=[admin_data.iloc[0]['count']], 
                    y=[selected_admin], 
                    marker_color='orange', name='Seleccionado'
                )
            )

    fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])
    return fig

@app.callback(
    Output('canceled-hours-pie', 'figure'),
    [Input('medico-dropdown', 'value'),
     Input('dado-por-dropdown', 'value'),
     Input('mes-dropdown', 'value')]
)
def update_canceled_hours_pie(selected_medico, selected_dado_por, selected_mes):
    filtered_data = canceled_hours.copy()
    if selected_medico != 'all':
        filtered_data = filtered_data[filtered_data['Medico'] == selected_medico]
    if selected_dado_por:
        filtered_data = filtered_data[filtered_data['dadoporperfil'] == selected_dado_por]
    if selected_mes:
        filtered_data = filtered_data[filtered_data['fecha'].dt.strftime('%Y-%m') == selected_mes]

    fig = px.pie(
        filtered_data, names='Medico', title='Proporción de Horas Anuladas',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    return fig

@app.callback(
    Output('finalized-hours-area', 'figure'),
    [Input('tipo-consulta-dropdown', 'value'),
     Input('mes-finalizada-dropdown', 'value')]
)
def update_finalized_hours_area(selected_tipo_consulta, selected_mes):
    filtered_data = finalized_hours.copy()
    if selected_tipo_consulta:
        filtered_data = filtered_data[filtered_data['tipoconsulta'] == selected_tipo_consulta]
    if selected_mes:
        filtered_data = filtered_data[filtered_data['fecha'].dt.strftime('%Y-%m') == selected_mes]

    fig = px.area(
        filtered_data, x='fecha', y='count', color='tipoconsulta',
        title='Horas Finalizadas por Tipo de Consulta',
        color_discrete_sequence=['#2A9D8F', '#E76F51']
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
