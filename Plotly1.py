import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import subprocess
import platform
import threading
import time

# Dicionário para armazenar os resultados
results = {}

# Função de ping
def ping(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    response = subprocess.run(command, stdout=subprocess.PIPE)
    return response.returncode == 0

# Função para monitorar os hosts continuamente em segundo plano
def monitor_hosts(hosts):
    global results
    while True:
        for host in hosts:
            success = ping(host)
            if host in results:
                results[host].append(success)
        time.sleep(2)


# Tentar travar a aplicação até inserir os hosts
# Iniciar a aplicação Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Monitoramento de Ping em Tempo Real"),
    html.Div([
        html.Label("Digite os hosts para monitorar (separados por vírgulas):"),
        dcc.Input(id='input-hosts', type='text', value=""),
        html.Button(id='submit-button', n_clicks=0, children='Iniciar Monitoramento')
    ]),
    html.Div(id='graphs-container'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # A cada 1 segundo ?
        n_intervals=0
    )
])

@app.callback(
    Output('graphs-container', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('input-hosts', 'value')]
)
def update_hosts(n_clicks, input_value):
    global results
    if n_clicks > 0:
        hosts = [host.strip() for host in input_value.split(",")]
        results = {host: [] for host in hosts}
        
        # Iniciar a thread de monitoramento
        thread = threading.Thread(target=monitor_hosts, args=(hosts,))
        thread.daemon = True
        thread.start()

        # Gerar um gráfico para cada host 
        graphs = [] # Rever essa geração
        for host in hosts:
            graphs.append(dcc.Graph(id=f'graph-{host}'))

        return graphs
    return []

@app.callback(
    Output({'type': 'dynamic-graph', 'index': dash.dependencies.ALL}, 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph_live(n):
    figures = []
    for host in results.keys():
        data = go.Scatter(
            x=list(range(len(results[host]))),
            y=results[host],
            mode='lines+markers',
            name=host
        )
        figure = {
            'data': [data],
            'layout': go.Layout(
                xaxis=dict(range=[max(0, len(results[host]) - 10), len(results[host])]),
                yaxis=dict(range=[-0.5, 1.5]),
                title=f'Monitoramento de Ping - {host}'
            )
        }
        figures.append(figure)
    return figures

if __name__ == '__main__':
    app.run_server(debug=True)
