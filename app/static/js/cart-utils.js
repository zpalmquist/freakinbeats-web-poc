// Shared cart utilities
class CartUtils {
    /**
     * Standard cart item structure:
     * {
     *   listing_id: string,      // Required: Discogs listing ID
     *   title: string,           // Required: Album/release title
     *   artist: string,          // Required: Artist name
     *   price: number,           // Required: Price as number
     *   currency: string,        // Required: Currency symbol/code
     *   quantity: number,        // Required: Quantity (positive integer)
     *   image: string|null       // Optional: Image URL
     * }
     */

    static getCart() {
        const cart = localStorage.getItem('vinyl-cart');
        return cart ? JSON.parse(cart) : [];
    }

    static saveCart(cart) {
        // Validate cart items before saving
        const validatedCart = cart.filter(item => this.isValidCartItem(item));
        localStorage.setItem('vinyl-cart', JSON.stringify(validatedCart));
        this.updateCartCount();
    }

    static isValidCartItem(item) {
        const requiredFields = ['listing_id', 'title', 'artist', 'price', 'currency', 'quantity'];
        
        // Check all required fields exist
        for (const field of requiredFields) {
            if (!(field in item) || item[field] === null || item[field] === undefined) {
                console.warn(`Invalid cart item: missing ${field}`, item);
                return false;
            }
        }

        // Validate quantity is positive integer
        if (!Number.isInteger(item.quantity) || item.quantity < 1) {
            console.warn('Invalid cart item: quantity must be positive integer', item);
            return false;
        }

        // Validate price is a valid number
        if (typeof item.price !== 'number' || isNaN(item.price) || item.price < 0) {
            console.warn('Invalid cart item: price must be a valid non-negative number', item);
            return false;
        }

        return true;
    }

    static createCartItem(listing) {
        /**
         * Create a standardized cart item from a listing object
         * @param {Object} listing - The listing object from the API
         * @returns {Object} Standardized cart item
         */
        return {
            listing_id: listing.listing_id,
            title: listing.release_title || 'Unknown Title',
            artist: listing.artist_names || 'Unknown Artist',
            price: parseFloat(listing.price_value) || 0,
            currency: listing.price_currency || '$',
            quantity: 1,
            image: listing.image_uri || null,
            available_quantity: listing.quantity || 1
        };
    }

    static addToCart(listing, quantity = 1) {
        /**
         * Add item to cart or update quantity if it already exists
         * @param {Object} listing - The listing object from the API
         * @param {number} quantity - Quantity to add (default: 1)
         */
        const cart = this.getCart();
        const existingItem = cart.find(item => item.listing_id === listing.listing_id);
        
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            const cartItem = this.createCartItem(listing);
            cartItem.quantity = quantity;
            cart.push(cartItem);
        }
        
        this.saveCart(cart);
    }

    static removeFromCart(listingId) {
        /**
         * Remove item completely from cart
         * @param {string} listingId - The listing ID to remove
         */
        const cart = this.getCart();
        const filteredCart = cart.filter(item => item.listing_id !== listingId);
        this.saveCart(filteredCart);
    }

    static updateQuantity(listingId, quantity) {
        /**
         * Update quantity of specific cart item
         * @param {string} listingId - The listing ID to update
         * @param {number} quantity - New quantity (if 0 or less, item is removed)
         */
        const cart = this.getCart();
        const item = cart.find(item => item.listing_id === listingId);
        
        if (!item) return;
        
        if (quantity <= 0) {
            this.removeFromCart(listingId);
        } else {
            item.quantity = quantity;
            this.saveCart(cart);
        }
    }

    static clearCart() {
        /**
         * Remove all items from cart
         */
        localStorage.removeItem('vinyl-cart');
        this.updateCartCount();
    }

    static updateCartCount() {
        const cart = this.getCart();
        const count = cart.reduce((total, item) => total + item.quantity, 0);
        const countEl = document.getElementById('cart-count');
        if (countEl) countEl.textContent = count;
    }

    static formatPrice(value, currency = '$') {
        if (!value || value === '') return 'Price N/A';
        const numValue = parseFloat(value);
        if (isNaN(numValue)) return 'Price N/A';
        
        // Handle currency symbol formatting
        const symbol = currency === 'USD' ? '$' : currency;
        return `${symbol}${numValue.toFixed(2)}`;
    }
}

// Update cart count on page load
document.addEventListener('DOMContentLoaded', () => {
    CartUtils.updateCartCount();
});
