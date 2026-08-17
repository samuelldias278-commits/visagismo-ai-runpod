'use strict';

window.geometryClient = {
  apiBase() {
    const configured = localStorage.getItem('visagismoBarber.v2ApiBase');
    if (configured) return configured.replace(/\/$/, '');
    if (['localhost', '127.0.0.1'].includes(location.hostname)) return 'http://127.0.0.1:8001';
    return location.origin;
  },

  async analyzeView({ dataUrl, position, consentId, storeHistory }) {
    const imageResponse = await fetch(dataUrl);
    const blob = await imageResponse.blob();
    const form = new FormData();
    form.append('photo', blob, `${String(position).replace(/[^a-z0-9]/gi, '-').toLowerCase()}.jpg`);
    form.append('consent_id', consentId);
    form.append('store_history', String(Boolean(storeHistory)));
    form.append('view_label', position);

    const response = await fetch(`${this.apiBase()}/api/v2/analyze/front`, {
      method: 'POST',
      body: form,
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.detail || `Falha HTTP ${response.status}`);
    return body;
  },

  analyzeFront(options) {
    return this.analyzeView({ ...options, position: 'Foto frontal' });
  },
};
