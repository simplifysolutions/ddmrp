# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from openerp import api, fields, models, _

_logger = logging.getLogger(__name__)


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.multi
    def _calc_adu(self):
        """Apply DAFs if existing for the buffer."""
        res = super(StockWarehouseOrderpoint, self)._calc_adu()
        today = fields.Date.today()
        adjustments = self.env['ddmrp.adjustment'].search([
            ('buffer_id', '=', self.id), ('daf', '>', 0.0),
            ('date_range_id.date_start', '<=', today),
            ('date_range_id.date_end', '>=', today)])
        if adjustments:
            daf = 1
            values = adjustments.mapped('daf')
            for val in values:
                daf *= val
            prev = self.adu
            self.adu *= daf
            # TODO: change to debug when tested.
            _logger.info(
                "DAF=%s applied to %s. ADU: %s -> %s" %
                (daf, self.name, prev, self.adu))
            # TODO: compute generated demand and apply to components...
        return res
