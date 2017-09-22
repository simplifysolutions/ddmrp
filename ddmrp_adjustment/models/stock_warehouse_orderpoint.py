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
            increased_demand = self.adu - prev
            self.explode_demand_to_components(
                increased_demand, self.product_uom)
        # Add demand related to DAFs applied to parent buffers.
        self.adu += self.extra_demand # FIXME: how not to sum again??
        return res

    extra_demand = fields.Float(
        string="Extra Demand",
        help="Demand associated to Demand Adjustment Factors applied to "
             "parent buffers")

    def _get_init_bom(self):
        # TODO: This is on pull/13 and its the correct method. Need to adapt
        # when 13 gets merge.
        # init_bom = self.env['mrp.bom'].search([
        #     '|',
        #     ('product_id', '=', self.product_id.id),
        #     ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
        #     '|',
        #     ('location_id', '=', self.location_id.id),
        #     ('location_id', '=', False)], limit=1)
        # return init_bom
        self.ensure_one()
        init_bom = self.env['mrp.bom'].search([
            '|',
            ('product_id', '=', self.product_id.id),
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)
        ], limit=1)
        return init_bom

    def explode_demand_to_components(self, demand, uom_id):
        uom_obj = self.env['product.uom']
        init_bom = self._get_init_bom()
        self.ensure_one()

        def _get_extra_demand(bom, line, buffer_id, factor):
            qty = factor * line.product_qty / bom.product_qty
            extra = uom_obj._compute_qty_obj(
                line.product_uom, qty, buffer_id.product_uom)
            return extra

        def _create_demand(bom, factor=1, level=0):
            level += 1
            for line in bom.bom_line_ids:
                buffer_id = self.search([
                    ('product_id', '=', line.product_id.id)], limit=1)  # TODO: pull/13: filter by location also
                if buffer_id: # TODO: In #13 the buffered flag is added to bom
                    buffer_id.extra_demand += _get_extra_demand(
                        bom, line, buffer_id, factor)
                # location = line.location_id  # TODO: pull/13: with locations:
                line_boms = line.product_id.bom_ids
                # bom = line_boms.filtered(
                #     lambda bom: bom.location_id == location) or \
                #     line_boms.filtered(lambda b: not b.location_id) # TODO: pull/13: with locations:
                child_bom = line_boms
                if child_bom:
                    line_qty = self.env['product.uom']._compute_qty_obj(
                        line.product_uom, line.product_qty,
                        child_bom.product_uom)
                    new_factor = factor * line_qty / bom.product_qty
                    _create_demand(child_bom[0], new_factor, level)

        initial_factor = uom_obj._compute_qty_obj(
            uom_id, demand, init_bom.product_uom)
        _create_demand(init_bom, factor=initial_factor)
        return True
