// Shared cart utilities
class CartUtils {
    static getCart() {
        const cart = localStorage.getItem('vinyl-cart');
        return cart ? JSON.parse(cart) : [];
    }

    static saveCart(cart) {
        localStorage.setItem('vinyl-cart', JSON.stringify(cart));
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
        return `${currency}${numValue.toFixed(2)}`;
    }
}

// Update cart count on page load
document.addEventListener('DOMContentLoaded', () => {
    CartUtils.updateCartCount();
});
