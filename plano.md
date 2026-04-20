## Plan: Migrar Dashboard para Consumo Direto do Banco de Dados

Implementar uma arquitetura de API backend para que o dashboard consuma dados diretamente do PostgreSQL, seguindo melhores práticas de programação. O backend gerará resultados de consultas e o frontend os consumirá via requisições assíncronas.

**Steps**

1. **Configurar API Backend com Flask/FastAPI**  
   - Instalar e configurar Flask (ou FastAPI) no `main.py` para criar endpoints REST.  
   - Adicionar middleware para CORS, tratamento de erros e logging.  
   - Garantir uso de variáveis de ambiente para credenciais do DB (já implementado em `db_connection.py`).

2. **Criar Funções de Consulta ao Banco**  
   - Desenvolver módulo `queries.py` com funções para consultas específicas (ex.: métricas NPS, listagem de respostas, filtros por CSM/data).  
   - Implementar consultas otimizadas com índices sugeridos (CSM, nota_numerica, data_resposta).  
   - Adicionar paginação para grandes volumes de dados.

3. **Implementar Endpoints da API**  
   - `/api/nps/data`: Retorna dados completos (responseRecords e sentRecords) com filtros opcionais.  
   - `/api/nps/metrics`: Retorna cálculos agregados (NPS score, distribuições) pré-computados.  
   - `/api/nps/options`: Retorna opções de filtro (CSMs, classificações) para o frontend.  
   - Usar JSON como formato de resposta; incluir metadados (total de registros, timestamps).

4. **Atualizar Frontend para Consumo da API**  
   - Modificar `dashboard.js` para carregar dados via `fetch()` em vez de JSON embutido.  
   - Implementar loading states e tratamento de erros no frontend.  
   - Manter compatibilidade com filtros client-side, mas permitir fallback para API se necessário.

5. **Adicionar Segurança e Otimizações**  
   - Implementar rate limiting e validação de entrada nos endpoints.  
   - Adicionar cache (ex.: Redis) para consultas frequentes.  
   - Configurar logs estruturados para auditoria de acessos.

**Relevant files**
- `main.py` — Adicionar rotas Flask e lógica de API.  
- `queries.py` (novo) — Funções de consulta ao DB.  
- `dashboard.js` — Alterar carregamento de dados para API.  
- `db_connection.py` — Reutilizar conexão existente.  
- `requirements.txt` — Adicionar Flask e dependências de API.

**Verification**
1. Testar endpoints da API manualmente (ex.: curl) para validar respostas JSON.  
2. Executar dashboard localmente e verificar carregamento de dados via DevTools.  
3. Comparar métricas calculadas (backend vs. client-side) para consistência.  
4. Testar filtros e paginação com dados reais do DB.  
5. Verificar performance com queries grandes (usar profiling do DB).

**Decisions**
- Framework: Usar Flask por compatibilidade com código existente (pandas já usado).  
- Autenticação: Não implementada inicialmente; assumir ambiente controlado.  
- Paginacao: Implementar para /api/nps/data com parâmetros limit/offset.  
- Cache: Opcional; priorizar otimização de queries primeiro.  
- Excluído: Migração completa para framework JS (React); manter vanilla JS para simplicidade.

**Further Considerations**
1. Volume de dados: Se >10k registros, considerar lazy loading no frontend.  
2. Atualizações em tempo real: Implementar WebSockets se necessário para dashboards dinâmicos.  
3. Testes: Adicionar testes unitários para funções de queries e endpoints.