# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv,fields
import netsvc
import base64
from tools.translate import _
import time

class account_payment_make_payment(osv.osv_memory):
    _inherit = "account.payment.make.payment"
#    _description = "Account make payment"
    _columns = {
        'state': fields.selection(
            [
                ('create', 'Create'),
                ('finish', 'Finish')
            ],
            'State',
            readonly=True,
        ),
#        'test': fields.boolean(),
#        'reference': fields.char(
#            'Reference', size=35,
#            help=('The bank will use this reference in feedback communication '
#                  'to refer to this run. 35 characters are available.'
#                  ),
#            ),
#        'execution_date_create': fields.date(
#            'Execution Date',
#            help=('This is the date the file should be processed by the bank. '
#                  'Don\'t choose a date beyond the nearest date in your '
#                  'payments. The latest allowed date is 30 days from now.\n'
##                  'Please keep in mind that banks only execute on working days '
#                  'and typically use a delay of two days between execution date '
#                  'and effective transfer date.'
#                  ),
#            ),
#        'file_id': fields.many2one(
#            'account.banking.exported.file',
#            'Exported File',
#            readonly=True
#            ),
       'filename': fields.char('Filename', size=64),
       'file': fields.binary(string='File', readonly = True ),
#        'payment_order_ids': fields.many2many(
#            'payment.order', 'rel_wiz_payorders', 'wizard_id',
#            'payment_order_id', 'Payment Orders',
#            readonly=True,
#            ),
        }
    _defaults = {
        'state' : 'create'
    }

    def launch_wizard(self, cr, uid, ids, context=None):
        """
        Search for a wizard to launch according to the type.
        If type is manual. just confirm the order.
        """
#        logger = netsvc.Logger()
#        netsvc.Logger().notifyChannel("in launch wizard", netsvc.LOG_WARNING,"The line: %s"%context['active_id'])

        obj_payment_order = self.pool.get('payment.order')
        if context is None:
            context = {}
        settings_obj = self.pool.get('bank.integration.settings')
        exported_file_obj = self.pool.get('account.banking.exported.file')
        bank_parsers_obj = self.pool.get('bank.parsers')
        order = obj_payment_order.browse(cr, uid, context['active_id'], context)
#        settings_ids = settings_obj.search(cr, uid, [('partner_bank_id','=',order.mode.bank_id.id),('company_id','=',order.mode.company_id.id)])
#        if not settings_ids:
#            raise osv.except_osv( _('ERROR!'),
#                _('Not found any configuration for bank account specified in Payment Mode %(mode)s.') % {'mode': order.mode.name})
#        settings = settings_obj.browse(cr, uid, settings_ids[0], context)
#        if settings.parser_export == 'none':
#            raise osv.except_osv( _('ERROR!'),
#                _('Configuration for account %(account)s doesn\'t contain any Export Parser.') % {'account': settings.partner_bank_id.name})

        # get the parser to parse the file
        if not order.mode.banking_settings_id:
# TODO    SET DONE   !!!!!
            return {}

        for line in order.line_ids:
            if not line.bank_id:
                raise osv.except_osv( _('ERROR!'),
                    _('Line %s has no bank account.') % line.name)



        parser_code = order.mode.banking_settings_id.parser + "_export"
        if not hasattr(bank_parsers_obj,parser_code):
            raise osv.except_osv( _('ERROR!'),
                _('Unable to find export method for parser %(parser)s. Parser class not found.') % {'parser': parser_code})

        parser = getattr(bank_parsers_obj,parser_code)
        if not parser:
            raise osv.except_osv( _('ERROR!'),
            _('Unable to import parser %(parser)s. Parser class not found.') % {'parser': parser_code})
        file_data = parser(cr, uid, context['active_id'], context=context)

#        obj_model = self.pool.get('ir.model.data')
#        obj_act = self.pool.get('ir.actions.act_window')
#        order = obj_payment_order.browse(cr, uid, context['active_id'], context)
        file = base64.encodestring(file_data)
        filename = order.reference.replace("/","_") + "_" + parser_code +'.csv'
#        netsvc.Logger().notifyChannel("in launch wizard", netsvc.LOG_WARNING,"FILENAME: %s"%filename)

        export_result = {
            'company_id': order.mode.company_id.id,
#             'date': ,
            'format': parser_code,
            'log': "log ....",
            'user_id': uid,
            'state': 'ready',
            'pay_order_ids': [
                    [6, 0, [order.id]]
                ],
            'filename' : filename,
            'file': file,

#            'file': base64.encodestring(file),
#            'payment_order_ids': [
#                [6, 0, [po.id for po in payment_orders]]
#            ],
        }
        file_id = exported_file_obj.create(cr, uid, export_result, context)
#        netsvc.Logger().notifyChannel("in launch wizard", netsvc.LOG_WARNING,"FILENAME file _id: %s"%filename)

        self.write(cr, uid, [ids[0]], {
                'file': file,
                'filename' : filename,
    #            'no_transactions' : len(batch.transactions),
                'state': 'finish',
        }, context)
#        netsvc.Logger().notifyChannel("in launch wizard", netsvc.LOG_WARNING,"After write FILENAME file _id: %s"%filename)

# TODO    SET DONE   !!!!!
        return {
                'name': _('Exported file'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': self._name,
                'domain': [],
                'context': dict(context, active_ids=ids),
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': ids[0] or False,
            }


#        obj_payment_order.set_done(cr, uid, [context['active_id']], context)
#        return {'type': 'ir.actions.act_window_close'}




#        t = order.mode and order.mode.type.code or 'manual'
#        if t == 'manual':
#            obj_payment_order.set_done(cr,uid,context['active_id'],context)
#            return {}
#
#        gw = obj_payment_order.get_wizard(t)
#        if not gw:
#            obj_payment_order.set_done(cr,uid,context['active_id'],context)
#            return {}
#
#        module, wizard= gw
#        result = obj_model._get_id(cr, uid, module, wizard)
#        id = obj_model.read(cr, uid, [result], ['res_id'])[0]['res_id']
#        return obj_act.read(cr, uid, [id])[0]

account_payment_make_payment()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
