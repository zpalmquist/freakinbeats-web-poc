class ShoppingCart {
    constructor() {
        this.cart = [];
        this.loadCart();
    }

    loadCart() {
        try {
            this.cart = CartUtils.getCart();
            this.renderCart();
        } catch (error) {
            console.error('Error loading cart:', error);
            this.showError();
        }
    }

    renderCart() {
        const loading = document.getElementById('loading');
        const emptyCart = document.getElementById('empty-cart');
        const cartContent = document.getElementById('cart-content');
        
        loading.style.display = 'none';

        if (this.cart.length === 0) {
            emptyCart.style.display = 'block';
            cartContent.style.display = 'none';
        } else {
            emptyCart.style.display = 'none';
            cartContent.style.display = 'block';
            this.renderCartItems();
            this.updateSummary();
        }
    }

    renderCartItems() {
        const container = document.getElementById('cart-items');
        container.innerHTML = '';
        this.cart.forEach((item, index) => {
            container.appendChild(this.createCartItem(item, index));
        });
    }

    createCartItem(item, index) {
        const div = document.createElement('div');
        div.className = 'cart-item';
        
        div.innerHTML = `
            <div class="cart-item-image-container">
                ${item.image ? 
                    `<img src="${item.image}" alt="${item.title}" class="cart-item-image" onerror="this.parentElement.innerHTML='<div class=\\'no-image cart-item-image\\'>No Image</div>'">` :
                    `<div class="no-image cart-item-image">No Image</div>`
                }
            </div>
            <div class="cart-item-info">
                <div class="cart-item-title">${item.title}</div>
                <div class="cart-item-artist">${item.artist}</div>
            </div>
            <div class="cart-item-price">${CartUtils.formatPrice(item.price * item.quantity, item.currency)}</div>
            <div class="cart-item-controls">
                <div class="quantity-controls">
                    <button class="quantity-btn" onclick="cart.decreaseQuantity(${index})" ${item.quantity <= 1 ? 'disabled' : ''}>-</button>
                    <span class="quantity">${item.quantity}</span>
                    <button class="quantity-btn" onclick="cart.increaseQuantity(${index})">+</button>
                </div>
                <button class="remove-btn" onclick="cart.removeItem(${index})">Remove</button>
            </div>
        `;

        return div;
    }

    increaseQuantity(index) {
        this.cart[index].quantity += 1;
        CartUtils.saveCart(this.cart);
        this.renderCart();
    }

    decreaseQuantity(index) {
        if (this.cart[index].quantity > 1) {
            this.cart[index].quantity -= 1;
            CartUtils.saveCart(this.cart);
            this.renderCart();
        }
    }

    removeItem(index) {
        this.cart.splice(index, 1);
        CartUtils.saveCart(this.cart);
        this.renderCart();
    }

    updateSummary() {
        const totalItems = this.cart.reduce((total, item) => total + item.quantity, 0);
        const subtotal = this.cart.reduce((total, item) => total + (item.price * item.quantity), 0);

        document.getElementById('total-items').textContent = totalItems;
        document.getElementById('subtotal').textContent = CartUtils.formatPrice(subtotal);
        document.getElementById('total').textContent = CartUtils.formatPrice(subtotal);
    }

    showError() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').style.display = 'block';
    }
}

let cart;
document.addEventListener('DOMContentLoaded', () => {
    cart = new ShoppingCart();
});
