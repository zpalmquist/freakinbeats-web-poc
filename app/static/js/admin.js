/**
 * Admin Panel JavaScript for Access Logs
 * Handles data fetching, filtering, pagination, and modal display
 */

class AdminPanel {
    constructor() {
        this.currentPage = 1;
        this.currentFilters = {
            search: '',
            method: '',
            status: '',
            per_page: 50
        };
        this.currentData = null;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadLogs();
    }

    bindEvents() {
        // Filter controls
        document.getElementById('apply-filters').addEventListener('click', () => this.applyFilters());
        document.getElementById('clear-filters').addEventListener('click', () => this.clearFilters());
        
        // Search input with debounce
        let searchTimeout;
        document.getElementById('search').addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.applyFilters();
            }, 500);
        });

        // Per page change
        document.getElementById('per-page').addEventListener('change', () => this.applyFilters());
        
        // Method and status filters
        document.getElementById('method').addEventListener('change', () => this.applyFilters());
        document.getElementById('status').addEventListener('change', () => this.applyFilters());
        
        // Refresh button
        document.getElementById('refresh-logs').addEventListener('click', () => this.loadLogs());
        
        // Export button
        document.getElementById('export-logs').addEventListener('click', () => this.exportLogs());
        
        // Sync Discogs button
        document.getElementById('sync-discogs-btn').addEventListener('click', () => this.syncDiscogs());
        
        // Clear Label Cache button
        document.getElementById('clear-label-cache-btn').addEventListener('click', () => this.clearLabelCache());
        
        // Modal controls
        document.getElementById('close-modal').addEventListener('click', () => this.closeModal());
        document.getElementById('log-modal').addEventListener('click', (e) => {
            if (e.target.id === 'log-modal') {
                this.closeModal();
            }
        });
        
        // Sync modal controls
        document.getElementById('close-sync-modal').addEventListener('click', () => this.closeSyncModal());
        document.getElementById('sync-modal').addEventListener('click', (e) => {
            if (e.target.id === 'sync-modal') {
                this.closeSyncModal();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
                this.closeSyncModal();
            }
            if (e.key === 'r' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                this.loadLogs();
            }
        });
    }

    async loadLogs(page = 1) {
        this.showLoading(true);
        this.hideError();

        try {
            const params = new URLSearchParams({
                page: page,
                per_page: this.currentFilters.per_page,
                ...(this.currentFilters.search && { search: this.currentFilters.search }),
                ...(this.currentFilters.method && { method: this.currentFilters.method }),
                ...(this.currentFilters.status && { status: this.currentFilters.status })
            });

            const response = await fetch(`/admin/access-logs?${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.currentData = data;
            this.currentPage = page;
            
            this.renderLogs(data.logs);
            this.renderPagination(data.pagination);
            this.updateStats(data.logs);
            
        } catch (error) {
            console.error('Error loading logs:', error);
            this.showError(`Failed to load access logs: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    renderLogs(logs) {
        const tbody = document.getElementById('logs-tbody');
        tbody.innerHTML = '';

        if (logs.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" style="text-align: center; padding: 40px; color: #666;">
                        No access logs found matching your criteria.
                    </td>
                </tr>
            `;
            return;
        }

        logs.forEach(log => {
            const row = this.createLogRow(log);
            tbody.appendChild(row);
        });
    }

    createLogRow(log) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${log.id}</td>
            <td>${this.formatTimestamp(log.timestamp)}</td>
            <td><span class="method-badge method-${log.method}">${log.method}</span></td>
            <td>
                <div class="truncated" title="${log.path}">${this.escapeHtml(log.path)}</div>
                ${log.query_string ? `<small style="color: #666;">?${this.escapeHtml(log.query_string)}</small>` : ''}
            </td>
            <td><span class="status-badge status-${log.status_code}">${log.status_code}</span></td>
            <td>${log.response_time_ms ? `${log.response_time_ms.toFixed(1)}ms` : '-'}</td>
            <td>${this.escapeHtml(log.ip_address || '-')}</td>
            <td>
                <div class="truncated" title="${log.user_agent || ''}">
                    ${this.escapeHtml(this.truncateUserAgent(log.user_agent))}
                </div>
            </td>
            <td>
                <button class="btn btn-secondary" onclick="adminPanel.showLogDetails(${log.id})" style="padding: 5px 10px; font-size: 0.8rem;">
                    View
                </button>
            </td>
        `;
        return row;
    }

    renderPagination(pagination) {
        const paginationContainer = document.getElementById('pagination');
        
        if (pagination.pages <= 1) {
            paginationContainer.innerHTML = `
                <div class="pagination-info">
                    Showing ${pagination.total} log${pagination.total !== 1 ? 's' : ''}
                </div>
            `;
            return;
        }

        const startItem = (pagination.page - 1) * pagination.per_page + 1;
        const endItem = Math.min(pagination.page * pagination.per_page, pagination.total);

        paginationContainer.innerHTML = `
            <div class="pagination-info">
                Showing ${startItem}-${endItem} of ${pagination.total} log${pagination.total !== 1 ? 's' : ''}
            </div>
            <div class="pagination-controls">
                <button onclick="adminPanel.loadLogs(${pagination.prev_num})" ${!pagination.has_prev ? 'disabled' : ''}>
                    ← Previous
                </button>
                <span class="current-page">Page ${pagination.page} of ${pagination.pages}</span>
                <button onclick="adminPanel.loadLogs(${pagination.next_num})" ${!pagination.has_next ? 'disabled' : ''}>
                    Next →
                </button>
            </div>
        `;
    }

    updateStats(logs) {
        if (!logs || logs.length === 0) {
            document.getElementById('total-requests').textContent = '0';
            document.getElementById('avg-response-time').textContent = '-';
            document.getElementById('error-rate').textContent = '-';
            document.getElementById('unique-ips').textContent = '0';
            return;
        }

        const totalRequests = logs.length;
        const avgResponseTime = logs.reduce((sum, log) => sum + (log.response_time_ms || 0), 0) / totalRequests;
        const errorCount = logs.filter(log => log.status_code >= 400).length;
        const errorRate = ((errorCount / totalRequests) * 100).toFixed(1);
        const uniqueIPs = new Set(logs.map(log => log.ip_address).filter(ip => ip)).size;

        document.getElementById('total-requests').textContent = totalRequests.toLocaleString();
        document.getElementById('avg-response-time').textContent = avgResponseTime.toFixed(1);
        document.getElementById('error-rate').textContent = errorRate;
        document.getElementById('unique-ips').textContent = uniqueIPs;
    }

    showLogDetails(logId) {
        const log = this.currentData.logs.find(l => l.id === logId);
        if (!log) return;

        const modalBody = document.getElementById('modal-body');
        modalBody.innerHTML = this.createLogDetailHTML(log);
        
        document.getElementById('log-modal').classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    createLogDetailHTML(log) {
        return `
            <div class="log-detail">
                <div class="log-detail-row">
                    <div class="log-detail-label">ID:</div>
                    <div class="log-detail-value">${log.id}</div>
                </div>
                <div class="log-detail-row">
                    <div class="log-detail-label">Timestamp:</div>
                    <div class="log-detail-value">${this.formatTimestamp(log.timestamp, true)}</div>
                </div>
                <div class="log-detail-row">
                    <div class="log-detail-label">Method:</div>
                    <div class="log-detail-value">${log.method}</div>
                </div>
                <div class="log-detail-row">
                    <div class="log-detail-label">Path:</div>
                    <div class="log-detail-value">${this.escapeHtml(log.path)}</div>
                </div>
                ${log.query_string ? `
                <div class="log-detail-row">
                    <div class="log-detail-label">Query String:</div>
                    <div class="log-detail-value">${this.escapeHtml(log.query_string)}</div>
                </div>
                ` : ''}
                <div class="log-detail-row">
                    <div class="log-detail-label">Full URL:</div>
                    <div class="log-detail-value">${this.escapeHtml(log.full_url || '-')}</div>
                </div>
                <div class="log-detail-row">
                    <div class="log-detail-label">Status Code:</div>
                    <div class="log-detail-value">${log.status_code}</div>
                </div>
                <div class="log-detail-row">
                    <div class="log-detail-label">Response Time:</div>
                    <div class="log-detail-value">${log.response_time_ms ? `${log.response_time_ms.toFixed(2)} ms` : '-'}</div>
                </div>
                <div class="log-detail-row">
                    <div class="log-detail-label">IP Address:</div>
                    <div class="log-detail-value">${this.escapeHtml(log.ip_address || '-')}</div>
                </div>
                <div class="log-detail-row">
                    <div class="log-detail-label">User Agent:</div>
                    <div class="log-detail-value">${this.escapeHtml(log.user_agent || '-')}</div>
                </div>
                ${log.referrer ? `
                <div class="log-detail-row">
                    <div class="log-detail-label">Referrer:</div>
                    <div class="log-detail-value">${this.escapeHtml(log.referrer)}</div>
                </div>
                ` : ''}
                ${log.endpoint ? `
                <div class="log-detail-row">
                    <div class="log-detail-label">Endpoint:</div>
                    <div class="log-detail-value">${this.escapeHtml(log.endpoint)}</div>
                </div>
                ` : ''}
            </div>
        `;
    }

    closeModal() {
        document.getElementById('log-modal').classList.add('hidden');
        document.body.style.overflow = '';
    }

    async syncDiscogs() {
        const syncBtn = document.getElementById('sync-discogs-btn');
        const originalText = syncBtn.textContent;
        
        try {
            // Update button state
            syncBtn.disabled = true;
            syncBtn.classList.add('syncing');
            syncBtn.textContent = '🔄 Syncing...';
            
            // Show sync modal with loading state
            this.showSyncModal('Starting Discogs synchronization...', true);
            
            const response = await fetch('/admin/sync-discogs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Show success message with stats and detailed listings
                const stats = data.stats;
                const successMessage = `
                    <div class="sync-success">
                        <h4>✅ Sync Completed Successfully!</h4>
                        <div class="sync-stats">
                            <div class="stat-item">
                                <strong>Total Processed:</strong> ${stats.total || 0} listings
                            </div>
                            <div class="stat-item">
                                <strong>Added:</strong> ${stats.added || 0} new listings
                            </div>
                            <div class="stat-item">
                                <strong>Updated:</strong> ${stats.updated || 0} existing listings
                            </div>
                            <div class="stat-item">
                                <strong>Removed:</strong> ${stats.removed || 0} obsolete listings
                            </div>
                        </div>
                        <p class="sync-message">${data.message}</p>
                        
                        ${this.renderListingDetails(stats)}
                    </div>
                `;
                this.showSyncModal(successMessage, false);
            } else {
                // Show error message
                const errorMessage = `
                    <div class="sync-error">
                        <h4>❌ Sync Failed</h4>
                        <p class="error-text">${data.error || 'Unknown error occurred'}</p>
                    </div>
                `;
                this.showSyncModal(errorMessage, false);
            }
            
        } catch (error) {
            console.error('Sync error:', error);
            const errorMessage = `
                <div class="sync-error">
                    <h4>❌ Sync Failed</h4>
                    <p class="error-text">Network error: ${error.message}</p>
                </div>
            `;
            this.showSyncModal(errorMessage, false);
        } finally {
            // Reset button state
            syncBtn.disabled = false;
            syncBtn.classList.remove('syncing');
            syncBtn.textContent = originalText;
        }
    }

    showSyncModal(content, isLoading = false) {
        const modalBody = document.getElementById('sync-modal-body');
        
        if (isLoading) {
            modalBody.innerHTML = `
                <div class="sync-loading">
                    <div class="spinner"></div>
                    <p>${content}</p>
                    <p class="sync-note">This may take several minutes depending on your inventory size...</p>
                </div>
            `;
        } else {
            modalBody.innerHTML = content;
        }
        
        document.getElementById('sync-modal').classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    closeSyncModal() {
        document.getElementById('sync-modal').classList.add('hidden');
        document.body.style.overflow = '';
    }

    renderListingDetails(stats) {
        let html = '';
        
        // Added listings
        if (stats.added_listings && stats.added_listings.length > 0) {
            html += `
                <div class="listing-section">
                    <h5 class="listing-section-title added">➕ Added Listings (${stats.added_listings.length})</h5>
                    <div class="listing-list">
                        ${stats.added_listings.map(listing => this.renderListingItem(listing, 'added')).join('')}
                    </div>
                </div>
            `;
        }
        
        // Updated listings
        if (stats.updated_listings && stats.updated_listings.length > 0) {
            html += `
                <div class="listing-section">
                    <h5 class="listing-section-title updated">🔄 Updated Listings (${stats.updated_listings.length})</h5>
                    <div class="listing-list">
                        ${stats.updated_listings.map(listing => this.renderListingItem(listing, 'updated')).join('')}
                    </div>
                </div>
            `;
        }
        
        // Removed listings
        if (stats.removed_listings && stats.removed_listings.length > 0) {
            html += `
                <div class="listing-section">
                    <h5 class="listing-section-title removed">➖ Removed Listings (${stats.removed_listings.length})</h5>
                    <div class="listing-list">
                        ${stats.removed_listings.map(listing => this.renderListingItem(listing, 'removed')).join('')}
                    </div>
                </div>
            `;
        }
        
        return html;
    }

    renderListingItem(listing, type) {
        const price = listing.price ? `${listing.currency || '$'}${listing.price.toFixed(2)}` : 'No price';
        const condition = listing.condition ? `(${listing.condition})` : '';
        const format = listing.format ? `[${listing.format}]` : '';
        
        let changesHtml = '';
        if (type === 'updated' && listing.changed_fields) {
            changesHtml = this.renderFieldChanges(listing.changed_fields);
        }
        
        return `
            <div class="listing-item listing-${type}">
                <div class="listing-info">
                    <div class="listing-artist">${this.escapeHtml(listing.artist)}</div>
                    <div class="listing-title">${this.escapeHtml(listing.title)}</div>
                    <div class="listing-meta">
                        ${this.escapeHtml(format)} ${this.escapeHtml(condition)} - ${price}
                    </div>
                    ${changesHtml}
                </div>
                <div class="listing-id">Discogs Listing ID: ${listing.listing_id}</div>
            </div>
        `;
    }

    renderFieldChanges(changedFields) {
        const changes = Object.entries(changedFields).map(([field, values]) => {
            const oldValue = this.formatFieldValue(values.old);
            const newValue = this.formatFieldValue(values.new);
            const fieldName = this.getFieldDisplayName(field);
            
            return `
                <div class="field-change">
                    <span class="field-name">${fieldName}:</span>
                    <span class="field-change-values">
                        <span class="old-value">${oldValue}</span>
                        <span class="change-arrow">→</span>
                        <span class="new-value">${newValue}</span>
                    </span>
                </div>
            `;
        }).join('');
        
        return `
            <div class="listing-changes">
                <div class="changes-header">Changed:</div>
                ${changes}
            </div>
        `;
    }

    formatFieldValue(value) {
        if (value === null || value === undefined || value === '') {
            return '<em>empty</em>';
        }
        if (typeof value === 'number') {
            return value.toFixed(2);
        }
        return this.escapeHtml(String(value));
    }

    getFieldDisplayName(field) {
        const fieldNames = {
            'price_value': 'Price',
            'price_currency': 'Currency',
            'condition': 'Condition',
            'sleeve_condition': 'Sleeve Condition',
            'status': 'Status',
            'shipping_price': 'Shipping Price',
            'shipping_currency': 'Shipping Currency',
            'weight': 'Weight',
            'format_quantity': 'Quantity',
            'external_id': 'External ID',
            'location': 'Location',
            'comments': 'Comments',
            'release_title': 'Release Title',
            'release_year': 'Release Year',
            'artist_names': 'Artist',
            'primary_artist': 'Primary Artist',
            'label_names': 'Label',
            'primary_label': 'Primary Label',
            'format_names': 'Format',
            'primary_format': 'Primary Format',
            'genres': 'Genres',
            'styles': 'Styles',
            'country': 'Country',
            'catalog_number': 'Catalog Number',
            'barcode': 'Barcode',
            'master_id': 'Master ID',
            'release_community_have': 'Community Have',
            'release_community_want': 'Community Want'
        };
        return fieldNames[field] || field;
    }

    async clearLabelCache() {
        const cacheBtn = document.getElementById('clear-label-cache-btn');
        const originalText = cacheBtn.textContent;
        
        try {
            // Update button state
            cacheBtn.disabled = true;
            cacheBtn.classList.add('syncing');
            cacheBtn.textContent = '🗑️ Clearing...';
            
            const response = await fetch('/admin/clear-label-cache', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                const successMessage = `
                    <div class="sync-success">
                        <h4>✅ Label Cache Cleared Successfully!</h4>
                        <p class="sync-message">${data.message}</p>
                        <p class="sync-note">Label overviews will be regenerated when users visit detail pages.</p>
                    </div>
                `;
                this.showSyncModal(successMessage, false);
            } else {
                const errorMessage = `
                    <div class="sync-error">
                        <h4>❌ Cache Clear Failed</h4>
                        <p class="error-text">${data.error || 'Unknown error occurred'}</p>
                    </div>
                `;
                this.showSyncModal(errorMessage, false);
            }
            
        } catch (error) {
            console.error('Cache clear error:', error);
            const errorMessage = `
                <div class="sync-error">
                    <h4>❌ Cache Clear Failed</h4>
                    <p class="error-text">Network error: ${error.message}</p>
                </div>
            `;
            this.showSyncModal(errorMessage, false);
        } finally {
            // Reset button state
            cacheBtn.disabled = false;
            cacheBtn.classList.remove('syncing');
            cacheBtn.textContent = originalText;
        }
    }

    applyFilters() {
        this.currentFilters = {
            search: document.getElementById('search').value.trim(),
            method: document.getElementById('method').value,
            status: document.getElementById('status').value,
            per_page: parseInt(document.getElementById('per-page').value)
        };
        
        this.loadLogs(1); // Reset to first page
    }

    clearFilters() {
        document.getElementById('search').value = '';
        document.getElementById('method').value = '';
        document.getElementById('status').value = '';
        document.getElementById('per-page').value = '50';
        
        this.applyFilters();
    }

    async exportLogs() {
        try {
            const params = new URLSearchParams({
                per_page: 10000, // Large number to get all logs
                ...(this.currentFilters.search && { search: this.currentFilters.search }),
                ...(this.currentFilters.method && { method: this.currentFilters.method }),
                ...(this.currentFilters.status && { status: this.currentFilters.status })
            });

            const response = await fetch(`/admin/access-logs?${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.downloadCSV(data.logs, 'access-logs.csv');
            
        } catch (error) {
            console.error('Error exporting logs:', error);
            this.showError(`Failed to export logs: ${error.message}`);
        }
    }

    downloadCSV(logs, filename) {
        const headers = [
            'ID', 'Timestamp', 'Method', 'Path', 'Query String', 'Full URL',
            'Status Code', 'Response Time (ms)', 'IP Address', 'User Agent', 'Referrer', 'Endpoint'
        ];

        const csvContent = [
            headers.join(','),
            ...logs.map(log => [
                log.id,
                `"${log.timestamp}"`,
                log.method,
                `"${(log.path || '').replace(/"/g, '""')}"`,
                `"${(log.query_string || '').replace(/"/g, '""')}"`,
                `"${(log.full_url || '').replace(/"/g, '""')}"`,
                log.status_code,
                log.response_time_ms || '',
                `"${(log.ip_address || '').replace(/"/g, '""')}"`,
                `"${(log.user_agent || '').replace(/"/g, '""')}"`,
                `"${(log.referrer || '').replace(/"/g, '""')}"`,
                `"${(log.endpoint || '').replace(/"/g, '""')}"`
            ].join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        if (show) {
            loading.classList.remove('hidden');
        } else {
            loading.classList.add('hidden');
        }
    }

    showError(message) {
        const errorElement = document.getElementById('error-message');
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');
        
        // Auto-hide error after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    hideError() {
        document.getElementById('error-message').classList.add('hidden');
    }

    // Utility functions
    formatTimestamp(timestamp, detailed = false) {
        if (!timestamp) return '-';
        
        const date = new Date(timestamp);
        if (detailed) {
            return date.toLocaleString('en-US', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            });
        }
        
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return date.toLocaleDateString();
    }

    truncateUserAgent(userAgent) {
        if (!userAgent) return '-';
        if (userAgent.length <= 50) return userAgent;
        return userAgent.substring(0, 47) + '...';
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize admin panel when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminPanel = new AdminPanel();
});
