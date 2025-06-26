"""
Seed Data - Sistema DEC7588
Sistema para popular banco de dados com dados iniciais
"""

import sys
import os
import logging
from decimal import Decimal
from datetime import datetime
from typing import Dict

# Adicionar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.connection import get_database_connection
from src.crud import *

logger = logging.getLogger(__name__)

class SeedDataManager:
    """Gerenciador de dados iniciais do sistema"""
    
    def __init__(self):
        self.db_connection = get_database_connection()
        
        # Inicializar CRUDs
        self.regioes_crud = RegiaosCRUD()
        self.estados_crud = EstadosCRUD()
        self.orgaos_crud = OrgaosPublicosCRUD()
        self.fontes_crud = FontesRecursosCRUD()
        self.categorias_crud = CategoriasDespesasCRUD()
        self.periodos_crud = PeriodosCRUD()
        self.despesas_crud = DespesasCRUD()
        self.indicadores_crud = IndicadoresIDHCRUD()
        self.usuarios_crud = UsuariosCRUD()
        self.relatorios_crud = RelatoriosCRUD()
    
    def executar_seed_completo(self) -> bool:
        """Executa seed completo do sistema"""
        try:
            logger.info("🌱 Iniciando seed completo do sistema...")
            
            # Executar seeds em ordem
            steps = [
                ("Regiões", self._seed_regioes),
                ("Estados", self._seed_estados),
                ("Órgãos Públicos", self._seed_orgaos_publicos),
                ("Fontes de Recursos", self._seed_fontes_recursos),
                ("Categorias de Despesas", self._seed_categorias_despesas),
                ("Períodos", self._seed_periodos),
                ("Usuários", self._seed_usuarios),
                ("Dados IDH", self._seed_dados_idh),
                ("Dados Despesas", self._seed_dados_despesas),
                ("Relatórios", self._seed_relatorios)
            ]
            
            for step_name, step_func in steps:
                logger.info(f"📊 Processando: {step_name}")
                if not step_func():
                    logger.error(f"❌ Falha no seed: {step_name}")
                    return False
                logger.info(f"✅ Concluído: {step_name}")
            
            logger.info("🎉 Seed completo executado com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no seed completo: {e}")
            return False
    
    def _seed_regioes(self) -> bool:
        """Cria as 5 regiões do Brasil"""
        try:
            if self.regioes_crud.count() > 0:
                return True
                
            regioes_brasil = [
                {'nome_regiao': 'Norte', 'descricao': 'Região Norte do Brasil'},
                {'nome_regiao': 'Nordeste', 'descricao': 'Região Nordeste do Brasil'},
                {'nome_regiao': 'Sudeste', 'descricao': 'Região Sudeste do Brasil'},
                {'nome_regiao': 'Sul', 'descricao': 'Região Sul do Brasil'},
                {'nome_regiao': 'Centro-Oeste', 'descricao': 'Região Centro-Oeste do Brasil'}
            ]
            
            for regiao_data in regioes_brasil:
                self.regioes_crud.create(**regiao_data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar regiões: {e}")
            return False
    
    def _seed_estados(self) -> bool:
        """Cria todos os 27 estados + DF do Brasil"""
        try:
            # Verificar se já existem todos os estados (27)
            current_count = self.estados_crud.count()
            if current_count >= 27:
                print(f"✅ Estados já existem no banco: {current_count}")
                return True
                
            print(f"📊 Estados no banco: {current_count}/27 - criando restantes...")
                
            # Buscar regiões e criar mapeamento de nome para ID
            # Usar uma única sessão para evitar problemas de detached instances
            with self.db_connection.get_session() as session:
                from src.models.entities import Regiao
                regioes_query = session.query(Regiao).all()
                regioes = {r.nome_regiao: r.id for r in regioes_query}
                
                # Verificar se regiões existem
                if len(regioes) == 0:
                    print("⚠️ Criando regiões primeiro...")
                    self._seed_regioes()
                    regioes_query = session.query(Regiao).all()
                    regioes = {r.nome_regiao: r.id for r in regioes_query}
            
            estados_completos = [
                # REGIÃO NORTE (7 estados)
                {'nome_estado': 'Acre', 'sigla_uf': 'AC', 'regiao': 'Norte', 'capital': 'Rio Branco', 'populacao_estimada': 906876},
                {'nome_estado': 'Amapá', 'sigla_uf': 'AP', 'regiao': 'Norte', 'capital': 'Macapá', 'populacao_estimada': 877613},
                {'nome_estado': 'Amazonas', 'sigla_uf': 'AM', 'regiao': 'Norte', 'capital': 'Manaus', 'populacao_estimada': 4269995},
                {'nome_estado': 'Pará', 'sigla_uf': 'PA', 'regiao': 'Norte', 'capital': 'Belém', 'populacao_estimada': 8777124},
                {'nome_estado': 'Rondônia', 'sigla_uf': 'RO', 'regiao': 'Norte', 'capital': 'Porto Velho', 'populacao_estimada': 1815278},
                {'nome_estado': 'Roraima', 'sigla_uf': 'RR', 'regiao': 'Norte', 'capital': 'Boa Vista', 'populacao_estimada': 652713},
                {'nome_estado': 'Tocantins', 'sigla_uf': 'TO', 'regiao': 'Norte', 'capital': 'Palmas', 'populacao_estimada': 1607363},
                
                # REGIÃO NORDESTE (9 estados)
                {'nome_estado': 'Alagoas', 'sigla_uf': 'AL', 'regiao': 'Nordeste', 'capital': 'Maceió', 'populacao_estimada': 3365351},
                {'nome_estado': 'Bahia', 'sigla_uf': 'BA', 'regiao': 'Nordeste', 'capital': 'Salvador', 'populacao_estimada': 14985284},
                {'nome_estado': 'Ceará', 'sigla_uf': 'CE', 'regiao': 'Nordeste', 'capital': 'Fortaleza', 'populacao_estimada': 9240580},
                {'nome_estado': 'Maranhão', 'sigla_uf': 'MA', 'regiao': 'Nordeste', 'capital': 'São Luís', 'populacao_estimada': 7153262},
                {'nome_estado': 'Paraíba', 'sigla_uf': 'PB', 'regiao': 'Nordeste', 'capital': 'João Pessoa', 'populacao_estimada': 4059905},
                {'nome_estado': 'Pernambuco', 'sigla_uf': 'PE', 'regiao': 'Nordeste', 'capital': 'Recife', 'populacao_estimada': 9674793},
                {'nome_estado': 'Piauí', 'sigla_uf': 'PI', 'regiao': 'Nordeste', 'capital': 'Teresina', 'populacao_estimada': 3289290},
                {'nome_estado': 'Rio Grande do Norte', 'sigla_uf': 'RN', 'regiao': 'Nordeste', 'capital': 'Natal', 'populacao_estimada': 3560903},
                {'nome_estado': 'Sergipe', 'sigla_uf': 'SE', 'regiao': 'Nordeste', 'capital': 'Aracaju', 'populacao_estimada': 2338474},
                
                # REGIÃO SUDESTE (4 estados)
                {'nome_estado': 'Espírito Santo', 'sigla_uf': 'ES', 'regiao': 'Sudeste', 'capital': 'Vitória', 'populacao_estimada': 4108508},
                {'nome_estado': 'Minas Gerais', 'sigla_uf': 'MG', 'regiao': 'Sudeste', 'capital': 'Belo Horizonte', 'populacao_estimada': 21411923},
                {'nome_estado': 'Rio de Janeiro', 'sigla_uf': 'RJ', 'regiao': 'Sudeste', 'capital': 'Rio de Janeiro', 'populacao_estimada': 17463349},
                {'nome_estado': 'São Paulo', 'sigla_uf': 'SP', 'regiao': 'Sudeste', 'capital': 'São Paulo', 'populacao_estimada': 46649132},
                
                # REGIÃO SUL (3 estados)
                {'nome_estado': 'Paraná', 'sigla_uf': 'PR', 'regiao': 'Sul', 'capital': 'Curitiba', 'populacao_estimada': 11597484},
                {'nome_estado': 'Rio Grande do Sul', 'sigla_uf': 'RS', 'regiao': 'Sul', 'capital': 'Porto Alegre', 'populacao_estimada': 11466630},
                {'nome_estado': 'Santa Catarina', 'sigla_uf': 'SC', 'regiao': 'Sul', 'capital': 'Florianópolis', 'populacao_estimada': 7338473},
                
                # REGIÃO CENTRO-OESTE (3 estados + 1 DF)
                {'nome_estado': 'Distrito Federal', 'sigla_uf': 'DF', 'regiao': 'Centro-Oeste', 'capital': 'Brasília', 'populacao_estimada': 3094325},
                {'nome_estado': 'Goiás', 'sigla_uf': 'GO', 'regiao': 'Centro-Oeste', 'capital': 'Goiânia', 'populacao_estimada': 7206589},
                {'nome_estado': 'Mato Grosso', 'sigla_uf': 'MT', 'regiao': 'Centro-Oeste', 'capital': 'Cuiabá', 'populacao_estimada': 3567234},
                {'nome_estado': 'Mato Grosso do Sul', 'sigla_uf': 'MS', 'regiao': 'Centro-Oeste', 'capital': 'Campo Grande', 'populacao_estimada': 2839188}
            ]
            
            created_count = 0
            for estado_data in estados_completos:
                try:
                    # Verificar se estado já existe
                    existing = self.estados_crud.get_by_sigla(estado_data['sigla_uf'])
                    if existing:
                        continue
                        
                    regiao_nome = estado_data.pop('regiao')
                    estado_data['regiao_id'] = regioes[regiao_nome]
                    self.estados_crud.create(**estado_data)
                    created_count += 1
                    
                except Exception as e:
                    print(f"⚠️ Erro ao criar estado {estado_data.get('nome_estado', '?')}: {e}")
            
            print(f"✅ Estados criados: {created_count}, Total no banco: {self.estados_crud.count()}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar estados: {e}")
            return False
    
    def _seed_orgaos_publicos(self) -> bool:
        """Cria órgãos públicos principais"""
        try:
            if self.orgaos_crud.count() > 0:
                return True
                
            orgaos = [
                {'nome_orgao': 'Ministério da Educação', 'sigla_orgao': 'MEC', 'tipo_orgao': 'Federal'},
                {'nome_orgao': 'Ministério da Saúde', 'sigla_orgao': 'MS', 'tipo_orgao': 'Federal'},
                {'nome_orgao': 'Ministério da Fazenda', 'sigla_orgao': 'MF', 'tipo_orgao': 'Federal'},
                {'nome_orgao': 'Secretaria Estadual de Educação', 'sigla_orgao': 'SEE', 'tipo_orgao': 'Estadual'},
                {'nome_orgao': 'Secretaria Estadual de Saúde', 'sigla_orgao': 'SES', 'tipo_orgao': 'Estadual'}
            ]
            
            for orgao_data in orgaos:
                self.orgaos_crud.create(**orgao_data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar órgãos: {e}")
            return False
    
    def _seed_fontes_recursos(self) -> bool:
        """Cria fontes de recursos principais"""
        try:
            if self.fontes_crud.count() > 0:
                return True
                
            fontes = [
                {'nome_fonte': 'Tesouro Nacional', 'tipo_fonte': 'Tesouro Nacional', 'codigo_fonte': '100'},
                {'nome_fonte': 'Recursos Próprios', 'tipo_fonte': 'Receitas Próprias', 'codigo_fonte': '200'},
                {'nome_fonte': 'Transferências da União', 'tipo_fonte': 'Transferências', 'codigo_fonte': '300'}
            ]
            
            for fonte_data in fontes:
                self.fontes_crud.create(**fonte_data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar fontes: {e}")
            return False
    
    def _seed_categorias_despesas(self) -> bool:
        """Cria categorias de despesas"""
        try:
            if self.categorias_crud.count() > 0:
                return True
                
            categorias = [
                {'nome_categoria': 'Pessoal e Encargos Sociais', 'descricao': 'Despesas com pessoal e encargos sociais'},
                {'nome_categoria': 'Material de Consumo', 'descricao': 'Materiais de consumo e custeio'},
                {'nome_categoria': 'Equipamentos e Material Permanente', 'descricao': 'Investimentos em equipamentos e material permanente'},
                {'nome_categoria': 'Transferências a Municípios', 'descricao': 'Transferências de recursos para municípios'}
            ]
            
            for categoria_data in categorias:
                self.categorias_crud.create(**categoria_data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar categorias: {e}")
            return False
    
    def _seed_periodos(self) -> bool:
        """Cria períodos de 2019 a 2023"""
        try:
            if self.periodos_crud.count() >= 5:
                return True
                
            for ano in range(2019, 2024):
                # Verificar se já existe
                existing = self.periodos_crud.search({'ano': ano})
                if existing:
                    continue
                    
                self.periodos_crud.create(
                    ano=ano,
                    descricao=f'Ano fiscal {ano}'
                )
            
            print(f"✅ Períodos criados: {self.periodos_crud.count()} (2019-2023)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar períodos: {e}")
            return False
    
    def _seed_usuarios(self) -> bool:
        """Cria usuários iniciais"""
        try:
            if self.usuarios_crud.count() > 0:
                return True
                
            usuarios = [
                {
                    'nome_usuario': 'Administrador',
                    'email': 'admin@sistema.gov.br',
                    'senha': 'admin123',
                    'tipo_usuario': 'admin'
                },
                {
                    'nome_usuario': 'Analista',
                    'email': 'analista@sistema.gov.br',
                    'senha': 'analista123', 
                    'tipo_usuario': 'normal'
                }
            ]
            
            for usuario_data in usuarios:
                self.usuarios_crud.create(**usuario_data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar usuários: {e}")
            return False
    
    def _seed_dados_idh(self) -> bool:
        """Cria dados de IDH para todos os estados e anos (2019-2023)"""
        try:
            if self.indicadores_crud.count() >= 135:  # 27 estados x 5 anos
                return True
                
            # Buscar dados necessários usando sessão própria
            with self.db_connection.get_session() as session:
                from src.models.entities import Estado, Periodo
                
                estados_query = session.query(Estado).all()
                estados_data = [(e.id, e.nome_estado) for e in estados_query]
                
                periodos_query = session.query(Periodo).filter(
                    Periodo.ano.between(2019, 2023)
                ).all()
                periodos_data = [(p.id, p.ano) for p in periodos_query]
                
                if not periodos_data:
                    print("⚠️ Criando períodos primeiro...")
                    return False
            
            # Dados fictícios para demonstração
            import random
            random.seed(42)
            
            for periodo_id, ano in periodos_data:
                for i, (estado_id, estado_nome) in enumerate(estados_data):
                    # Verificar se já existe
                    existing = self.indicadores_crud.search({
                        'estado_id': estado_id,
                        'periodo_id': periodo_id
                    })
                    if existing:
                        continue
                    
                    # IDH base com variação por ano e estado
                    base_idh = random.uniform(0.550, 0.850)
                    # Tendência de melhoria ao longo dos anos
                    year_factor = 1 + (ano - 2019) * 0.01
                    idh_base = min(0.900, base_idh * year_factor)
                    
                    self.indicadores_crud.create(
                        estado_id=estado_id,
                        periodo_id=periodo_id,
                        idh_geral=round(idh_base, 3),
                        idh_educacao=round(idh_base * random.uniform(0.85, 0.95), 3),
                        idh_longevidade=round(idh_base * random.uniform(1.05, 1.15), 3),
                        idh_renda=round(idh_base * random.uniform(0.90, 1.00), 3),
                        ranking_nacional=i + 1
                    )
            
            print(f"✅ Dados IDH criados: {self.indicadores_crud.count()} registros")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar dados IDH: {e}")
            return False
    
    def _seed_dados_despesas(self) -> bool:
        """Cria dados de despesas para todos os anos (2019-2023) e estados"""
        try:
            if self.despesas_crud.count() >= 300:  # Limite mínimo de registros
                return True
                
            # Buscar dados necessários usando sessão própria
            with self.db_connection.get_session() as session:
                from src.models.entities import OrgaoPublico, FonteRecurso, CategoriaDespesa, Periodo, Estado
                
                orgaos_query = session.query(OrgaoPublico).all()
                orgaos_data = [(o.id, o.nome_orgao) for o in orgaos_query]
                
                fontes_query = session.query(FonteRecurso).all()
                fontes_data = [(f.id, f.nome_fonte) for f in fontes_query]
                
                categorias_query = session.query(CategoriaDespesa).all()
                categorias_data = [(c.id, c.nome_categoria) for c in categorias_query]
                
                periodos_query = session.query(Periodo).filter(
                    Periodo.ano.between(2019, 2023)
                ).all()
                periodos_data = [(p.id, p.ano) for p in periodos_query]
                
                estados_query = session.query(Estado).limit(10).all()  # Principais estados
                estados_data = [(e.id, e.nome_estado) for e in estados_query]
                
                if not periodos_data:
                    print("⚠️ Criando períodos primeiro...")
                    return False
            
            import random
            random.seed(42)
            
            for periodo_id, ano in periodos_data:
                for categoria_id, categoria_nome in categorias_data:
                    for estado_id, estado_nome in estados_data:
                        # Usar apenas o primeiro órgão e fonte para simplicidade
                        if orgaos_data and fontes_data:
                            orgao_id = orgaos_data[0][0]
                            fonte_id = fontes_data[0][0]
                            
                            # Verificar se já existe
                            existing = self.despesas_crud.search({
                                'categoria_despesa_id': categoria_id,
                                'periodo_id': periodo_id,
                                'estado_id': estado_id
                            })
                            if existing:
                                continue
                            
                            # Valor base com variação por ano e estado
                            base_valor = random.uniform(1.0, 10.0)  # Milhões
                            # Tendência de crescimento ao longo dos anos
                            year_factor = 1 + (ano - 2019) * 0.05
                            valor_final = base_valor * year_factor
                            
                            self.despesas_crud.create(
                                orgao_publico_id=orgao_id,
                                fonte_recurso_id=fonte_id,
                                categoria_despesa_id=categoria_id,
                                periodo_id=periodo_id,
                                estado_id=estado_id,
                                valor_milhoes=round(valor_final, 2),
                                tipo_despesa='Corrente',
                                descricao=f'Despesa {categoria_nome} - {estado_nome} - {ano}'
                            )
            
            print(f"✅ Dados Despesas criados: {self.despesas_crud.count()} registros")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar dados de despesas: {e}")
            return False
    
    def _seed_relatorios(self) -> bool:
        """Cria relatórios de exemplo"""
        try:
            if self.relatorios_crud.count() > 0:
                return True
                
            # Buscar usuário admin usando sessão própria
            with self.db_connection.get_session() as session:
                from src.models.entities import Usuario
                
                admin_query = session.query(Usuario).filter(
                    Usuario.email == 'admin@sistema.gov.br'
                ).first()
                
                if not admin_query:
                    return False
                    
                admin_id = admin_query.id
            
            relatorios = [
                {
                    'titulo': 'Relatório de Despesas por Órgão',
                    'tipo_relatorio': 'Despesas por Órgão',
                    'usuario_id': admin_id,
                    'descricao': 'Relatório detalhado das despesas'
                },
                {
                    'titulo': 'Análise IDH por Estado',
                    'tipo_relatorio': 'Análise IDH',
                    'usuario_id': admin_id,
                    'descricao': 'Comparativo do IDH entre estados'
                }
            ]
            
            for relatorio_data in relatorios:
                self.relatorios_crud.create(**relatorio_data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar relatórios: {e}")
            return False
    
    def get_estatisticas_seed(self) -> Dict[str, int]:
        """Retorna estatísticas dos dados criados"""
        try:
            return {
                'regioes': self.regioes_crud.count(),
                'estados': self.estados_crud.count(),
                'orgaos_publicos': self.orgaos_crud.count(),
                'fontes_recursos': self.fontes_crud.count(),
                'categorias_despesas': self.categorias_crud.count(),
                'periodos': self.periodos_crud.count(),
                'usuarios': self.usuarios_crud.count(),
                'indicadores_idh': self.indicadores_crud.count(),
                'despesas': self.despesas_crud.count(),
                'relatorios': self.relatorios_crud.count()
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}


def executar_seed_sistema():
    """Função principal para executar seed do sistema"""
    try:
        print("🌱 Iniciando população do banco de dados...")
        
        seed_manager = SeedDataManager()
        
        if seed_manager.executar_seed_completo():
            print("\n✅ Seed executado com sucesso!")
            
            # Mostrar estatísticas
            stats = seed_manager.get_estatisticas_seed()
            print("\n📊 Dados criados:")
            for entidade, count in stats.items():
                print(f"   • {entidade.replace('_', ' ').title()}: {count}")
            
            return True
        else:
            print("❌ Falha na execução do seed")
            return False
            
    except Exception as e:
        print(f"❌ Erro na execução do seed: {e}")
        return False


if __name__ == "__main__":
    executar_seed_sistema() 