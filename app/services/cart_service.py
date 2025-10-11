"""
Cart service for managing shopping cart operations.

This service provides methods to manage cart items, validate cart contents,
and integrate with inventory and payment services.
"""

from typing import List, Dict, Optional, Tuple
from app.models.listing import Listing
from app.services.inventory_service import InventoryService


class CartService:
    """Service for managing shopping cart operations."""
    
    def __init__(self):
        self.inventory_service = InventoryService()
    
    def validate_cart_item(self, cart_item: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate a single cart item structure and data.
        
        Args:
            cart_item: Dictionary containing cart item data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['listing_id', 'quantity']
        
        # Check required fields
        for field in required_fields:
            if field not in cart_item or cart_item[field] is None:
                return False, f"Missing required field: {field}"
        
        # Validate quantity
        try:
            quantity = int(cart_item['quantity'])
            if quantity < 1:
                return False, "Quantity must be a positive integer"
        except (ValueError, TypeError):
            return False, "Quantity must be a valid integer"
        
        # Validate listing exists
        listing = self.inventory_service.get_item_by_listing_id(cart_item['listing_id'])
        if not listing:
            return False, f"Item {cart_item['listing_id']} no longer available"
        
        return True, None
    
    def validate_cart(self, cart_items: List[Dict]) -> Tuple[bool, List[Dict], float, str]:
        """
        Validate entire cart and calculate totals.
        
        Args:
            cart_items: List of cart item dictionaries
            
        Returns:
            Tuple of (is_valid, validated_items, total_price, currency)
        """
        if not cart_items:
            return False, [], 0.0, '$'
        
        validated_items = []
        total_price = 0.0
        currency = '$'
        
        for item in cart_items:
            # Validate item structure
            is_valid, error = self.validate_cart_item(item)
            if not is_valid:
                return False, [], 0.0, currency
            
            # Get current listing data
            listing = self.inventory_service.get_item_by_listing_id(item['listing_id'])
            quantity = int(item['quantity'])
            
            # Calculate item total
            price = float(listing.get('price_value', 0))
            item_total = price * quantity
            total_price += item_total
            
            # Set currency from first item
            if not validated_items:
                currency = listing.get('price_currency', '$')
            
            validated_items.append({
                'listing_id': item['listing_id'],
                'title': listing.get('release_title'),
                'artist': listing.get('artist_names'),
                'price': price,
                'quantity': quantity,
                'item_total': item_total,
                'currency': listing.get('price_currency', '$'),
                'image': listing.get('image_uri')
            })
        
        return True, validated_items, total_price, currency
    
    def calculate_cart_summary(self, validated_items: List[Dict]) -> Dict:
        """
        Calculate cart summary including totals, taxes, shipping, etc.
        
        Args:
            validated_items: List of validated cart items
            
        Returns:
            Dictionary containing cart summary
        """
        if not validated_items:
            return {
                'subtotal': 0.0,
                'tax': 0.0,
                'shipping': 0.0,
                'total': 0.0,
                'currency': '$',
                'item_count': 0
            }
        
        subtotal = sum(item['item_total'] for item in validated_items)
        item_count = sum(item['quantity'] for item in validated_items)
        currency = validated_items[0]['currency']
        
        # Calculate tax (example: 8.5% sales tax)
        tax_rate = 0.085
        tax = subtotal * tax_rate
        
        # Calculate shipping (free shipping over $50, otherwise $5.99)
        shipping = 0.0 if subtotal >= 50.0 else 5.99
        
        total = subtotal + tax + shipping
        
        return {
            'subtotal': round(subtotal, 2),
            'tax': round(tax, 2),
            'shipping': round(shipping, 2),
            'total': round(total, 2),
            'currency': currency,
            'item_count': item_count,
            'free_shipping_eligible': subtotal >= 50.0
        }
    
    def prepare_cart_for_payment(self, cart_items: List[Dict]) -> Dict:
        """
        Prepare cart data for payment processing.
        
        Args:
            cart_items: List of cart item dictionaries
            
        Returns:
            Dictionary containing payment-ready cart data
        """
        is_valid, validated_items, total_price, currency = self.validate_cart(cart_items)
        
        if not is_valid:
            raise ValueError("Cart validation failed")
        
        cart_summary = self.calculate_cart_summary(validated_items)
        
        return {
            'items': validated_items,
            'summary': cart_summary,
            'is_valid': True,
            'payment_amount': int(cart_summary['total'] * 100),  # Amount in cents for Stripe
            'currency_code': 'usd' if currency == '$' else currency.lower()
        }
    
    def get_cart_for_stripe(self, cart_items: List[Dict]) -> Dict:
        """
        Format cart data specifically for Stripe payment processing.
        
        Args:
            cart_items: List of cart item dictionaries
            
        Returns:
            Dictionary formatted for Stripe integration
        """
        payment_data = self.prepare_cart_for_payment(cart_items)
        
        # Format line items for Stripe
        line_items = []
        for item in payment_data['items']:
            line_items.append({
                'price_data': {
                    'currency': payment_data['currency_code'],
                    'product_data': {
                        'name': f"{item['title']} - {item['artist']}",
                        'images': [item['image']] if item.get('image') else [],
                    },
                    'unit_amount': int(item['price'] * 100),  # Convert to cents
                },
                'quantity': item['quantity'],
            })
        
        # Add shipping as line item if applicable
        if payment_data['summary']['shipping'] > 0:
            line_items.append({
                'price_data': {
                    'currency': payment_data['currency_code'],
                    'product_data': {
                        'name': 'Shipping',
                    },
                    'unit_amount': int(payment_data['summary']['shipping'] * 100),
                },
                'quantity': 1,
            })
        
        # Add tax as line item
        if payment_data['summary']['tax'] > 0:
            line_items.append({
                'price_data': {
                    'currency': payment_data['currency_code'],
                    'product_data': {
                        'name': 'Tax',
                    },
                    'unit_amount': int(payment_data['summary']['tax'] * 100),
                },
                'quantity': 1,
            })
        
        return {
            'line_items': line_items,
            'total_amount': payment_data['payment_amount'],
            'currency': payment_data['currency_code'],
            'summary': payment_data['summary']
        }