from openerp import models, fields, api, _

import logging
l = logging.getLogger()


class stock_picking(models.Model):
    _inherit = "stock.picking"


    @api.one
    def _compue_client_order_ref2(self):
        if self.client_order_ref == False:
            if self.sale_id and self.sale_id.client_order_ref:
                self.write({'client_order_ref':self.sale_id.client_order_ref})

        self.client_order_ref2 = 'test'
        return 'test'

    client_order_ref2 = fields.Char(string="Client Order Ref", compute=_compue_client_order_ref2)
