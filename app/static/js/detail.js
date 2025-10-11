class VinylDetail {
    constructor() {
        this.item = null;
        this.itemIndex = this.getItemIndexFromUrl();
        this.loadData();
    }

    getItemIndexFromUrl() {
        const path = window.location.pathname;
        const match = path.match(/\/detail\/(\d+)/);
        return match ? parseInt(match[1]) : null;
    }

    async loadData() {
        try {
            const response = await fetch('/api/data');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            
            if (this.itemIndex !== null && data[this.itemIndex]) {
                this.item = data[this.itemIndex];
                this.renderDetail();
            } else {
                this.showError();
            }
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError();
        }
    }

    renderDetail() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('detail-content').style.display = 'grid';

        document.getElementById('vinyl-title').textContent = this.item.release_title || 'Unknown Title';
        document.getElementById('vinyl-artist').textContent = this.item.artist_names || 'Unknown Artist';
        document.getElementById('vinyl-price').textContent = CartUtils.formatPrice(this.item.price_value);
        document.getElementById('vinyl-label').textContent = this.item.label_names || 'Unknown';
        document.getElementById('vinyl-year').textContent = this.item.release_year || 'Unknown';
        document.getElementById('vinyl-condition').textContent = this.item.condition || 'Unknown';
        document.getElementById('vinyl-sleeve').textContent = this.item.sleeve_condition || 'Unknown';
        document.getElementById('vinyl-comments').textContent = this.item.comments || 'No comments available';

        const imageContainer = document.getElementById('vinyl-image-container');
        const imageUrl = this.item.image_uri?.trim();
        
        if (imageUrl) {
            imageContainer.innerHTML = `<img src="${imageUrl}" alt="${this.item.release_title || 'Vinyl'}" class="vinyl-image" onerror="this.parentElement.innerHTML='<div class=&quot;no-image vinyl-image&quot;>No Image Available</div>'">`;
        } else {
            imageContainer.innerHTML = '<div class="vinyl-image no-image">No Image Available</div>';
        }

        document.getElementById('add-to-cart').addEventListener('click', () => this.addToCart());
    }

    addToCart() {
        // Use the new utility method for consistent cart management
        CartUtils.addToCart(this.item, 1);
        
        const button = document.getElementById('add-to-cart');
        const originalText = button.textContent;
        button.textContent = 'Added to Cart!';
        button.disabled = true;
        
        setTimeout(() => {
            button.textContent = originalText;
            button.disabled = false;
        }, 2000);
    }

    showError() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new VinylDetail();
});
