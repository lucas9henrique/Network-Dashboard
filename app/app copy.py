import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import subprocess
import platform
import threading
import time
import re

# Lista de hosts para monitoramento
hosts = []

# Dicionário para armazenar os resultados
results = {host: [] for host in hosts}

# Função de pingdefping(host):
    param = "-n"if platform.system().lower() == "windows"else"-c"
    command = ["ping", param, "1", host]
    response = subprocess.run(command, stdout=subprocess.PIPE)
    
    if response.returncode == 0:
        output = response.stdout.decode("utf-8", errors='ignore')
        # Extrair o tempo de resposta do ping (em ms)match = re.search(r"tempo[=<]\s*(\d+\.?\d*)\s*ms", output)
        ifmatch:
            returnTrue, float(match.group(1))  # Retorna sucesso e tempo em ms   returnFalse, None# Se o ping falhar, retorna False e None# Função para monitorar os hosts continuamente em segundo planodefmonitor_hosts():
    whileTrue:
        for host in hosts:
            success, ping_time = ping(host)
            if success:
                results[host].append(ping_time)
            else:
                results[host].append(None)  # Armazena None se o ping falhar
        time.sleep(2)

# Iniciar a thread de monitoramento 
thread = threading.Thread(target=monitor_hosts)
thread.daemon = True
thread.start()

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

# IP controls
controls = [
    dbc.CardGroup(
        [
            dbc.Label("IP's:", style={"align-self": "center","font-size": "16px"}),
            dbc.Input(
                id="ips",
                value=None,
                type="text",
                placeholder="Enter IPs, separated by space",
                style={"width": "20vw","height": "2vw","margin":"0.5vw","align-self": "center"}
            ),
            dbc.Button("Submit", color="primary", id="submit-button",
                       style={"height": "2vw","align-self": "center"}),

            dcc.Store(id='n-clicks-store'),  # Armazena o valor anterior de n_clicks

            html.Div(id='output-div', style={"align-self": "center", "margin": "0.5vw"})

        ]
    ),
]

@app.callback(
    [Output('graphs-container', 'children'), Output('output-div', 'children')],
    [Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('ips', 'value')],
    prevent_initial_call=True)defupdate_output(n_clicks, value):
    if n_clicks isNone:
        return"", ""# Usando regex para extrair todos os IPs
    input_hosts = re.findall(r'\d+\.\d+\.\d+\.\d+', value)

    for host in input_hosts:
        if host notin hosts:
            hosts.append(host)  # Adiciona o IP à lista de hosts
            results[host] = []  # Inicializa a entrada no dicionário de resultados# Gera o layout dos gráficos dinamicamente
    graphs_layout = generate_graphs_layout(results)
    
    return graphs_layout, f"IP's on check: {', '.join(input_hosts)}"# Função para converter IP em um ID válido (substituir '.' por '-')defconvert_ip_to_id(ip):
    return ip.replace('.', '-')

# Função para criar o layout dos gráficos dinamicamentedefgenerate_graphs_layout(results):
    hosts = list(results.keys())
    rows = []
    num_hosts = len(hosts)
    
    # Divida os gráficos em até 3 linhas e 2 colunas por linhafor i inrange(0, min(num_hosts, 6), 2):  # Itera de 2 em 2
        row = dbc.Row(
            [
                dbc.Col(dbc.Card(dcc.Graph(id=f'ip-graph-{convert_ip_to_id(hosts[i])}')), width=6),
                dbc.Col(dbc.Card(dcc.Graph(id=f'ip-graph-{convert_ip_to_id(hosts[i+1])}')), width=6) if i+1 < num_hosts else dbc.Col()
            ],
            className="g-0",
        )
        rows.append(row)
    
    return rows

# Configure main app layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        html.Header([html.H3("Dashboard",className="text-center")],   
                    style={"marginBottom": "10px",
                           "marginTop": "10px"}), 

        dbc.Card(dbc.Row([dbc.Col(c) for c in controls]), body=True),

        html.Div(id='graphs-container'),  # Container onde os gráficos serão gerados
        dcc.Interval(id='interval', interval=5000, n_intervals=0)  # Intervalo para atualização dos gráficos
    ])

# Callback para atualizar os dados dos gráficos@app.callback(
    [Output(f'ip-graph-{convert_ip_to_id(host)}', 'figure') for host in results.keys()],
    [Input('interval', 'n_intervals')]
)defupdate_graph_data(n_intervals):
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
