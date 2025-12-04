import json
import math

class RAGChatbot:
    def __init__(self):
        self.transactions = []
        self.texts = []
        
    def load_data(self, file_path):
        """Load and preprocess transactional data"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.transactions = json.load(f)
        
        # Convert transactions to descriptive text
        self.texts = []
        for transaction in self.transactions:
            text = f"On {transaction['date']}, {transaction['customer']} purchased a {transaction['product']} for ₹{transaction['amount']}."
            self.texts.append(text)
        
    def simple_similarity(self, query, text):
        """Calculate simple word-based similarity"""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        if not query_words:
            return 0
            
        common_words = query_words.intersection(text_words)
        return len(common_words) / len(query_words)
    
    def retrieve_transactions(self, query, top_k=3):
        """Retrieve top_k most relevant transactions based on simple similarity"""
        if not self.texts:
            return []
            
        # Calculate similarities
        similarities = []
        for text in self.texts:
            similarity = self.simple_similarity(query, text)
            similarities.append(similarity)
        
        # Get top_k indices
        indexed_sims = list(enumerate(similarities))
        indexed_sims.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, sim in indexed_sims[:top_k]]
        
        # Return relevant texts and their transactions
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:
                results.append({
                    'text': self.texts[idx],
                    'transaction': self.transactions[idx],
                    'similarity': similarities[idx]
                })
        
        return results if results else [{
            'text': self.texts[0],
            'transaction': self.transactions[0],
            'similarity': 0.1
        }]
    
    def get_customer_transactions(self, customer_name):
        """Get all transactions for a specific customer"""
        return [t for t in self.transactions if t['customer'].lower() == customer_name.lower()]
    
    def get_total_spending(self, customer_name):
        """Calculate total spending for a customer"""
        customer_transactions = self.get_customer_transactions(customer_name)
        return sum(t['amount'] for t in customer_transactions)
    
    def get_monthly_transactions(self, year_month):
        """Get transactions for a specific month (format: YYYY-MM)"""
        return [t for t in self.transactions if t['date'].startswith(year_month)]
    
    def get_average_order_amount(self):
        """Calculate average order amount"""
        if not self.transactions:
            return 0
        total = sum(t['amount'] for t in self.transactions)
        return total / len(self.transactions)
    
    def get_most_purchased_product(self):
        """Find the most frequently purchased product"""
        products = [t['product'] for t in self.transactions]
        product_count = {}
        for product in products:
            product_count[product] = product_count.get(product, 0) + 1
        return max(product_count, key=product_count.get) if product_count else "No products"
    
    def get_all_customers(self):
        """Get list of all customers"""
        return list(set(t['customer'] for t in self.transactions))
    
    def generate_spending_data(self):
        """Generate data for spending analysis"""
        # Monthly spending
        monthly_data = {}
        for transaction in self.transactions:
            month = transaction['date'][:7]  # YYYY-MM
            monthly_data[month] = monthly_data.get(month, 0) + transaction['amount']
        
        # Customer spending
        customer_data = {}
        for transaction in self.transactions:
            customer = transaction['customer']
            customer_data[customer] = customer_data.get(customer, 0) + transaction['amount']
        
        # Product frequency
        product_data = {}
        for transaction in self.transactions:
            product = transaction['product']
            product_data[product] = product_data.get(product, 0) + 1
        
        return {
            'monthly_spending': [{'month': k, 'amount': v} for k, v in monthly_data.items()],
            'customer_spending': [{'customer': k, 'amount': v} for k, v in customer_data.items()],
            'product_frequency': [{'product': k, 'count': v} for k, v in product_data.items()]
        }
    
    def process_question(self, question):
        """Process a question and return the response"""
        # Retrieve relevant transactions
        relevant_transactions = self.retrieve_transactions(question, top_k=3)
        
        # Build context from retrieved transactions
        context = "\n".join([t['text'] for t in relevant_transactions])
        
        # Simple rule-based response generation
        question_lower = question.lower()
        
        if "total spending" in question_lower or "total spent" in question_lower:
            for customer in self.get_all_customers():
                if customer.lower() in question_lower:
                    total = self.get_total_spending(customer)
                    return f"{customer.title()} spent a total of ₹{total:,}."
            return "Please specify which customer's total spending you want to know."
        
        elif "purchase history" in question_lower or "transactions" in question_lower:
            for customer in self.get_all_customers():
                if customer.lower() in question_lower:
                    transactions = self.get_customer_transactions(customer)
                    if transactions:
                        response = f"{customer.title()} made {len(transactions)} purchases: "
                        purchases = []
                        for t in transactions:
                            purchases.append(f"a {t['product']} for ₹{t['amount']:,} on {t['date']}")
                        response += " and ".join(purchases)
                        return response + "."
                    else:
                        return f"No transactions found for {customer.title()}."
            return "Please specify which customer's purchase history you want to see."
        
        elif "average" in question_lower and "order" in question_lower:
            avg = self.get_average_order_amount()
            return f"The average order amount is ₹{avg:,.2f}."
        
        elif "most" in question_lower and ("purchased" in question_lower or "popular" in question_lower):
            product = self.get_most_purchased_product()
            return f"The most frequently purchased product is {product}."
        
        elif "month" in question_lower:
            # Month detection
            months = {
                'january': '01', 'february': '02', 'march': '03', 
                'april': '04', 'may': '05', 'june': '06',
                'july': '07', 'august': '08', 'september': '09', 
                'october': '10', 'november': '11', 'december': '12'
            }
            for month_name, month_num in months.items():
                if month_name in question_lower:
                    month_str = f"2024-{month_num}"
                    transactions = self.get_monthly_transactions(month_str)
                    if transactions:
                        response = f"Transactions for {month_name.title()} 2024: "
                        trans_list = []
                        for t in transactions:
                            trans_list.append(f"{t['customer']} bought {t['product']} for ₹{t['amount']:,}")
                        response += ", ".join(trans_list)
                        return response + "."
                    else:
                        return f"No transactions found for {month_name.title()} 2024."
        
        elif "list customers" in question_lower or "all customers" in question_lower:
            customers = self.get_all_customers()
            return f"We have {len(customers)} customers: {', '.join(customers)}."
        
        elif "help" in question_lower:
            return """I can help you with:
• Customer spending totals (e.g., "What was Amit's total spending?")
• Purchase history (e.g., "Show me Riya's purchases")
• Average order amounts
• Most popular products
• Monthly transactions
• List all customers
Try asking me anything about the transaction data!"""
        
        # Default response based on retrieved context
        if context:
            return f"Based on the transaction data:\n\n{context}\n\nIs there anything specific you'd like to know about these transactions?"
        else:
            return "I can help you analyze transaction data. You can ask about customer spending, purchase history, average orders, or popular products. Try 'help' for more options."