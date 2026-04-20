#!/usr/bin/env python3
"""
Script de automação diária para:
1. Exportar dados NPS do banco
2. Gerar novo HTML do dashboard
3. Fazer commit e push no GitHub
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Adicionar diretório raiz ao path para importar módulos
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from export_data import export_nps_data
from DASHBOARD.main import generate_dashboard


def run_command(command: list[str], description: str) -> bool:
    """Executa comando no shell e retorna sucesso/falha."""
    try:
        print(f"\n▶️  {description}...")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"✅ {description} - OK")
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ERRO")
        print(f"   {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ {description} - ERRO: {e}")
        return False


def main():
    """Executa o pipeline de atualização diária."""
    print("=" * 70)
    print("🤖 INICIANDO ROTINA DIÁRIA DE ATUALIZAÇÃO DO DASHBOARD NPS")
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # 1. Exportar dados do banco
        print("\n[1/3] EXPORTANDO DADOS DO BANCO")
        csv_path = export_nps_data()
        csv_filename = Path(csv_path).name
        
        # 2. Gerar novo HTML do dashboard
        print("\n[2/3] GERANDO HTML DO DASHBOARD")
        generate_dashboard(Path(csv_path))
        
        # 3. Fazer commit e push no GitHub
        print("\n[3/3] ATUALIZANDO REPOSITÓRIO GIT")
        
        # Mudar para o diretório do projeto
        os.chdir(PROJECT_ROOT)
        
        # Verificar status do git
        run_command(
            ["git", "status"],
            "Verificando status do repositório"
        )
        
        # Adicionar todas as mudanças
        run_command(
            ["git", "add", "-A"],
            "Adicionando arquivos modificados"
        )
        
        # Criar commit com mensagem automática
        today = datetime.now().strftime("%d/%m/%Y")
        commit_message = f"🔄 Atualização automática do Dashboard NPS - {today}"
        
        run_command(
            ["git", "commit", "-m", commit_message],
            f"Criando commit: '{commit_message}'"
        )
        
        # Fazer push para o repositório remoto
        run_command(
            ["git", "push", "origin", "main"],
            "Enviando alterações para GitHub"
        )
        
        print("\n" + "=" * 70)
        print("✅ ROTINA CONCLUÍDA COM SUCESSO!")
        print(f"📊 Dados exportados de: {csv_filename}")
        print(f"🌐 Dashboard gerado em: DASHBOARD/index.html")
        print(f"📝 Commit realizado em: main")
        print("=" * 70)
        
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ ERRO NA ROTINA: {e}")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    import os
    main()
