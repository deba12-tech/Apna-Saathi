import json
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime

class RecommendationEngine:
    def __init__(self):
        self.suppliers_data = []
        self.load_suppliers_data()
    
    def load_suppliers_data(self):
        """Load suppliers data from database or sample data"""
        # Sample supplier data - in real app, this would come from database
        self.suppliers_data = [
            {
                'id': 1,
                'name': 'Fresh Vegetables Co.',
                'location': 'Mumbai',
                'items': ['onion', 'tomato', 'potato', 'carrot'],
                'rating': 4.5,
                'total_ratings': 25,
                'price_range': 'medium',
                'delivery_time': 'same_day',
                'description': 'Fresh vegetables delivered daily'
            },
            {
                'id': 2,
                'name': 'Quality Foods Ltd.',
                'location': 'Mumbai',
                'items': ['rice', 'flour', 'oil', 'spices'],
                'rating': 4.2,
                'total_ratings': 18,
                'price_range': 'low',
                'delivery_time': 'next_day',
                'description': 'Quality dry goods and spices'
            },
            {
                'id': 3,
                'name': 'Mumbai Market Hub',
                'location': 'Mumbai',
                'items': ['onion', 'tomato', 'potato', 'rice', 'flour'],
                'rating': 4.8,
                'total_ratings': 42,
                'price_range': 'medium',
                'delivery_time': 'same_day',
                'description': 'One-stop shop for all ingredients'
            },
            {
                'id': 4,
                'name': 'Delhi Fresh Foods',
                'location': 'Delhi',
                'items': ['onion', 'tomato', 'potato', 'carrot'],
                'rating': 4.3,
                'total_ratings': 31,
                'price_range': 'low',
                'delivery_time': 'same_day',
                'description': 'Fresh vegetables from Delhi markets'
            },
            {
                'id': 5,
                'name': 'Capital Vegetables',
                'location': 'Delhi',
                'items': ['rice', 'flour', 'oil', 'spices'],
                'rating': 4.6,
                'total_ratings': 28,
                'price_range': 'medium',
                'delivery_time': 'next_day',
                'description': 'Premium quality dry goods'
            },
            {
                'id': 6,
                'name': 'Bangalore Fresh',
                'location': 'Bangalore',
                'items': ['onion', 'tomato', 'potato', 'carrot'],
                'rating': 4.4,
                'total_ratings': 22,
                'price_range': 'medium',
                'delivery_time': 'same_day',
                'description': 'Fresh vegetables from Bangalore farms'
            },
            # West Bengal Suppliers
            {
                'id': 7,
                'name': 'Siliguri Fresh Market',
                'location': 'Siliguri',
                'items': ['onion', 'tomato', 'potato', 'carrot', 'rice', 'flour'],
                'rating': 4.6,
                'total_ratings': 35,
                'price_range': 'low',
                'delivery_time': 'same_day',
                'description': 'Fresh vegetables and grains from Siliguri markets'
            },
            {
                'id': 8,
                'name': 'Darjeeling Organic Foods',
                'location': 'Darjeeling',
                'items': ['potato', 'carrot', 'onion', 'tomato', 'spices', 'tea'],
                'rating': 4.8,
                'total_ratings': 28,
                'price_range': 'medium',
                'delivery_time': 'next_day',
                'description': 'Organic vegetables and premium Darjeeling spices'
            },
            {
                'id': 9,
                'name': 'Jalpaiguri Wholesale Hub',
                'location': 'Jalpaiguri',
                'items': ['rice', 'flour', 'oil', 'spices', 'onion', 'tomato'],
                'rating': 4.3,
                'total_ratings': 19,
                'price_range': 'low',
                'delivery_time': 'same_day',
                'description': 'Wholesale supplier for all food ingredients'
            },
            {
                'id': 10,
                'name': 'Cooch Behar Food Supply',
                'location': 'Cooch Behar',
                'items': ['rice', 'flour', 'oil', 'spices', 'onion', 'tomato', 'potato'],
                'rating': 4.5,
                'total_ratings': 31,
                'price_range': 'medium',
                'delivery_time': 'same_day',
                'description': 'Complete food supply for street vendors'
            },
            {
                'id': 11,
                'name': 'North Bengal Fresh Vegetables',
                'location': 'Siliguri',
                'items': ['onion', 'tomato', 'potato', 'carrot', 'cabbage', 'cauliflower'],
                'rating': 4.7,
                'total_ratings': 42,
                'price_range': 'medium',
                'delivery_time': 'same_day',
                'description': 'Fresh vegetables from North Bengal farms'
            },
            {
                'id': 12,
                'name': 'Darjeeling Spice Traders',
                'location': 'Darjeeling',
                'items': ['spices', 'tea', 'cardamom', 'ginger', 'garlic'],
                'rating': 4.9,
                'total_ratings': 38,
                'price_range': 'high',
                'delivery_time': 'next_day',
                'description': 'Premium Darjeeling spices and tea'
            }
        ]
    
    def get_supplier_recommendations(self, vendor_needs, vendor_location, max_recommendations=5):
        """
        Get supplier recommendations based on vendor needs and location
        
        Args:
            vendor_needs (list): List of items the vendor needs
            vendor_location (str): Vendor's location
            max_recommendations (int): Maximum number of recommendations to return
        
        Returns:
            list: List of recommended suppliers with scores
        """
        if not vendor_needs:
            return []
        
        recommendations = []
        
        for supplier in self.suppliers_data:
            score = self.calculate_supplier_score(supplier, vendor_needs, vendor_location)
            if score > 0:
                recommendations.append({
                    'supplier': supplier,
                    'score': score,
                    'matching_items': self.get_matching_items(supplier['items'], vendor_needs)
                })
        
        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top recommendations
        return recommendations[:max_recommendations]
    
    def calculate_supplier_score(self, supplier, vendor_needs, vendor_location):
        """
        Calculate a score for a supplier based on various factors
        """
        score = 0
        
        # Location match (highest weight)
        if supplier['location'].lower() == vendor_location.lower():
            score += 40
        elif self.is_nearby_location(supplier['location'], vendor_location):
            score += 20
        
        # Item availability (high weight)
        matching_items = self.get_matching_items(supplier['items'], vendor_needs)
        item_coverage = len(matching_items) / len(vendor_needs) if vendor_needs else 0
        score += item_coverage * 30
        
        # Rating (medium weight)
        score += supplier['rating'] * 2
        
        # Price range (medium weight)
        price_score = self.get_price_score(supplier['price_range'])
        score += price_score * 3
        
        # Delivery time (low weight)
        delivery_score = self.get_delivery_score(supplier['delivery_time'])
        score += delivery_score * 2
        
        # Total ratings (reliability indicator)
        if supplier['total_ratings'] > 20:
            score += 5
        elif supplier['total_ratings'] > 10:
            score += 3
        
        return score
    
    def get_matching_items(self, supplier_items, vendor_needs):
        """Get items that match between supplier and vendor needs"""
        return [item for item in vendor_needs if item in supplier_items]
    
    def is_nearby_location(self, supplier_location, vendor_location):
        """Check if supplier is in a nearby location"""
        nearby_mappings = {
            'mumbai': ['thane', 'navi mumbai', 'kalyan'],
            'delhi': ['noida', 'gurgaon', 'ghaziabad'],
            'bangalore': ['mysore', 'mandya', 'tumkur'],
            'siliguri': ['darjeeling', 'jalpaiguri', 'cooch behar', 'alipurduar'],
            'darjeeling': ['siliguri', 'jalpaiguri', 'kurseong', 'kalimpong'],
            'jalpaiguri': ['siliguri', 'cooch behar', 'alipurduar', 'darjeeling'],
            'cooch behar': ['jalpaiguri', 'alipurduar', 'siliguri']
        }
        
        vendor_loc = vendor_location.lower()
        supplier_loc = supplier_location.lower()
        
        for city, nearby in nearby_mappings.items():
            if vendor_loc == city and supplier_loc in nearby:
                return True
            if supplier_loc == city and vendor_loc in nearby:
                return True
        
        return False
    
    def get_price_score(self, price_range):
        """Convert price range to score"""
        price_scores = {
            'low': 5,
            'medium': 3,
            'high': 1
        }
        return price_scores.get(price_range, 3)
    
    def get_delivery_score(self, delivery_time):
        """Convert delivery time to score"""
        delivery_scores = {
            'same_day': 5,
            'next_day': 3,
            'within_week': 1
        }
        return delivery_scores.get(delivery_time, 3)
    
    def get_suppliers_by_location(self, location):
        """Get all suppliers in a specific location"""
        return [s for s in self.suppliers_data if s['location'].lower() == location.lower()]
    
    def get_suppliers_by_item(self, item):
        """Get all suppliers that provide a specific item"""
        return [s for s in self.suppliers_data if item in s['items']]
    
    def get_price_recommendations(self, item, location):
        """Get price recommendations for a specific item in a location"""
        suppliers = self.get_suppliers_by_item(item)
        location_suppliers = [s for s in suppliers if s['location'].lower() == location.lower()]
        
        if not location_suppliers:
            return None
        
        prices = {
            'low': [],
            'medium': [],
            'high': []
        }
        
        for supplier in location_suppliers:
            prices[supplier['price_range']].append(supplier)
        
        return prices
    
    def get_quality_recommendations(self, item, location):
        """Get quality-based recommendations"""
        suppliers = self.get_suppliers_by_item(item)
        location_suppliers = [s for s in suppliers if s['location'].lower() == location.lower()]
        
        # Sort by rating
        location_suppliers.sort(key=lambda x: x['rating'], reverse=True)
        
        return location_suppliers[:3]  # Top 3 by rating

def get_supplier_recommendations(vendor_needs, vendor_location, max_recommendations=5):
    """
    Main function to get supplier recommendations
    
    Args:
        vendor_needs (list): List of items the vendor needs
        vendor_location (str): Vendor's location
        max_recommendations (int): Maximum number of recommendations
    
    Returns:
        dict: Recommendations with suppliers and scores
    """
    engine = RecommendationEngine()
    recommendations = engine.get_supplier_recommendations(vendor_needs, vendor_location, max_recommendations)
    
    # Format the response
    formatted_recommendations = []
    for rec in recommendations:
        supplier = rec['supplier']
        formatted_recommendations.append({
            'id': supplier['id'],
            'name': supplier['name'],
            'location': supplier['location'],
            'rating': supplier['rating'],
            'total_ratings': supplier['total_ratings'],
            'price_range': supplier['price_range'],
            'delivery_time': supplier['delivery_time'],
            'description': supplier['description'],
            'score': round(rec['score'], 2),
            'matching_items': rec['matching_items'],
            'coverage_percentage': round(len(rec['matching_items']) / len(vendor_needs) * 100, 1) if vendor_needs else 0
        })
    
    return {
        'recommendations': formatted_recommendations,
        'total_found': len(formatted_recommendations),
        'vendor_needs': vendor_needs,
        'vendor_location': vendor_location
    }

# Test the recommendation engine
if __name__ == "__main__":
    # Test scenarios
    test_cases = [
        {
            'needs': ['onion', 'tomato', 'potato'],
            'location': 'Mumbai',
            'description': 'Vendor needs vegetables in Mumbai'
        },
        {
            'needs': ['rice', 'flour', 'oil'],
            'location': 'Delhi',
            'description': 'Vendor needs dry goods in Delhi'
        },
        {
            'needs': ['onion', 'tomato', 'rice', 'flour'],
            'location': 'Bangalore',
            'description': 'Vendor needs mixed items in Bangalore'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n=== {test_case['description']} ===")
        recommendations = get_supplier_recommendations(
            test_case['needs'], 
            test_case['location']
        )
        
        print(f"Found {recommendations['total_found']} recommendations:")
        for i, rec in enumerate(recommendations['recommendations'], 1):
            print(f"{i}. {rec['name']} (Score: {rec['score']})")
            print(f"   Location: {rec['location']}, Rating: {rec['rating']}")
            print(f"   Matching items: {', '.join(rec['matching_items'])}")
            print(f"   Coverage: {rec['coverage_percentage']}%")
            print() 