# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 OpenGLOBE (<http://www.openglobe.pl>).
#    All Rights Reserved
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
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

# OpenGLOBE changed a lot of original logic of EduSense.

# Many thanks to our contributors
#
# Kaspars Vilkens (KNdati): lenghty discussions, bugreports and bugfixes
# Stefan Rijnhart (Therp): bugreport and bugfix
#
#This module contains the business logic of the wizard account_import_wizard.
#The parsing is done in the parser modules. Every parser module is required to
#use parser.models as a mean of communication with the business logic.
#
from osv import osv, fields
import time
#import netsvc
import logging
import base64
import datetime
#from datetime import datetime
#from tools import config
from tools.translate import _
#from account_banking.parsers import models
#from account_banking.parsers.convert import *
from bank_integration.struct import struct
#from account_banking import sepa
#from banktools import *
import decimal_precision as dp
#from account_bank_integration import parsers

def _format_iban(string):
    res = ""
    for char in string:
        if char.isalnum():
            res += char.upper()
    return res

def str2date(datestr, format='%Y-%m-%d'):
    '''Convert a string to a datatime object'''
    return datetime.datetime.strptime(datestr, format)

def date2str(date, format='%Y-%m-%d'):
    '''Convert a datetime object to a string'''
    return date.strftime(format)

class import_wizard(osv.osv_memory):
    _name = 'account.banking.bank.import'

# GG rewritten
    def get_bank_accounts(self, cr, uid, account_number, account_bank_code, account_bank_swift, 
            company, log, fail=False, context=None):
#        Get the bank account with account number account_number
        # No need to search for nothing
        if not (account_number):
            return False
        bank_account_ids = False
        partner_bank_obj = self.pool.get('res.partner.bank')
# TODO Searching within comapmny
        if account_number[0].isalpha():
            bank_account_ids = partner_bank_obj.search(cr, uid, [('acc_number', '=', account_number),'|',
                    ('partner_id.company_id','=',company.id),('partner_id.company_id','=',False)])
        if not account_number[0].isalpha():
            if account_bank_code or account_bank_swift:
                bank_obj = self.pool.get('res.bank')
                bank_ids = bank_obj.search(cr, uid, ['|',('bic','=',account_bank_code),('bic','=',account_bank_swift)])
                if bank_ids:
                    bank_account_ids = partner_bank_obj.search(cr, uid, [
                        ('acc_number', '=', account_number),('bank','in',bank_ids), '|',
                    ('partner_id.company_id','=',company.id),('partner_id.company_id','=',False)])
                else:
                    log.append( _('Bank code %(bank_code)s was not found in the database')
                        % dict(bank_code = account_bank_code or account_bank_swift)  )
        if not bank_account_ids:
            if not fail:
                log.append( _('Bank account %(account_no)s was not found in the database')
                    % dict(account_no = account_number) )
            return []
        return partner_bank_obj.browse(cr, uid, bank_account_ids)

# Separated for inheriting and expanding by parsers
    def search_partner(self,cr, uid, transaction, country_id, context=None):
# TODO Searching within company
        partner_obj = self.pool.get('res.partner')
        address_obj = self.pool.get('res.partner.address')
        partner_ids = partner_obj.search(cr, uid, [('name', 'ilike', transaction['partner_name'])])
#        logger = netsvc.Logger()
#        logger.notifyChannel("BANKING GENERAL", netsvc.LOG_DEBUG,"After partner search. Partner_ids: %s"%partner_ids)
        if not partner_ids:
            address_ids = address_obj.search(cr, uid, [('name', 'ilike', transaction['partner_address_name']),('partner_id', '<>', None)])
            address_ids += address_obj.search(cr, uid, [('name', 'ilike', transaction['partner_name']),('partner_id', '<>', None)])
#            logger.notifyChannel("BANKING GENERAL", netsvc.LOG_DEBUG,"After address search. Address_ids: %s"%address_ids)
            if address_ids:
                addresses = address_obj.browse(cr, uid, address_ids)
                for address in addresses:
                    partner_ids.append(address.partner_id.id)
    #    if not partner_ids:
            # Try brute search on address and then match reverse
    #        filter = [('partner_id', '<>', None)]
    #        filter.append(('country_id', '=', country_id))
    #        if transaction['partner_street']:
    #            filter.append(('street', 'ilike', transaction['partner_street']))   # GG fix
    #        if  transaction['partner_city']:
    #            filter.append(('city', 'ilike', transaction['partner_city']))
    #        if transaction['partner_zip']:
    #            filter.append(('zip', 'ilike', transaction['partner_zip']))
    #        address_ids = address_obj.search(cr, uid, filter)
    #        key = transaction['partner_name'].lower()
    
            # Make sure to get a unique list
    #        partner_ids = list(set([x.partner_id.id
    #                       for x in address_obj.browse(cr, uid, address_ids)
                           # Beware for dangling addresses
    #                       if _has_attr(x.partner_id, 'name') and x.partner_id.name.lower() in key  ]))
    #    logger.notifyChannel("BANKING GENERAL", netsvc.LOG_DEBUG,"Partner ids: %s"%partner_ids)
        return partner_ids

# Separated for inheriting and expanding by parsers
    def create_partner(self,cr, uid, transaction, country_id, results, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.create(cr, uid, dict(
            name= "(?)"+transaction['partner_name'], active=True, comment='Generated from Bank Statements Import',
            address=[(0,0,{
                        'name': transaction['partner_address_name'] or '',
                        'street': transaction['partner_street'] or '',
    #                    'street2': len(address) > 1 and address[1] or '',
                        'city': transaction['partner_city'] or '',
                        'zip': transaction['partner_zip'] or '',
                        'country_id': country_id,
            })],
        ))
        results.trans_partner_created_cnt += 1
        return partner_id

# Separated for inheriting and expanding by parsers
    def search_create_partner_unknown(self,cr, uid, transaction, country_id, results, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_ids = partner_obj.search(cr, uid, [('name','=','Unknown')])
        if partner_ids:
            partner_id = partner_ids[0]
        else:
            partner_id = partner_obj.create(cr, uid, dict(name= 'Unknown',
                comment='Generated from Bank Statements Import, For reassigning the bank account to real Partner.', 
                address=[(0,0,{'name': 'Unknown'})]))
        results.log.append( _("Partner with name: %(name)s and address: %(address)s assigned to 'Unknown' partner") \
                        % {'name': transaction['partner_name'], 'address': transaction['partner_street']})
        return partner_id

    def get_or_create_partner(self,cr, uid, transaction, country_id, results, matching, context=None):
#        Get or create the partner belonging to the account holders name <name>
#        logger = netsvc.Logger()
#        logger.notifyChannel("BANKING GENERAL", netsvc.LOG_DEBUG,"In get or create Partner")
        partner_obj = self.pool.get('res.partner')
        address_obj = self.pool.get('res.partner.address')
        partner_ids = self.search_partner(cr, uid, transaction, country_id)
        if not partner_ids:
            if matching == 'partner_create':
                partner_id = self.create_partner(cr, uid, transaction, country_id, results)
            elif matching == 'partner_unknown':
                partner_id = self.search_create_partner_unknown(cr, uid, transaction, country_id, results)
            else:
                partner_id = False
        elif len(partner_ids) > 1:
            results.log.append( _('More then one possible match found for partner with name %(name)s') % {'name': transaction['partner_name']})
            return False
        else:
            partner_id = partner_ids[0]
            results.trans_partner_matched_cnt += 1
        return partner_id
    
#    def get_account_settings(self, cr, uid, account_iban, account_number, account_bank_code, account_bank_swift, 
#            company, log, bank_accounts, context=None):
##        Get the matching bank account for this company. Currency is the ISO code
##        for the requested currency.
#    #    bank_settings_obj = pool.get('bank.integration.settings')
#    
#        if not bank_accounts:
#            bank_accounts = self.get_bank_accounts(cr, uid, account_iban, account_number, account_bank_code, account_bank_swift,
#                company, log, fail=True)
#        if not bank_accounts:
#            return False
#        elif len(bank_accounts) != 1:
#            log.append(_('More than one bank account was found with the same number %(account_no)s')
#                % dict(account_no = account_number))
#            return False
#        if bank_accounts[0].partner_id.id != company.partner_id.id:
#            log.append(_('Account %(account_no)s is not owned by %(partner)s')
#                % dict(account_no = account_number, partner = company.partner_id.name, ))
#            return False
##        results = struct()
##        results.account = bank_accounts[0]
#        bank_settings_obj = self.pool.get('bank.integration.settings')
#        criteria = [('partner_bank_id', '=', bank_accounts[0].id)]
#    
#        # Find matching journal for currency
#        journal_obj = self.pool.get('account.journal')
#        journal_ids = journal_obj.search(cr, uid, [('type', '=', 'bank'),('company_id','=',company.id)])
#        if journal_ids:
#            criteria.append(('journal_id', 'in', journal_ids))
#        # Find bank account settings
#        bank_settings_ids = bank_settings_obj.search(cr, uid, criteria)
#        if bank_settings_ids:
#            settings = bank_settings_obj.browse(cr, uid, bank_settings_ids)[0]
#        else:
#            settings = False
#        return settings
    
    def create_bank_account(self, cr, uid, partner, transaction, country_id, context=None ):
#        Create a matching bank account with this holder for this partner.
    #    logger = netsvc.Logger()
    #    logger.notifyChannel("BANKING GENERAL", netsvc.LOG_DEBUG,"account_number '%s'" % (account_number,))
        bank_obj = self.pool.get('res.bank')
        values = struct(partner_id = partner.id,)
        bank_code = transaction['partner_bank_code']
        bank_swift = transaction['partner_bank_swift']
        values.country_id = country_id
        bank_ids = []
        if partner.name == 'Unknown':
            values.owner_name = transaction['partner_name']
            values.street = transaction['partner_street']+transaction['partner_street2']
            values.city = transaction['partner_city']
            values.zip = transaction['partner_zip']
            values.name = _("Object created to keep Bank Account in database. Reassign it to real Partner.")
        else:
            values.owner_name = partner.name
        if transaction['partner_bank_account'][0].isalpha():
            values.state = 'iban'
#            values.iban = _format_iban(transaction['partner_bank_account'])
        else:
            values.state = 'bank'
        values.acc_number = _format_iban( transaction['partner_bank_account'])
        if bank_swift:
            bank_ids = bank_obj.search(cr, uid, [('bic', 'ilike', bank_swift ),])
        elif bank_code:
            bank_ids = bank_obj.search(cr, uid, [('bic', 'ilike', bank_code ),])
        if bank_ids:
            bank_id = bank_ids[0]
        elif bank_code or bank_swift:  # TODO If bank acc number is iban the swift (bic) must be present and correct. Otherwise OpenERP crashes.
            bank_id = bank_obj.create(cr, uid,dict(bic= (bank_swift or bank_code), name = _("Bank to fix, ")+ (bank_swift or bank_code), country_id = country_id))
        elif transaction['partner_bank_account']:
            bank_id = bank_obj.create(cr, uid, dict(code = transaction['partner_bank_account'], name = _("Bank to fix."), country_id = country_id))
        else:
            return False
        values.bank = bank_id
        return self.pool.get('res.partner.bank').create(cr, uid, values)
    
        
    def _link_payment(self, cr, uid, trans, payment_lines, partner_ids, bank_account_ids, results, linked_payments, context=None):
        '''
        Find the payment order belonging to this reference - if there is one
        This is the easiest part: when sending payments, the returned bank info
        should be identical to ours.
        '''
        # TODO: Not sure what side effects are created when payments are done
        # for credited customer invoices, which will be matched later on too.
        digits = dp.get_precision('Account')(cr)[1]
        candidates = [x for x in payment_lines
                      if x.communication == trans['ref'] 
                      and round(x.amount, digits) == -round(trans.transferred_amount, digits)
                      and trans.remote_account == x.bank_id.acc_number
                     ]
        if len(candidates) == 1:
            candidate = candidates[0]
            # Check cache to prevent multiple matching of a single payment
            if candidate.id not in linked_payments:
                linked_payments[candidate.id] = True
                payment_line_obj = self.pool.get('payment.line')
                payment_line_obj.write(cr, uid, [candidate.id], {
                    'export_state': 'done',
                    'date_done': trans.effective_date.strftime('%Y-%m-%d')}
                )
                
                return self._get_move_info(cr, uid, candidate.move_line_id)

        return False

    def _link_invoice(self, cr, uid, trans, settings, values, results, context=None):
        def eyecatcher(invoice):
            '''
            Return the eyecatcher for an invoice
            '''
            return invoice.type.startswith('in_') and invoice.name or invoice.number

        def has_id_match(invoice, ref, msg):
            '''
            Aid for debugging - way more comprehensible than complex
            comprehension filters ;-)

            Match on ID of invoice (reference, name or number, whatever
            available and sensible)
            '''
            if invoice.reference:
                # Reference always comes first, as it is manually set for a
                # reason.
                iref = invoice.reference.upper()
                if iref in ref or iref in msg:
                    return True
            if invoice.type.startswith('in_'):
                # Internal numbering, no likely match on number
                if invoice.name:
                    iname = invoice.name.upper()
                    if iname in ref or iname in msg:
                        return True
            elif invoice.type.startswith('out_'):
                # External id's possible and likely
                inum = invoice.number.upper()
                if inum in ref or inum in msg:
                    return True

            return False

        def _sign(invoice):
            '''Return the direction of an invoice'''
            return {'in_invoice': -1, 
                    'in_refund': 1,
                    'out_invoice': 1,
                    'out_refund': -1
                   }[invoice.type]


        logger = logging.getLogger('BANK_INTEGRATION')
#        logger.notifyChannel("BANKING GENERAL", netsvc.LOG_DEBUG,"After partner search. transfer: %s"% trans)
        digits = dp.get_precision('Account')(cr)[1]
        partial = False
        voucher_id = False
#        payment_window = datetime.timedelta(days=20)  # make settings.payment_window   !!!!
    # TODO put this as parameter to Default settings object
#        difference_percent = 3.0                        # make settings difference_percent 
        journal_obj = self.pool.get('account.journal')
        move_line_obj = self.pool.get('account.move.line')
        voucher_line_obj = self.pool.get('account.voucher.line')
        currency_id = settings.journal_id.company_id.currency_id.id
        amount = trans['amount']
        if settings.journal_id.currency and settings.journal_id.currency.id != currency_id:
            currency_id = settings.journal_id.currency.id
            currency_obj = self.pool.get('res.currency')
            amount = currency_obj.compute(cr, uid, 
                        currency_id,  # from currency
                        settings.journal_id.company_id.currency_id.id,  # to currency
                        trans['amount'],     # amount
                        round=True, context=context)

#        partner = self.pool.get('res.partner').browse(cr, uid, partner_ids[0])
        if amount > 0:
            journal_types = ('sale', 'purchase_refund')
        else:
            journal_types = ('purchase', 'sale_refund')
        journal_ids = journal_obj.search(cr, uid, [
                ('type', 'in', journal_types),
                ('company_id', '=', settings.journal_id.company_id.id),
            ])
            # Get all unreconciled moves predating the last statement in one big
            # swoop. Assumption: the statements in the file are sorted in ascending
            # order of date.
#        logger.notifyChannel("BANKING GENERAL", netsvc.LOG_DEBUG,"Journals: %s Values %s"% (str(journal_ids),str(values)))
        if values.partner_id:
            move_line_ids = move_line_obj.search(cr, uid, [
                ('reconcile_id', '=', False),
                ('journal_id', 'in', journal_ids),
                ('account_id.reconcile', '=', True),
                ('date', '<=', trans['date']),
                ('partner_id', '=', values.partner_id),
            ])
        else:
            move_line_ids = move_line_obj.search(cr, uid, [
                ('reconcile_id', '=', False),
                ('journal_id', 'in', journal_ids),
                ('account_id.reconcile', '=', True),
                ('date', '<=', trans['date']),
#                ('partner_id', '=', values.partner.id),
            ])

        if move_line_ids:
            candidates = move_line_obj.browse(cr, uid, move_line_ids)
        else:
            candidates = []
        logger.warn("Candidates: %s", candidates)
#        logger.notifyChannel("BANKING GENERAL", netsvc.LOG_DEBUG,"Candidates: %s"% str(candidates))

        best = False
        by_amount = False
        if candidates:
            better_candidates = [x for x in candidates 
                      if x.invoice and has_id_match(x.invoice, trans['ref'], trans['note'])
#                             and str2date(x.invoice.date_invoice, '%Y-%m-%d')
#                                <= (trans['date'] + payment_window)
                     ]
            if better_candidates:
                partner = better_candidates[0].partner_id or False
                if partner:
                    values.partner_id = partner.id
                    if not partner.bank_ids:
                        self.create_bank_account(cr, uid, partner, trans, partner.country.id,)
            best = better_candidates
            if best:
                voucher_line_ids = voucher_line_obj.search(cr, uid, [('move_line_id','=', best[0].id)])
                existing_lines = voucher_line_obj.browse(cr, uid, voucher_line_ids)
                existing_sum = 0
                for voucher_line in existing_lines:
                    existing_sum += voucher_line.amount
                sum_of_vouchers = existing_sum + abs(trans['amount'])
#                logger.notifyChannel("BANKING GENERAL", netsvc.LOG_DEBUG,"Existing lines: %s Sum of vouchers: %s, credit: %s, debit: %s "% \
#                            (str(existing_lines), sum_of_vouchers, best[0].credit, best[0].debit))
                if sum_of_vouchers > (best[0].credit or best[0].debit):     # Some voucher line for this account move already exists so don't create another.
                    return False

            if not best and values.partner_id:
                best = [x for x in candidates
                        if round(abs(x.credit or x.debit), digits) == 
                              round(abs(amount), digits)
                   ]
                if not best:
                    best = [x for x in candidates
                            if abs(round(abs(x.credit or x.debit), digits) - round(abs(amount), digits)) / round(abs(amount), digits) \
                            <= settings.amount_tolerance/100 ]
                if best:
                    by_amount = True
                    voucher_line_ids = voucher_line_obj.search(cr, uid, [('move_line_id','=', best[0].id)])
                    if len(voucher_line_ids):     # Some voucher line for this account move already exists so don't create another.
                        return False

        if best:
            # Exact match
            move_line = best[0]
            results.trans_matched_cnt += 1
            invoice_number = move_line.invoice.number
            values.ref = invoice_number
            if by_amount:
                results.log.append( _('Invoice found by amount: %(invoice)s') % { 'invoice': invoice_number})
            else:
                results.log.append( _('Invoice found by description: %(invoice)s') % { 'invoice': invoice_number})
            values.account_id = move_line.account_id.id
            if trans['amount'] > 0:
                voucher_account_id = settings.journal_id.default_credit_account_id.id
                type = 'receipt'
            else:
                voucher_account_id = settings.journal_id.default_debit_account_id.id
                type = 'payment'
            voucher_id = self.pool.get('account.voucher').create(cr, uid, {
                    'type': type ,
                    'name': trans['name'],
                    'date': trans['date'],
                    'journal_id':  settings.journal_id.id,
                    'account_id': voucher_account_id, 
#        'narration':fields.text('Notes', readonly=True, states={'draft':[('readonly',False)]}),
                    'currency_id': currency_id,
                    'company_id': settings.journal_id.company_id.id,
                    'state': 'draft',
                    'amount': abs(trans['amount']),
#        'tax_amount':fields.float('Tax Amount', digits_compute=dp.get_precision('Account'), readonly=True, states={'draft':[('readonly',False)]}),
                    'reference': invoice_number,
#        'number': fields.char('Number', size=32, readonly=True,),
#        'move_id':fields.many2one('account.move', 'Account Entry'),
                   'partner_id': values.partner_id,
#        'audit': fields.related('move_id','to_check', type='boolean', relation='account.move', string='Audit Complete ?'),
                   'pay_now': 'pay_later',
#        'tax_id':fields.many2one('account.tax', 'Tax', readonly=True, states={'draft':[('readonly',False)]}),
#        'pre_line':fields.boolean('Previous Payments ?', required=False),
#        'date_due': fields.date('Due Date', readonly=True, select=True, states={'draft':[('readonly',False)]}),
#        'payment_option':fields.selection([
#                                           ('without_writeoff', 'Keep Open'),
#                                           ('with_writeoff', 'Reconcile with Write-Off'),
#                                           ], 'Payment Difference', required=True, readonly=True, states={'draft': [('readonly', False)]}),
#        'writeoff_acc_id': fields.many2one('account.account', 'Write-Off account', readonly=True, states={'draft': [('readonly', False)]}),
#        'comment': fields.char('Write-Off Comment', size=64, required=True, readonly=True, states={'draft': [('readonly', False)]}),
#        'analytic_id': fields.many2one('account.analytic.account','Write-Off Analytic Account', readonly=True, states={'draft': [('readonly', False)]}),
#        'writeoff_amount': fields.function(_get_writeoff_amount, method=True, string='Write-Off Amount', type='float', readonly=True),
            })

            voucher_line_obj.create(cr, uid, {
                    'voucher_id': voucher_id,
                    'name':invoice_number,
                    'account_id': move_line.account_id.id,
#        'untax_amount':fields.float('Untax Amount'),
                    'amount': abs(trans['amount']),
                    'type': trans['amount'] >0 and 'cr' or 'dr',
#        'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account'),
                    'move_line_id': move_line.id,
            })

        return voucher_id

    def _link_canceled_debit(self, cr, uid, trans, payment_lines, partner_ids, bank_account_ids, log, context=None):
        '''
        Direct debit transfers can be canceled by the remote owner within a
        legaly defined time period. These 'payments' are most likely
        already marked 'done', which makes them harder to match. Also the
        reconciliation has to be reversed.
        '''
        # TODO: code _link_canceled_debit
        return False

    def _link_costs(self, cr, uid, trans, period_id, settings, log, context=None):
        '''
        Get or create a costs invoice for the bank and return it with
        the payment as seen in the transaction (when not already done).
        '''
        if not settings.costs_account_id:
            return []

        digits = dp.get_precision('Account')(cr)[1]
        amount = round(abs(trans.transferred_amount), digits)
        # Make sure to be able to pinpoint our costs invoice for later
        # matching
        reference = '%s.%s: %s' % (trans.statement_id, trans['name'], trans['ref'])

        # search supplier invoice
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = invoice_obj.search(cr, uid, [
            '&',
            ('type', '=', 'in_invoice'),
            ('partner_id', '=', settings.bank_partner_id.id),
            ('company_id', '=', settings.company_id.id),
            ('date_invoice', '=', date2str(trans.effective_date)),
            ('reference', '=', reference),
            ('amount_total', '=', amount),
            ]
        )
        if invoice_ids and len(invoice_ids) == 1:
            invoice = invoice_obj.browse(cr, uid, invoice_ids)[0]
        elif not invoice_ids:
            # create supplier invoice
            partner_obj = self.pool.get('res.partner')
            invoice_lines = [(0,0,dict(
                amount = 1,
                price_unit = amount,
                name = trans['note'] or trans['ref'],
                account_id = settings.costs_account_id.id
            ))]
            invoice_address_id = partner_obj.address_get(
                cr, uid, [settings.bank_partner_id.id], ['invoice']
            )
            invoice_id = invoice_obj.create(cr, uid, dict(
                type = 'in_invoice',
                company_id = settings.company_id.id,
                partner_id = settings.bank_partner_id.id,
                address_invoice_id = invoice_address_id['invoice'],
                period_id = period_id,
                journal_id = settings.invoice_journal_id.id,
                account_id = settings.bank_partner_id.property_account_payable.id,
                date_invoice = date2str(trans.effective_date),
                reference_type = 'none',
                reference = reference,
                name = trans['ref'] or trans['note'],
                check_total = amount,
                invoice_line = invoice_lines,
            ))
            invoice = invoice_obj.browse(cr, uid, invoice_id)
            # Create workflow
            invoice_obj.button_compute(cr, uid, [invoice_id], 
                                       {'type': 'in_invoice'}, set_total=True)
            wf_service = netsvc.LocalService('workflow')
            # Move to state 'open'
            wf_service.trg_validate(uid, 'account.invoice', invoice.id,
                                    'invoice_open', cr)

        # return move_lines to mix with the rest
        return [x for x in invoice.move_id.line_id if x.account_id.reconcile]

    def _check_accounts(self, cr, uid, import_wizard, statement, results, error_accounts, context=None):

#        bank_accounts = [import_wizard.import_settings_id.partner_bank_id]
#        if not (bank_accounts or statement['home_bank_account_iban'] or statement['home_bank_account']):
#            results.log.append( _('No home bank account number provided. Nor in defaults and file.') )
#            error_accounts[statement['name']] = True
#            results.error_cnt += 1
#            return False
#        settings = self.get_account_settings(cr, uid, statement['home_bank_account_iban'],statement['home_bank_account'],
#                   statement['home_bank_code'], statement['home_bank_swift'], company, results.log, bank_accounts, )
#        if not settings:
#            results.log.append( _('Statements found for unknown account %(bank_account)s') % {'bank_account': statement['name']})
#            error_accounts[statement['name']] = True
#            results.error_cnt += 1
#            return False
        home_bank_account = import_wizard.banking_settings_id.partner_bank_id
        if home_bank_account.state == "iban" and statement['home_bank_account'] and statement['home_bank_account'][0].isalpha():
            if _format_iban(home_bank_account.acc_number).lower() != _format_iban(statement['home_bank_account']).lower():
                results.log.append(
                    _('Bank account in import %(bank_account)s is different than in wizard %(home_bank_account)s') %
                    {'bank_account': statement['home_bank_account'], 'home_bank_account':home_bank_account.acc_number}
                )
                error_accounts[statement['name']] = True
                results.error_cnt += 1
                return False
        elif statement['home_bank_account'] and \
            not ( _format_iban(home_bank_account.acc_number).lower() == _format_iban(statement['home_bank_account']).lower() \
                and ( home_bank_account.bank.bic == statement['home_bank_swift'] \
                      or home_bank_account.bank.bic == statement['home_bank_code'] \
                    ) \
            ):
            results.log.append(
                   _('Bank account and swift or code in import %(bank_account)s is different than in wizard %(home_bank_account)s') %
                   {'bank_account': statement['home_bank_account'], 'home_bank_account':home_bank_account.acc_number}
               )
            error_accounts[statement['name']] = True
            results.error_cnt += 1
            return False
        return True

    def get_account(self, cr, uid, settings, transaction, values, context=None):
        if transaction['type'] == 'bank':
            values.partner_id = settings.bank_partner_id and settings.bank_partner_id.id or False
            if transaction['amount'] > 0:
                values.account_id = settings.income_account_id.id
            else:
                values.account_id = settings.costs_account_id.id


    def import_statements_file(self, cr, uid, ids, context):
#        Import bank statements / bank transactions file.
#        This method represents the business logic, the parser modules
#        represent the decoding logic.
#        logger = netsvc.Logger()
#        logger.notifyChannel("BANKING GENERAL", netsvc.LOG_DEBUG,"After partner search. Partner_ids: %s"%partner_ids)
        import_wizard = self.browse(cr, uid, ids, context)[0]
#        statements_file = import_wizard.file
#        data = base64.decodestring(statements_file)

        company_obj = self.pool.get('res.company')
        user_obj = self.pool.get('res.user')
        partner_bank_obj = self.pool.get('res.partner.bank')
        journal_obj = self.pool.get('account.journal')
        move_line_obj = self.pool.get('account.move.line')  # ????
        payment_line_obj = self.pool.get('payment.line')
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        statement_file_obj = self.pool.get('account.banking.imported.file')
        payment_order_obj = self.pool.get('payment.order')
        currency_obj = self.pool.get('res.currency')

        bank_parsers_obj = self.pool.get('bank.parsers')
        settings = import_wizard.banking_settings_id
        if not settings.journal_id:
            raise osv.except_osv( _('ERROR!'),
                _("Configuration settings for import: %(settings)s doesn't contain journal for Bank Statement. Please set one.") % {'settings': settings.name})

        # get the parser to parse the file
        parser_code = settings.parser + "_import"
        if not hasattr(bank_parsers_obj,parser_code):
            raise osv.except_osv( _('ERROR!'),
                _('Unable to find import method for parser %(parser)s. Parser class not found.') % {'parser': parser_code})
        parser = getattr(bank_parsers_obj,parser_code)
#        parser = models.create_parser(parser_code)
        if not parser:
            raise osv.except_osv( _('ERROR!'),
                _('Unable to import parser %(parser)s. Parser class not found.') % {'parser': parser_code})
        company = settings.company_id
        statements = parser(cr, uid, import_wizard, context=context)
        if not statements:
            raise osv.except_osv( _('INFORMATION'), _('Nothing to import.'))

        import_id = statement_file_obj.create(cr, uid, dict(         # Create the file now, as the statements need to be linked to it
            company_id = company.id,
            format = parser_code,
            file = import_wizard.file,
            state = 'unfinished',
        ))
        # Results
        results = struct(
            stat_loaded_cnt = 0,
            trans_loaded_cnt = 0,
            stat_skipped_cnt = 0,
            trans_skipped_cnt = 0,
            trans_account_matched_cnt = 0,   # partners matched by bank account
            trans_partner_matched_cnt = 0,   # partners matched by name or address
            trans_partner_created_cnt = 0,   # partners created
            trans_matched_cnt = 0,
            bank_costs_invoice_cnt = 0,
            error_cnt = 0,
            log = [],
        )

        # Caching
        error_accounts = {}
#        info = {}
        imported_statement_ids = []
#        linked_payments = {}
#        linked_invoices = {}
        payment_lines = []
        for statement in statements:
            if statement['name'] in error_accounts:
                # Don't repeat messages
                results.stat_skipped_cnt += 1
                results.trans_skipped_cnt += len(statement['lines'])
                continue
            if not self._check_accounts(cr, uid, import_wizard, statement, results, error_accounts,  context):
                continue

            # Final check: no coercion of currencies!
            if settings.journal_id.currency:
                if statement['currency'] and settings.journal_id.currency.name != statement['currency']:
                    results.log.append(
                        _('Statement %(statement_id)s for account %(bank_account)s uses different currency than the defined bank journal.'
                         ) % {'statement_id': statement['name'], 'bank_account': statement['home_bank_account'],} )
                    error_accounts[statement['name']] = True
                    results.error_cnt += 1
                    continue
#                import_currency = settings.journal_id.currency

            else:
                if statement['currency'] and settings.journal_id.company_id.currency_id.name != statement['currency']:
                    results.log.append(
                        _('Statement %(statement_id)s for account %(bank_account)s uses different currency than journal company.'
                         ) % { 'statement_id': statement['name'], 'bank_account': statement['home_bank_account'], })
                    error_accounts[statement['name']] = True
                    results.error_cnt += 1
                    continue
#                import_currency = company.currency_id

            # Check existence of previous statement
            statement_ids = statement_obj.search(cr, uid, [
                ('name', '=', statement['name']),
                ('date', '=', statement['date']),
            ])
            if statement_ids:
                results.log.append(_('Statement %(id)s known - skipped') % {'id': statement['name'] })
                continue

            statement_id = statement_obj.create(cr, uid, dict(
                name = statement['name'],
                journal_id = settings.journal_id.id,
                date = statement['date'],
                balance_start = statement['balance_start'],
                balance_end_real = statement['balance_end_real'],
#                balance_end = statement.end_balance,
                state = 'draft',
                user_id = uid,
                banking_id = import_id,
            ))
            imported_statement_ids.append(statement_id)
            i = 0
            max_trans = len(statement['lines'])
            while i < max_trans:
                move_info = False
                account_id = False
                st_line_type = 'general'
                transaction = statement['lines'][i]
                values = struct(
                    name = '%s.%s' % (statement['name'], transaction['name'] or subno),
                    date = transaction['date'],
                    amount = transaction['amount'],
                    partner_id = False,
                    account_id = False,
                    type = 'general',
                    statement_id = statement_id,
                    note = transaction['note'],
                    ref = transaction['ref'],
                    sequence = int(transaction['sequence'])
                )

                if transaction['type'] and transaction['type'] not in ['supplier','customer','general']:
                    self.get_account(cr, uid, settings, transaction, values, context)
                else:     #if transaction['type'] in ['supplier','customer']:
                    partner = False
                    if not settings.partner_matching == 'no_matching':
                    # Link remote partner, import account when needed
                        partner_banks = self.get_bank_accounts(cr, uid, 
#                            transaction['partner_bank_account_iban'], 
                            transaction['partner_bank_account'],
                            transaction['partner_bank_code'], transaction['partner_bank_swift'],
                            company, results.log, fail=False )  # True
                        if partner_banks:
                            results.trans_account_matched_cnt += 1
                            partner = partner_banks[0].partner_id
                    if not partner and transaction['partner_name'] \
                            and settings.partner_matching in ['by_name','partner_create','partner_unknown']:
                        if transaction['partner_country']:
                            country_obj = self.pool.get('res.country')
                            country_ids = country_obj.search(cr, uid, [('code', '=', transaction['partner_country'])])
                            country_id = country_ids and country_ids[0] or False
                        else:
                            country_id = False
                        partner_id = self.get_or_create_partner(cr, uid, transaction, country_id, results, settings.partner_matching, context)
                        if partner_id:
                            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
                            self.create_bank_account(cr, uid, partner, transaction, country_id, context)
                    if partner:
                        values.partner_id = partner.id
                    if partner and settings.invoice_matching != 'no_matching' or settings.partner_matching == "by_invoice":
                        values.voucher_id = self._link_invoice(cr, uid, transaction, settings, values, results, context)
                        partner = values.partner_id and self.pool.get('res.partner').browse(cr, uid, values.partner_id, context)
                    if partner:
                        if transaction['amount'] < 0:
                            values.type = 'supplier'
                            values.account_id = partner.property_account_payable.id
                        else:
                            values.type = 'customer'
                            values.account_id = partner.property_account_receivable.id

                # Credit means payment... isn't it?
                if transaction['amount'] < 0 and payment_lines:
                    # Link open payment - if any
                    move_info = self._link_payment(
                        cr, uid, transaction,
                        payment_lines, partner_ids,
                        partner_banks, results.log, linked_payments,
                        )
                if not values.account_id:
                    if transaction['amount'] < 0:
                        values.account_id = settings.default_credit_account_id.id
                    else:
                        values.account_id = settings.default_debit_account_id.id
                statement_line_id = statement_line_obj.create(cr, uid, values)
                results.trans_loaded_cnt += 1
                # Only increase index when all generated transactions are
                # processed as well
                i += 1

            results.stat_loaded_cnt += 1

        #recompute statement end_balance for validation
        statement_obj.button_dummy(cr, uid, imported_statement_ids, context=context)

        report = [
            '%s: %s' % (_('Total number of statements'),  results.stat_skipped_cnt + results.stat_loaded_cnt),
            '%s: %s' % (_('Total number of transactions'), results.trans_skipped_cnt + results.trans_loaded_cnt),
            '%s: %s' % (_('Number of errors found'), results.error_cnt),
            '%s: %s' % (_('Number of statements skipped due to errors'), results.stat_skipped_cnt),
            '%s: %s' % (_('Number of transactions skipped due to errors'), results.trans_skipped_cnt),
            '%s: %s' % (_('Number of statements loaded'),  results.stat_loaded_cnt),
            '%s: %s' % (_('Number of transactions loaded'), results.trans_loaded_cnt),
            '%s: %s' % (_('Number of bank accounts matched'), results.trans_account_matched_cnt),
            '%s: %s' % (_('Number of partners matched'), results.trans_partner_matched_cnt),
            '%s: %s' % (_('Number of partners created'), results.trans_partner_created_cnt),
            '%s: %s' % (_('Number of transactions matched'), results.trans_matched_cnt),
            '%s: %s' % (_('Number of bank costs invoices created'), results.bank_costs_invoice_cnt),
            '',
            '%s:' % ('Error report'),
            '',
        ]
        text_log = '\n'.join(report + results.log)
        state = results.error_cnt and 'error' or 'ready'
        statement_file_obj.write(cr, uid, import_id, dict(state = state, log = text_log,), context)
        if not imported_statement_ids:
            # file state can be 'ready' while import state is 'error'
            state = 'error'
        self.write(cr, uid, [ids[0]], dict(import_id = import_id, log = text_log, state = state,
                statement_ids = [[6, 0, imported_statement_ids]],), context)
        return {
            'name': _('Import Bank Transactions File'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': self._name,
            'domain': [],
            'context': dict(context, active_ids=ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': ids[0] or False,
        }

    _columns = {
        'banking_settings_id' : fields.many2one(
            'bank.integration.settings', 'Import Settings', required=True,
                help = "Select your import configuration settings for import.",
            states={
                'ready': [('readonly', True)],
                'error': [('readonly', True)],
                },
            ), 
        'file': fields.binary(
            'Statements File', 
            help = ('The Transactions File to import. Please note that while it is '
            'perfectly safe to reload the same file multiple times or to load in '
            'timeframe overlapping statements files, there are formats that may '
            'introduce different sequencing, which may create double entries.\n\n'
            'For some import the file selection is not needed. Fe. for OnLine pulling.'),
            states={
                'ready': [('readonly', True)],
                'error': [('readonly', True)],
                },),
        'log': fields.text('Log', readonly=True),
        'state': fields.selection(
            [('init', 'init'), ('ready', 'ready'),
             ('error', 'error')],
            'State', readonly=True),
        'import_id': fields.many2one(
            'account.banking.imported.file', 'Import File'),
        # osv_memory does not seem to support one2many
        'statement_ids': fields.many2many(
            'account.bank.statement', 'rel_wiz_statements', 'wizard_id',
            'statement_id', 'Imported Bank Statements'),
        }

    _defaults = {
        'state': 'init',
#        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        }
import_wizard()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
