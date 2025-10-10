class DiscogsCollage {
    constructor() {
        this.data = [];
        this.loadData();
    }

    async loadData() {
        try {
            const response = await fetch('/api/data');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            this.data = await response.json();
            this.renderCollage();
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError();
        }
    }

    renderCollage() {
        const grid = document.getElementById('collage-grid');
        const loading = document.getElementById('loading');
        
        loading.style.display = 'none';
        grid.style.display = 'grid';

        this.data.forEach((item, index) => {
            grid.appendChild(this.createVinylItem(item, index));
        });
    }

    createVinylItem(item, index) {
        const div = document.createElement('div');
        div.className = 'vinyl-item';
        
        const imageUrl = item.image_uri?.trim();
        
        div.innerHTML = `
            <div class="vinyl-image-container">
                ${imageUrl ? 
                    `<img src="${imageUrl}" alt="${item.release_title || 'Vinyl'}" class="vinyl-image" loading="lazy" onerror="this.parentElement.innerHTML='<div class=&quot;no-image vinyl-image&quot;>No Image</div>'">` :
                    `<div class="no-image vinyl-image">No Image</div>`
                }
            </div>
            <div class="vinyl-info">
                <div class="vinyl-title">${item.release_title || 'Unknown Title'}</div>
                <div class="vinyl-artist">${item.artist_names || 'Unknown Artist'}</div>
                <div class="vinyl-price">${CartUtils.formatPrice(item.price_value, item.price_currency)}</div>
                <div class="vinyl-condition">${item.condition || 'Unknown'}</div>
            </div>
        `;

        div.addEventListener('click', () => {
            window.location.href = `/detail/${index}`;
        });

        return div;
    }

    showError() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new DiscogsCollage();
});
