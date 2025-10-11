class CheckoutPage {
    constructor() {
        this.cart = [];
        this.orderData = null;
        this.init();
    }

    init() {
        this.loadCartAndValidate();
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.getElementById('back-to-cart').addEventListener('click', () => {
            window.location.href = '/cart';
        });

        document.getElementById('complete-order').addEventListener('click', () => {
            this.showMessage('Order completion will be available after Stripe integration!', 'info');
        });
    }

    async loadCartAndValidate() {
        try {
            this.cart = CartUtils.getCart();
            
            if (this.cart.length === 0) {
                this.showEmptyCart();
                return;
            }

            // Validate cart with server
            const response = await fetch('/checkout/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    items: this.cart.map(item => ({
                        listing_id: item.listing_id,
                        quantity: item.quantity
                    }))
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to validate cart');
            }

            this.orderData = await response.json();
            this.renderCheckout();

        } catch (error) {
            console.error('Checkout validation error:', error);
            this.showError(error.message);
        }
    }

    renderCheckout() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('checkout-content').style.display = 'block';
        
        this.renderOrderItems();
        this.renderOrderTotal();
    }

    renderOrderItems() {
        const container = document.getElementById('order-items');
        container.innerHTML = '';

        this.orderData.items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'order-item';
            
            div.innerHTML = `
                <div class="order-item-info">
                    <div class="order-item-title">${item.title}</div>
                    <div class="order-item-artist">${item.artist}</div>
                    <div class="order-item-quantity">Qty: ${item.quantity}</div>
                </div>
                <div class="order-item-price">
                    ${CartUtils.formatPrice(item.item_total, item.currency)}
                </div>
            `;
            
            container.appendChild(div);
        });
    }

    renderOrderTotal() {
        const total = this.orderData.total;
        const currency = this.orderData.currency;
        
        document.getElementById('order-subtotal').textContent = CartUtils.formatPrice(total, currency);
        document.getElementById('order-total').textContent = CartUtils.formatPrice(total, currency);
    }

    showEmptyCart() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('empty-cart').style.display = 'block';
    }

    showError(message) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error-message').textContent = message;
        document.getElementById('error').style.display = 'block';
    }

    showMessage(message, type = 'info') {
        // Simple alert for now - can be enhanced with toast notifications later
        alert(message);
    }
}

// Initialize checkout when page loads
let checkout;
document.addEventListener('DOMContentLoaded', () => {
    checkout = new CheckoutPage();
});