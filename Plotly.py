import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import subprocess
import platform
import threading
import time

# Lista de hosts para monitoramento
hosts = ["8.8.8.8", "10.4.0.40", "10.4.0.13"]

# Dicionário para armazenar os resultados
results = {host: [] for host in hosts}

# Função de ping
def ping(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    response = subprocess.run(command, stdout=subprocess.PIPE)
    return response.returncode == 0

# Função para monitorar os hosts continuamente em segundo plano
def monitor_hosts():
    while True:
        for host in hosts:
            success = ping(host)
            results[host].append(success)
        time.sleep(2)

# Iniciar a thread de monitoramento 
thread = threading.Thread(target=monitor_hosts)
thread.daemon = True
thread.start()

# Iniciar a aplicação Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # A cada 1 segundo?
        n_intervals=0
    )
])

@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    data = []
    for host in hosts:
        data.append(go.Scatter(
            x=list(range(len(results[host]))),
            y=results[host],
            mode='lines+markers',
            name=host
        ))

    return {'data': data,
            'layout': go.Layout(xaxis=dict(range=[max(0, len(results[hosts[0]]) - 10), len(results[hosts[0]])]),
                                yaxis=dict(range=[-0.5, 1.5]))}

if __name__ == '__main__':
    app.run_server(debug=True, host='10.4.0.161', port=8050)
