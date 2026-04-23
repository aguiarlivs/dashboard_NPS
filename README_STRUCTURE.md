# 🚀 Dashboard NPS - Estrutura Refatorada

## 📋 Visão Geral

Projeto de Dashboard NPS com separação completa entre código privado (BACKEND) e código público (FRONTEND/DASHBOARD), respeitando LGPD.

### ✅ Conformidade LGPD

- ✅ **Dados sensíveis em LOCAL** apenas (não vão para GitHub)
- ✅ **GitHub Pages publica apenas HTML/CSS/JS** (sem dados pessoais)
- ✅ **Arquivos CSV nunca são commitados** no repositório
- ✅ **Credenciais de banco em .env** (bloqueado no .gitignore)

---

## 📁 Estrutura do Projeto

```
DASH NPS/
│
├── 🔐 BACKEND/                    # Código privado (não vai para GitHub)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_connection.py       # Conexão PostgreSQL
│   │   └── export_nps.py          # Extração de dados do banco
│   │
│   ├── scripts/
│   │   ├── __init__.py
│   │   └── update_dashboard.py    # ⭐ CLI PRINCIPAL - Entry point
│   │
│   └── requirements.txt           # pandas, psycopg, python-dotenv
│
├── 🎨 FRONTEND/                   # Código público (compilado)
│   ├── __init__.py
│   ├── main.py                    # Gerador de HTML
│   ├── styles.css                 # Estilos
│   ├── dashboard.js               # Lógica JavaScript
│   ├── index.html                 # HTML gerado (intermediário)
│   └── requirements.txt           # pandas
│
├── 🌐 DASHBOARD/                  # GitHub Pages (cópia de FRONTEND/)
│   ├── index.html                 # HTML público ✅ commitado
│   ├── styles.css                 # CSS público ✅ commitado
│   └── dashboard.js               # JS público ✅ commitado
│
├── 🔒 DATA/                       # Dados sensíveis (nunca commitado)
│   └── nps_dados_20260423.csv     # ❌ não entra no Git
│
├── 📄 .env                        # Credenciais DB ❌ não entra no Git
├── .gitignore                     # Configuração de segurança
└── README.md                      # Esta documentação
```

---

## 🎯 Pipeline de Execução

### Fluxo Completo

```
$ python3 BACKEND/scripts/update_dashboard.py

┌─────────────────────────────────────────────────────────────┐
│ [1] EXPORTAR DADOS DO BANCO                                 │
│     └─ database/export_nps.py                               │
│        └─ Salva em: DATA/nps_dados_20260423.csv (🔒)       │
└─────────────────────────────────────────────────────────────┘
                             ⬇
┌─────────────────────────────────────────────────────────────┐
│ [2] COMPILAR DASHBOARD (FRONTEND)                          │
│     └─ FRONTEND/main.py                                     │
│        └─ Lê: DATA/nps_dados_20260423.csv                  │
│        └─ Gera: FRONTEND/index.html                        │
└─────────────────────────────────────────────────────────────┘
                             ⬇
┌─────────────────────────────────────────────────────────────┐
│ [3] COPIAR PARA GITHUB PAGES                               │
│     └─ scripts/update_dashboard.py                         │
│        └─ Copia: FRONTEND/* → DASHBOARD/*                 │
│           • index.html ✅ público
│           • styles.css ✅ público
│           • dashboard.js ✅ público
└─────────────────────────────────────────────────────────────┘
                             ⬇
┌─────────────────────────────────────────────────────────────┐
│ [4] PUBLICAR NO GITHUB                                      │
│     └─ git add DASHBOARD/ README.md                        │
│     └─ git commit -m "🔄 Atualização automática..."        │
│     └─ git push origin main                                │
│                                                             │
│     📦 GitHub Pages atualiza automaticamente                │
│     🌐 Dashboard publicado em:                              │
│        https://aguiarlivs.github.io/dashboard_NPS/        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Como Usar

### 1️⃣ Configuração Inicial

```bash
cd "/Users/liviaaguiar/Desktop/DASH NPS"

# Instalar dependências
pip install -r BACKEND/requirements.txt
pip install -r FRONTEND/requirements.txt

# Configurar .env (NÃO COMMITADO)
cat > .env << EOF
DB_HOST=seu_host
DB_PORT=5432
DB_NAME=seu_banco
DB_USER=seu_user
DB_PASSWORD=sua_senha
DB_SSLMODE=require
EOF
```

### 2️⃣ Execução Manual (CLI)

```bash
# Pipeline completo
python3 BACKEND/scripts/update_dashboard.py

# Apenas exportar dados
python3 BACKEND/scripts/update_dashboard.py --export-only

# Apenas compilar HTML
python3 BACKEND/scripts/update_dashboard.py --compile-only

# Apenas fazer push no GitHub
python3 BACKEND/scripts/update_dashboard.py --push-only

# Ver ajuda
python3 BACKEND/scripts/update_dashboard.py --help
```

### 3️⃣ Automatização Diária

```bash
# Reativar scheduler (se necessário)
cd "/Users/liviaaguiar/Desktop/DASH NPS"
nohup python3 scheduler_service.py > scheduler.log 2>&1 &

# Ver logs em tempo real
tail -f scheduler.log
```

---

## 🔐 Segurança (LGPD)

### ✅ O que É Seguro

- ✅ `DASHBOARD/index.html` - HTML público, sem dados pessoais
- ✅ `DASHBOARD/styles.css` - CSS público
- ✅ `DASHBOARD/dashboard.js` - JavaScript público
- ✅ `FRONTEND/main.py` - Código público do compilador

### ❌ O que NÃO Vai para GitHub

- ❌ `DATA/nps_dados_*.csv` - Contém dados de clientes (bloqueado no .gitignore)
- ❌ `.env` - Credenciais do banco (bloqueado no .gitignore)
- ❌ `BACKEND/` - Código de conexão ao banco (bloqueado no .gitignore)
- ❌ `*.env*` - Todos arquivos .env (bloqueado)

### 📋 Arquivo .gitignore

```
# Bloqueia dados sensíveis
DATA/
*.csv
BACKEND/

# Permite apenas DASHBOARD/ e FRONTEND/
# (sem commits de dados temporários)
```

---

## 📊 Arquivos Publicados no GitHub

**Apenas estes arquivos entram no repositório:**

```
aguiarlivs/dashboard_NPS
├── DASHBOARD/
│   ├── index.html         ✅ HTML do dashboard
│   ├── styles.css         ✅ Estilos CSS
│   └── dashboard.js       ✅ Lógica JavaScript
├── FRONTEND/              ✅ Código fonte do gerador
├── .gitignore             ✅ Configuração de segurança
└── README.md              ✅ Documentação
```

**Estes arquivos NÃO entram (.gitignore):**
- Nenhum arquivo CSV ou dados
- Nenhuma credencial de banco
- Nenhum código backend de conexão

---

## 🌐 Acessar Dashboard

```
👉 https://aguiarlivs.github.io/dashboard_NPS/
```

Atualiza automaticamente quando há novo commit em `DASHBOARD/index.html`

---

## 🛠️ Troubleshooting

### Problema: "CSV não encontrado em DATA/"

```bash
# Executar apenas exportação
python3 BACKEND/scripts/update_dashboard.py --export-only
```

### Problema: "Erro de conexão com banco"

```bash
# Verificar .env
cat .env

# Testar conexão manualmente
python3 -c "from BACKEND.database.db_connection import get_connection; print(get_connection())"
```

### Problema: "Arquivo styles.css/dashboard.js não encontrado"

```bash
# Verificar se FRONTEND/ tem os arquivos
ls -la FRONTEND/

# Reconsertar (copiar de DASHBOARD/ se necessário)
cp DASHBOARD/{styles.css,dashboard.js} FRONTEND/
```

---

## 📝 Próximos Passos

1. ✅ Testar pipeline completo
2. ✅ Validar dados em GitHub Pages
3. ✅ Ativar scheduler automático
4. ✅ Monitorar logs

---

**Última atualização:** 23/04/2026
**Status:** ✅ Pronto para produção
