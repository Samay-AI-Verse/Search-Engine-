class AISearch {
    constructor() {
        this.searchInput = document.getElementById('searchInput');
        this.searchBtn = document.getElementById('searchBtn');
        this.resultsContainer = document.getElementById('resultsContainer');
        this.welcomeScreen = document.getElementById('welcomeScreen');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.aiOverview = document.getElementById('aiOverview');
        this.aiContent = document.getElementById('aiContent');
        this.resultCount = document.getElementById('resultCount');
        this.processingTime = document.getElementById('processingTime');
        this.resultsStats = document.getElementById('resultsStats');
        this.suggestionsDropdown = document.getElementById('suggestionsDropdown');
        this.suggestionsList = document.getElementById('suggestionsList');
        this.searchBar = document.getElementById('searchBar');
        this.aiModeBtn = document.getElementById('aiModeBtn');
        
        // New Chatbot elements
        this.chatContainer = document.getElementById('chatContainer');
        this.userMessageText = document.getElementById('userMessageText');

        this.apiUrl = 'http://localhost:8000/api';
        this.isSearching = false;
        this.aiMode = true;
        this.suggestions = [];
        this.selectedSuggestionIndex = -1;

        this.init();
    }

    init() {
        this.aiModeBtn.classList.add('active');
        this.setupEventListeners();
        this.setupQuickButtons();
        this.checkHealth();
        setTimeout(() => this.searchInput.focus(), 300);
    }

    setupEventListeners() {
        this.searchBtn.addEventListener('click', () => this.performSearch());
        this.aiModeBtn.addEventListener('click', () => this.toggleAiMode());

        this.searchInput.addEventListener('input', () => {
            const query = this.searchInput.value.trim();
            if (query.length > 1) {
                this.getSuggestions(query);
            } else {
                this.hideSuggestions();
            }
            this.selectedSuggestionIndex = -1;
        });

        this.searchInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                if (this.selectedSuggestionIndex >= 0 && this.suggestions[this.selectedSuggestionIndex]) {
                    this.searchInput.value = this.suggestions[this.selectedSuggestionIndex];
                }
                this.hideSuggestions();
                this.performSearch();
            } else if (event.key === 'ArrowDown') {
                event.preventDefault();
                this.selectedSuggestionIndex = Math.min(this.selectedSuggestionIndex + 1, this.suggestions.length - 1);
                this.highlightSuggestion();
            } else if (event.key === 'ArrowUp') {
                event.preventDefault();
                this.selectedSuggestionIndex = Math.max(this.selectedSuggestionIndex - 1, -1);
                this.highlightSuggestion();
            } else if (event.key === 'Escape') {
                this.hideSuggestions();
            }
        });

        document.addEventListener('click', (event) => {
            if (!this.searchBar.contains(event.target) && !this.suggestionsDropdown.contains(event.target)) {
                this.hideSuggestions();
            }
        });
    }

    toggleAiMode() {
        this.aiMode = !this.aiMode;
        this.aiModeBtn.classList.toggle('active', this.aiMode);
        if (!this.aiMode) {
            this.aiOverview.style.display = 'none';
            if (this.chatContainer) {
                this.chatContainer.style.display = 'none';
            }
        }
    }

    highlightSuggestion() {
        const items = this.suggestionsList.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            item.style.background = index === this.selectedSuggestionIndex ? '#f1f3f4' : 'transparent';
            if (index === this.selectedSuggestionIndex) {
                this.searchInput.value = this.suggestions[index];
            }
        });
    }

    async getSuggestions(query) {
        try {
            const localSuggestions = this.getLocalSuggestions(query);
            const response = await fetch(`${this.apiUrl}/suggestions?q=${encodeURIComponent(query)}`);
            let apiSuggestions = [];
            if (response.ok) {
                const data = await response.json();
                apiSuggestions = data.suggestions || [];
            }
            this.suggestions = [...new Set([...localSuggestions, ...apiSuggestions])];
            this.renderSuggestions(this.suggestions.slice(0, 8));
        } catch (error) {
            console.error('Suggestions error:', error);
            const localSuggestions = this.getLocalSuggestions(query);
            this.suggestions = localSuggestions;
            this.renderSuggestions(localSuggestions.slice(0, 8));
        }
    }

    getLocalSuggestions(query) {
        const q = query.toLowerCase();
        const suggestions = [
            'w3schools python', 'w3schools html', 'w3schools css', 'w3schools javascript',
            'python tutorial', 'javascript tutorial', 'html tutorial', 'css tutorial',
            'react tutorial', 'node.js tutorial', 'mongodb tutorial', 'sql tutorial',
            'git tutorial', 'docker tutorial', 'kubernetes tutorial', 'aws tutorial',
            'machine learning tutorial', 'deep learning tutorial', 'artificial intelligence tutorial',
            'web development tutorial', 'app development tutorial', 'game development tutorial',
            'stackoverflow', 'github', 'reddit', 'medium', 'dev.to', 'hacker news',
            'latest tech news', 'how to build ai app', 'google search tips'
        ];
        return suggestions.filter((suggestion) => suggestion.toLowerCase().includes(q));
    }

    renderSuggestions(suggestions) {
        if (suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        this.suggestionsList.innerHTML = '';
        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.innerHTML = `
                <i class="fas fa-magnifying-glass"></i>
                <span class="suggestion-text">${this.escapeHtml(suggestion)}</span>
                <span class="suggestion-type">search</span>
            `;
            item.addEventListener('click', () => {
                this.searchInput.value = suggestion;
                this.hideSuggestions();
                this.performSearch();
            });
            item.addEventListener('mouseenter', () => {
                this.selectedSuggestionIndex = index;
                this.highlightSuggestion();
            });
            this.suggestionsList.appendChild(item);
        });

        this.suggestionsDropdown.style.display = 'block';
        this.suggestionsDropdown.classList.add('active');
    }

    hideSuggestions() {
        this.suggestionsDropdown.style.display = 'none';
        this.suggestionsDropdown.classList.remove('active');
        this.selectedSuggestionIndex = -1;
    }

    setupQuickButtons() {
        document.querySelectorAll('.quick-btn').forEach((button) => {
            button.addEventListener('click', () => {
                this.searchInput.value = button.dataset.query;
                this.performSearch();
            });
        });
    }

    async checkHealth() {
        try {
            const response = await fetch(`${this.apiUrl}/health`);
            if (response.ok) {
                console.log('AI Search ready');
            }
        } catch (error) {
            console.log('Backend not running');
        }
    }

    async performSearch() {
        const query = this.searchInput.value.trim();
        if (!query || this.isSearching) return;

        this.isSearching = true;
        document.body.classList.add('has-results');
        this.welcomeScreen.style.display = 'none';
        this.aiOverview.style.display = 'none';
        
        // Hide the new chat container when starting a search
        if (this.chatContainer) {
            this.chatContainer.style.display = 'none';
        }
        
        this.resultsStats.style.display = 'none';
        this.resultsContainer.innerHTML = '';
        this.loadingIndicator.style.display = 'block';
        this.hideSuggestions();

        try {
            const response = await fetch(`${this.apiUrl}/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query,
                    max_results: 15,
                    use_semantic: true,
                    use_sentiment: true,
                    ai_mode: this.aiMode
                })
            });

            if (!response.ok) throw new Error('Search failed');

            const data = await response.json();
            this.renderResults(data);
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Failed to search. Please try again.');
        } finally {
            this.isSearching = false;
            this.loadingIndicator.style.display = 'none';
        }
    }

    renderResults(data) {
        this.resultsStats.style.display = 'flex';
        this.resultCount.textContent = `About ${data.total_results || 0} results`;
        this.processingTime.textContent = `(${((data.processing_time || 0) * 1000).toFixed(0)} ms)`;

        // Updated Chatbot AI Mode logic
        if (this.aiMode && data.ai_summary && data.ai_summary.summary) {
            if (this.chatContainer) this.chatContainer.style.display = 'flex';
            this.aiOverview.style.display = 'block';
            if (this.userMessageText) this.userMessageText.textContent = this.searchInput.value;
            this.aiContent.innerHTML = `<p>${this.escapeHtml(data.ai_summary.summary)}</p>`;
        } else if (this.aiMode && data.results && data.results.length > 0) {
            if (this.chatContainer) this.chatContainer.style.display = 'flex';
            this.aiOverview.style.display = 'block';
            if (this.userMessageText) this.userMessageText.textContent = this.searchInput.value;
            this.aiContent.innerHTML = this.createLocalAiOverview(data.results);
        }

        if (data.results && data.results.length > 0) {
            data.results.forEach((result, index) => {
                const item = this.createResultItem(result, index);
                this.resultsContainer.appendChild(item);
            });
        } else {
            this.resultsContainer.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #5f6368;">
                    <i class="fas fa-magnifying-glass" style="font-size: 40px; color: #ccc; display: block; margin-bottom: 15px;"></i>
                    <p>No results found for "${this.escapeHtml(this.searchInput.value)}"</p>
                </div>
            `;
        }
    }

    createLocalAiOverview(results) {
        const topResults = results.slice(0, 3);
        const sources = [...new Set(topResults.map((result) => result.source || result.domain || 'Web'))].slice(0, 3);
        const best = topResults[0];
        const chips = sources.map((source) => `<span class="ai-chip">${this.escapeHtml(source)}</span>`).join('');

        return `
            <div class="ai-fallback">
                <p><strong>${this.escapeHtml(best.title)}</strong></p>
                <p>${this.escapeHtml(best.snippet || 'Here are the most relevant results for your search.')}</p>
                <div class="ai-chips">${chips}</div>
            </div>
        `;
    }

    createResultItem(result, index) {
        const item = document.createElement('div');
        item.className = 'result-item';
        item.style.animationDelay = `${index * 0.04}s`;

        const domain = result.domain || 'web';
        const displayUrl = domain.length > 42 ? `${domain.substring(0, 42)}...` : domain;
        const iconHtml = result.icon
            ? `<img src="${this.escapeAttribute(result.icon)}" class="result-icon" onerror="this.style.display='none'" alt="">`
            : '<i class="fas fa-globe" style="color: #5f6368; font-size: 14px;"></i>';

        let sentimentHtml = '';
        if (result.sentiment && result.sentiment.sentiment) {
            const sentiment = result.sentiment.sentiment;
            sentimentHtml = `<span class="sentiment ${this.escapeAttribute(sentiment)}">${this.escapeHtml(sentiment)}</span>`;
        }

        const relevance = result.relevance_score
            ? `<span class="relevance">${(result.relevance_score * 100).toFixed(0)}% match</span>`
            : '';

        item.innerHTML = `
            <div class="result-url">
                <span class="result-icon-wrapper">${iconHtml}</span>
                <span class="domain">${this.escapeHtml(displayUrl)}</span>
            </div>
            <div class="result-title">
                <a href="${this.escapeAttribute(result.link)}" target="_blank" rel="noopener noreferrer">${this.escapeHtml(result.title)}</a>
            </div>
            <div class="result-snippet">${this.escapeHtml(result.snippet || 'No description available')}</div>
            <div class="result-meta">
                ${sentimentHtml}
                ${relevance}
                <span class="source">${this.escapeHtml(result.source || 'Web')}</span>
            </div>
        `;

        return item;
    }

    showError(message) {
        this.resultsContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #d93025;">
                <i class="fas fa-circle-exclamation" style="font-size: 40px; display: block; margin-bottom: 15px;"></i>
                <p>${this.escapeHtml(message)}</p>
            </div>
        `;
    }

    escapeHtml(value) {
        const div = document.createElement('div');
        div.textContent = value || '';
        return div.innerHTML;
    }

    escapeAttribute(value) {
        return this.escapeHtml(value).replace(/"/g, '&quot;');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new AISearch();
    console.log('AI Search ready');
});