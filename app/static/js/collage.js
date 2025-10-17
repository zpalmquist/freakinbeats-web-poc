class DiscogsCollage {
    constructor() {
        this.allData = [];
        this.filteredData = [];
        this.facets = {};
        this.activeFilters = {
            query: '',
            artist: null,
            label: null,
            year: null,
            condition: null,
            sleeve_condition: null
        };
        this.searchTimeout = null;
        this.init();
    }

    async init() {
        await Promise.all([
            this.loadData(),
            this.loadFacets()
        ]);
        this.setupEventListeners();
        this.renderCollage();
        this.showFilterSection();
    }

    async loadData() {
        try {
            const response = await fetch('/api/data');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            this.allData = await response.json();
            this.filteredData = [...this.allData];
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError();
        }
    }

    async loadFacets() {
        try {
            const response = await fetch('/api/facets');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            this.facets = await response.json();
            this.renderFacets();
        } catch (error) {
            console.error('Error loading facets:', error);
        }
    }

    renderFacets() {
        // Render artist filters
        this.renderFacetButtons('artist', this.facets.artists, 'artist-buttons');
        
        // Render label filters
        this.renderFacetButtons('label', this.facets.labels, 'label-buttons');
        
        // Render year filters
        this.renderFacetButtons('year', this.facets.years, 'year-buttons');
        
        // Render condition filters
        this.renderFacetButtons('condition', this.facets.conditions, 'condition-buttons');
        
        // Render sleeve condition filters
        this.renderFacetButtons('sleeve_condition', this.facets.sleeve_conditions, 'sleeve-buttons');
    }

    renderFacetButtons(filterType, facetData, containerId) {
        const container = document.getElementById(containerId);
        if (!container || !facetData) return;

        container.innerHTML = '';
        
        // Store all buttons for search filtering
        const buttons = facetData.map(facet => {
            const button = document.createElement('button');
            button.className = 'filter-btn';
            button.dataset.filterType = filterType;
            button.dataset.filterValue = facet.value;
            button.innerHTML = `
                <span class="filter-btn-label">${facet.value}</span>
                <span class="filter-btn-count">${facet.count}</span>
            `;
            button.addEventListener('click', () => this.toggleFilter(filterType, facet.value));
            container.appendChild(button);
            return button;
        });

        // Store for search filtering
        container.dataset.allButtons = JSON.stringify(facetData);
    }

    toggleFilter(filterType, value) {
        const mappedType = filterType === 'sleeve_condition' ? 'sleeve_condition' : filterType;
        
        if (this.activeFilters[mappedType] === value) {
            // Deactivate filter
            this.activeFilters[mappedType] = null;
        } else {
            // Activate filter
            this.activeFilters[mappedType] = value;
        }
        
        this.updateFilterButtons();
        this.updateActiveFiltersDisplay();
        this.applyFilters();
    }

    updateFilterButtons() {
        // Update all filter buttons to show active state
        document.querySelectorAll('.filter-btn').forEach(btn => {
            const filterType = btn.dataset.filterType;
            const filterValue = btn.dataset.filterValue;
            const mappedType = filterType === 'sleeve_condition' ? 'sleeve_condition' : filterType;
            
            if (this.activeFilters[mappedType] === filterValue) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    updateActiveFiltersDisplay() {
        const activeFiltersDiv = document.getElementById('active-filters');
        const filterTagsDiv = document.getElementById('filter-tags');
        
        const hasActiveFilters = Object.entries(this.activeFilters).some(([key, value]) => 
            key !== 'query' && value !== null
        ) || this.activeFilters.query !== '';

        if (hasActiveFilters) {
            activeFiltersDiv.style.display = 'flex';
            filterTagsDiv.innerHTML = '';

            // Add search query tag
            if (this.activeFilters.query) {
                this.addFilterTag('Search', this.activeFilters.query, 'query');
            }

            // Add other filter tags
            Object.entries(this.activeFilters).forEach(([key, value]) => {
                if (key !== 'query' && value !== null) {
                    const label = key === 'sleeve_condition' ? 'Sleeve' : 
                                  key.charAt(0).toUpperCase() + key.slice(1);
                    this.addFilterTag(label, value, key);
                }
            });
        } else {
            activeFiltersDiv.style.display = 'none';
        }
    }

    addFilterTag(label, value, filterType) {
        const filterTagsDiv = document.getElementById('filter-tags');
        const tag = document.createElement('span');
        tag.className = 'filter-tag';
        tag.innerHTML = `
            ${label}: ${value}
            <button class="filter-tag-remove" data-filter-type="${filterType}">✕</button>
        `;
        
        tag.querySelector('.filter-tag-remove').addEventListener('click', (e) => {
            e.stopPropagation();
            if (filterType === 'query') {
                this.activeFilters.query = '';
                document.getElementById('search-input').value = '';
            } else {
                this.activeFilters[filterType] = null;
            }
            this.updateFilterButtons();
            this.updateActiveFiltersDisplay();
            this.applyFilters();
        });
        
        filterTagsDiv.appendChild(tag);
    }

    async applyFilters() {
        try {
            // Build query parameters
            const params = new URLSearchParams();
            
            if (this.activeFilters.query) {
                params.append('q', this.activeFilters.query);
            }
            if (this.activeFilters.artist) {
                params.append('artist', this.activeFilters.artist);
            }
            if (this.activeFilters.label) {
                params.append('label', this.activeFilters.label);
            }
            if (this.activeFilters.year) {
                params.append('year', this.activeFilters.year);
            }
            if (this.activeFilters.condition) {
                params.append('condition', this.activeFilters.condition);
            }
            if (this.activeFilters.sleeve_condition) {
                params.append('sleeve_condition', this.activeFilters.sleeve_condition);
            }

            const url = params.toString() ? `/api/filter?${params.toString()}` : '/api/data';
            const response = await fetch(url);
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            this.filteredData = await response.json();
            this.renderCollage();
            this.updateResultsCount();
        } catch (error) {
            console.error('Error applying filters:', error);
        }
    }

    updateResultsCount() {
        const resultsCount = document.getElementById('results-count');
        const total = this.allData.length;
        const filtered = this.filteredData.length;
        
        if (filtered === total) {
            resultsCount.textContent = `Showing all ${total} records`;
        } else {
            resultsCount.textContent = `Showing ${filtered} of ${total} records`;
        }
    }

    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('search-input');
        const clearSearchBtn = document.getElementById('clear-search');
        
        searchInput.addEventListener('input', (e) => {
            const value = e.target.value.trim();
            
            // Show/hide clear button
            clearSearchBtn.style.display = value ? 'block' : 'none';
            
            // Debounce search
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.activeFilters.query = value;
                this.updateActiveFiltersDisplay();
                this.applyFilters();
            }, 300);
        });

        clearSearchBtn.addEventListener('click', () => {
            searchInput.value = '';
            clearSearchBtn.style.display = 'none';
            this.activeFilters.query = '';
            this.updateActiveFiltersDisplay();
            this.applyFilters();
        });

        // Clear all filters button
        document.getElementById('clear-all-filters').addEventListener('click', () => {
            this.clearAllFilters();
        });

        // Filter toggle buttons
        document.querySelectorAll('.filter-toggle').forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                const filterType = e.currentTarget.dataset.filter;
                const filterOptions = document.getElementById(`${filterType}-filters`);
                const arrow = e.currentTarget.querySelector('.filter-arrow');
                
                if (filterOptions.style.display === 'none') {
                    // Close all other filters
                    document.querySelectorAll('.filter-options').forEach(opt => {
                        opt.style.display = 'none';
                    });
                    document.querySelectorAll('.filter-arrow').forEach(arr => {
                        arr.textContent = '▼';
                    });
                    
                    // Open this filter
                    filterOptions.style.display = 'block';
                    arrow.textContent = '▲';
                } else {
                    filterOptions.style.display = 'none';
                    arrow.textContent = '▼';
                }
            });
        });

        // Filter search inputs
        document.querySelectorAll('.filter-search-input').forEach(input => {
            input.addEventListener('input', (e) => {
                const filterType = e.target.dataset.filter;
                const searchTerm = e.target.value.toLowerCase();
                this.filterFacetButtons(filterType, searchTerm);
            });
        });
    }

    filterFacetButtons(filterType, searchTerm) {
        const containerId = `${filterType}-buttons`;
        const container = document.getElementById(containerId);
        if (!container) return;

        const allButtons = container.querySelectorAll('.filter-btn');
        
        allButtons.forEach(button => {
            const label = button.querySelector('.filter-btn-label').textContent.toLowerCase();
            if (label.includes(searchTerm)) {
                button.style.display = 'flex';
            } else {
                button.style.display = 'none';
            }
        });
    }

    clearAllFilters() {
        // Reset all filters
        this.activeFilters = {
            query: '',
            artist: null,
            label: null,
            year: null,
            condition: null,
            sleeve_condition: null
        };

        // Clear search input
        document.getElementById('search-input').value = '';
        document.getElementById('clear-search').style.display = 'none';

        // Clear filter search inputs
        document.querySelectorAll('.filter-search-input').forEach(input => {
            input.value = '';
        });

        // Reset all facet buttons visibility
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.style.display = 'flex';
        });

        this.updateFilterButtons();
        this.updateActiveFiltersDisplay();
        this.applyFilters();
    }

    showFilterSection() {
        document.getElementById('filter-section').style.display = 'block';
        this.updateResultsCount();
    }

    renderCollage() {
        const grid = document.getElementById('collage-grid');
        const loading = document.getElementById('loading');
        
        loading.style.display = 'none';
        grid.style.display = 'grid';
        grid.innerHTML = '';

        this.filteredData.forEach((item, index) => {
            // Find the original index in allData for correct detail page linking
            const originalIndex = this.allData.findIndex(d => d.listing_id === item.listing_id);
            grid.appendChild(this.createVinylItem(item, originalIndex));
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
                <div class="vinyl-price">${CartUtils.formatPrice(item.price_value)}</div>
                <div class="vinyl-condition">Media: ${item.condition || 'Unknown'}</div>
                <div class="vinyl-condition">Sleeve: ${item.sleeve_condition || 'Unknown'}</div>
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
