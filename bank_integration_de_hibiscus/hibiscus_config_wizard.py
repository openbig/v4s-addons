# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 OpenGLOBE (<http://www.openglobe.pl>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#import time
#import sys
#import sepa
from osv import osv, fields
from tools.translate import _
#import xmlrpclib
import urllib
#from wizard.banktools import get_or_create_bank
#import decimal_precision as dp
#import pooler
import netsvc

#For initialization wizard
class hibiscus_config_wizard(osv.osv_memory):
    _name = 'hibiscus.config.wizard'

    _columns = {
#        'name': fields.char('Name',size=64, required=True),
        'company_id': fields.many2one('res.company', 'Company', select=True, required=True),
        'server': fields.char('Server Name', size=64, required=True),
        'port': fields.char('Port Number', size=5, required=True),
        'user': fields.char('User Name', size=32, required=True),
        'password': fields.char('Password', size=32, required=True,),
#        'active': fields.boolean('Active'),
        'secure': fields.boolean('Secure Connection'),
    }
    _defaults = {
#        'active': lambda *a: True,
        'port': lambda *a: '8080',
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
#    def action_cancel(self,cr,uid,ids,conect=None):
#        return {
#                'view_type': 'form',
#                "view_mode": 'form',
#                'res_model': 'ir.actions.configuration.wizard',
#                'type': 'ir.actions.act_window',
#                'target':'new',
#        }

    def action_create(self, cr, uid, ids, context=None):
        hibiscus_tools_obj = self.pool.get('hibiscus.tools')
        settings_obj = self.pool.get('bank.integration.settings')
        partner_bank_obj = self.pool.get('res.partner.bank')
        bank_obj = self.pool.get('res.bank')
        wizard = self.browse(cr, uid, ids[0], context=context)
        server = hibiscus_tools_obj.get_server(cr, uid, wizard.server, wizard.user, wizard.password, wizard.port, wizard.secure)
        try:
            accounts = getattr(server,'hibiscus.xmlrpc.konto.find')()
#            accounts = getattr(server,'hibiscus.xmlrpc.konto.list')()  # deprecated
        except Exception, e:
            raise osv.except_osv(_('Error!'),_('Cannot import Hibiscus accounts: %s')%e)
        logger = netsvc.Logger()
#        netsvc.Logger().notifyChannel("warning", netsvc.LOG_WARNING,"accounts: %s"%accounts)
        for account in accounts:
# Fields Available in dictionary
#kundennummer
#name
#blz
#saldo_available
#unterkonto
#saldo_datum
#bic
#iban
#saldo
#kontonummer
#waehrung
#bezeichnung
#id
#kommentar
            bank_name = False
            try:
                bank_name = getattr(server,'hibiscus.xmlrpc.konto.getBankname')(account['blz'])
            except Exception, e:
                pass
            setting_ids = settings_obj.search(cr, uid, [('parser','=','hibi_ol'), ('hibiscus_server','=',wizard.server), \
                                            ('hibiscus_account_id','=',int(account['id'])), \
                                            ('company_id','=',wizard.company_id.id)], context=context)
            if setting_ids:
                for setting in settings_obj.browse(cr, uid, setting_ids):
                    if setting.partner_bank_id.acc_number != account['kontonummer']:
                        settings_obj.unlink(cr, uid, [setting.id], context=context)
            setting_ids = settings_obj.search(cr,uid,[('parser','=','hibi_ol'),('company_id','=',wizard.company_id.id)], context=context)
            setting_exists = False
#            netsvc.Logger().notifyChannel("WIZARD", netsvc.LOG_WARNING,"Wizard server: %s"%wizard.server)

            for setting in settings_obj.browse(cr, uid, setting_ids):
                if setting.partner_bank_id.acc_number == account['kontonummer'] \
                        and setting.partner_bank_id.bank.bic == account['blz']:
#                        and setting.partner_bank_id.bank.code == account['blz']:
                    settings_obj.write(cr, uid, setting.id, {
                            'hibiscus_account_id' : int(account['id']),
                            'hibiscus_server'   : wizard.server,
                            'hibiscus_port'     : wizard.port,
                            'hibiscus_user'     : wizard.user,
                            'hibiscus_password' : wizard.password,
#                            'active':active,
                            'hibiscus_secure'   : wizard.secure,
                    })
                    bank_name = bank_name or setting.partner_bank_id.bank.name
                    bank_obj.write(cr, uid, setting.partner_bank_id.bank.id, {
#                            'bic' : account['bic'],
                            'bic' : account['blz'],
                            'name' : bank_name, 
                    })
                    setting_exists = True
            if setting_exists:
                continue

            bank_name = bank_name or _("Bank from Hibiscus")
            bank_id = bank_obj.create(cr, uid, {
                'name' : bank_name,
#                'code' : account['blz'],
                'bic' : account['blz'],
                })
            partner_bank_id = partner_bank_obj.create(cr, uid, {
                'acc_number': account['kontonummer'],
                'iban': account['iban'],
                'owner_name' : account['name'],
                'bank': bank_id,
                'name': _("Currency: ") + account['waehrung'] \
                        + _(" Sub Account: ") + account['unterkonto'] \
                        + _(" Description: ") + account['bezeichnung'] \
                        + _(" Customer No: ") + account['kundennummer'] \
                        + _(" Comment: ") + account['kommentar'],
                'partner_id': wizard.company_id.partner_id.id,
                'state': "bank",
                })
            settings_obj.create(cr, uid, {
                'name' : _("Hibiscus OnLine Settings"),
                'active': True,
                'partner_bank_id' : partner_bank_id,
                'parser' : "hibi_ol",
                'hibiscus_account_id' : int(account['id']),
                'hibiscus_server' : wizard.server,
                'hibiscus_port' : wizard.port,
                'hibiscus_user' : wizard.user,
                'hibiscus_password' : wizard.password,
                'hibiscus_secure' : wizard.secure,
#                'journal_id': journal_id,
                })
            
        return {}
hibiscus_config_wizard()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
