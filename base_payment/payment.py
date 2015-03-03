##############################################################################
#
# Copyright (c) 2008-2013 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
#                    General contacts <info@alistek.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import osv
from openerp.osv import fields
import openerp.netsvc
from openerp.tools.translate import _

import base64

def _agencies_get(self, cr, uid, context=None):
    obj = self.pool.get('payment.profile')
    ids = obj.search(cr, uid, [])
    res = obj.read(cr, uid, ids, ['code', 'name'], context=context)
    res = [(r['code'], r['name']) for r in res]
    return res

class payment_profile(osv.osv):
    _name = 'payment.profile'
    _description = 'Payment profile'

    _columns = {
        'name':fields.char('Name', size=64, required=True),
        'code':fields.char('Code', size=64, required=True),

    }
payment_profile()
#
class payment_agency(osv.osv):
    _name = 'payment.agency'
    _description = 'Payment agency'

    _columns = {
        'name':fields.char('Name', size=64, required=True),
        'code':fields.char('Code', size=64, required=True),
        'profile':fields.char('Profile code', size=64, required=True),
    }
payment_agency()
#
class payment_agency_config(osv.osv):
    _name = 'payment.agency.config'
    _description = 'Payment agencies configurations'
    _order = 'sequence'

    _columns = {
        'name':fields.char('Name', size=64, required=True),
        'code': fields.selection(_agencies_get, 'Payment profile', required=True),
        'agency_id':fields.many2one('payment.agency', 'Agency', required=True),
        'api_url':fields.char('API url of payment agency', size=256, required=True),
        'user':fields.char('API username', size=64, required=True),
        'pwd':fields.char('Password', size=64, required=True),
        'shop_id':fields.many2one('sale.shop', 'Shop', required=True),
        'signature':fields.char('Signature', size=256),
        'sslcert':fields.char('SSL Certificate', size=256, help="Path to ssl certificate file."),
        'logo':fields.binary('Logo'),
        'button_url':fields.char('Button Image URL', size=256),
        'sequence': fields.integer('Sequence'),
        'active':fields.boolean('Active'),
        'inv_details':fields.boolean('Invoice Details', help="Show invoice details while paying the invoice. May cause amount unmatch errors, if checked."),
        'currency_ids':fields.many2many('res.currency', 'payment_agency_config_res_currency_rel', 'payment_agency_config_id', 'res_currency_id', 'Accepted Currencies', domain="[]", readonly=False, help=''),

    }
#
#     def jera_request_payment(self, cr, uid, context=None):
#         agency_id = context.get('payment')
#         agency_data = self.browse(cr, 1, int(agency_id), context=context)
#         action = 'action' in context and context['action'] and '_'+context.get('action') or ''
#         request_func = getattr(self, "request_"+agency_data.agency_id.profile.lower()+action)
#         return request_func(cr, uid, agency_data, context=context)
#
#     ########## Old version ############
#     def jera_request_confirm_order(self, cr, uid, order_id, context=None):
#         so_obj = self.pool.get('sale.order')
#         report_obj = self.pool.get('ir.actions.report.xml')
#         wf_service = netsvc.LocalService("workflow")
#         order_id = int(order_id)
#         wf_service.trg_validate(uid, 'sale.order', order_id, 'order_confirm', cr)
#
#         invoices = so_obj.read(cr, uid, order_id, ['invoice_ids'], context=context)['invoice_ids']
#         if invoices:
#             report_id = report_obj.search(cr, uid, [('report_name','=','html_payment_invoice')], context=context, limit=1)[0]
#             name = report_obj.read(cr, uid, report_id, ['name'], context=context)['name']
#             data = {'model':'account.invoice','id':invoices[0],'report_type': u'aeroo','ids':invoices}
#             result = netsvc.Service._services['report.html_payment_invoice'].create(cr, 1, invoices, data, context=context)
#             return 'page', (base64.encodestring(result[0]), result[1]), 'account.invoice', name
#         else:
#             raise osv.except_osv(_('Invalid action!'), _('Can not create invoice, please contact website owner!'))
#     ###################################
#
#     def confirm_order(self, cr, uid, order_id, context=None):
#         so_obj = self.pool.get('sale.order')
#         report_obj = self.pool.get('ir.actions.report.xml')
#         wf_service = netsvc.LocalService("workflow")
#
#         order_id = type(order_id)==list and int(order_id[0]) or int(order_id)
#         wf_service.trg_validate(1, 'sale.order', order_id, 'order_confirm', cr)
#
#         invoices = so_obj.read(cr, 1, order_id, ['invoice_ids'], context=context)['invoice_ids']
#         if invoices:
#             wf_service.trg_validate(1, 'account.invoice', invoices[0], 'invoice_proforma2', cr)
#             report_id = report_obj.search(cr, uid, [('report_name','=','html_payment_invoice')], context=context, limit=1)[0]
#             name = report_obj.read(cr, uid, report_id, ['name'], context=context)['name']
#             data = {'model':'account.invoice','id':invoices[0],'report_type': u'aeroo','ids':invoices}
#             return {
#                 'type': 'ir.actions.report.xml',
#                 'report_name': 'html_payment_invoice',
#                 'datas': data,
#             }
#         else:
#             raise osv.except_osv(_('Invalid action!'), _('Can not create invoice, please contact website owner!'))
#
#
#     _defaults = {
#         'active': True,
#         'inv_details': False,
#     }
#
payment_agency_config()

class payment_log(osv.osv):
    _name = 'payment.log'
    _description = 'Pyment Log'

    _columns = {
        'name':fields.char('Agency Name', size=64, required=True),
        'agency_id':fields.many2one('payment.agency.config', 'Agency'),
        'invoice_id':fields.many2one('account.invoice', 'Invoice'),
        'trans_ref':fields.char('Transaction Ref.', size=64),
        'state':fields.selection([
            ('draft','Draft'),
            ('error','Error'),
            ('cancelled','Cancelled'),
            ('progress','In Progress'),
            ('confirmed','Confirmed'),
            ('done','Done'),

        ],'State', select=True, readonly=True),
        'note': fields.text('Notes', readonly=True),
        'user_msg': fields.text('Message'),
        'datetime': fields.datetime('Date'),
        'create_date': fields.datetime('Create Date'),

    }

    _defaults = {
        'state': 'draft',
    }
#
# payment_log()
#
# class sale_shop(osv.osv):
#     _name = 'sale.shop'
#     _inherit = 'sale.shop'
#
#     _columns = {
#         'host':fields.char('Host', size=128),
#
#     }
#
# sale_shop()

