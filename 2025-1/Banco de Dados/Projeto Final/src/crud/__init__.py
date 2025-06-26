"""
Módulo CRUD - Sistema DEC7588
Operações Create, Read, Update, Delete para todas as entidades
"""

from .base_crud import BaseCRUD
from .geografia_crud import RegiaosCRUD, EstadosCRUD, MunicipiosCRUD
from .organizacional_crud import OrgaosPublicosCRUD, FontesRecursosCRUD
from .financeiro_crud import CategoriasDespesasCRUD, PeriodosCRUD, OrcamentosCRUD, DespesasCRUD
from .indicadores_crud import IndicadoresIDHCRUD
from .sistema_crud import UsuariosCRUD, RelatoriosCRUD

__all__ = [
    'BaseCRUD',
    # Geografia
    'RegiaosCRUD',
    'EstadosCRUD', 
    'MunicipiosCRUD',
    # Organizacional
    'OrgaosPublicosCRUD',
    'FontesRecursosCRUD',
    # Financeiro
    'CategoriasDespesasCRUD',
    'PeriodosCRUD',
    'OrcamentosCRUD',
    'DespesasCRUD',
    # Indicadores
    'IndicadoresIDHCRUD',
    # Sistema
    'UsuariosCRUD',
    'RelatoriosCRUD',
] 