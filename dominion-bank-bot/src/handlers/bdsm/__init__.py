"""
The Phantom Bot - BDSM Command Handlers
"""
from src.handlers.bdsm.collars import (
    aceptar_collar_command,
    amo_command,
    collar_command,
    exhibir_command,
    liberar_command,
    rechazar_collar_command,
    suplicar_libertad_command,
)
from src.handlers.bdsm.punishments import (
    azotar_command,
    castigar_command,
    castigos_dados_command,
    mis_castigos_command,
)
from src.handlers.bdsm.dungeon import (
    calabozo_command,
    liberar_calabozo_command,
    mi_calabozo_command,
    presos_command,
    suplicar_libertad_calabozo_command,
)
from src.handlers.bdsm.auctions import (
    cancelar_subasta_command,
    mis_subastas_command,
    pujar_command,
    subasta_command,
    subastas_command,
    ver_subasta_command,
)
from src.handlers.bdsm.contracts import (
    contrato_command,
    firmar_contrato_command,
    mis_contratos_command,
    rechazar_contrato_command,
    romper_contrato_command,
    ver_contrato_command,
)
from src.handlers.bdsm.tribute import (
    adorar_command,
    altar_command,
    devotos_command,
    mi_altar_command,
    tributo_command,
)

__all__ = [
    # Collars
    "collar_command",
    "liberar_command",
    "exhibir_command",
    "amo_command",
    "aceptar_collar_command",
    "rechazar_collar_command",
    "suplicar_libertad_command",
    # Punishments
    "azotar_command",
    "castigar_command",
    "mis_castigos_command",
    "castigos_dados_command",
    # Dungeon
    "calabozo_command",
    "liberar_calabozo_command",
    "presos_command",
    "mi_calabozo_command",
    "suplicar_libertad_calabozo_command",
    # Auctions
    "subasta_command",
    "pujar_command",
    "subastas_command",
    "cancelar_subasta_command",
    "ver_subasta_command",
    "mis_subastas_command",
    # Contracts
    "contrato_command",
    "firmar_contrato_command",
    "rechazar_contrato_command",
    "mis_contratos_command",
    "romper_contrato_command",
    "ver_contrato_command",
    # Tribute
    "tributo_command",
    "adorar_command",
    "altar_command",
    "mi_altar_command",
    "devotos_command",
]
