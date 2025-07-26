import re
import json
from datetime import datetime

# FAQ Database
FAQ_DATABASE = {
    "storage": {
        "onion": "Store onions in a cool, dry place with good ventilation. Avoid storing near potatoes as they release gases that can spoil onions faster.",
        "tomato": "Store tomatoes at room temperature until ripe, then refrigerate. Don't store in plastic bags as they need air circulation.",
        "potato": "Store potatoes in a cool, dark place (not refrigerator). Keep them dry and away from onions.",
        "rice": "Store rice in an airtight container in a cool, dry place. Brown rice should be refrigerated due to its oil content.",
        "flour": "Store flour in an airtight container in a cool, dry place. Whole wheat flour should be refrigerated.",
        "oil": "Store cooking oil in a cool, dark place away from heat sources. Keep the container tightly sealed.",
        "spices": "Store spices in airtight containers away from heat, light, and moisture. Ground spices lose potency faster than whole spices."
    },
    "pricing": {
        "onion": "Current market price for onions ranges from ₹20-40 per kg depending on quality and season.",
        "tomato": "Tomato prices typically range from ₹30-60 per kg, with seasonal variations.",
        "potato": "Potato prices are usually stable around ₹25-35 per kg.",
        "rice": "Rice prices vary by type: Basmati ₹80-120/kg, regular rice ₹40-60/kg.",
        "flour": "Wheat flour costs ₹30-45 per kg, depending on quality and brand."
    },
    "quality": {
        "onion": "Good onions should be firm, have dry outer skin, and no soft spots or mold.",
        "tomato": "Ripe tomatoes should be firm but slightly soft, with bright color and no cracks.",
        "potato": "Quality potatoes should be firm, smooth, and free from sprouts or green spots.",
        "rice": "Good rice should be clean, uniform in size, and free from insects or foreign matter."
    },
    "suppliers": {
        "mumbai": "Top suppliers in Mumbai: Fresh Vegetables Co., Mumbai Market Hub, Quality Foods Ltd.",
        "delhi": "Top suppliers in Delhi: Delhi Fresh Foods, Capital Vegetables, Quality Supply Co.",
        "bangalore": "Top suppliers in Bangalore: Bangalore Fresh, Garden City Foods, Quality Veggies."
    }
}

# General responses
GENERAL_RESPONSES = {
    "greeting": [
        "Namaste! How can I help you with your street food business today?",
        "Hello! I'm here to help you find the best suppliers and manage your business better.",
        "Welcome to Apna Saathi! What would you like to know about suppliers or ingredients?"
    ],
    "help": [
        "I can help you with:\n• Storage tips for ingredients\n• Current market prices\n• Quality checking tips\n• Finding suppliers in your area\n• Business advice for street food vendors",
        "Here's what I can assist you with:\n• Ingredient storage and handling\n• Market price information\n• Quality assessment\n• Supplier recommendations\n• Business tips and tricks"
    ],
    "unknown": [
        "I'm not sure about that. Could you ask me about ingredient storage, prices, quality tips, or supplier recommendations?",
        "I don't have information on that topic. I can help with storage tips, pricing, quality checks, or finding suppliers.",
        "That's beyond my knowledge. Try asking about ingredients, suppliers, or business tips!"
    ]
}

def get_chatbot_response(message):
    """
    Generate chatbot response based on user message
    """
    message = message.lower().strip()
    
    # Greeting patterns
    if any(word in message for word in ['hello', 'hi', 'namaste', 'hey']):
        return get_random_response(GENERAL_RESPONSES["greeting"])
    
    # Help patterns
    if any(word in message for word in ['help', 'what can you do', 'assist']):
        return get_random_response(GENERAL_RESPONSES["help"])
    
    # Storage questions
    if any(word in message for word in ['store', 'storage', 'keep', 'preserve']):
        return handle_storage_question(message)
    
    # Price questions
    if any(word in message for word in ['price', 'cost', 'rate', 'how much']):
        return handle_price_question(message)
    
    # Quality questions
    if any(word in message for word in ['quality', 'good', 'fresh', 'check']):
        return handle_quality_question(message)
    
    # Supplier questions
    if any(word in message for word in ['supplier', 'vendor', 'where to buy', 'source']):
        return handle_supplier_question(message)
    
    # Business advice
    if any(word in message for word in ['business', 'profit', 'margin', 'earn']):
        return handle_business_question(message)
    
    # Ingredient-specific questions
    ingredients = ['onion', 'tomato', 'potato', 'rice', 'flour', 'oil', 'spices', 'chicken', 'fish', 'vegetables']
    for ingredient in ingredients:
        if ingredient in message:
            return handle_ingredient_specific_question(message, ingredient)
    
    return get_random_response(GENERAL_RESPONSES["unknown"])

def handle_storage_question(message):
    """Handle storage-related questions"""
    ingredients = ['onion', 'tomato', 'potato', 'rice', 'flour', 'oil', 'spices']
    for ingredient in ingredients:
        if ingredient in message:
            return FAQ_DATABASE["storage"].get(ingredient, f"I don't have specific storage tips for {ingredient}.")
    
    return "For storage tips, please specify the ingredient. I can help with onions, tomatoes, potatoes, rice, flour, oil, and spices."

def handle_price_question(message):
    """Handle price-related questions"""
    ingredients = ['onion', 'tomato', 'potato', 'rice', 'flour']
    for ingredient in ingredients:
        if ingredient in message:
            return FAQ_DATABASE["pricing"].get(ingredient, f"I don't have current pricing for {ingredient}.")
    
    return "For pricing information, please specify the ingredient. I can help with onions, tomatoes, potatoes, rice, and flour."

def handle_quality_question(message):
    """Handle quality-related questions"""
    ingredients = ['onion', 'tomato', 'potato', 'rice']
    for ingredient in ingredients:
        if ingredient in message:
            return FAQ_DATABASE["quality"].get(ingredient, f"I don't have quality tips for {ingredient}.")
    
    return "For quality tips, please specify the ingredient. I can help with onions, tomatoes, potatoes, and rice."

def handle_supplier_question(message):
    """Handle supplier-related questions"""
    cities = ['mumbai', 'delhi', 'bangalore', 'siliguri', 'darjeeling', 'jalpaiguri', 'cooch behar']
    for city in cities:
        if city in message:
            return FAQ_DATABASE["suppliers"].get(city, f"I don't have supplier information for {city}.")
    
    return "I can help you find suppliers in Mumbai, Delhi, Bangalore, and West Bengal cities like Siliguri, Darjeeling, Jalpaiguri, and Cooch Behar. Which city are you in?"

def handle_business_question(message):
    """Handle business-related questions"""
    if 'profit' in message or 'margin' in message:
        return "For street food businesses, typical profit margins range from 30-50%. Focus on quality ingredients, efficient operations, and good customer service to maximize profits."
    
    if 'earn' in message or 'income' in message:
        return "Street food vendors can earn ₹500-2000 per day depending on location, menu, and business hours. Popular locations and unique recipes can significantly increase earnings."
    
    return "For business success: 1) Use quality ingredients 2) Maintain hygiene 3) Offer good customer service 4) Find reliable suppliers 5) Keep costs low while maintaining quality."

def handle_ingredient_specific_question(message, ingredient):
    """Handle ingredient-specific questions"""
    if 'storage' in message or 'store' in message:
        return FAQ_DATABASE["storage"].get(ingredient, f"I don't have storage tips for {ingredient}.")
    
    if 'price' in message or 'cost' in message:
        return FAQ_DATABASE["pricing"].get(ingredient, f"I don't have pricing for {ingredient}.")
    
    if 'quality' in message or 'fresh' in message:
        return FAQ_DATABASE["quality"].get(ingredient, f"I don't have quality tips for {ingredient}.")
    
    return f"I can help you with storage, pricing, and quality information for {ingredient}. What would you like to know?"

def get_random_response(responses):
    """Get a random response from a list"""
    import random
    return random.choice(responses)

def get_business_tips():
    """Get general business tips for street food vendors"""
    tips = [
        "Always maintain high hygiene standards - customers notice cleanliness",
        "Source fresh ingredients daily for better taste and customer satisfaction",
        "Build relationships with reliable suppliers for consistent quality",
        "Keep your menu simple but delicious - quality over quantity",
        "Use social media to promote your business and attract customers",
        "Offer combo deals to increase average order value",
        "Maintain consistent pricing while ensuring good profit margins",
        "Get customer feedback regularly to improve your offerings",
        "Keep track of your expenses and profits daily",
        "Invest in good equipment and maintain it regularly"
    ]
    return tips

def get_seasonal_advice():
    """Get seasonal business advice"""
    current_month = datetime.now().month
    
    seasonal_tips = {
        "summer": "Focus on cooling drinks and light snacks. Stock up on ice and cold storage.",
        "monsoon": "Ensure your setup is waterproof. Offer hot beverages and fried snacks.",
        "winter": "Hot beverages and warm snacks sell well. Consider adding soup to your menu.",
        "spring": "Fresh vegetables are abundant and cheaper. Update your menu with seasonal items."
    }
    
    if current_month in [3, 4, 5]:  # March to May
        return seasonal_tips["summer"]
    elif current_month in [6, 7, 8, 9]:  # June to September
        return seasonal_tips["monsoon"]
    elif current_month in [10, 11, 12, 1, 2]:  # October to February
        return seasonal_tips["winter"]
    else:
        return seasonal_tips["spring"]

# Test the chatbot
if __name__ == "__main__":
    test_messages = [
        "Hello",
        "How should I store onions?",
        "What's the price of tomatoes?",
        "How to check rice quality?",
        "Find suppliers in Mumbai",
        "How to increase profit?",
        "What can you help me with?"
    ]
    
    for message in test_messages:
        response = get_chatbot_response(message)
        print(f"Q: {message}")
        print(f"A: {response}")
        print("-" * 50) 