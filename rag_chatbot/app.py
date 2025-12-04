import http.server
import socketserver
import json
import urllib.parse
from utils import RAGChatbot

# Initialize chatbot
chatbot = RAGChatbot()
chatbot.load_data('transactions.json')

class ChatbotHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()
    
    def do_POST(self):
        if self.path == '/ask':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            question = data.get('question', '')
            response = chatbot.process_question(question)
            
            # Get stats for the response
            stats = {
                'total_transactions': len(chatbot.transactions),
                'total_revenue': sum(t['amount'] for t in chatbot.transactions),
                'avg_order': chatbot.get_average_order_amount(),
                'popular_product': chatbot.get_most_purchased_product()
            }
            
            # Get chart data
            chart_data = chatbot.generate_spending_data()
            
            response_data = {
                'answer': response,
                'stats': stats,
                'charts': chart_data
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=8000):
    with socketserver.TCPServer(("", port), ChatbotHandler) as httpd:
        print(f" RAG Chatbot Server running at http://localhost:{port}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n Server stopped")

if __name__ == "__main__":
    run_server()