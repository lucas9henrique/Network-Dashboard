import dash
from dash import dcc, html, Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Suponha que 'results' seja o dicionário contendo os tempos de ping para cada IP
results = {
    '8.8.8.8': [58.0, 58.0, 59.0, 59.0, 59.0, 58.0, 58.0,None,None,57.0, 57.0, 56.0],
    '1.1.1.1': [56.0, 57.0, 56.0, 57.0, 57.0, 56.0,None,None,57.0,57.0, 56.0,90,100,200],
    '1.1.1.2': [56.0, 57.0, 56.0, 57.0, 57.0, 56.0,None,None,57.0,57.0, 56.0,90,100,200]
}

# Função para converter IP em um ID válido (substituir '.' por '-')
def convert_ip_to_id(ip):
    return ip.replace('.', '-')

# Função para criar o layout dos gráficos dinamicamente
def generate_graphs_layout(results):
    hosts = list(results.keys())
    rows = []
    num_hosts = len(hosts)
    
    # Divida os gráficos em até 3 linhas e 2 colunas por linha
    for i in range(0, min(num_hosts, 6), 2):  # Itera de 2 em 2
        row = dbc.Row(
            [
                dbc.Col(dbc.Card(dcc.Graph(id=f'ip-graph-{convert_ip_to_id(hosts[i])}')), width=6),
                dbc.Col(dbc.Card(dcc.Graph(id=f'ip-graph-{convert_ip_to_id(hosts[i+1])}')), width=6) if i+1 < num_hosts else dbc.Col()
            ],
            className="g-0",
        )
        rows.append(row)
    
    return rows

# Layout inicial do app
app.layout = dbc.Container(
    fluid=True,
    children=[
        html.Header([html.H3("Dashboard", className="text-center")], style={"marginBottom": "10px", "marginTop": "10px"}),
        html.Div(id='graphs-container'),  # Container onde os gráficos serão gerados
        dcc.Interval(id='interval', interval=5000, n_intervals=0)  # Intervalo para atualização dos gráficos
    ]
)

# Callback para atualizar o layout dos gráficos dinamicamente
@app.callback(
    Output('graphs-container', 'children'),
    [Input('interval', 'n_intervals')]
)
def update_graphs(n_intervals):
    # Atualiza o layout dos gráficos com base no número de IPs em 'results'
    return generate_graphs_layout(results)

# Callback para atualizar os dados dos gráficos
@app.callback(
    [Output(f'ip-graph-{convert_ip_to_id(host)}', 'figure') for host in results.keys()],
    [Input('interval', 'n_intervals')]
)
def update_graph_data(n_intervals):
    figures = []
    for host in results.keys():
        # Criar o gráfico para cada host com base nos dados de 'results'
        figures.append(go.Figure(
            data=[go.Scatter(x=list(range(len(results[host]))), y=results[host], mode='lines+markers')],
            layout=go.Layout(title=f"Ping Times for IP: {host}", xaxis_title="Ping Attempt", yaxis_title="Time (ms)")
        ))
    return figures

if __name__ == "__main__":
    app.run_server(debug=True)
