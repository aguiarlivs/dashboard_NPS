# 📊 Rotina Diária de Atualização do Dashboard NPS

## 📋 Descrição

Sistema automático para atualizar o Dashboard NPS com dados mais recentes do banco de dados PostgreSQL, incluindo:
- ✅ Exportação automática de dados do banco
- ✅ Geração de novo HTML do dashboard
- ✅ Versionamento automático no GitHub

## 🚀 Como Usar

### Opção 1: Execução Manual (Sob Demanda)

Execute manualmente a rotina de atualização:

```bash
python3 daily_update.py
```

**O que faz:**
1. Exporta dados do banco para `DASHBOARD/dados_YYYYMMDD.csv`
2. Gera novo `DASHBOARD/index.html` com os dados
3. Faz commit e push automático no GitHub

### Opção 2: Agendamento Automático (Scheduler)

Para executar a rotina diariamente em um horário específico:

```bash
python3 scheduler_service.py
```

**Configuração:**
- Hora padrão: 08:00 (manhã)
- Local: `scheduler_service.py`, linha 56
- Para mudar: `scheduler = DashboardScheduler(hour=8, minute=0)`

**Exemplo - Alterar para 9:30 da manhã:**
```python
scheduler = DashboardScheduler(hour=9, minute=30)
```

### Opção 3: Agendamento via Cron (Linux/macOS)

Para executar automaticamente todos os dias às 8 da manhã:

```bash
# Editar crontab
crontab -e

# Adicionar esta linha (ajustar caminho conforme necessário):
0 8 * * * cd /Users/liviaaguiar/Desktop/DASH\ NPS && /usr/bin/python3 daily_update.py >> scheduler.log 2>&1
```

## 📁 Estrutura de Arquivos

```
DASH NPS/
├── daily_update.py          # Script de atualização manual
├── scheduler_service.py     # Serviço de agendamento automático
├── export_data.py           # Exporta dados do banco
├── db_connection.py         # Conexão com PostgreSQL
├── scheduler.log            # Log do scheduler
└── DASHBOARD/
    ├── main.py              # Gerador de HTML
    ├── dashboard.js         # Interatividade do dashboard
    ├── styles.css           # Estilos
    ├── index.html           # Dashboard (gerado)
    └── dados_YYYYMMDD.csv   # Dados exportados (versionados por data)
```

## 🔄 Fluxo de Atualização

```
┌─────────────────────┐
│  Rotina Iniciada    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 1. Exportar dados do banco          │
│    → dados_20260420.csv             │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 2. Gerar HTML do dashboard          │
│    → index.html (novo)              │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 3. Commit e Push no GitHub          │
│    → "🔄 Atualização automática..." │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────┐
│   ✅ Concluído!     │
└─────────────────────┘
```

## 📊 Exemplo de Saída

```
======================================================================
🤖 INICIANDO ROTINA DIÁRIA DE ATUALIZAÇÃO DO DASHBOARD NPS
⏰ 20/04/2026 08:00:15
======================================================================

[1/3] EXPORTANDO DADOS DO BANCO
▶️  Exportando dados NPS...
✅ Exportando dados NPS... - OK

[2/3] GERANDO HTML DO DASHBOARD
▶️  Gerando dashboard HTML...
✅ Dashboard gerado com sucesso em: /Users/liviaaguiar/Desktop/DASH NPS/DASHBOARD/index.html

[3/3] ATUALIZANDO REPOSITÓRIO GIT
▶️  Adicionando arquivos modificados...
✅ Adicionando arquivos modificados... - OK

▶️  Criando commit: '🔄 Atualização automática do Dashboard NPS - 20/04/2026'...
✅ Criando commit... - OK

▶️  Enviando alterações para GitHub...
✅ Enviando alterações para GitHub... - OK

======================================================================
✅ ROTINA CONCLUÍDA COM SUCESSO!
📊 Dados exportados de: dados_20260420.csv
🌐 Dashboard gerado em: DASHBOARD/index.html
📝 Commit realizado em: main
======================================================================
```

## ⚙️ Instalação de Dependências

```bash
# Instalar dependências necessárias
pip install -r DASHBOARD/requirements.txt

# Ou manualmente:
pip install pandas psycopg python-dotenv apscheduler
```

## 🔐 Variáveis de Ambiente

Certifique-se de que o arquivo `.env` está configurado com:

```env
DB_HOST=seu_host
DB_PORT=5432
DB_NAME=seu_banco
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_SSLMODE=require
```

## 📝 Logs

- **Scheduler Log**: `scheduler.log` - Registro de execuções automáticas
- **Console Output**: Saída em tempo real durante execução manual

## 🐛 Troubleshooting

### Erro: "Arquivo CSV não encontrado"
```bash
# Rodar exportação manualmente primeiro
python3 export_data.py
```

### Erro: "Falha ao fazer push"
```bash
# Verificar status do git
cd "/Users/liviaaguiar/Desktop/DASH NPS"
git status
git log --oneline -5
```

### Scheduler não está executando
```bash
# Verificar logs
tail -f scheduler.log

# Testar execução manual
python3 daily_update.py
```

## 📌 Notas

- ✅ Cada execução cria um novo arquivo CSV com data (`dados_YYYYMMDD.csv`)
- ✅ O arquivo `index.html` é sempre sobrescrito com os dados mais recentes
- ✅ Todos os commits incluem timestamp automático
- ✅ O push é feito para a branch `main`

## 📞 Suporte

Para mais informações, consulte:
- [Documentação do Scheduler](/scheduler_service.py)
- [Script de Atualização](/daily_update.py)
- [Exportador de Dados](/export_data.py)
