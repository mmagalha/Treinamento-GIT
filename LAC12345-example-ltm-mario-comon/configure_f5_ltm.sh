#!/bin/bash
# Script gerado automaticamente para configuração F5 LTM
# Configuração: example-ltm-mario
# LAC: LAC12345
# Descrição: Example configuration for LTM with virtual servers, pools, and nodes
# Data de geração: 2025-07-15 16:18:54

set -e  # Parar execução em caso de erro

# Variáveis
PARTITION="comon"
CONFIG_NAME="example-ltm-mario"

# Conectar ao F5
echo "Conectando ao F5: $F5_HOST"

# Criar partição
tmsh create auth partition comon || echo "Partição comon já existe"

# Criar Monitors
tmsh create ltm monitor http /comon/http \
  interval 30 \
  timeout 90 \
  send "GET / HTTP/1.1
Host: example.com

" \
  recv "HTTP/1.1 200 OK" || echo "Monitor http já existe"

# Criar Profiles
tmsh create ltm profile http /comon/http_profile \
  description "HTTP profile for web traffic" || echo "Profile http_profile já existe"

# Criar Nodes
tmsh create ltm node /comon/node1 \
  address 10.0.0.10 || echo "Node node1 já existe"

tmsh create ltm node /comon/node2 \
  address 10.0.0.11 || echo "Node node2 já existe"

# Criar Pools
tmsh create ltm pool /comon/web_pool \
  monitor /comon/http || echo "Pool web_pool já existe"

# Adicionar membros ao pool web_pool
tmsh modify ltm pool /comon/web_pool \
  members add { 10.0.0.10:80 } || echo "Membro 10.0.0.10:80 já existe no pool web_pool"

tmsh modify ltm pool /comon/web_pool \
  members add { 10.0.0.11:80 } || echo "Membro 10.0.0.11:80 já existe no pool web_pool"

# Criar Virtual Servers
tmsh create ltm virtual /comon/vs_web_80 \
  destination 192.168.1.100:80 \
  mask 255.255.255.255 \
  ip-protocol tcp \
  pool /comon/web_pool \
  profiles add { tcp } || echo "Virtual Server vs_web_80 já existe"

# Salvar configuração
tmsh save sys config

echo "Configuração F5 LTM aplicada com sucesso!"
echo "Configuração: example-ltm-mario"
echo "Partição: comon"
echo "LAC: LAC12345"