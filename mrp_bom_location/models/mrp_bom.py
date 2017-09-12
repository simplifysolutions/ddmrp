# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    location_id = fields.Many2one(
        comodel_name="stock.location", string="Location",
        help="Set the preferred location for this BOM.",
        domain=[('usage', '=', 'internal')])


    # @api.model
    # def _prepare_consume_line(self, bom_line_id, quantity):
    #     res = super(MrpBom, self)._prepare_consume_line(bom_line_id, quantity)
    #     level = self.env.context.get('bom_level', 0)
    #     res.update(level=level)
    #     return res
    #
    # @api.model
    # def _bom_explode(self, bom, product, factor, properties=None,
    #                  level=0, routing_id=False, previous_products=None,
    #                  master_bom=None):
    #     return super(MrpBom, self.with_context(bom_level=level))._bom_explode(
    #         bom, product, factor, properties=properties, level=level,
    #         routing_id=routing_id, previous_products=previous_products,
    #         master_bom=master_bom)


class MrpBom(models.Model):
    _inherit = "mrp.bom.line"

    location_id = fields.Many2one(
        comodel_name="stock.location", string="Location",
        help="Location which it is expected to get the products from.",
        domain=[('usage', '=', 'internal')])
