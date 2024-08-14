import subprocess
import platform
import matplotlib.pyplot as plt
import time
import collections

def ping(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    response = subprocess.run(command, stdout=subprocess.PIPE)
    return response.returncode == 0

def monitor_hosts(hosts):
    results = {}
    for host in hosts:
        success = ping(host)
        results[host] = success
    return results

def display_results(history):
    plt.clf()  # Limpa a figura antes de desenhar novamente
    
    hosts = list(history[0].keys())
    num_cycles = len(history)
    
    for i, host in enumerate(hosts):
        host_history = [cycle[host] for cycle in history]
        status = [1 if success else 0 for success in host_history]

        plt.plot(range(num_cycles), status, label=host, marker='o')

    plt.ylim(-0.5, 1.5)
    plt.xlim(max(0, num_cycles-5), num_cycles-1)  # Mostrar apenas os últimos 5 ciclos
    plt.xlabel("Ciclos")
    plt.ylabel("Status")
    plt.title("Monitoramento de Pings - Últimos 5 Ciclos")
    plt.legend()
    plt.draw()  # Desenha o gráfico atualizado
    plt.pause(0.1)  # Pausa para permitir a atualização do gráfico

# Hosts a serem monitorados
hosts = ["8.8.8.8", "10.4.0.40", "10.4.0.13"]  

# Configuração do modo interativo
plt.ion()
fig = plt.figure(figsize=(10, 5))

# Histórico dos últimos 10 ciclos(deu errado)
history = collections.deque(maxlen=10)

# Loop para atualização contínua
while True:
    results = monitor_hosts(hosts)
    history.append(results)  # Armazena os resultados no histórico
    display_results(history)
    time.sleep(2)  # Atualiza a cada 2 segundos
