class VinylDetail {
    constructor() {
        this.item = null;
        this.videos = [];
        this.currentVideoIndex = 0;
        this.id = this.getIdFromUrl();
        this.loadData();
    }

    getIdFromUrl() {
        const path = window.location.pathname;
        const match = path.match(/\/detail\/(\d+)/);
        return match ? parseInt(match[1]) : null;
    }

    async loadData() {
        try {
            // Try to get detailed data with videos using the database ID
            const detailResponse = await fetch(`/api/detail/${this.id + 1}`);
            if (detailResponse.ok) {
                const detailData = await detailResponse.json();
                this.item = detailData;
                this.videos = detailData.videos || [];
                this.renderDetail();
                return;
            }
            
            // Fallback to basic listing data
            const basicResponse = await fetch(`/api/data/${this.id}`);
            if (basicResponse.ok) {
                const basicData = await basicResponse.json();
                this.item = basicData;
                this.videos = [];
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

        // Render video player if videos are available
        this.renderVideoPlayer();

        document.getElementById('add-to-cart').addEventListener('click', () => this.addToCart());
    }

    renderVideoPlayer() {
        const videoContainer = document.getElementById('video-player-container');
        const detailContent = document.getElementById('detail-content');
        const detailContainer = document.querySelector('.detail-container');
        
        if (this.videos && this.videos.length > 0) {
            videoContainer.style.display = 'block';
            detailContent.classList.add('has-videos');
            detailContainer.classList.add('has-videos');
            
            // Set up main video
            this.loadVideo(0);
            
            // Create thumbnails
            this.renderVideoThumbnails();
        } else {
            videoContainer.style.display = 'none';
            detailContent.classList.remove('has-videos');
            detailContainer.classList.remove('has-videos');
        }
    }

    loadVideo(index) {
        if (!this.videos || !this.videos[index]) return;
        
        const video = this.videos[index];
        const iframe = document.getElementById('main-video-iframe');
        
        // Convert YouTube URL to embed URL
        const embedUrl = `https://www.youtube.com/embed/${video.youtube_id}`;
        iframe.src = embedUrl;
        
        this.currentVideoIndex = index;
        this.updateActiveThumbnail();
    }

    renderVideoThumbnails() {
        const container = document.getElementById('video-thumbnails');
        
        if (!this.videos || this.videos.length <= 1) {
            container.style.display = 'none';
            return;
        }
        
        container.style.display = 'flex';
        container.innerHTML = '';
        
        this.videos.forEach((video, index) => {
            const thumbnail = this.createVideoThumbnail(video, index);
            container.appendChild(thumbnail);
        });
    }

    createVideoThumbnail(video, index) {
        const div = document.createElement('div');
        div.className = 'video-thumbnail';
        div.dataset.index = index;
        
        // Format duration
        const duration = this.formatDuration(video.duration);
        
        div.innerHTML = `
            <img src="${video.thumbnail}" alt="${video.title}" class="thumb-image" loading="lazy">
            <div class="thumb-info">
                <div class="thumb-title">${video.title || 'Untitled'}</div>
                ${duration ? `<div class="thumb-duration">${duration}</div>` : ''}
            </div>
        `;
        
        div.addEventListener('click', () => this.loadVideo(index));
        
        return div;
    }

    updateActiveThumbnail() {
        document.querySelectorAll('.video-thumbnail').forEach((thumb, index) => {
            if (index === this.currentVideoIndex) {
                thumb.classList.add('active');
            } else {
                thumb.classList.remove('active');
            }
        });
    }

    formatDuration(seconds) {
        if (!seconds || seconds === 0) return '';
        
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    addToCart() {
        const cart = CartUtils.getCart();
        const existingItem = cart.find(item => item.id === this.id);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({
                id: this.id,
                listing_id: this.item.listing_id,
                title: this.item.release_title || 'Unknown Title',
                artist: this.item.artist_names || 'Unknown Artist',
                price: parseFloat(this.item.price_value) || 0,
                currency: this.item.price_currency || '$',
                image: this.item.image_uri || null,
                quantity: 1
            });
        }
        
        CartUtils.saveCart(cart);
        
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
