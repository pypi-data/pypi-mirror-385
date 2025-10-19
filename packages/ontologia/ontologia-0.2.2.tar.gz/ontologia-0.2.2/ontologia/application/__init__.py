"""
ontologia.application
---------------------
Application layer: serviços e casos de uso de alto nível.

Este módulo contém a lógica de aplicação que orquestra
os componentes do domínio para realizar tarefas complexas.
"""

from ontologia.application.sync_service import OntologySyncService, SyncMetrics

__all__ = ["OntologySyncService", "SyncMetrics"]
