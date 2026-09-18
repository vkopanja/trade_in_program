/** @odoo-module **/

import publicWidget from "web.public.widget";

publicWidget.registry.TradeInQuote = publicWidget.Widget.extend({
    selector: '#trade_in_form',
    events: {
        'change select[name="device_id"]': '_onInputChange',
        'change select[name="condition_id"]': '_onInputChange',
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
});
