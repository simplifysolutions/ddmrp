# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class MakeProcurementBuffer(models.TransientModel):
    _name = 'make.procurement.buffer'
    _description = 'Make Procurements from Buffer'

    @api.model
    def default_get(self, fields):
        defaults = super(MakeProcurementBuffer, self).default_get(fields)
        record_id = self.env.context.get('active_id')
        active_ids = self.env.context.get('active_ids', [])
        active_model = self.env.context.get('active_model')

        if len(active_ids) > 1:
            raise UserError(_('Please select only one buffer.'))

        if not record_id:
            return defaults
        assert active_model == 'stock.warehouse.orderpoint', \
            'Bad context propagation'
        buffer = self.env['stock.warehouse.orderpoint'].browse(record_id)
        defaults['qty'] = buffer.procure_recommended_qty
        defaults['uom_id'] = buffer.product_id.uom_id.id
        defaults['date_planned'] = buffer.procure_recommended_date
        defaults['buffer_id'] = buffer.id
        defaults['product_id'] = buffer.product_id.id
        defaults['warehouse_id'] = buffer.warehouse_id.id
        defaults['location_id'] = buffer.location_id.id

        return defaults

    qty = fields.Float(string='Quantity', required=True)
    uom_id = fields.Many2one(string='Unit of Measure',
                             comodel_name='product.uom',
                             required=True, readonly=True)
    date_planned = fields.Date(string='Planned Date', required=True)

    buffer_id = fields.Many2one(string='Stock Buffer',
                                comodel_name='stock.warehouse.orderpoint',
                                required=True, readonly=True)
    product_id = fields.Many2one(string='Product',
                                 comodel_name='product.product',
                                 required=True, readonly=True)
    warehouse_id = fields.Many2one(string='Warehouse',
                                   comodel_name='stock.warehouse',
                                   readonly=True)
    location_id = fields.Many2one(string='Location',
                                  comodel_name='stock.location',
                                  readonly=True)

    @api.multi
    def _prepare_procurement(self):
        return {
            'name': self.buffer_id.name,
            'date_planned': self.date_planned,
            'product_id': self.product_id.id,
            'product_qty': self.qty,
            'product_uom': self.uom_id.id,
            'warehouse_id': self.warehouse_id.id,
            'location_id': self.location_id.id,
            'company_id': self.buffer_id.company_id.id,
            'orderpoint_id': self.buffer_id.id,
            'origin': self.buffer_id.name
        }

    @api.multi
    def make_procurement(self):
        self.ensure_one()
        data = self._prepare_procurement()
        procurement = self.env['procurement.order'].create(data)

        return {
            'view_type': 'form',
            'view_mode': 'form, tree',
            'res_model': 'procurement.order',
            'res_id': procurement.id,
            'type': 'ir.actions.act_window',
         }