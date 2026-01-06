#!/usr/bin/env python3
"""
Servidor proxy simples para contornar problemas de CORS
Faz requisições para a API Lambda e retorna os dados
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import webbrowser

API_URL = "https://auwb72k75qnn3ncgrchc6qpyv40kvdaa.lambda-url.sa-east-1.on.aws/"

class ProxyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '3600')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/logs' or self.path == '/api/logs/':
            try:
                # Fazer requisição para a API Lambda
                req = urllib.request.Request(API_URL)
                req.add_header('Accept', 'application/json')
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = response.read()
                    json_data = json.loads(data.decode('utf-8'))
                    
                    # Retornar JSON
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(json_data).encode('utf-8'))
                    
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {'error': str(e)}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        elif self.path == '/' or self.path == '/index.html':
            # Servir o index.html
            try:
                with open('index.html', 'rb') as f:
                    content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write(content)
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Override para suprimir logs"""
        pass

def main():
    PORT = 9000
    
    server = HTTPServer(('', PORT), ProxyHandler)
    print(f"Servidor Proxy rodando em http://localhost:{PORT}")
    print("Abrindo index.html no navegador...")
    print("Pressione Ctrl+C para parar o servidor\n")
    
    # Abre o navegador automaticamente
    webbrowser.open(f'http://localhost:{PORT}/index.html')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor parado.")

if __name__ == "__main__":
    main()

