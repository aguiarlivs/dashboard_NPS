import csv
from datetime import datetime
from pathlib import Path
from db_connection import get_connection

def export_nps_data(output_dir: str = None) -> str:
    """
    Exporta dados NPS do banco de dados para CSV.
    
    Args:
        output_dir: Diretório de saída. Se None, usa DASHBOARD/
    
    Returns:
        Caminho do arquivo criado
    """
    if output_dir is None:
        output_dir = str(Path(__file__).resolve().parent / "DASHBOARD")
    
    # Gerar timestamp para arquivo com data de hoje
    today = datetime.now().strftime("%Y%m%d")
    csv_filename = f"dados_{today}.csv"
    csv_path = Path(output_dir) / csv_filename
    
    query = """
    SELECT *
    FROM public.integracao_nps
    ORDER BY data_resposta DESC;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            colunas = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

    # Salvar em CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=colunas)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(zip(colunas, row)))

    print(f"✅ Dados NPS exportados: {csv_path}")
    return str(csv_path)


if __name__ == "__main__":
    export_nps_data()
