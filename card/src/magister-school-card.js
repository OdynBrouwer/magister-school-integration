import { LitElement, html, css } from 'lit';

class MagisterSchoolCard extends LitElement {
  static properties = {
    hass: {},
    config: {},
    _data: { state: true },
    _kindNaam: { state: true }
  };

  static styles = css`
    :host {
      display: block;
      width: 100%;
    }
    
    .card {
      padding: 20px;
      background: var(--card-background-color);
      border-radius: var(--ha-card-border-radius, 12px);
      box-shadow: var(--ha-card-box-shadow, 0px 2px 4px rgba(0,0,0,0.1));
      width: 100%;
      box-sizing: border-box;
    }
    
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
      flex-wrap: wrap;
      gap: 16px;
    }
    
    .header h1 {
      margin: 0;
      font-size: 1.8em;
      color: var(--primary-text-color);
      flex-grow: 1;
    }
    
    .kind-info {
      background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
      color: white;
      padding: 12px 20px;
      border-radius: 10px;
      margin-bottom: 20px;
    }
    
    .kind-info h2 {
      margin: 0;
      font-size: 1.4em;
    }
    
    .kind-meta {
      display: flex;
      gap: 16px;
      margin-top: 8px;
      font-size: 0.9em;
      opacity: 0.9;
    }
    
    .layout-selector {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    
    .layout-btn {
      padding: 10px 16px;
      border: 1px solid var(--primary-color);
      background: transparent;
      color: var(--primary-color);
      border-radius: 8px;
      cursor: pointer;
      font-size: 0.9em;
      transition: all 0.3s ease;
    }
    
    .layout-btn:hover {
      background: var(--primary-color);
      color: white;
      transform: translateY(-2px);
    }
    
    .layout-btn.active {
      background: var(--primary-color);
      color: white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    /* Responsive Grid Layouts */
    .grid-1 { 
      display: grid; 
      grid-template-columns: 1fr; 
      gap: 20px; 
      width: 100%;
    }
    
    .grid-2 { 
      display: grid; 
      grid-template-columns: repeat(2, 1fr); 
      gap: 20px; 
      width: 100%;
    }
    
    .grid-3 { 
      display: grid; 
      grid-template-columns: repeat(3, 1fr); 
      gap: 20px; 
      width: 100%;
    }
    
    .grid-4 { 
      display: grid; 
      grid-template-columns: repeat(4, 1fr); 
      gap: 20px; 
      width: 100%;
    }
    
    .grid-5 { 
      display: grid; 
      grid-template-columns: repeat(5, 1fr); 
      gap: 20px; 
      width: 100%;
    }
    
    .grid-6 { 
      display: grid; 
      grid-template-columns: repeat(6, 1fr); 
      gap: 20px; 
      width: 100%;
    }
    
    .grid-auto { 
      display: grid; 
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
      gap: 20px; 
      width: 100%;
    }

    /* Custom Column Layout */
    .column-container {
      display: flex;
      gap: 20px;
      width: 100%;
    }

    .column {
      display: flex;
      flex-direction: column;
      gap: 20px;
      flex: 1;
      min-width: 0;
    }

    @media (max-width: 1200px) {
      .column-container {
        flex-wrap: wrap;
      }
      
      .column {
        flex: 1 1 calc(50% - 10px);
        min-width: 300px;
      }
    }

    @media (max-width: 768px) {
      .column-container {
        flex-direction: column;
      }
      
      .column {
        flex: 1 1 100%;
        min-width: 100%;
      }
    }
    
    @media (max-width: 1200px) {
      .grid-3 {
        grid-template-columns: repeat(2, 1fr);
      }
      
      .grid-4,
      .grid-5,
      .grid-6 {
        grid-template-columns: repeat(3, 1fr);
      }
    }
    
    @media (max-width: 768px) {
      .card {
        padding: 16px;
      }
      
      .header {
        flex-direction: column;
        align-items: flex-start;
      }
      
      .header h1 {
        font-size: 1.5em;
      }
      
      .layout-selector {
        width: 100%;
        justify-content: center;
      }
      
      .grid-2,
      .grid-3,
      .grid-4,
      .grid-5,
      .grid-6 {
        grid-template-columns: 1fr;
      }
      
      .grid-auto {
        grid-template-columns: 1fr;
      }
      
      .kind-meta {
        flex-direction: column;
        gap: 4px;
      }
    }
    
    @media (max-width: 480px) {
      .card {
        padding: 12px;
      }
      
      .layout-btn {
        padding: 8px 12px;
        font-size: 0.8em;
      }
    }
    
    /* Widget Styling */
    .widget {
      background: var(--secondary-background-color);
      border-radius: 12px;
      padding: 20px;
      border-left: 6px solid var(--primary-color);
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      height: fit-content;
      min-height: 200px;
      display: flex;
      flex-direction: column;
    }
    
    .widget:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    .widget-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--divider-color);
    }
    
    .widget-title {
      font-size: 1.3em;
      font-weight: bold;
      color: var(--primary-text-color);
      margin: 0;
    }
    
    .widget-icon {
      font-size: 1.4em;
      background: var(--primary-color);
      color: white;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
    }
    
    .widget-content {
      flex-grow: 1;
      overflow-y: auto;
      max-height: 400px;
    }
    
    /* Specifieke Widget Styles */
    .cijfer-item, .afspraak-item, .opdracht-item, .mededeling-item {
      padding: 12px;
      border-left: 4px solid var(--accent-color);
      margin-bottom: 12px;
      background: var(--primary-background-color);
      border-radius: 8px;
      transition: background-color 0.2s ease;
    }
    
    .cijfer-item:hover, .afspraak-item:hover, .opdracht-item:hover {
      background: var(--secondary-background-color);
    }

    /* Uitval styling */
    .afspraak-item.uitval {
      border-left-color: var(--error-color, #f44336);
      background: rgba(244, 67, 54, 0.08);
      opacity: 0.85;
      position: relative;
    }

    .afspraak-item.uitval .uitval-label {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: var(--error-color, #f44336);
      color: white;
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 0.78em;
      font-weight: bold;
      margin-bottom: 4px;
      letter-spacing: 0.04em;
    }

    .afspraak-item.uitval .les-tijd,
    .afspraak-item.uitval .les-omschrijving {
      text-decoration: line-through;
      opacity: 0.6;
    }

    /* Gewijzigd styling */
    .afspraak-item.gewijzigd {
      border-left-color: var(--warning-color, #ff9800);
      background: rgba(255, 152, 0, 0.08);
      position: relative;
    }

    .afspraak-item.gewijzigd .uitval-label {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: var(--warning-color, #ff9800);
      color: white;
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 0.78em;
      font-weight: bold;
      margin-bottom: 4px;
      letter-spacing: 0.04em;
    }
    
    .vak { 
      font-weight: bold; 
      font-size: 1.1em;
    }
    
    .waarde { 
      font-size: 1.3em; 
      color: var(--accent-color);
      font-weight: bold;
    }
    
    .cijfer-item .wf {
      font-size: 0.85em;
      opacity: 0.75;
      margin-left: 4px;
    }
    
    .tijd { 
      font-size: 0.9em; 
      color: var(--secondary-text-color);
      margin-top: 4px;
    }
    
    .empty-state {
      text-align: center;
      color: var(--secondary-text-color);
      font-style: italic;
      padding: 40px 20px;
      font-size: 1.1em;
    }
    
    /* Scrollbar styling */
    .widget-content::-webkit-scrollbar {
      width: 6px;
    }
    
    .widget-content::-webkit-scrollbar-track {
      background: var(--secondary-background-color);
      border-radius: 3px;
    }
    
    .widget-content::-webkit-scrollbar-thumb {
      background: var(--primary-color);
      border-radius: 3px;
    }
    
    .widget-content::-webkit-scrollbar-thumb:hover {
      background: var(--accent-color);
    }
    
    /* Badge voor belangrijke items */
    .badge {
      background: var(--error-color);
      color: white;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.8em;
      margin-left: 8px;
    }
    
    .badge-warning {
      background: var(--warning-color);
    }

    .badge-boeking {
      background: var(--disabled-text-color, #9e9e9e);
      opacity: 0.9;
    }

    .afspraak-item.boeking {
      border-left-color: var(--disabled-text-color, #9e9e9e);
      opacity: 0.85;
    }
    
    .badge-success {
      background: var(--success-color);
    }

    .schoolweek-row {
      display: grid;
      grid-template-columns: minmax(90px, 1fr) minmax(120px, 1fr);
      gap: 12px;
      align-items: center;
      padding: 10px 0;
      border-bottom: 1px solid var(--divider-color);
    }

    .schoolweek-row:last-child {
      border-bottom: 0;
    }

    .schoolweek-day {
      color: var(--primary-text-color);
      font-weight: 600;
    }

    .schoolweek-time {
      color: var(--secondary-text-color);
      text-align: right;
    }
  `;

  constructor() {
    super();
    this._data = null;
    this._kindNaam = '';
    this._layout = 'grid-auto';
  }

  setConfig(config) {
    this.config = {
      layout: 'auto',
      show_widgets: ['stats', 'schooltijden', 'volgende_schooldag', 'rooster_vandaag', 'huiswerk', 'cijfers', 'voortgangscijfers', 'opdrachten'],
      widget_columns: null,
      hide_layout_selector: false,
      hide_kind_info: false,
      hide_boekingen: false,
      ...config
    };
    this._layout = this._normalizeLayout(this.config.layout);
  }

  _normalizeLayout(layout) {
    if (!layout || layout === 'auto') return 'grid-auto';
    const allowed = ['grid-1', 'grid-2', 'grid-3', 'grid-4', 'grid-5', 'grid-6', 'grid-auto'];
    return allowed.includes(layout) ? layout : 'grid-auto';
  }

  connectedCallback() {
    super.connectedCallback();
    this._fetchData();
  }

  _fetchData() {
    if (!this.hass) return;
    
    const entity = this.hass.states[this.config.entity];
    if (entity) {
      this._data = entity.attributes;
      this._extractKindInfo();
    }
  }

  _extractKindInfo() {
    if (!this._data) return;

    const entityId = this.config.entity || '';
    this._kindNaam =
      this._data.naam ||
      this._data.kind_naam ||
      entityId.replace('sensor.magister_', '').replace(/_/g, ' ');
  }

  /**
   * Converteert een UTC datetime string ("2026-04-14 08:35:00") naar lokale tijd "HH:MM".
   * De Magister sensor slaat tijden op in UTC; we converteren naar de lokale tijdzone
   * van de browser zodat de weergave klopt met de werkelijke lestijden.
   */
  _formatTijd(dateStr) {
    if (!dateStr) return '';
    // Vervang spatie door 'T' zodat JS het als lokale tijd behandelt wanneer er geen timezone is opgegeven.
    const localStr = dateStr.replace(' ', 'T');
    const date = new Date(localStr);
    if (isNaN(date.getTime())) return dateStr.substr(11, 5);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
  }

  /**
   * Geeft de lokale datum terug als "YYYY-MM-DD" voor een datumtijd-waarde.
   * De Magister data bevat al lokale tijd (omgezet door datum() functie).
   * We gebruiken substr(0,10) om de datum direct uit de string te halen,
   * zodat we geen last hebben van JS Date timezone-offsets.
   */
  _getLocaleDateStr(dateStr) {
    if (!dateStr) return '';
    return dateStr.substr(0, 10);
  }

  /**
   * Geeft de datum van vandaag in lokale YYYY-MM-DD formaat (string).
   * Gebruikt toLocaleDateString('en-CA') die altijd YYYY-MM-DD retourneert.
   */
  _getVandaag() {
    return new Date().toLocaleDateString('en-CA');
  }

  _getMorgen() {
    const morgen = new Date();
    morgen.setDate(morgen.getDate() + 1);
    return morgen.toLocaleDateString('en-CA');
  }

  _setLayout(layout) {
    this._layout = layout;
  }

  render() {
    if (!this._data) {
      return html`
        <div class="card">
          <div class="empty-state">📚 School data laden...</div>
        </div>
      `;
    }

    const useColumnLayout = this.config.widget_columns && Object.keys(this.config.widget_columns).length > 0;

    return html`
      <div class="card">
        <div class="header">
          <h1>🏫 School Dashboard</h1>
          ${!useColumnLayout && !this.config.hide_layout_selector ? html`
            <div class="layout-selector">
              <button class="layout-btn ${this._layout === 'grid-1' ? 'active' : ''}" 
                      @click=${() => this._setLayout('grid-1')}>1 Kolom</button>
              <button class="layout-btn ${this._layout === 'grid-2' ? 'active' : ''}" 
                      @click=${() => this._setLayout('grid-2')}>2 Kolommen</button>
              <button class="layout-btn ${this._layout === 'grid-3' ? 'active' : ''}" 
                      @click=${() => this._setLayout('grid-3')}>3 Kolommen</button>
              <button class="layout-btn ${this._layout === 'grid-auto' ? 'active' : ''}" 
                      @click=${() => this._setLayout('grid-auto')}>Auto Fit</button>
            </div>
          ` : ''}
        </div>
        
        ${this.config.hide_kind_info ? '' : this._renderKindInfo()}
        
        ${useColumnLayout ? this._renderColumnLayout() : html`
          <div class="${this._layout}">
            ${this._renderWidgets()}
          </div>
        `}
      </div>
    `;
  }

  _renderKindInfo() {
    if (!this._kindNaam) return html``;

    return html`
      <div class="kind-info">
        <h2>${this._kindNaam}</h2>
        <div class="kind-meta">
          ${this._data.stamnummer ? html`<span>🎫 Stamnummer: ${this._data.stamnummer}</span>` : ''}
          ${this._data.klas ? html`<span>🏫 Klas: ${this._data.klas}</span>` : ''}
          ${this._data.profiel ? html`<span>🧭 Profiel: ${this._data.profiel}</span>` : ''}
          ${this._data.geboortedatum ? html`<span>🎂 Geboortedatum: ${this._data.geboortedatum}</span>` : ''}
          <span>🕒 Laatste update: ${this.hass.states[this.config.entity].state}</span>
        </div>
      </div>
    `;
  }

  _renderColumnLayout() {
    const columns = this.config.widget_columns;
    const columnKeys = Object.keys(columns).sort();

    return html`
      <div class="column-container">
        ${columnKeys.map(columnKey => html`
          <div class="column">
            ${this._renderWidgetsForColumn(columns[columnKey])}
          </div>
        `)}
      </div>
    `;
  }

  _renderWidgetsForColumn(widgetNames) {
    if (!widgetNames || !Array.isArray(widgetNames)) return [];
    return widgetNames.map(widgetName => this._getWidgetByName(widgetName)).filter(w => w);
  }

  _getWidgetByName(name) {
    switch(name) {
      case 'stats': return this._renderStatsWidget();
      case 'schooltijden': return this._renderSchooltijdenWidget();
      case 'week_schooltijden': return this._renderWeekSchooltijdenWidget();
      case 'volgende_schooldag': return this._renderVolgendeSchooldagWidget();
      case 'volgende_les': return this._renderVolgendeLesWidget();
      case 'rooster_vandaag': return this._renderRoosterWidget();
      case 'rooster_meta': return this._renderRoosterMetaWidget();
      case 'rooster_morgen': return this._renderRoosterMorgenWidget();
      case 'huiswerk': return this._renderHuiswerkWidget();
      case 'cijfers': return this._renderCijfersWidget();
      case 'voortgangscijfers': return this._renderVoortgangscijfersWidget();
      case 'opdrachten': return this._renderOpdrachtenWidget();
      case 'absenties': return this._renderAbsentiesWidget();
      case 'wijzigingen': return this._renderWijzigingenWidget();
      case 'aanmeldingen': return this._renderAanmeldingenWidget();
      case 'activiteiten': return this._renderActiviteitenWidget();
      default: return null;
    }
  }

  _renderWidgets() {
    const showWidgets = this.config.show_widgets || ['stats', 'schooltijden', 'volgende_schooldag', 'rooster_vandaag', 'huiswerk', 'cijfers', 'voortgangscijfers', 'opdrachten'];
    const widgets = [];
    
    if (showWidgets.includes('stats')) widgets.push(this._renderStatsWidget());
    if (showWidgets.includes('schooltijden')) widgets.push(this._renderSchooltijdenWidget());
    if (showWidgets.includes('week_schooltijden')) widgets.push(this._renderWeekSchooltijdenWidget());
    if (showWidgets.includes('volgende_schooldag')) widgets.push(this._renderVolgendeSchooldagWidget());
    if (showWidgets.includes('volgende_les')) widgets.push(this._renderVolgendeLesWidget());
    if (showWidgets.includes('rooster_vandaag')) widgets.push(this._renderRoosterWidget());
    if (showWidgets.includes('rooster_meta')) widgets.push(this._renderRoosterMetaWidget());
    if (showWidgets.includes('rooster_morgen')) widgets.push(this._renderRoosterMorgenWidget());
    if (showWidgets.includes('huiswerk')) widgets.push(this._renderHuiswerkWidget());
    if (showWidgets.includes('cijfers')) widgets.push(this._renderCijfersWidget());
    if (showWidgets.includes('voortgangscijfers')) widgets.push(this._renderVoortgangscijfersWidget());
    if (showWidgets.includes('opdrachten')) widgets.push(this._renderOpdrachtenWidget());
    if (showWidgets.includes('absenties')) widgets.push(this._renderAbsentiesWidget());
    if (showWidgets.includes('wijzigingen')) widgets.push(this._renderWijzigingenWidget());
    if (showWidgets.includes('aanmeldingen')) widgets.push(this._renderAanmeldingenWidget());
    if (showWidgets.includes('activiteiten')) widgets.push(this._renderActiviteitenWidget());

    return widgets;
  }

  // Magister also schedules room and group bookings as soort 'Algemeen':
  // 'Studie na school' in a study room, or an evening booked as '10 leerlingen'.
  // The integration marks those as categorie 'boeking'; they are not lessons.
  _isBoeking(afspraak) {
    return afspraak.categorie === 'boeking';
  }

  _visibleAfspraken(afspraken) {
    if (!this.config || !this.config.hide_boekingen) return afspraken;
    return afspraken.filter(afspraak => !this._isBoeking(afspraak));
  }

  _renderAfspraakItem(afspraak) {
    const isUitval = afspraak.is_uitval === true;
    const isGewijzigd = !isUitval && afspraak.was_afwijkend === true;
    const isBoeking = this._isBoeking(afspraak);
    return html`
      <div class="afspraak-item ${isUitval ? 'uitval' : ''} ${isGewijzigd ? 'gewijzigd' : ''} ${isBoeking ? 'boeking' : ''}">
        ${isUitval ? html`<div class="uitval-label">🚫 Vervallen</div>` : ''}
        ${isGewijzigd ? html`<div class="uitval-label">🔄 Gewijzigd</div>` : ''}
        <div class="les-tijd">
          <strong>${this._formatTijd(afspraak.start)} - ${this._formatTijd(afspraak.einde)}</strong>
          ${isBoeking ? html`<span class="badge badge-boeking">📌 Boeking</span>` : ''}
          ${afspraak.is_online ? html`<span class="badge badge-success">💻 Online</span>` : ''}
          ${afspraak.duurt_hele_dag ? html`<span class="badge badge-warning">🕐 Hele dag</span>` : ''}
        </div>
        <div class="les-omschrijving">${afspraak.omschrijving}</div>
        ${afspraak.opmerking ? html`<div class="tijd">💬 ${afspraak.opmerking}</div>` : ''}
        ${afspraak.lokaal ? html`<div class="tijd">📍 ${afspraak.lokaal}</div>` : ''}
        ${afspraak.is_huiswerk ? html`<span class="badge">HW</span>` : ''}
      </div>
    `;
  }

  _renderRoosterWidget() {
    const afspraken = this._visibleAfspraken(this._data.afspraken || []);
    const vandaag = this._getVandaag();
    const afsprakenVandaag = afspraken.filter(afspraak =>
      this._getLocaleDateStr(afspraak.start) === vandaag
    );

    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📅 Rooster Vandaag</h3>
          <span class="widget-icon">${afsprakenVandaag.length}</span>
        </div>
        <div class="widget-content">
          ${afsprakenVandaag.length > 0 ? 
            afsprakenVandaag.map(afspraak => this._renderAfspraakItem(afspraak)) : 
            html`<div class="empty-state">Geen lessen vandaag 🎉</div>`
          }
        </div>
      </div>
    `;
  }

  _nextSchoolDay(afspraken) {
    const lessen = (afspraken || []).filter(a =>
      a.soort === 'Les' &&
      !a.is_uitval &&
      a.start &&
      a.start.substr(11, 8) !== '00:00:00'
    );
    const vandaag = this._getVandaag();
    const data = [...new Set(lessen.map(a => this._getLocaleDateStr(a.start)).filter(Boolean))].sort();
    return data.find(d => d >= vandaag) || null;
  }

  _renderRoosterMetaWidget() {
    const afspraken = this._visibleAfspraken(this._data.afspraken || []);
    const dateStr = this._nextSchoolDay(afspraken);
    const afsprakenFiltered = dateStr
      ? afspraken.filter(afspraak => this._getLocaleDateStr(afspraak.start) === dateStr)
      : [];

    const vandaag = this._getVandaag();
    const morgen = this._getMorgen();
    let titel;
    if (!dateStr) {
      titel = '📅 Rooster';
    } else if (dateStr === vandaag) {
      titel = '📅 Rooster (Vandaag)';
    } else if (dateStr === morgen) {
      titel = '📅 Rooster (Morgen)';
    } else {
      titel = `📅 Rooster (${dateStr})`;
    }

    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">${titel}</h3>
          <span class="widget-icon">${afsprakenFiltered.length}</span>
        </div>
        <div class="widget-content">
          ${afsprakenFiltered.length > 0 ?
            afsprakenFiltered.map(afspraak => this._renderAfspraakItem(afspraak)) :
            html`<div class="empty-state">Geen lessen gevonden 🎉</div>`
          }
        </div>
      </div>
    `;
  }

  _renderRoosterMorgenWidget() {
    const afspraken = this._visibleAfspraken(this._data.afspraken || []);
    const morgen = this._getMorgen();
    const afsprakenMorgen = afspraken.filter(afspraak =>
      this._getLocaleDateStr(afspraak.start) === morgen
    );

    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📅 Rooster Morgen</h3>
          <span class="widget-icon">${afsprakenMorgen.length}</span>
        </div>
        <div class="widget-content">
          ${afsprakenMorgen.length > 0 ?
            afsprakenMorgen.map(afspraak => this._renderAfspraakItem(afspraak)) :
            html`<div class="empty-state">Geen lessen morgen 🎉</div>`
          }
        </div>
      </div>
    `;
  }

  _renderWeekSchooltijdenWidget() {
    const dayNames = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag'];
    const afspraken = (this._data.afspraken || []).filter(afspraak =>
      afspraak.soort === 'Les' && !afspraak.is_uitval
    );
    const days = dayNames.map((name, index) => {
      const lessons = afspraken.filter(afspraak => {
        const date = this._getLocaleDateStr(afspraak.start);
        if (!date) return false;
        const weekday = new Date(`${date}T12:00:00`).getDay();
        return (weekday === 0 ? 6 : weekday - 1) === index;
      });

      if (lessons.length === 0) return { name, start: null, end: null };

      const starts = lessons.map(afspraak => afspraak.start?.substr(11, 5)).filter(Boolean).sort();
      const ends = lessons.map(afspraak => afspraak.einde?.substr(11, 5)).filter(Boolean).sort();
      return { name, start: starts[0], end: ends[ends.length - 1] };
    });

    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">Schooltijden per week</h3>
        </div>
        <div class="widget-content">
          ${days.map(day => html`
            <div class="schoolweek-row">
              <span class="schoolweek-day">${day.name}</span>
              <span class="schoolweek-time">
                ${day.start && day.end ? `${day.start} - ${day.end}` : 'Geen lessen'}
              </span>
            </div>
          `)}
        </div>
      </div>
    `;
  }

  _renderVoortgangscijfersWidget() {
    const cijfers = (this._data.voortgangscijfers || [])
      .slice()
      .sort((a, b) => (b.ingevoerd_op || '').localeCompare(a.ingevoerd_op || ''));

    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📈 Voortgangscijfers</h3>
          <span class="widget-icon">${cijfers.length}</span>
        </div>
        <div class="widget-content">
          ${cijfers.length > 0 ? 
            cijfers.slice(0, 10).map(cijfer => html`
              <div class="cijfer-item" style="${cijfer.is_voldoende === false ? 'border-left-color: var(--error-color);' : ''}">
                <div>
                  <span class="vak">${cijfer.vak?.toUpperCase()}</span>: 
                  <span class="waarde">${cijfer.waarde}</span>
                  ${cijfer.weegfactor ? html` <span class="wf">(x${cijfer.weegfactor})</span>` : ''}
                  ${cijfer.vrijstelling ? html`<span class="badge badge-warning">Vrijstelling</span>` : ''}
                </div>
                <div class="tijd">
                  ${cijfer.omschrijving}${cijfer.periode ? ` · ${cijfer.periode}` : ''}
                  ${cijfer.ingevoerd_op ? ` - ${cijfer.ingevoerd_op.substr(0, 10)}` : ''}
                </div>
              </div>
            `) : 
            html`<div class="empty-state">Nog geen cijfers dit schooljaar</div>`
          }
        </div>
      </div>
    `;
  }

  _renderHuiswerkWidget() {
    const huiswerk = (this._data.afspraken || []).filter(a => a.is_huiswerk === true);
    const open = huiswerk.filter(a => a.is_afgerond !== true);
    const afgerond = huiswerk.length - open.length;

    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📚 Huiswerk</h3>
          <span class="widget-icon">${open.length}</span>
        </div>
        <div class="widget-content">
          ${open.length > 0 ?
            open.slice(0, 8).map(item => html`
              <div class="afspraak-item">
                <div>
                  <strong>${item.omschrijving}</strong>
                  ${item.is_online ? html`<span class="badge badge-success">💻 Online</span>` : ''}
                </div>
                ${item.inhoud ? html`<div class="tijd">${item.inhoud}</div>` : ''}
                <div class="tijd">📅 ${item.start?.substr(0, 10)} · ${this._formatTijd(item.start)}</div>
              </div>
            `) :
            html`<div class="empty-state">Geen open huiswerk 🎉</div>`
          }
          ${afgerond > 0 ? html`<div class="tijd" style="margin-top: 8px;">✅ ${afgerond} afgerond</div>` : ''}
        </div>
      </div>
    `;
  }

  _renderCijfersWidget() {
    const cijfers = this._data.cijfers || [];

    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">🎓 Recente Cijfers</h3>
          <span class="widget-icon">${cijfers.length}</span>
        </div>
        <div class="widget-content">
          ${cijfers.length > 0 ? 
            cijfers.slice(0, 5).map(cijfer => html`
              <div class="cijfer-item">
                <div>
                  <span class="vak">${cijfer.vak?.toUpperCase()}</span>: 
                  <span class="waarde">${cijfer.waarde}</span>
                  ${cijfer.weegfactor ? html` <span class="wf">(x${cijfer.weegfactor})</span>` : ''}
                </div>
                <div class="tijd">${cijfer.omschrijving} - ${cijfer.ingevoerd_op?.substr(0, 10)}</div>
              </div>
            `) : 
            html`<div class="empty-state">Geen cijfers beschikbaar</div>`
          }
        </div>
      </div>
    `;
  }

  _renderOpdrachtenWidget() {
    const opdrachten = this._data.opdrachten || [];
    const openOpdrachten = opdrachten.filter(opdracht => !opdracht.ingeleverd_op);

    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📝 Open Opdrachten</h3>
          <span class="widget-icon">${openOpdrachten.length}</span>
        </div>
        <div class="widget-content">
          ${openOpdrachten.length > 0 ? 
            openOpdrachten.slice(0, 5).map(opdracht => {
              const inleverDatum = new Date(opdracht.inleveren_voor);
              const nu = new Date();
              const dagenOver = (inleverDatum - nu) / (1000 * 60 * 60 * 24);
              const isSpoed = dagenOver < 1;
              const isWaarschuwing = dagenOver < 2;
              
              return html`
                <div class="opdracht-item" style="${isSpoed ? 'border-left-color: var(--error-color); background: rgba(244, 67, 54, 0.1);' : isWaarschuwing ? 'border-left-color: var(--warning-color); background: rgba(255, 152, 0, 0.1);' : ''}">
                  <div>
                    <strong>${opdracht.titel}</strong> 
                    ${isSpoed ? html`<span class="badge">SPOED!</span>` : isWaarschuwing ? html`<span class="badge badge-warning">BIJNA!</span>` : ''}
                  </div>
                  <div class="tijd">Vak: ${opdracht.vak?.toUpperCase()}</div>
                  <div class="tijd">📅 ${opdracht.inleveren_voor?.substr(0, 16)}</div>
                </div>
              `;
            }) : 
            html`<div class="empty-state">Geen open opdrachten ✅</div>`
          }
        </div>
      </div>
    `;
  }

  _renderAbsentiesWidget() {
    const absenties = (this._data.absenties || [])
      .slice()
      .sort((a, b) => (b.start || '').localeCompare(a.start || ''));

    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">⚠️ Recente Absenties</h3>
          <span class="widget-icon">${absenties.length}</span>
        </div>
        <div class="widget-content">
          ${absenties.length > 0 ? 
            absenties.slice(0, 5).map(absentie => html`
              <div class="afspraak-item" style="${absentie.geoorloofd === false ? 'border-left-color: var(--error-color); background: rgba(244, 67, 54, 0.06);' : ''}">
                <div>
                  <strong>${absentie.start?.substr(0, 10)}</strong>
                  ${absentie.lesuur ? html`<span class="tijd"> · ${absentie.lesuur}e uur</span>` : ''}
                </div>
                <div>${absentie.omschrijving}</div>
                <div>
                  ${absentie.code ? html`<span class="badge">${absentie.code.toUpperCase()}</span>` : ''}
                  ${absentie.geoorloofd === false ? html`<span class="badge">Ongeoorloofd</span>` : html`<span class="badge badge-success">Geoorloofd</span>`}
                </div>
                ${absentie.afspraak ? html`<div class="tijd">${absentie.afspraak}</div>` : ''}
              </div>
            `) : 
            html`<div class="empty-state">Geen recente absenties 👍</div>`
          }
        </div>
      </div>
    `;
  }

  _renderWijzigingenWidget() {
    const wijzigingen = this._data.wijzigingen || [];

    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">🔄 Roosterwijzigingen</h3>
          <span class="widget-icon">${wijzigingen.length}</span>
        </div>
        <div class="widget-content">
          ${wijzigingen.length > 0 ? 
            wijzigingen.slice(-3).map(wijziging => this._renderAfspraakItem(wijziging)) : 
            html`<div class="empty-state">Geen wijzigingen</div>`
          }
        </div>
      </div>
    `;
  }

  _renderStatsWidget() {
    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📊 Overzicht</h3>
          <span class="widget-icon">📈</span>
        </div>
        <div class="widget-content">
          <div class="afspraak-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>📅 Lessen vandaag:</span>
              <strong style="color: var(--accent-color);">${this._data.aantal_afspraken_vandaag || 0}</strong>
            </div>
          </div>
          <div class="afspraak-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>📚 Huiswerk open:</span>
              <strong style="color: var(--accent-color);">${this._data.aantal_huiswerk_onafgerond ?? this._data.aantal_huiswerk ?? 0}</strong>
            </div>
          </div>
          <div class="afspraak-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>✅ Huiswerk afgerond:</span>
              <strong style="color: var(--accent-color);">${this._data.aantal_huiswerk_afgerond || 0}</strong>
            </div>
          </div>
          <div class="afspraak-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>🎓 Cijfers:</span>
              <strong style="color: var(--accent-color);">${this._data.cijfers?.length || 0}</strong>
            </div>
          </div>
          <div class="afspraak-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>📈 Cijfers dit jaar:</span>
              <strong style="color: var(--accent-color);">${this._data.voortgangscijfers?.length || 0}</strong>
            </div>
          </div>
          <div class="afspraak-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>📝 Opdrachten:</span>
              <strong style="color: var(--accent-color);">${this._data.opdrachten?.length || 0}</strong>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  _renderVolgendeLesWidget() {
    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">⏰ Volgende Les</h3>
          <span class="widget-icon">🕒</span>
        </div>
        <div class="widget-content">
          ${this._data.volgende_afspraak && this._data.volgende_afspraak !== 'Geen' ? 
            html`
              <div style="text-align: center; padding: 20px;">
                <div style="font-size: 1.4em; font-weight: bold; color: var(--accent-color); margin-bottom: 8px;">
                  ${this._data.volgende_afspraak}
                </div>
                ${this._data.volgende_vak ? html`
                  <div style="font-size: 1.1em; color: var(--primary-text-color); margin-bottom: 16px;">
                    ${this._data.volgende_vak}
                  </div>
                ` : ''}
                <div style="background: var(--primary-color); color: white; padding: 8px 16px; border-radius: 20px; display: inline-block;">
                  🎯 Komende les
                </div>
              </div>
            ` : 
            html`<div class="empty-state">Geen komende lessen 🎉</div>`
          }
        </div>
      </div>
    `;
  }

  _renderAanmeldingenWidget() {
    const aanmeldingen = this._data.aanmeldingen || [];

    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">🏫 Aanmeldingen</h3>
          <span class="widget-icon">${aanmeldingen.length}</span>
        </div>
        <div class="widget-content">
          ${aanmeldingen.length > 0 ? 
            aanmeldingen.slice(0, 3).map(aanmelding => html`
              <div class="afspraak-item">
                <div><strong>${aanmelding.start} - ${aanmelding.einde}</strong></div>
                <div>${aanmelding.studie || ''}</div>
                <div class="tijd">${aanmelding.lesperiode || ''}</div>
              </div>
            `) : 
            html`<div class="empty-state">Geen aanmeldingen</div>`
          }
        </div>
      </div>
    `;
  }

  _renderActiviteitenWidget() {
    const activiteiten = this._data.activiteiten || [];

    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📢 Activiteiten</h3>
          <span class="widget-icon">${activiteiten.length}</span>
        </div>
        <div class="widget-content">
          ${activiteiten.length > 0 ? 
            activiteiten.slice(0, 3).map(activiteit => html`
              <div class="afspraak-item">
                <div><strong>${activiteit.titel}</strong></div>
                <div class="tijd">Zichtbaar: ${activiteit.zichtbaar_vanaf} t/m ${activiteit.zichtbaar_tot}</div>
              </div>
            `) : 
            html`<div class="empty-state">Geen activiteiten</div>`
          }
        </div>
      </div>
    `;
  }

  _renderSchooltijdenWidget() {
    const startVandaag = this._data.school_start_vandaag || 'Geen';
    const eindeVandaag = this._data.school_einde_vandaag || 'Geen';
    const lessen = this._data.lessen_vandaag || [];

    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">🏫 Schooltijden Vandaag</h3>
          <span class="widget-icon">${lessen.length}</span>
        </div>
        <div class="widget-content">
          <div class="afspraak-item" style="border-left: 4px solid var(--success-color);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>⏰ Eerste les:</span>
              <strong style="color: var(--accent-color);">${startVandaag}</strong>
            </div>
          </div>
          <div class="afspraak-item" style="border-left: 4px solid var(--warning-color);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>🔔 Laatste les:</span>
              <strong style="color: var(--accent-color);">${eindeVandaag}</strong>
            </div>
          </div>
          ${lessen.length > 0 ? lessen.map(les => html`
            <div class="afspraak-item" style="border-left: 4px solid var(--primary-color);">
              <div><strong>${les.start} - ${les.einde}</strong> ${les.vak ? html`<span class="vak">${les.vak}</span>` : ''}</div>
              ${les.omschrijving ? html`<div>${les.omschrijving}</div>` : ''}
              ${les.lokaal ? html`<div class="tijd">📍 ${les.lokaal}</div>` : ''}
            </div>
          `) : html`<div class="empty-state">Geen lessen vandaag 🎉</div>`}
        </div>
      </div>
    `;
  }

  _renderVolgendeSchooldagWidget() {
    const volgDag = this._data.volgende_schooldag || 'Geen';
    const volgStart = this._data.volgende_schooldag_start || 'Geen';
    const volgEinde = this._data.volgende_schooldag_einde || 'Geen';

    return html`
      <div class="widget">
        <div class="widget-header">
          <h3 class="widget-title">📆 Volgende Schooldag</h3>
          <span class="widget-icon">→</span>
        </div>
        <div class="widget-content">
          <div class="afspraak-item" style="border-left: 4px solid var(--accent-color);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>📅 Datum:</span>
              <strong style="color: var(--accent-color);">${volgDag}</strong>
            </div>
          </div>
          <div class="afspraak-item" style="border-left: 4px solid var(--success-color);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>⏰ Eerste les:</span>
              <strong style="color: var(--accent-color);">${volgStart}</strong>
            </div>
          </div>
          <div class="afspraak-item" style="border-left: 4px solid var(--warning-color);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>🔔 Laatste les:</span>
              <strong style="color: var(--accent-color);">${volgEinde}</strong>
            </div>
          </div>
          ${volgDag === 'Geen' ? html`<div class="empty-state">Geen komende schooldag gevonden</div>` : ''}
        </div>
      </div>
    `;
  }
}

// The card may also be installed as a standalone HACS plugin. Guard the
// registration so loading both copies does not throw.
if (!customElements.get('magister-school-card')) {
  customElements.define('magister-school-card', MagisterSchoolCard);
}
