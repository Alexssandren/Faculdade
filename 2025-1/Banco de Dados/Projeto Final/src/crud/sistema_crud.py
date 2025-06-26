"""
CRUD Sistema - Sistema DEC7588
Operações CRUD para entidades de sistema (Usuários e Relatórios)
"""

import sys
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
import json

# Adicionar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.crud.base_crud import BaseCRUD, ValidationException, CRUDException
from src.models.entities import Usuario, Relatorio

class UsuariosCRUD(BaseCRUD[Usuario]):
    """CRUD para Usuários do Sistema"""
    
    def __init__(self):
        super().__init__(Usuario)
    
    def validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validação específica para criação de usuário"""
        required_fields = ['nome_usuario', 'email', 'senha', 'tipo_usuario']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationException(f"Campo '{field}' é obrigatório")
        
        # Validar email
        if not self._validar_email(data['email']):
            raise ValidationException("Email inválido")
        
        # Validar senha
        if len(data['senha']) < 6:
            raise ValidationException("Senha deve ter pelo menos 6 caracteres")
        
        # Validar tipo de usuário
        tipos_validos = ['admin', 'normal', 'readonly']
        if data['tipo_usuario'] not in tipos_validos:
            raise ValidationException(f"Tipo de usuário deve ser: {', '.join(tipos_validos)}")
        
        # Hash da senha e mudar nome do campo
        data['senha_hash'] = self._hash_senha(data['senha'])
        del data['senha']  # Remover campo senha original
        
        # Normalizar campos
        data['nome_usuario'] = data['nome_usuario'].strip()
        data['email'] = data['email'].strip().lower()
        
        return super().validate_create_data(data)
    
    def validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validação específica para atualização de usuário"""
        # Validar email (se fornecido)
        if 'email' in data and data['email']:
            if not self._validar_email(data['email']):
                raise ValidationException("Email inválido")
            data['email'] = data['email'].strip().lower()
        
        # Validar senha (se fornecida)
        if 'senha' in data and data['senha']:
            if len(data['senha']) < 6:
                raise ValidationException("Senha deve ter pelo menos 6 caracteres")
            data['senha_hash'] = self._hash_senha(data['senha'])
            del data['senha']  # Remover campo senha original
        
        # Validar tipo de usuário (se fornecido)
        if 'tipo_usuario' in data and data['tipo_usuario']:
            tipos_validos = ['admin', 'normal', 'readonly']
            if data['tipo_usuario'] not in tipos_validos:
                raise ValidationException(f"Tipo de usuário deve ser: {', '.join(tipos_validos)}")
        
        # Normalizar nome (se fornecido)
        if 'nome_usuario' in data and data['nome_usuario']:
            data['nome_usuario'] = data['nome_usuario'].strip()
        
        return super().validate_update_data(data)
    
    def check_duplicates(self, session: Session, data: Dict[str, Any]):
        """Verifica se usuário já existe"""
        # Verificar email
        existing_email = session.query(Usuario).filter(
            Usuario.email == data['email']
        ).first()
        
        if existing_email:
            raise ValidationException(f"Email '{data['email']}' já está em uso")
        
        # Verificar nome de usuário
        existing_nome = session.query(Usuario).filter(
            Usuario.nome_usuario == data['nome_usuario']
        ).first()
        
        if existing_nome:
            raise ValidationException(f"Nome de usuário '{data['nome_usuario']}' já existe")
    
    def _validar_email(self, email: str) -> bool:
        """Valida formato de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _hash_senha(self, senha: str) -> str:
        """Gera hash da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def autenticar(self, email: str, senha: str) -> Optional[Usuario]:
        """Autentica usuário por email e senha"""
        try:
            senha_hash = self._hash_senha(senha)
            
            with self.db_connection.get_session() as session:
                usuario = session.query(Usuario).filter(
                    Usuario.email == email.lower(),
                    Usuario.senha_hash == senha_hash,
                    Usuario.ativo == True
                ).first()
                
                if usuario:
                    # Atualizar último acesso
                    usuario.ultimo_acesso = datetime.now()
                    session.flush()
                    
                    self.logger.info(f"✅ Usuário autenticado: {email}")
                    return usuario
                else:
                    self.logger.warning(f"⚠️ Falha na autenticação: {email}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"❌ Erro na autenticação: {e}")
            return None
    
    def alterar_senha(self, usuario_id: int, senha_atual: str, nova_senha: str) -> bool:
        """Altera senha do usuário"""
        try:
            usuario = self.get_by_id(usuario_id)
            if not usuario:
                return False
            
            # Verificar senha atual
            senha_atual_hash = self._hash_senha(senha_atual)
            if usuario.senha_hash != senha_atual_hash:
                raise ValidationException("Senha atual incorreta")
            
            # Validar nova senha
            if len(nova_senha) < 6:
                raise ValidationException("Nova senha deve ter pelo menos 6 caracteres")
            
            # Atualizar senha
            nova_senha_hash = self._hash_senha(nova_senha)
            return self.update(usuario_id, senha_hash=nova_senha_hash) is not None
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao alterar senha: {e}")
            return False
    
    def get_by_email(self, email: str) -> Optional[Usuario]:
        """Busca usuário por email"""
        results = self.search({'email': email.lower()})
        return results[0] if results else None
    
    def get_by_tipo(self, tipo: str) -> List[Usuario]:
        """Busca usuários por tipo de usuário"""
        return self.search({'tipo_usuario': tipo})
    
    def get_administradores(self) -> List[Usuario]:
        """Busca apenas administradores"""
        return self.get_by_tipo('admin')
    
    def get_ativos(self) -> List[Usuario]:
        """Busca apenas usuários ativos"""
        return self.search({'ativo': True})
    
    def ativar_usuario(self, usuario_id: int) -> bool:
        """Ativa um usuário"""
        return self.update(usuario_id, ativo=True) is not None
    
    def desativar_usuario(self, usuario_id: int) -> bool:
        """Desativa um usuário"""
        return self.update(usuario_id, ativo=False) is not None
    
    def get_custom_stats(self) -> Dict[str, Any]:
        """Estatísticas específicas de usuários"""
        try:
            with self.db_connection.get_session() as session:
                from sqlalchemy import func
                
                # Usuários por tipo
                stats_tipo = session.query(
                    Usuario.tipo_usuario,
                    func.count(Usuario.id).label('total')
                ).group_by(Usuario.tipo_usuario).all()
                
                # Usuários ativos vs inativos
                total_ativos = session.query(func.count(Usuario.id)).filter(
                    Usuario.ativo == True
                ).scalar()
                total_inativos = session.query(func.count(Usuario.id)).filter(
                    Usuario.ativo == False
                ).scalar()
                
                # Usuários com acesso recente (últimos 30 dias)
                from datetime import timedelta
                data_limite = datetime.now() - timedelta(days=30)
                acessos_recentes = session.query(func.count(Usuario.id)).filter(
                    Usuario.ultimo_acesso >= data_limite
                ).scalar()
                
                return {
                    'por_tipo': {tipo: total for tipo, total in stats_tipo},
                    'ativos': total_ativos,
                    'inativos': total_inativos,
                    'acessos_recentes': acessos_recentes
                }
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular estatísticas de usuários: {e}")
            return {}


class RelatoriosCRUD(BaseCRUD[Relatorio]):
    """CRUD para Relatórios"""
    
    def __init__(self):
        super().__init__(Relatorio)
    
    def validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validação específica para criação de relatório"""
        required_fields = ['titulo', 'tipo_relatorio', 'usuario_id']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationException(f"Campo '{field}' é obrigatório")
        
        # Validar tipos de relatório
        tipos_validos = [
            'Despesas por Órgão', 'Análise IDH', 'Comparativo Regional',
            'Evolução Temporal', 'Dashboard Executivo', 'Personalizado'
        ]
        if data['tipo_relatorio'] not in tipos_validos:
            raise ValidationException(f"Tipo deve ser um dos: {', '.join(tipos_validos)}")
        
        # Validar se usuário existe
        from src.crud.sistema_crud import UsuariosCRUD
        usuario_crud = UsuariosCRUD()
        if not usuario_crud.get_by_id(data['usuario_id']):
            raise ValidationException(f"Usuário com ID {data['usuario_id']} não existe")
        
        # Validar parâmetros (se fornecidos)
        if 'parametros' in data and data['parametros']:
            try:
                # Tentar fazer parse do JSON
                if isinstance(data['parametros'], str):
                    json.loads(data['parametros'])
                elif isinstance(data['parametros'], dict):
                    data['parametros'] = json.dumps(data['parametros'])
            except json.JSONDecodeError:
                raise ValidationException("Parâmetros devem estar em formato JSON válido")
        
        # Normalizar título
        data['titulo'] = data['titulo'].strip()
        
        return super().validate_create_data(data)
    
    def get_by_usuario(self, usuario_id: int) -> List[Relatorio]:
        """Busca relatórios por usuário"""
        return self.search({'usuario_id': usuario_id})
    
    def get_by_tipo(self, tipo: str) -> List[Relatorio]:
        """Busca relatórios por tipo"""
        return self.search({'tipo_relatorio': tipo})
    
    def get_recentes(self, limit: int = 10) -> List[Relatorio]:
        """Busca relatórios mais recentes"""
        try:
            with self.db_connection.get_session() as session:
                return session.query(Relatorio).order_by(
                    Relatorio.data_criacao.desc()
                ).limit(limit).all()
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar relatórios recentes: {e}")
            return []
    
    def executar_relatorio(self, relatorio_id: int) -> bool:
        """Marca relatório como executado"""
        try:
            return self.update(relatorio_id, 
                             data_execucao=datetime.now(),
                             status='Executado') is not None
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar relatório: {e}")
            return False
    
    def marcar_como_favorito(self, relatorio_id: int) -> bool:
        """Marca relatório como favorito"""
        return self.update(relatorio_id, favorito=True) is not None
    
    def remover_favorito(self, relatorio_id: int) -> bool:
        """Remove relatório dos favoritos"""
        return self.update(relatorio_id, favorito=False) is not None
    
    def get_favoritos(self, usuario_id: int = None) -> List[Relatorio]:
        """Busca relatórios favoritos"""
        filters = {'favorito': True}
        if usuario_id:
            filters['usuario_id'] = usuario_id
        return self.search(filters)
    
    def get_por_periodo(self, data_inicio: datetime, data_fim: datetime) -> List[Relatorio]:
        """Busca relatórios por período"""
        try:
            with self.db_connection.get_session() as session:
                return session.query(Relatorio).filter(
                    Relatorio.data_criacao >= data_inicio,
                    Relatorio.data_criacao <= data_fim
                ).order_by(Relatorio.data_criacao.desc()).all()
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar relatórios por período: {e}")
            return []
    
    def get_estatisticas_usuario(self, usuario_id: int) -> Dict[str, Any]:
        """Estatísticas de relatórios por usuário"""
        try:
            with self.db_connection.get_session() as session:
                from sqlalchemy import func
                
                # Total de relatórios
                total = session.query(func.count(Relatorio.id)).filter(
                    Relatorio.usuario_id == usuario_id
                ).scalar()
                
                # Por tipo
                por_tipo = session.query(
                    Relatorio.tipo_relatorio,
                    func.count(Relatorio.id).label('total')
                ).filter(
                    Relatorio.usuario_id == usuario_id
                ).group_by(Relatorio.tipo_relatorio).all()
                
                # Favoritos
                favoritos = session.query(func.count(Relatorio.id)).filter(
                    Relatorio.usuario_id == usuario_id,
                    Relatorio.favorito == True
                ).scalar()
                
                return {
                    'total_relatorios': total,
                    'por_tipo': {tipo: total for tipo, total in por_tipo},
                    'favoritos': favoritos
                }
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular estatísticas: {e}")
            return {}
    
    def get_custom_stats(self) -> Dict[str, Any]:
        """Estatísticas específicas de relatórios"""
        try:
            with self.db_connection.get_session() as session:
                from sqlalchemy import func
                
                # Relatórios por tipo
                stats_tipo = session.query(
                    Relatorio.tipo_relatorio,
                    func.count(Relatorio.id).label('total')
                ).group_by(Relatorio.tipo_relatorio).all()
                
                # Total de favoritos
                total_favoritos = session.query(func.count(Relatorio.id)).filter(
                    Relatorio.favorito == True
                ).scalar()
                
                # Relatórios executados
                executados = session.query(func.count(Relatorio.id)).filter(
                    Relatorio.data_execucao.isnot(None)
                ).scalar()
                
                return {
                    'por_tipo': {tipo: total for tipo, total in stats_tipo},
                    'total_favoritos': total_favoritos,
                    'executados': executados
                }
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular estatísticas de relatórios: {e}")
            return {} 