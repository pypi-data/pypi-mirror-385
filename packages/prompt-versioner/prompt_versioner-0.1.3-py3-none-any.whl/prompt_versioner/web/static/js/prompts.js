/**
 * Gestione Layout a Due Colonne per Prompts
 */

// Variabili globali per il layout a due colonne
let currentSelectedPrompt = null;
let promptsData = new Map();

const PromptsLayout = {
    allData: [],

    /**
     * Inizializza il layout a due colonne
     */
    init() {
        this.loadPrompts();
        this.setupEventListeners();
    },

    /**
     * Setup event listeners per ricerca e ordinamento
     */
    setupEventListeners() {
        // Input di ricerca
        const searchInput = document.querySelector('.search-input-minimal');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => this.searchPrompts(), 300));
        }

        // Select per ordinamento
        const sortSelect = document.querySelector('.sort-select-minimal');
        if (sortSelect) {
            sortSelect.addEventListener('change', () => this.searchPrompts());
        }
    },

    /**
     * Carica tutti i prompts dall'API
     */
    async loadPrompts() {
        try {
            const response = await fetch('/api/prompts');
            const data = await response.json();

            // Verifica che ci siano i dati corretti
            if (!data || !Array.isArray(data.prompts)) {
                throw new Error('Risposta API non valida: prompts non trovati');
            }

            this.allData = data.prompts;

            // Aggiorna le statistiche
            this.updateStats(data);

            // Popola la mappa dei dati
            promptsData.clear();
            data.prompts.forEach(prompt => {
                // Aggiungi proprietà computed necessarie
                prompt.versions = new Array(prompt.version_count || 0);
                prompt.updated_at = prompt.latest_timestamp || new Date().toISOString();
                promptsData.set(prompt.name, prompt);
            });

            // Mostra i prompts nella sidebar
            this.displayPromptsInSidebar(data.prompts);

        } catch (error) {
            console.error('Errore nel caricamento dei prompts:', error);
            this.showError('Errore nel caricamento dei prompts: ' + error.message);
        }
    },

    /**
     * Aggiorna le statistiche nell'header
     */
    updateStats(data) {
        const elements = {
            'total-prompts': data.prompts.length,
            'total-versions': data.total_versions,
            'total-cost': (data.total_cost || 0).toFixed(4),
            'total-tokens': (data.total_tokens || 0).toLocaleString(),
            'total-calls': (data.total_calls || 0).toLocaleString()
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });
    },

    /**
     * Mostra i prompts nella sidebar sinistra
     */
    displayPromptsInSidebar(prompts) {
        const promptList = document.querySelector('.prompt-list-minimal');
        if (!promptList) return;

        promptList.innerHTML = '';

        if (prompts.length === 0) {
            promptList.appendChild(this.createEmptyState({
                icon: '📄',
                title: 'Nessun prompt trovato',
                message: 'Prova a modificare i filtri di ricerca'
            }));
            this.showEmptyState();
            return;
        }

        prompts.forEach(prompt => {
            const promptElement = this.createPromptItem(prompt);
            promptList.appendChild(promptElement);
        });
    },

    /**
     * Crea un elemento prompt usando il template
     */
    createPromptItem(prompt) {
        const template = document.getElementById('prompt-item-template');
        const clone = template.content.cloneNode(true);

        const promptElement = clone.querySelector('.prompt-item-minimal');
        promptElement.dataset.promptName = prompt.name;

        // Popola i dati
        const nameElement = clone.querySelector('.prompt-name-minimal');
        nameElement.textContent = prompt.name;

        const metaElement = clone.querySelector('.prompt-meta-minimal');
        const lastUpdate = prompt.latest_timestamp || prompt.updated_at || new Date().toISOString();
        metaElement.textContent = `${prompt.version_count || 0} versions · Last: ${this.formatDate(lastUpdate)}`;

        // Aggiungi event listeners
        const deleteBtn = clone.querySelector('.delete-prompt-btn');
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            this.deletePrompt(prompt.name);
        };

        promptElement.addEventListener('click', (e) => {
            if (!e.target.closest('.btn-icon')) {
                this.selectPrompt(prompt.name);
            }
        });

        return clone;
    },

    /**
     * Seleziona un prompt e mostra le sue versioni
     */
    selectPrompt(promptName) {
        // Rimuovi selezione precedente
        document.querySelectorAll('.prompt-item-minimal.active').forEach(item => {
            item.classList.remove('active');
        });

        // Verifica che il prompt esista nei dati
        if (!promptsData.has(promptName)) {
            console.error('Prompt non trovato nei dati:', promptName);
            this.showEmptyState();
            return;
        }

        // Seleziona il nuovo prompt
        const promptElement = document.querySelector(`[data-prompt-name="${promptName}"]`);
        if (promptElement) {
            promptElement.classList.add('active');
            currentSelectedPrompt = promptName;
            this.displayVersionsForPrompt(promptName);
        }
    },

    /**
     * Mostra le versioni per il prompt selezionato
     */
    displayVersionsForPrompt(promptName) {
        const versionsPanel = document.querySelector('.versions-panel');
        const prompt = promptsData.get(promptName);

        if (!prompt || !versionsPanel) return;

        versionsPanel.innerHTML = `
            <div class="version-header">
                <h3>
                    📄 ${this.escapeHtml(promptName)}
                    <span style="font-weight: normal; color: #94a3b8; font-size: 0.9rem;">
                        ${prompt.version_count || 0} versions
                    </span>
                </h3>
            </div>
            <div class="version-list-clean" id="versionListClean"></div>
        `;

        // Mostra loading state
        const versionList = document.getElementById('versionListClean');
        versionList.appendChild(this.createLoadingState());

        // Carica le versioni dettagliate
        this.loadVersionsForPrompt(promptName);
    },

    /**
     * Carica le versioni dettagliate per un prompt
     */
    async loadVersionsForPrompt(promptName) {
        console.log('Caricamento versioni per prompt:', promptName);

        try {
            const url = `/api/prompts/${encodeURIComponent(promptName)}/versions`;
            console.log('URL richiesta:', url);

            const response = await fetch(url);
            console.log('Risposta HTTP:', response.status, response.statusText);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Errore HTTP response:', errorText);
                throw new Error(`HTTP ${response.status}: ${response.statusText}. ${errorText}`);
            }

            const versions = await response.json();
            console.log('Versioni ricevute:', versions);

            if (!Array.isArray(versions)) {
                console.error('Tipo di risposta non valido:', typeof versions, versions);

                // Se è un oggetto con proprietà error, mostra il messaggio
                if (versions && typeof versions === 'object' && versions.error) {
                    throw new Error(`Errore API: ${versions.error}`);
                }

                throw new Error('Risposta API non valida: atteso un array di versioni');
            }

            // Verifica che ogni versione abbia le proprietà minime necessarie
            const validVersions = versions.filter(version => {
                if (!version || typeof version !== 'object') {
                    console.warn('Versione non valida trovata:', version);
                    return false;
                }
                return true;
            });

            this.displayVersionsList(validVersions);
        } catch (error) {
            console.error('Errore completo nel caricamento delle versioni:', error);
            const versionList = document.getElementById('versionListClean');
            if (versionList) {
                versionList.innerHTML = '';
                versionList.appendChild(this.createErrorState({
                    title: 'Errore nel caricamento',
                    message: error.message,
                    onRetry: () => this.loadVersionsForPrompt(promptName)
                }));
            }
        }
    },

    /**
     * Mostra la lista delle versioni nel pannello destro
     */
    displayVersionsList(versions) {
        const versionList = document.getElementById('versionListClean');
        if (!versionList) return;

        versionList.innerHTML = '';

        if (!versions || versions.length === 0) {
            versionList.appendChild(this.createEmptyState({
                icon: '📝',
                title: 'Nessuna versione',
                message: 'Questo prompt non ha ancora versioni'
            }));
            return;
        }

        versions.forEach((version, index) => {
            if (!version) {
                console.warn(`Versione ${index} è undefined o null`);
                return;
            }

            const versionElement = this.createVersionItem(version);
            versionList.appendChild(versionElement);
        });
    },

    /**
     * Crea un elemento versione usando il template
     */
    createVersionItem(version) {
        const template = document.getElementById('version-item-template');
        const clone = template.content.cloneNode(true);

        // Debug: mostra i campi disponibili
        console.log(`Version v${version.version}:`, {
            id: version.id,
            version: version.version,
            model_name: version.model_name,
            prompt_name: version.prompt_name || version.name,
            full_data: version
        });

        const versionNumber = version.version || 'N/A';
        const promptName = version.prompt_name || version.name || 'N/A';
        const createdAt = version.created_at || version.timestamp || new Date().toISOString();
        const tags = Array.isArray(version.tags) ? version.tags.join(', ') : 'Nessun tag';

        // Popola i dati base
        const versionTag = clone.querySelector('.version-tag-clean');
        versionTag.textContent = `v${versionNumber}`;

        const versionMeta = clone.querySelector('.version-meta');
        versionMeta.textContent = `${this.formatDate(createdAt)} · ${tags}`;

        // Aggiungi metriche
        const metricsContainer = clone.querySelector('.version-metrics-container');
        const summary = version.summary || version.metrics_summary || {};
        const hasMetrics = summary && (summary.call_count > 0 || summary.avg_total_tokens > 0 || summary.total_cost > 0);

        if (hasMetrics) {
            metricsContainer.appendChild(this.createMetricsRow(summary));
        } else {
            metricsContainer.appendChild(this.createNoMetrics());
        }

        // Aggiungi event listeners
        const viewBtn = clone.querySelector('.view-details-btn');
        viewBtn.onclick = () => this.viewVersionDetails(promptName, versionNumber);

        const exportBtn = clone.querySelector('.export-version-btn');
        exportBtn.onclick = () => this.exportVersion(promptName, versionNumber);

        const deleteBtn = clone.querySelector('.delete-version-btn');
        deleteBtn.onclick = () => this.deleteVersion(promptName, versionNumber);

        return clone;
    },

    /**
     * Funzione di ricerca e filtro
     */
    searchPrompts() {
        const searchTerm = document.querySelector('.search-input-minimal')?.value.toLowerCase() || '';
        const sortBy = document.querySelector('.sort-select-minimal')?.value || 'name';

        // Filtra i prompts
        let filteredPrompts = this.allData.filter(prompt =>
            prompt.name.toLowerCase().includes(searchTerm)
        );

        // Ordina i prompts
        filteredPrompts.sort((a, b) => {
            switch(sortBy) {
                case 'updated':
                    const dateA = new Date(a.latest_timestamp || a.updated_at || 0);
                    const dateB = new Date(b.latest_timestamp || b.updated_at || 0);
                    return dateB - dateA;
                case 'versions':
                    return (b.version_count || 0) - (a.version_count || 0);
                default:
                    return a.name.localeCompare(b.name);
            }
        });

        // Aggiorna i dati nella mappa
        promptsData.clear();
        filteredPrompts.forEach(prompt => {
            promptsData.set(prompt.name, prompt);
        });

        this.displayPromptsInSidebar(filteredPrompts);

        // Mantieni la selezione se ancora valida
        if (currentSelectedPrompt && filteredPrompts.find(p => p.name === currentSelectedPrompt)) {
            this.selectPrompt(currentSelectedPrompt);
        } else {
            this.showEmptyState();
        }
    },

    /**
     * Visualizza dettagli di una versione specifica
     */
    async viewVersionDetails(promptName, version) {
        try {
            // Carica i dettagli completi della versione
            const response = await fetch(`/api/prompts/${encodeURIComponent(promptName)}/versions/${version}`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const versionData = await response.json();
            this.showVersionModal(versionData);

        } catch (error) {
            console.error('Errore nel caricamento dei dettagli:', error);
            alert('Errore nel caricamento dei dettagli della versione: ' + error.message);
        }
    },

    /**
     * Mostra i dettagli della versione in un modal
     */
    showVersionModal(versionData) {
        // Rimuovi modal esistente se presente
        const existingModal = document.getElementById('versionModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Crea modal usando il template
        const template = document.getElementById('version-modal-template');
        const modal = template.content.cloneNode(true);

        // Popola i dati del modal
        this.populateModalData(modal, versionData);

        // Aggiungi il modal al body
        document.body.appendChild(modal);

        // Aggiungi event listeners
        this.setupModalEventListeners();
    },

    /**
     * Popola i dati nel modal template
     */
    populateModalData(modal, versionData) {
        const systemPrompt = versionData.system_prompt || 'Nessun prompt di sistema';
        const userPrompt = versionData.user_prompt || 'Nessun prompt utente';
        const metadata = versionData.metadata ? JSON.stringify(versionData.metadata, null, 2) : 'Nessun metadata';
        const tags = Array.isArray(versionData.tags) ? versionData.tags.join(', ') : 'Nessun tag';
        const model = versionData.model_name || versionData.model || versionData.metadata?.model || 'N/A';

        // Debug: verifica dati del modal
        console.log('Modal version data:', {
            id: versionData.id,
            version: versionData.version,
            name: versionData.name || versionData.prompt_name,
            model_name: versionData.model_name,
            model_resolved: model,
            full_data: versionData
        });

        // Popola header
        modal.querySelector('.modal-prompt-name').textContent = versionData.name || versionData.prompt_name;
        modal.querySelector('.modal-version-number').textContent = `v${versionData.version}`;
        modal.querySelector('.modal-model-badge').textContent = model;

        // Popola contenuti prompt
        modal.querySelector('.system-prompt-content').textContent = systemPrompt;
        modal.querySelector('.user-prompt-content').textContent = userPrompt;

        // Popola metadata
        modal.querySelector('.creation-date').textContent = this.formatDate(versionData.timestamp || versionData.created_at);
        modal.querySelector('.tags-list').textContent = tags;
        modal.querySelector('.model-name').textContent = model;

        // Popola sezioni opzionali
        const gitCommitSection = modal.querySelector('.git-commit-section');
        if (versionData.git_commit) {
            gitCommitSection.style.display = 'block';
            modal.querySelector('.git-commit').textContent = versionData.git_commit;
        }

        const createdBySection = modal.querySelector('.created-by-section');
        if (versionData.created_by) {
            createdBySection.style.display = 'block';
            modal.querySelector('.created-by').textContent = versionData.created_by;
        }

        const metadataSection = modal.querySelector('.metadata-json-section');
        if (versionData.metadata && Object.keys(versionData.metadata).length > 0) {
            metadataSection.style.display = 'block';
            modal.querySelector('.metadata-json').textContent = metadata;
        }

        // Popola metriche
        const metricsSection = modal.querySelector('.metrics-section');
        metricsSection.appendChild(this.createModalMetricsSection(versionData));
    },

    /**
     * Crea la sezione metriche del modal
     */
    createModalMetricsSection(versionData) {
        const summary = versionData.metrics_summary || {};
        const hasMetrics = summary.call_count > 0;

        if (!hasMetrics) {
            const template = document.getElementById('modal-metrics-section-template');
            const clone = template.content.cloneNode(true);

            // Modifica per no-metrics
            const section = clone.querySelector('.modal-metrics-section');
            section.style.borderLeftColor = '#64748b';
            clone.querySelector('.metrics-title').style.color = '#64748b';
            clone.querySelector('.metrics-title').textContent = '📊 Performance Metrics';

            const container = clone.querySelector('.metrics-grid');
            container.innerHTML = '<p style="color: #64748b; margin: 0; font-style: italic; text-align: center;">No metrics data available for this version</p>';

            return clone;
        }

        const template = document.getElementById('modal-metrics-section-template');
        const clone = template.content.cloneNode(true);

        const callCount = summary.call_count || 0;
        const avgTokens = Math.round(summary.avg_total_tokens || 0);
        const totalCost = (summary.total_cost || 0).toFixed(4);
        const avgLatency = Math.round(summary.avg_latency || 0);
        const avgQuality = (summary.avg_quality || 0).toFixed(2);
        const successRate = (summary.success_rate * 100 || 0).toFixed(1);

        // Popola i valori
        clone.querySelector('.metric-calls .metric-value').textContent = callCount;
        clone.querySelector('.metric-tokens .metric-value').textContent = avgTokens;
        clone.querySelector('.metric-cost .metric-value').textContent = `€${totalCost}`;
        clone.querySelector('.metric-latency .metric-value').textContent = `${avgLatency}ms`;
        clone.querySelector('.metric-quality .metric-value').textContent = avgQuality;
        clone.querySelector('.metric-success .metric-value').textContent = `${successRate}%`;

        return clone;
    },

    /**
     * Setup event listeners per il modal
     */
    setupModalEventListeners() {
        const modal = document.getElementById('versionModal');
        if (!modal) return;

        // Chiudi modal con bottone
        const closeBtn = modal.querySelector('.modal-close-btn');
        closeBtn.onclick = () => modal.remove();

        // Chiudi modal cliccando fuori
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        // Chiudi modal con ESC
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    },

    /**
     * Elimina una versione specifica
     */
    async deleteVersion(promptName, version) {
        if (!confirm(`Sei sicuro di voler eliminare la versione ${version} del prompt "${promptName}"?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/prompts/${encodeURIComponent(promptName)}/versions/${version}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                // Ricarica le versioni per il prompt corrente
                if (currentSelectedPrompt === promptName) {
                    this.loadVersionsForPrompt(promptName);
                }
                // Ricarica anche la lista dei prompts per aggiornare i contatori
                this.loadPrompts();
            } else {
                const errorData = await response.json();
                const errorMessage = errorData.error || 'Errore durante l\'eliminazione della versione';
                alert(errorMessage);
            }
        } catch (error) {
            console.error('Errore:', error);
            alert('Errore durante l\'eliminazione della versione');
        }
    },

    /**
     * Esporta una versione specifica
     */
    async exportVersion(promptName, version) {
        try {
            await window.exportVersion(promptName, version);
        } catch (error) {
            console.error('Errore durante l\'export della versione:', error);
            alert('Errore durante l\'export della versione');
        }
    },

    /**
     * Elimina un intero prompt
     */
    async deletePrompt(promptName) {
        if (!confirm(`Sei sicuro di voler eliminare il prompt "${promptName}" e tutte le sue versioni?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/prompts/${encodeURIComponent(promptName)}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                // Rimuovi dai dati locali
                promptsData.delete(promptName);
                this.allData = this.allData.filter(p => p.name !== promptName);

                // Se era il prompt selezionato, resetta la selezione
                if (currentSelectedPrompt === promptName) {
                    currentSelectedPrompt = null;
                    this.showEmptyState();
                }

                // Ricarica la lista
                this.loadPrompts();
            } else {
                alert('Errore durante l\'eliminazione del prompt');
            }
        } catch (error) {
            console.error('Errore:', error);
            alert('Errore durante l\'eliminazione del prompt');
        }
    },

    /**
     * Mostra stato vuoto nel pannello versioni
     */
    showEmptyState() {
        const versionsPanel = document.querySelector('.versions-panel');
        if (versionsPanel) {
            versionsPanel.innerHTML = '';
            versionsPanel.appendChild(this.createEmptyState({
                icon: '📄',
                title: 'Choose a prompt',
                message: 'Select a prompt from the list to view its versions',
                className: 'versions-placeholder'
            }));
        }
    },

    /**
     * Mostra errore
     */
    showError(message) {
        const promptList = document.querySelector('.prompt-list-minimal');
        if (promptList) {
            promptList.innerHTML = '';
            promptList.appendChild(this.createErrorState({
                title: 'Errore',
                message: message
            }));
        }
    },

    // Template Helper Functions

    /**
     * Crea un loading state usando il template
     */
    createLoadingState() {
        const template = document.getElementById('loading-state-template');
        return template.content.cloneNode(true);
    },

    /**
     * Crea un empty state usando il template
     */
    createEmptyState(options) {
        const template = document.getElementById('empty-state-template');
        const clone = template.content.cloneNode(true);

        const container = clone.querySelector('.empty-state');
        if (options.className) {
            container.className = options.className;
        }

        clone.querySelector('.empty-icon').textContent = options.icon;
        clone.querySelector('.empty-title').textContent = options.title;
        clone.querySelector('.empty-message').textContent = options.message;

        return clone;
    },

    /**
     * Crea un error state usando il template
     */
    createErrorState(options) {
        const template = document.getElementById('error-state-template');
        const clone = template.content.cloneNode(true);

        clone.querySelector('.error-title').textContent = options.title;
        clone.querySelector('.error-message').textContent = options.message;

        if (options.onRetry) {
            const retryBtn = clone.querySelector('.retry-btn');
            retryBtn.onclick = options.onRetry;
        }

        return clone;
    },

    /**
     * Crea una riga di metriche usando il template
     */
    createMetricsRow(summary) {
        const template = document.getElementById('metrics-row-template');
        const clone = template.content.cloneNode(true);

        const callCount = summary.call_count || 0;
        const avgTokens = Math.round(summary.avg_total_tokens || 0);
        const totalCost = (summary.total_cost || 0).toFixed(4);
        const avgLatency = Math.round(summary.avg_latency || 0);
        const avgQuality = (summary.avg_quality || 0).toFixed(2);
        const successRate = (summary.success_rate * 100 || 0).toFixed(1);

        clone.querySelector('.metric-calls .value').textContent = callCount;
        clone.querySelector('.metric-tokens .value').textContent = avgTokens;
        clone.querySelector('.metric-cost .value').textContent = totalCost;
        clone.querySelector('.metric-latency .value').textContent = avgLatency;
        clone.querySelector('.metric-quality .value').textContent = avgQuality;
        clone.querySelector('.metric-success .value').textContent = successRate;

        return clone;
    },

    /**
     * Crea un indicatore "no metrics" usando il template
     */
    createNoMetrics() {
        const template = document.getElementById('no-metrics-template');
        return template.content.cloneNode(true);
    },

    /**
     * Utilità per formattare le date
     */
    formatDate(dateString) {
        if (!dateString) {
            return 'Data non disponibile';
        }

        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) {
                return 'Data non valida';
            }

            return date.toLocaleDateString('it-IT', {
                day: '2-digit',
                month: '2-digit',
                year: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            console.warn('Errore nel formato data:', dateString, error);
            return 'Data non valida';
        }
    },

    /**
     * Utilità per troncare il testo
     */
    truncateText(text, maxLength) {
        if (!text || typeof text !== 'string') {
            return 'Contenuto non disponibile';
        }

        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    /**
     * Utilità per escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Debounce per la ricerca
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Mantengo la compatibilità con il codice esistente
const Prompts = {
    async load() {
        PromptsLayout.init();
    }
};

// Espongo le funzioni globalmente per i nuovi layout handlers
window.PromptsLayout = PromptsLayout;
