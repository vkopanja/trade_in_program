/** @odoo-module **/

import publicWidget from "web.public.widget";

publicWidget.registry.TradeInQuote = publicWidget.Widget.extend({
    selector: '#trade_in_form',
    events: {
        'change select[name="device_id"]': '_onInputChange',
        'change select[name="condition_id"]': '_onInputChange',
        'submit': '_onSubmit',
    },

    start() {
        this._submitButton = this.el.querySelector('button[type="submit"]');
        this._submitLabel = this._submitButton.textContent;
        this._onPageShow = this._onPageShow.bind(this);
        window.addEventListener('pageshow', this._onPageShow);
        return this._super.apply(this, arguments);
    },

    destroy() {
        window.removeEventListener('pageshow', this._onPageShow);
        this._super.apply(this, arguments);
    },

    async _onInputChange() {
        const out = this.el.querySelector('#quote');
        const device = this.el.device_id.value;
        const condition = this.el.condition_id.value;

        if (!device || !condition) {
            out.textContent = '-';
            return;
        }

        const result = await this._rpc({
            route: '/trade-in/quote',
            params: {device_id: device, condition_id: condition},
        });
        out.textContent = result.ok ? result.value.toFixed(2) : '-';
    },

    // The browser only fires submit once its own validation has passed, so the button never stays stuck.
    _onSubmit() {
        this._setSubmitting(true);
    },

    // Back/forward navigation can restore this page from cache with the button still disabled.
    _onPageShow(ev) {
        if (ev.persisted) {
            this._setSubmitting(false);
        }
    },

    _setSubmitting(submitting) {
        this._submitButton.disabled = submitting;
        this._submitButton.textContent = submitting ? 'Sending…' : this._submitLabel;
    },
});
