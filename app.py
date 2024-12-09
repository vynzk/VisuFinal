import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

data = pd.read_excel('Llamados2024.xlsx')

# Figuras ############################################

fig = px.scatter(data, x='prevision', y='estado')

######################################################

app = Dash(__name__)
app.layout = html.Div([
    html.H1("Mi Proyecto de Visualización"),
    dcc.Graph(figure=fig),
    dcc.Slider(min=0, max=100, step=1, value=50)
])

if __name__ == '__main__':
    app.run_server(debug=True)
