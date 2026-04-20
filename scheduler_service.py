#!/usr/bin/env python3
"""
Serviço de agendamento de tarefas (scheduler) para execução da rotina diária.
Usa APScheduler para executar o daily_update.py em um horário específico.
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from daily_update import main as daily_update_main

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_ROOT / "scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DashboardScheduler:
    """Gerenciador do agendador de tarefas para o Dashboard NPS."""
    
    def __init__(self, hour: int = 8, minute: int = 0):
        """
        Inicializa o scheduler.
        
        Args:
            hour: Hora do dia para executar (0-23). Padrão: 8 (8h da manhã)
            minute: Minuto da hora para executar (0-59). Padrão: 0
        """
        self.scheduler = BackgroundScheduler()
        self.hour = hour
        self.minute = minute
        self.job_id = "daily_nps_dashboard_update"
        
    def start(self):
        """Inicia o scheduler."""
        try:
            # Agendar tarefa diária
            trigger = CronTrigger(hour=self.hour, minute=self.minute)
            self.scheduler.add_job(
                daily_update_main,
                trigger=trigger,
                id=self.job_id,
                name="Atualização Diária do Dashboard NPS",
                replace_existing=True,
                misfire_grace_time=60,
                coalesce=True
            )
            
            self.scheduler.start()
            logger.info(f"✅ Scheduler iniciado - Execução diária às {self.hour:02d}:{self.minute:02d}")
            print(f"🚀 Scheduler em execução - Dashboard será atualizado todos os dias às {self.hour:02d}:{self.minute:02d}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar scheduler: {e}")
            raise
    
    def stop(self):
        """Para o scheduler."""
        try:
            self.scheduler.shutdown()
            logger.info("✅ Scheduler parado")
            print("⛔ Scheduler parado")
        except Exception as e:
            logger.error(f"❌ Erro ao parar scheduler: {e}")
    
    def get_status(self) -> dict:
        """Retorna informações sobre o status do scheduler."""
        jobs = self.scheduler.get_jobs()
        return {
            "is_running": self.scheduler.running,
            "next_run_time": jobs[0].next_run_time if jobs else None,
            "job_count": len(jobs)
        }


def main():
    """Ponto de entrada do serviço."""
    print("=" * 70)
    print("📅 SERVIÇO DE AGENDAMENTO - DASHBOARD NPS")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)
    
    # Criar e iniciar scheduler
    # Você pode ajustar a hora aqui (hora=8, minuto=0 = 8h da manhã)
    scheduler = DashboardScheduler(hour=8, minute=0)
    scheduler.start()
    
    try:
        # Manter o serviço rodando
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⛔ Encerrando scheduler...")
        scheduler.stop()
        print("✅ Scheduler encerrado com sucesso")


if __name__ == "__main__":
    main()
