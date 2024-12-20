import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash.dash_table import DataTable

# Leer los datos desde el archivo
data = pd.read_excel('Llamados2024.xlsx')
data['fecha'] = pd.to_datetime(data['fecha'])

# Configurar los datos iniciales
contacted_counts = data['contactadopor'].value_counts().reset_index()
contacted_counts.columns = ['contactadopor', 'count']

canceled_hours = data[data['estado'] == 'anulada'].copy()
canceled_hours_counts = canceled_hours['Medico'].value_counts().reset_index()
canceled_hours_counts.columns = ['Medico', 'count']

canceled_hours.loc[:, 'count'] = 1

finalized_hours = data[data['estado'] == 'finalizada'].copy()
finalized_hours_counts = finalized_hours.groupby(['tipoconsulta'])['estado'].count().reset_index()
finalized_hours_counts.columns = ['tipoconsulta', 'count']

finalized_hours.loc[:, 'count'] = 1

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

app.layout = html.Div(style={'backgroundColor': colors['background'], 'fontFamily': 'Arial' }, children=[
    html.H1("Dashboard de Gestión", style={'color': colors['text'], 'textAlign': 'center'}),
    
    # ---------- Administrativos v/s Cantidad de pacientes contactados --------------------------

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
        dcc.Graph(id='bar-graph'),
        html.H3("Tabla de Datos Filtrados", style={'color': colors['secondary']}),
        DataTable(
            id='contacted-data-table',
            columns=[
                {"name": "Administrativo", "id": "contactadopor"},
                {"name": "Cantidad Contactada", "id": "count"}
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'fontFamily': 'Arial'},
            style_header={'backgroundColor': colors['primary'], 'color': 'white', 'fontWeight': 'bold'},
            page_size=10
        )
    ], style={'marginBottom': '50px'}),
    
    # ------------------ Médicos v/s Horas Anuladas --------------------------
    html.Div([
        html.H2("Médicos v/s Horas Anuladas", style={'color': colors['secondary']}),

        dcc.Dropdown(
            id='dado-por-dropdown',
            options=[
                {'label': 'Web', 'value': 'WEB'},
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
        dcc.Graph(id='canceled-hours-pie'),
        html.H3("Tabla de Datos Filtrados", style={'color': colors['secondary']}),
        DataTable(
            id='canceled-data-table',
            columns=[
                {"name": "Médico", "id": "Medico"},
                {"name": "Fecha", "id": "fecha"},
                {"name": "Dado Por", "id": "dadoporperfil"}
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'fontFamily': 'Arial'},
            style_header={'backgroundColor': colors['secondary'], 'color': 'white', 'fontWeight': 'bold'},
            page_size=10
        )
    ], style={'marginBottom': '50px'}),
    

    # ---------------------------- Horas Finalizadas v/s Tipo Consulta -----------------------
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
        dcc.Graph(id='finalized-hours-area'),
        html.H3("Tabla de Datos Filtrados", style={'color': colors['accent']}),
        DataTable(
            id='finalized-data-table',
            columns=[
                {"name": "Fecha", "id": "fecha"},
                {"name": "Tipo Consulta", "id": "tipoconsulta"},
                {"name": "Cantidad", "id": "count"}
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'fontFamily': 'Arial'},
            style_header={'backgroundColor': colors['accent'], 'color': 'white', 'fontWeight': 'bold'},
            page_size=10
        )
    ])
])


# ------------------------------------------- CallBacks -------------------------------------------


# Callback Tabla 1
@app.callback(
    Output('contacted-data-table', 'data'),
    [Input('category-dropdown', 'value'),
     Input('admin-dropdown', 'value')]
)
def update_contacted_table(selected_category, selected_admin):
    filtered_data = contacted_counts.copy()
    if selected_category == '0-4000':
        filtered_data = filtered_data[filtered_data['count'] <= 4000]
    elif selected_category == '4001-8000':
        filtered_data = filtered_data[(filtered_data['count'] > 4000) & (filtered_data['count'] <= 8000)]
    elif selected_category == '8001+':
        filtered_data = filtered_data[filtered_data['count'] > 8000]
    if selected_admin:
        filtered_data = filtered_data[filtered_data['contactadopor'] == selected_admin]
    return filtered_data.to_dict('records')


# Callbacks Grafico 1
@app.callback(
    Output('bar-graph', 'figure'),
    [Input('category-dropdown', 'value'),
     Input('admin-dropdown', 'value')]
)
def update_bar_graph(selected_category, selected_admin):
    # Filtrar los datos según el rango seleccionado
    if selected_category == '0-4000':
        filtered_data = contacted_counts[contacted_counts['count'] <= 4000]
    elif selected_category == '4001-8000':
        filtered_data = contacted_counts[(contacted_counts['count'] > 4000) & (contacted_counts['count'] <= 8000)]
    elif selected_category == '8001+':
        filtered_data = contacted_counts[contacted_counts['count'] > 8000]
    else:  # Caso de "Sin filtro"
        filtered_data = contacted_counts

    # Caso 1: Sin médico seleccionado
    if not selected_admin:
        graph_data = {
            'x': filtered_data['contactadopor'],
            'y': filtered_data['count'],
            'type': 'bar',
            'name': 'Cantidad por Médico'
        }
        title = "Cantidad de Pacientes Contactados por Administrativo"

    # Caso 2: Médico seleccionado
    else:
        # Calcular el promedio general
        avg_contacted = filtered_data['count'].mean() if not filtered_data.empty else 0

        # Obtener datos del médico seleccionado
        selected_admin_data = filtered_data[filtered_data['contactadopor'] == selected_admin]
        selected_admin_value = selected_admin_data['count'].sum() if not selected_admin_data.empty else 0

        graph_data = {
            'x': ['Promedio General', selected_admin],
            'y': [avg_contacted, selected_admin_value],
            'type': 'bar',
            'name': 'Comparación'
        }
        title = f"Comparación de {selected_admin} con el promedio"

    # Configurar la figura
    figure = {
        'data': [graph_data],
        'layout': {
            'title': title,
            'xaxis': {'title': 'Categoría'},
            'yaxis': {'title': 'Cantidad Contactada'},
            'barmode': 'group',
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {'color': colors['text']}
        }
    }
    return figure




# .------------------ Callback tabla 2 --------------------------

@app.callback(
    Output('canceled-data-table', 'data'),
    [
     Input('dado-por-dropdown', 'value'),
     Input('mes-dropdown', 'value')]
)
def update_canceled_table(selected_dado_por, selected_mes):
    filtered_data = canceled_hours.copy()
    if selected_dado_por:
        filtered_data = filtered_data[filtered_data['dadoporperfil'] == selected_dado_por]
    if selected_mes:
        filtered_data = filtered_data[filtered_data['fecha'].dt.strftime('%Y-%m') == selected_mes]
    return filtered_data[['Medico', 'fecha', 'dadoporperfil']].to_dict('records')




# ------------------ CallBack Grafico 2 -------------------------
@app.callback(
    Output('canceled-hours-pie', 'figure'),
    [
     Input('dado-por-dropdown', 'value'),
     Input('mes-dropdown', 'value')]
)
def update_canceled_hours_pie(selected_dado_por, selected_mes):
    filtered_data = canceled_hours.copy()
    if selected_dado_por:
        filtered_data = filtered_data[filtered_data['dadoporperfil'] == selected_dado_por]
    if selected_mes:
        filtered_data = filtered_data[filtered_data['fecha'].dt.strftime('%Y-%m') == selected_mes]
    
    c_canceled_hours = filtered_data.groupby('Medico')['count'].sum().reset_index()
    c_canceled_hours.columns = ['Medico', 'c_count']

    filtered_data = filtered_data.merge(c_canceled_hours, on='Medico', how='left')
    fig = px.pie(
        filtered_data, names='Medico', title='Proporción de Horas Anuladas',
        color_discrete_sequence=px.colors.sequential.RdBu,
        hover_data=['c_count'],
    )
    


    return fig



# ------------------- Callback Tabla 3 -----------------------------
@app.callback(
    Output('finalized-data-table', 'data'),
    [Input('tipo-consulta-dropdown', 'value'),
     Input('mes-finalizada-dropdown', 'value')]
)
def update_finalized_table(selected_tipo_consulta, selected_mes):
    filtered_data = finalized_hours.copy()
    if selected_tipo_consulta:
        filtered_data = filtered_data[filtered_data['tipoconsulta'] == selected_tipo_consulta]
    if selected_mes:
        filtered_data = filtered_data[filtered_data['fecha'].dt.strftime('%Y-%m') == selected_mes]
    return filtered_data[['fecha', 'tipoconsulta', 'count']].to_dict('records')


# ------------------- Callback grafico 3 -------------------------------
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

    # Agrupar por fecha y tipo de consulta y sumar los conteos
    aggregated_data = filtered_data.groupby(['fecha', 'tipoconsulta'])['count'].sum().reset_index()

    fig = go.Figure()
    for tipo in aggregated_data['tipoconsulta'].unique():
        tipo_data = aggregated_data[aggregated_data['tipoconsulta'] == tipo]
        fig.add_trace(go.Bar(
            x=tipo_data['fecha'],
            y=tipo_data['count'],
            name=tipo,
            customdata=tipo_data[['tipoconsulta']],
            hovertemplate='Tipo Consulta: %{customdata[0]}<br>Cantidad: %{y}<extra></extra>',
            
        ))
    fig.update_layout(
        title='Distribución de Horas Finalizadas por Fecha y Tipo de Consulta',
        yaxis_title='Cantidad de Horas',
        barmode='stack',
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    return fig




if __name__ == '__main__':
    app.run_server(debug=True)
