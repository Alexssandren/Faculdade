#!/usr/bin/env python3
"""
Script para abrir e testar as páginas do protótipo UFSC IHC Redesign
"""

import webbrowser
import http.server
import socketserver
import os
import sys
from pathlib import Path

# Porta do servidor local
PORT = 8000

def open_in_browser():
    """Abre o index.html no navegador padrão"""
    index_path = Path(__file__).parent / "index.html"
    
    if not index_path.exists():
        print("❌ Erro: arquivo index.html não encontrado!")
        print(f"   Procurando em: {index_path.absolute()}")
        return False
    
    # Abre no navegador padrão
    url = f"http://localhost:{PORT}"
    print(f"🌐 Abrindo {url} no navegador...")
    print(f"📁 Servindo arquivos de: {Path(__file__).parent.absolute()}")
    print(f"\n⚠️  Pressione Ctrl+C para parar o servidor\n")
    
    webbrowser.open(url)
    return True

def start_server():
    """Inicia um servidor HTTP simples para servir os arquivos"""
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
        
        def end_headers(self):
            # Adiciona headers CORS para permitir requisições locais
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Access-Control-Allow-Origin', '*')
            super().end_headers()
        
        def log_message(self, format, *args):
            # Log mais limpo
            return
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"✅ Servidor iniciado em http://localhost:{PORT}")
            print(f"📄 Páginas disponíveis:")
            print(f"   - http://localhost:{PORT}/index.html")
            print(f"   - http://localhost:{PORT}/pages/navegacao-melhorada.html")
            print(f"   - http://localhost:{PORT}/pages/feedback-visual.html")
            print(f"   - http://localhost:{PORT}/pages/hierarquia-visual.html")
            print(f"   - http://localhost:{PORT}/pages/acessibilidade.html")
            print(f"   - http://localhost:{PORT}/pages/linguagem-clara.html")
            print(f"   - http://localhost:{PORT}/pages/formularios.html")
            print(f"   - http://localhost:{PORT}/pages/consistencia.html")
            print(f"\n🛑 Pressione Ctrl+C para parar o servidor\n")
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Servidor encerrado. Até logo!")
        sys.exit(0)
    except OSError as e:
        if e.errno == 98 or "Address already in use" in str(e):
            print(f"❌ Erro: Porta {PORT} já está em uso!")
            print(f"   Tente fechar outros servidores ou altere a porta no código.")
        else:
            print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 UFSC IHC Redesign - Servidor de Teste")
    print("=" * 60)
    print()
    
    # Verifica se o index.html existe
    if not (Path(__file__).parent / "index.html").exists():
        print("❌ Erro: arquivo index.html não encontrado!")
        print("   Certifique-se de estar executando o script na pasta do projeto.")
        sys.exit(1)
    
    # Abre no navegador
    if open_in_browser():
        # Inicia o servidor
        start_server()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

