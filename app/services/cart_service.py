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
    
    def calculate_cart_summary(self, validated_items: List[Dict], customer_address: Optional[Dict] = None) -> Dict:
        """
        Calculate cart summary including totals, taxes, shipping, etc.
        
        Args:
            validated_items: List of validated cart items
            customer_address: Optional customer address for location-based tax calculation
                Expected format: {
                    'line1': str,           # Street address (required)
                    'line2': str,           # Apartment, suite, unit, etc. (optional)
                    'city': str,            # City (required)
                    'state': str,           # State/province (required)
                    'postal_code': str,     # ZIP/postal code (required)
                    'country': str          # Country code (required, e.g., 'US', 'CA')
                }
            
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
                'item_count': 0,
                'tax_calculation_method': 'none'
            }
        
        subtotal = sum(item['item_total'] for item in validated_items)
        item_count = sum(item['quantity'] for item in validated_items)
        currency = validated_items[0]['currency']
        
        # Calculate tax based on customer location if available
        tax, tax_method = self._calculate_tax(subtotal, customer_address)
        
        # Calculate shipping (free shipping over $65, otherwise $6.50)
        shipping = self._calculate_shipping(subtotal, customer_address)
        
        total = subtotal + tax + shipping
        
        return {
            'subtotal': round(subtotal, 2),
            'tax': round(tax, 2),
            'shipping': round(shipping, 2),
            'total': round(total, 2),
            'currency': currency,
            'item_count': item_count,
            'free_shipping_eligible': subtotal >= 65.0,
            'tax_calculation_method': tax_method
        }
    
    def prepare_cart_for_payment(self, cart_items: List[Dict], customer_address: Optional[Dict] = None) -> Dict:
        """
        Prepare cart data for payment processing.
        
        Args:
            cart_items: List of cart item dictionaries
            customer_address: Optional customer address for location-based calculations
            
        Returns:
            Dictionary containing payment-ready cart data
        """
        is_valid, validated_items, total_price, currency = self.validate_cart(cart_items)
        
        if not is_valid:
            raise ValueError("Cart validation failed")
        
        cart_summary = self.calculate_cart_summary(validated_items, customer_address)
        
        return {
            'items': validated_items,
            'summary': cart_summary,
            'is_valid': True,
            'payment_amount': int(cart_summary['total'] * 100),  # Amount in cents for Stripe
            'currency_code': 'usd' if currency == '$' else currency.lower(),
            'customer_address': customer_address
        }
    
    def get_cart_for_stripe(self, cart_items: List[Dict], customer_address: Optional[Dict] = None) -> Dict:
        """
        Format cart data specifically for Stripe payment processing.
        
        Args:
            cart_items: List of cart item dictionaries
            customer_address: Optional customer address for location-based calculations
            
        Returns:
            Dictionary formatted for Stripe integration
        """
        payment_data = self.prepare_cart_for_payment(cart_items, customer_address)
        
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
    
    def _calculate_tax(self, subtotal: float, customer_address: Optional[Dict] = None) -> Tuple[float, str]:
        """
        Calculate tax based on customer location or default rate.
        
        Args:
            subtotal: Cart subtotal amount
            customer_address: Optional customer address for location-based calculation
            
        Returns:
            Tuple of (tax_amount, calculation_method)
        """
        if customer_address and self._should_use_location_based_tax():
            # Future: Implement Stripe Tax API or other location-based service
            # For now, use state-based rates as example
            tax_amount = self._calculate_location_based_tax(subtotal, customer_address)
            return tax_amount, 'location_based'
        else:
            # Default tax rate (8.5% - adjust based on your business location)
            default_rate = 0.085
            tax_amount = subtotal * default_rate
            return tax_amount, 'default_rate'
    
    def _calculate_shipping(self, subtotal: float, customer_address: Optional[Dict] = None) -> float:
        """
        Calculate shipping cost based on cart value and destination.
        
        Args:
            subtotal: Cart subtotal amount
            customer_address: Optional customer address for location-based shipping
            
        Returns:
            Shipping cost
        """
        # Free shipping threshold
        free_shipping_threshold = 65.0
        
        if subtotal >= free_shipping_threshold:
            return 0.0
        
        # Future: Could implement zone-based shipping rates
        # For now, flat rate shipping
        if customer_address:
            # Could add international shipping logic here
            country = customer_address.get('country', 'US')
            if country != 'US':
                return 15.00  # International shipping
        
        return 6.50  # Domestic shipping
    
    def _should_use_location_based_tax(self) -> bool:
        """
        Determine if location-based tax calculation should be used.
        
        Returns:
            Boolean indicating if location-based tax is enabled
        """
        # Future: This could check a configuration setting
        # For now, return False to use default rates
        return False
    
    def _calculate_location_based_tax(self, subtotal: float, customer_address: Dict) -> float:
        """
        Calculate tax based on customer location (future Stripe Tax integration).
        
        Args:
            subtotal: Cart subtotal amount
            customer_address: Customer address dictionary
            
        Returns:
            Tax amount based on location
        """
        # Placeholder for future implementation
        # This would integrate with Stripe Tax API or similar service
        
        # Example state-based rates (placeholder)
        state_tax_rates = {
            'CA': 0.095,  # California
            'NY': 0.08,   # New York
            'TX': 0.0625, # Texas
            'FL': 0.06,   # Florida
            'WA': 0.065,  # Washington
        }
        
        state = customer_address.get('state', '').upper()
        tax_rate = state_tax_rates.get(state, 0.085)  # Default to 8.5%
        
        return subtotal * tax_rate
    
    def _validate_customer_address(self, customer_address: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate customer address format and completeness.
        
        Args:
            customer_address: Customer address dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not customer_address:
            return False, "Customer address is required"
        
        required_fields = ['line1', 'city', 'state', 'postal_code', 'country']
        
        for field in required_fields:
            if field not in customer_address or not customer_address[field].strip():
                return False, f"Address field '{field}' is required"
        
        # Validate country code format
        country = customer_address['country'].upper()
        if len(country) != 2:
            return False, "Country must be a 2-letter country code (e.g., 'US', 'CA')"
        
        return True, None
    
    def _format_address_for_display(self, customer_address: Dict) -> str:
        """
        Format customer address for display purposes.
        
        Args:
            customer_address: Customer address dictionary
            
        Returns:
            Formatted address string
        """
        parts = [customer_address['line1']]
        
        # Add apartment/suite/unit if provided
        if customer_address.get('line2'):
            parts.append(customer_address['line2'])
        
        # Add city, state, postal code
        city_state_zip = f"{customer_address['city']}, {customer_address['state']} {customer_address['postal_code']}"
        parts.append(city_state_zip)
        
        # Add country if not US
        if customer_address['country'].upper() != 'US':
            parts.append(customer_address['country'].upper())
        
        return '\n'.join(parts)