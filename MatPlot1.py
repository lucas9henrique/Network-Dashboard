import subprocess
import platform
import matplotlib.pyplot as plt
import time

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

def display_results(results):
    plt.clf()  # Limpa a figura antes de desenhar novamente
    hosts = list(results.keys())
    status = [1 if results[host] else 0 for host in hosts]

    plt.barh(hosts, status, color=['green' if status[i] == 1 else 'red' for i in range(len(status))])
    plt.xlabel("Status")
    plt.ylabel("Hosts")
    plt.title("Monitoramento de Pings")
    plt.draw()  # Desenha o gráfico atualizado
    plt.pause(0.1)  # Pausa para permitir a atualização do gráfico

# Hosts a serem monitorados
hosts = ["8.8.8.8", "10.4.0.40", "10.4.0.13"] 
# Configuração do modo interativo
plt.ion()
fig = plt.figure(figsize=(10, 5))

# Loop para atualização contínua
while True:
    results = monitor_hosts(hosts)
    display_results(results)
    time.sleep(2)  # Atualiza a cada x segundos
