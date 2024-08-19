import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
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

# Dicionário para armazenar o estado do modal para cada host
modal_states = {host: False for host in hosts}

# Função de ping
def ping(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    response = subprocess.run(command, stdout=subprocess.PIPE)
    
    if response.returncode == 0:
        output = response.stdout.decode("utf-8", errors='ignore')
        # Extrair o tempo de resposta do ping (em ms)
        match = re.search(r"tempo[=<]\s*(\d+\.?\d*)\s*ms", output)
        if match:
            return True, float(match.group(1))  # Retorna sucesso e tempo em ms   
    return False, None  # Se o ping falhar, retorna False e None

# Função para monitorar os hosts continuamente em segundo plano
def monitor_hosts():
    while True:
        for host in hosts:
            success, ping_time = ping(host)
            if success:
                results[host].append(ping_time)
                modal_states[host] = False  # Reseta o estado do modal se o ping voltar ao normal
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
                placeholder="Select IP's do you wanna see, sep by  \" \"",
                style={"width": "20vw","height": "2vw","margin":"0.5vw","align-self": "center"}
            ),
            dbc.Button("Submit", color="primary", id="submit-button", style={"height": "2vw","align-self": "center"}),
            dcc.Store(id='n-clicks-store'),  # Armazena o valor anterior de n_clicks
            html.Div(id='output-div', style={"align-self": "center","margin":"0.5vw"})
        ]
    ),
]

# Layout do modal, com persistência do header
modal_layout = dbc.Modal(
    id="modal",
    is_open=False,  # Modal começa fechado
    size="lg",  # Tamanho do modal
    centered=True,  # Modal centralizado na tela
    backdrop="static",  # Modal não fecha ao clicar fora dele
    children=[
        dbc.ModalHeader(id="modal-header", style={"font-size": "24px"}),  # Header persistente
        dbc.ModalBody(id="modal-body"),
        dbc.ModalFooter(
            dbc.Button("Close", id="close", className="ml-auto", n_clicks=0)
        ),
    ]
)

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

# Configure main app layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        html.Header([html.H3("Dashboard", className="text-center")],   
                    style={"marginBottom": "10px",
                           "marginTop": "10px"}), 

        dbc.Card(dbc.Row([dbc.Col(c) for c in controls]), body=True),

        html.Div(id='graphs-container'),  # Container onde os gráficos serão gerados
        dcc.Interval(id='interval', interval=1000, n_intervals=0),  # Intervalo para atualização dos gráficos

        modal_layout  # Adiciona o modal ao layout
    ]
)

@app.callback(
    Output('graphs-container', 'children'),
    Output('modal', 'is_open'),  # Controla a abertura e fechamento do modal
    Output('modal-header', 'children'),
    Output('modal-body', 'children'),
    [Input('submit-button', 'n_clicks'), Input('interval', 'n_intervals'), Input("close", "n_clicks")],
    [State('ips', 'value'), State('modal', 'is_open'), State('modal-body', 'children')]
)
def update_graphs(n_clicks, n_intervals, close_clicks, value, is_open, current_modal_body):
    if n_clicks is None and n_intervals is None:
        return [], is_open, "Urgent Warning", ""  # Define o header do modal ao iniciar

    # Usando regex para extrair todos os IPs
    if value:
        input_hosts = re.findall(r'\d+\.\d+\.\d+\.\d+', value)

        for host in input_hosts:
            if host not in hosts:
                hosts.append(host)  # Adiciona o IP à lista de hosts
                results[host] = []  # Inicializa a entrada no dicionário de resultados
                modal_states[host] = False  # Inicializa o estado do modal para o novo host

    figures = []
    modal_header = "Urgent Warning"  # Header persistente
    modal_body = current_modal_body if is_open else ""  # Mantém o corpo do modal se ele estiver aberto
    should_open_modal = is_open  # Mantém o estado atual do modal

    for host in results.keys():
        if results[host]:  # Garante que há dados para o host
            ping_data = [0 if val is not None else val for val in results[host]]
            shapes = []

            if any(value == None for value in ping_data):
                if not modal_states[host]:  # Só abre o modal se ele ainda não tiver sido mostrado para esse host
                    should_open_modal = True
                    modal_states[host] = True  # Marca o modal como mostrado para esse host
                    if modal_body:
                        modal_body += f"\nHost: {host} - One or more ping attempts have failed."
                    else:
                        modal_body = f"Host: {host} - One or more ping attempts have failed."

            # Adiciona uma linha vermelha em y=0 para cada valor de ping que é 0
            for i, value in enumerate(ping_data):
                if value == None:
                    shapes.append({
                        'type': 'line',
                        'x0': i - 0.5,
                        'x1': i + 0.5,
                        'y0': 0,
                        'y1': 0,
                        'line': {
                            'color': 'red',
                            'width': 2
                        }
                    })
            
            x_range = [max(0, len(ping_data) - 25), len(ping_data) - 1]
            
            figures.append(
                dbc.Col(
                    dcc.Graph(
                        id=f'ip-graph-{convert_ip_to_id(host)}',
                        figure=go.Figure(
                            data=[go.Scatter(x=list(range(len(results[host]))), y=results[host], mode='lines+markers')],
                            layout=go.Layout(
                                title={
                                    'text': f"Host: {host}",
                                    'font': {'size': 24},
                                    'x': 0.5,  
                                    'xanchor': 'center'
                                },
                                xaxis={
                                    'title': {'text': 'Ping Attempt'},
                                    'range': x_range,
                                    'showticklabels': False
                                }, 
                                yaxis_title="Time(ms)",
                                shapes=shapes 
                            )
                        )
                    ),
                    width=6
                )
            )

    # Lógica para abrir/fechar o modal
    ctx = dash.callback_context
    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == "close":
            should_open_modal = False  # Fecha o modal quando o botão Close for clicado

    return dbc.Row(figures), should_open_modal, modal_header, modal_body

if __name__ == "__main__":
    app.run_server(debug=True)
