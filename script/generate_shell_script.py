#!/usr/bin/env python3
"""
Script para gerar comandos shell (tmsh) baseado no arquivo ltm_config.yaml
para configurar o F5 LTM.
"""

import yaml
import os
from datetime import datetime

def load_config(config_file):
    """Carrega o arquivo de configuração YAML"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_shell_commands(config):
    """Gera os comandos shell baseado na configuração"""
    commands = []
    
    # Extrai variáveis do arquivo de configuração
    metadata = config.get('metadata', {})
    spec = config.get('spec', {})
    
    # Variáveis de metadados
    partition = metadata.get('partition', 'Common')
    config_name = metadata.get('name', 'default-config')
    lac = metadata.get('lac', '')
    description = metadata.get('description', '')

    output = f"{lac}-{config_name}-{partition}"
    
    # Cabeçalho do script
    commands.append("#!/bin/bash")
    commands.append(f"# Script gerado automaticamente para configuração F5 LTM")
    commands.append(f"# Configuração: {config_name}")
    commands.append(f"# LAC: {lac}")
    commands.append(f"# Descrição: {description}")
    commands.append(f"# Data de geração: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    commands.append("")
    commands.append("set -e  # Parar execução em caso de erro")
    commands.append("")
    
    # Variáveis
    commands.append("# Variáveis")
    commands.append(f'PARTITION="{partition}"')
    commands.append(f'CONFIG_NAME="{config_name}"')
    commands.append("")
    
    # Conectar ao F5 (assumindo que as variáveis de ambiente estão definidas)
    commands.append("# Conectar ao F5")
    commands.append('echo "Conectando ao F5: $F5_HOST"')
    commands.append("")
    
    # Criar partição se não for Common
    if partition != 'Common':
        commands.append("# Criar partição")
        commands.append(f'tmsh create auth partition {partition} || echo "Partição {partition} já existe"')
        commands.append("")
    
    # Processar monitors
    monitors = spec.get('monitors', [])
    if monitors:
        commands.append("# Criar Monitors")
        for monitor in monitors:
            monitor_name = monitor['name']
            monitor_type = monitor.get('type', 'HTTP').lower()
            interval = monitor.get('interval', 30)
            timeout = monitor.get('timeout', 90)
            send = monitor.get('send', 'GET / HTTP/1.1\\r\\nHost: example.com\\r\\n\\r\\n')
            receive = monitor.get('receive', 'HTTP/1.1 200 OK')
            
            if monitor_type == 'http':
                commands.append(f'tmsh create ltm monitor http /{partition}/{monitor_name} \\')
                commands.append(f'  interval {interval} \\')
                commands.append(f'  timeout {timeout} \\')
                commands.append(f'  send "{send}" \\')
                commands.append(f'  recv "{receive}" || echo "Monitor {monitor_name} já existe"')
                commands.append("")
            elif monitor_type == 'https':
                commands.append(f'tmsh create ltm monitor https /{partition}/{monitor_name} \\')
                commands.append(f'  interval {interval} \\')
                commands.append(f'  timeout {timeout} \\')
                commands.append(f'  send "{send}" \\')
                commands.append(f'  recv "{receive}" || echo "Monitor {monitor_name} já existe"')
                commands.append("")
            elif monitor_type == 'tcp':
                commands.append(f'tmsh create ltm monitor tcp /{partition}/{monitor_name} \\')
                commands.append(f'  interval {interval} \\')
                commands.append(f'  timeout {timeout} || echo "Monitor {monitor_name} já existe"')
                commands.append("")
    
    # Processar profiles
    profiles = spec.get('profiles', [])
    if profiles:
        commands.append("# Criar Profiles")
        for profile in profiles:
            profile_name = profile['name']
            profile_type = profile.get('type', 'HTTP').lower()
            profile_desc = profile.get('description', '')
            
            if profile_type == 'http':
                commands.append(f'tmsh create ltm profile http /{partition}/{profile_name} \\')
                if profile_desc:
                    commands.append(f'  description "{profile_desc}" || echo "Profile {profile_name} já existe"')
                else:
                    commands.append(f'  || echo "Profile {profile_name} já existe"')
                commands.append("")
            elif profile_type == 'tcp':
                commands.append(f'tmsh create ltm profile tcp /{partition}/{profile_name} \\')
                if profile_desc:
                    commands.append(f'  description "{profile_desc}" || echo "Profile {profile_name} já existe"')
                else:
                    commands.append(f'  || echo "Profile {profile_name} já existe"')
                commands.append("")
    
    # Processar nodes
    nodes = spec.get('nodes', [])
    if nodes:
        commands.append("# Criar Nodes")
        for node in nodes:
            node_name = node['name']
            node_address = node['address']
            
            commands.append(f'tmsh create ltm node /{partition}/{node_name} \\')
            commands.append(f'  address {node_address} || echo "Node {node_name} já existe"')
            commands.append("")
    
    # Processar pools
    pools = spec.get('pools', [])
    if pools:
        commands.append("# Criar Pools")
        for pool in pools:
            pool_name = pool['name']
            pool_monitor = pool.get('monitor', 'gateway_icmp')
            pool_members = pool.get('pool_members', [])
            
            # Criar pool
            commands.append(f'tmsh create ltm pool /{partition}/{pool_name} \\')
            commands.append(f'  monitor /{partition}/{pool_monitor} || echo "Pool {pool_name} já existe"')
            commands.append("")
            
            # Adicionar membros ao pool
            if pool_members:
                commands.append(f"# Adicionar membros ao pool {pool_name}")
                for member_name in pool_members:
                    # Encontrar o endereço do node correspondente
                    node_address = None
                    for node in nodes:
                        if node['name'] == member_name:
                            node_address = node['address']
                            break
                    
                    if node_address:
                        # Assumir porta 80 como padrão
                        commands.append(f'tmsh modify ltm pool /{partition}/{pool_name} \\')
                        commands.append(f'  members add {{ {node_address}:80 }} || echo "Membro {node_address}:80 já existe no pool {pool_name}"')
                        commands.append("")
                    else:
                        commands.append(f'echo "AVISO: Node {member_name} não encontrado para o pool {pool_name}"')
                        commands.append("")
    
    # Processar virtual servers
    virtual_servers = spec.get('virtual_servers', [])
    if virtual_servers:
        commands.append("# Criar Virtual Servers")
        for vs in virtual_servers:
            vs_name = vs['name']
            vs_destination = vs['destination']
            vs_port = vs['port']
            vs_pool = vs.get('pool', '')
            
            commands.append(f'tmsh create ltm virtual /{partition}/{vs_name} \\')
            commands.append(f'  destination {vs_destination}:{vs_port} \\')
            commands.append(f'  mask 255.255.255.255 \\')
            commands.append(f'  ip-protocol tcp \\')
            if vs_pool:
                commands.append(f'  pool /{partition}/{vs_pool} \\')
            commands.append(f'  profiles add {{ tcp }} || echo "Virtual Server {vs_name} já existe"')
            commands.append("")
    
    # Salvar configuração
    commands.append("# Salvar configuração")
    commands.append("tmsh save sys config")
    commands.append("")
    
    # Mensagem final
    commands.append('echo "Configuração F5 LTM aplicada com sucesso!"')
    commands.append(f'echo "Configuração: {config_name}"')
    commands.append(f'echo "Partição: {partition}"')
    if lac:
        commands.append(f'echo "LAC: {lac}"')
    
    return commands

def main():
    """Função principal"""
    config_file = "data/ltm_config.yaml"
    
    # Verificar se o arquivo de configuração existe
    if not os.path.exists(config_file):
        print(f"Erro: Arquivo de configuração {config_file} não encontrado!")
        return
    
    # Carregar configuração
    try:
        config = load_config(config_file)
        metadata = config.get('metadata', {})
        partition = metadata.get('partition', 'Common')
        config_name = metadata.get('name', 'default-config')
        lac = metadata.get('lac', '')
        output = f"{lac}-{config_name}-{partition}"
        output_file = f"{output}/configure_f5_ltm.sh"
        output_readme = f"{output}/README.md"
    except Exception as e:
        print(f"Erro ao carregar configuração: {e}")
        return    
    # Variáveis de metadados


    # Gerar comandos
    commands = generate_shell_commands(config)
    
    # Criar diretório de saída se não existir
    if os.path.exists(output):
        print(f"Erro: Configuração {output} já existe")
        return
    else: 
        os.makedirs(output, exist_ok=True)
    
    # Escrever script shell
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(commands))
        
        # Tornar o script executável
        os.chmod(output_file, 0o755)
        
    except Exception as e:
        print(f"Erro ao escrever arquivo de saída: {e}")

    try:
        with open(output_readme,'w', encoding='utf-8') as f:
            readme = f"""## Script shell gerado com sucesso:
            
{output_file}

---

Para executar:

```bash
$ chmod +x ./{output_file}"
$ ./{output_file}
```
Nota: Certifique-se de definir as variáveis de ambiente:"

```bash
export F5_HOST=<ip_do_f5>"
export F5_USER=<usuario>"
export F5_PASS=<senha>"
```    
            """    
            f.write(readme)
    except Exception as e:
        print(f"Erro ao escrever o README.md: {e}")            

if __name__ == "__main__":
    main()
