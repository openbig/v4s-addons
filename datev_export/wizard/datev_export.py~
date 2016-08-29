# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Module datev_export
#    Copyrigt (C) 2010 OpenGLOBE Grzegorz Grzelak (www.openglobe.pl)
#                       and big-consulting GmbH (www.openbig.de)
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

import netsvc
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from osv import fields, osv
from tools.translate import _
from xml.dom import minidom
import re
import zipfile
import StringIO
import base64
import logging
from lxml import etree
import tools
#import uuid

class datev_export_options(osv.osv_memory):
    _name = "datev.export.options"
    _description = "Export to XML Datev format using options"
    _columns = {
        'in_invoice': fields.boolean('Incoming Invoices'),
        'out_invoice': fields.boolean('Outgoing Invoices'),
        'in_refund': fields.boolean('Incoming Refunds'),
        'out_refund': fields.boolean('Outgoing Refunds'),
        'date_start': fields.date('From Date', help="Ignored if Period is selected"),
        'date_stop': fields.date('To Date', help="Ignored if Period is selected"),
        'period_id': fields.many2one('account.period', 'Period'),
        'company_id': fields.many2one('res.company', 'Company', required = True),
        'datev_file': fields.binary('.zip File', readonly = True),
#        'export_filename': fields.char('Filename',  size= 64,),
        'datev_filename': fields.char('Filename', 64, readonly=True),
        'state' : fields.selection( ( ('choose','choose'),('get','get'), ) )
    }


    def _get_period(self, cr, uid, context=None):
#        pool = pooler.get_pool(cr.dbname)
        ids = self.pool.get('account.period').find(cr, uid, context=context)
#        logging.getLogger('DATEV EXPORT').warn("Context "+"in get period")
        if len(ids):
            return ids[0]
        return False

    _defaults = {
        'datev_filename': lambda *a: 'xml.zip',
        'period_id': _get_period,
        'in_invoice': lambda *a: True,
        'out_invoice': lambda *a: True,
        'in_refund': lambda *a: True,
        'out_refund': lambda *a: True,
        'state': lambda *a: 'choose',
        'company_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,

    }

    def act_destroy(self, *args):
        return {'type':'ir.actions.act_window_close' }

    def do_export_file(self, cr, uid, ids, context=None):
        logging.getLogger('DATEV EXPORT').warn("Begin of export with options"+str(context))
        if context is None:
            context = {}
        wizard = self.browse(cr, uid, ids, context=context)[0]
        company_id = wizard.company_id.id
        invoice_type_list = []
        if wizard.in_invoice:
            invoice_type_list.append('in_invoice')
        if wizard.out_invoice:
            invoice_type_list.append('out_invoice')
        if wizard.in_refund:
            invoice_type_list.append('in_refund')
        if wizard.out_refund:
            invoice_type_list.append('out_refund')
        if not len(invoice_type_list):
            raise osv.except_osv(_('Data Insufficient !'), _('Please check at least one invoice type to export'))
        inv_obj = self.pool.get('account.invoice')
        if wizard.period_id:
            invoice_ids = inv_obj.search(cr, uid, [('period_id','=',wizard.period_id.id),('type','in',invoice_type_list),('company_id','=',company_id)])
        elif wizard.date_start:
            if wizard.date_stop:
                invoice_ids = inv_obj.search(cr, uid, [('date_invoice','>',wizard.date_start),('date_invoice','<',wizard.date_stop), \
                            ('type','in',invoice_type_list),('company_id','=',company_id)])
            else:
                invoice_ids = inv_obj.search(cr, uid, [('date_invoice','>',wizard.date_start),('type','in',invoice_type_list),('company_id','=',company_id)])
        else:
            raise osv.except_osv(_('Data Insufficient !'), _('Please select Period or at least Start Date'))
        logging.getLogger('DATEV EXPORT').warn("Invoices "+str(invoice_ids))
        zip_file = self.pool.get('datev.export').generate_zip(cr, uid, invoice_ids, context)
        ret= {
            'company_id': self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
            'datev_file': zip_file,
            'datev_filename': time.strftime('%Y_%m_%d_%H_%M')+'_xml.zip',
            'state': 'get',
            }

        res = self.write(cr, uid, ids, ret, context=context)
        logging.getLogger('DATEV EXPORT').warn("End of export with options"+str(context)+" IDS: "+str(ids)+ " RES: "+str(res))
        return False
#        self.write(cr, uid, ids, ret, context=context)

#       ctx = context.copy()
#       ctx.update({'active_ids': invoice_ids})
#        logging.getLogger('DATEV EXPORT').warn("Context"+str(ctx))

        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        xml_id = 'action_datev_export_options_final'
        result = mod_obj.get_object_reference(cr, uid, 'account_datev_export', xml_id)
        id = result and result[1] or False
        result = act_obj.read(cr, uid, id, context=context)
#            invoice_domain = eval(result['domain'])
#            invoice_domain.append(('id', 'in', created_inv))
        logging.getLogger('DATEV EXPORT').warn("Result"+str(result))

        result.update({'export_file': zip_file})
#        result['fields']['name'] = 'xml.zip'
        return result
        '''

#        self.pool.get("datev.export").generate_zip(cr, uid, context)
#        return True
datev_export_options()

class datev_export(osv.osv_memory):
    _name = "datev.export"
    _description = "Export to XML Datev format"
    _columns = {
        'file': fields.binary('.zip File', readonly = True),
        'filename': fields.char('Filename', 64, readonly = True),
    }

    def toprettyxml_fixed(self, cr, uid, input_string):
        fix = re.compile(r'((?<=>)(\n[\t]*)(?=[^<\t]))|(?<=[^>\t])(\n[\t]*)(?=<)')
        return re.sub(fix, '', input_string)

    # date for payment_conditions (in datev) acount.payment.term.line (in OpenERP)
    def compute_date_due(self, cr, uid, pay_term_line, date_ref=False, context=None):
        next_date = (datetime.strptime(date_ref, '%Y-%m-%d') + relativedelta(days=pay_term_line.days))
        if pay_term_line.days2 < 0:
            next_date = datetime(next_date.year, next_date.month+1, 1) - relativedelta(days = 1)  #Getting last day of the month
        if pay_term_line.days2 > 0:
            next_date = datetime(next_date.year, next_date.month+1, pay_term_line.days2)
        result =next_date.strftime('%Y-%m-%d')
        return result


    def createTextElement(self, cr, uid, doc, parent_element, element, text):
        text_element = doc.createElement(element)
        parent_element.appendChild(text_element)
        text_node = doc.createTextNode(text)
        text_element.appendChild(text_node)
        return True

    def include_doc_header(self, cr, uid, doc, company):
#        if not (company.consultant_number and company.client_number):  
#             raise osv.except_osv(_('Data Insufficient !'), _('In company settings you have to enter: Consultant Number and Client Number'))
        archive = doc.createElement("archive")
        doc.appendChild(archive)
        archive.setAttribute("version", "3.0")
#        if company.guid_number:     # ver 3
#        archive.setAttribute("guid",uuid.uuid4())
        archive.setAttribute("generatingSystem", "OpenERP")  # ver 3
        archive.setAttribute("xmlns:xsi","http://www.w3.org/2001/XMLSchema-instance")
        archive.setAttribute("xsi:schemaLocation","http://xml.datev.de/bedi/tps/document/v03.0 document_v030.xsd")
        archive.setAttribute("xmlns","http://xml.datev.de/bedi/tps/document/v03.0")
        header = doc.createElement("header")
        archive.appendChild(header)
        self.createTextElement(cr, uid, doc, header, "date", time.strftime('%Y-%m-%dT%H:%M:%S'))
        self.createTextElement(cr, uid, doc, header, "description", company.name+" Accounting")
        if company.consultant_number:
            self.createTextElement(cr, uid, doc, header, "consultantNumber", company.consultant_number)
        if company.consultant_number:
            self.createTextElement(cr, uid, doc, header, "clientNumber", company.client_number)
        self.createTextElement(cr, uid, doc, header, "clientName", company.name)
        return archive

    def set_address(self, cr, uid, address, inv_address):
        if not (inv_address.zip and inv_address.city and inv_address.name):
             raise osv.except_osv(_('Data Insufficient !'), _('Address of partner %s must have Name, Zip and City')%inv_address.partner_id.name)
        if inv_address.street:
            address.setAttribute("street",inv_address.street[:41])
        address.setAttribute("zip",inv_address.zip)
        address.setAttribute("city",inv_address.city[:30])
        address.setAttribute("name",inv_address.name[:50])
        if inv_address.country_id and inv_address.country_id.code:
            address.setAttribute("country",inv_address.country_id.code)

    def include_invoice_line(self,cr,uid, line, inv, invoice_el, invoice_sign = 1): 
        invoice_item_list = inv.createElement("invoice_item_list")
        invoice_el.appendChild(invoice_item_list)
        invoice_item_list.setAttribute("order_unit", line.uos_id.name)
        invoice_item_list.setAttribute("net_product_price", "%.3f"%(line.price_unit * invoice_sign) or "")
        line.product_id.default_code and invoice_item_list.setAttribute("product_id", line.product_id.default_code)
        invoice_item_list.setAttribute("quantity", "%.2f"%(line.quantity))
        invoice_item_list.setAttribute("description_short", line.product_id.name[:40])

        price_line_amount = inv.createElement("price_line_amount")
        invoice_item_list.appendChild(price_line_amount)
        price_line_amount.setAttribute("currency", line.invoice_id.currency_id.name)
        if not line.invoice_line_tax_id or line.invoice_id.amount_tax == 0:
            tax_rate = 0
            tax_amount = False
        else:
            tax_rate = line.invoice_line_tax_id[0].amount
            tax_rate = abs(tax_rate * 100)

            u_price = line.quantity and line.price_subtotal/line.quantity or 0
            tax = self.pool.get('account.tax').compute(cr, uid, line.invoice_line_tax_id, u_price, line.quantity, line.invoice_id.address_invoice_id.id, line.product_id, line.invoice_id.partner_id)
            tax_amount = abs(tax[0]['amount']) * invoice_sign

        price_line_amount.setAttribute("tax", "%.2f"%(tax_rate))
        tax_amount and price_line_amount.setAttribute("tax_amount", "%.2f"%(tax_amount))
        price_line_amount.setAttribute("net_price_line_amount", "%.2f"%(line.price_subtotal * invoice_sign))
        # Check this as it is written in description it should be gross price * quantity. Here is subtotal + tax.  !!!!!
        price_line_amount.setAttribute("gross_price_line_amount", "%.2f"%((line.price_subtotal + abs(tax_amount)) * invoice_sign))

        accounting_info = inv.createElement("accounting_info")
        invoice_item_list.appendChild(accounting_info)
        line.account_id.code and accounting_info.setAttribute("account_no", line.account_id.code)
        line.account_id.name and accounting_info.setAttribute("booking_text", line.account_id.name[:30])

        return tax_rate

    def pick_done_last(self, cr, uid, pickings):
#        done_last = False
#        logging.getLogger('DATEV EXPORT').warn("Pickings"+str(pickings))


        last_date = datetime.min   # (year=1900, month=1, day=1)
        for pick in pickings:

            if pick.state == 'done' and datetime.strptime(pick.date_done, '%Y-%m-%d %H:%M:%S') > last_date:
                last_date = datetime.strptime(pick.date_done, '%Y-%m-%d %H:%M:%S')
#                logging.getLogger('DATEV EXPORT').warn("Pickings"+str(pick.date_done)+" "+str(datetime.strptime(pick.date_done, '%Y-%m-%d %H:%M:%S'))+" "+str(last_date)+" "+str(pick.state))
        if last_date != datetime.min:
            return datetime.strftime(last_date, '%Y-%m-%d')
        else:
            return False

    def refunded_inv_search(self, cr, uid, invoice):
        drawee_no = False
        for move in invoice.move_lines:
            if move.reconcile_id:
                for move2 in move.reconcile_id.line_id:
                    if move2.invoice and move2.invoice.id != invoice.id:
                        drawee_no = move2.invoice.number
                        break
            if drawee_no:
                break
            if move.reconcile_partial_id:
                for move2 in move.reconcile_partial_id.line_id:
                    if move2.invoice and move2.invoice.id != invoice.id:
                        drawee_no = move2.invoice.number
                        break
            if drawee_no:
                break
        return drawee_no

    def tax_rate_find(self, cr, uid, tax, tax_rates):
        calc_rate = 100 * tax.amount / tax.base     # Calculation of tax rate as it is not in data
        rate_diff = calc_rate
        line_rate = tax_rates[0] # should exist if tax_line exist
        for rate in tax_rates:             # Searching for tax rate because it is not in data
            if rate_diff > abs(calc_rate - rate):
                rate_diff = abs(calc_rate - rate)
                line_rate = rate
        return line_rate

    def include_discount_line(self, cr, uid, invoice, pay_term_line, payment_conditions): 
        # for inheriting of cash discount suplement module
        return True

    def include_invoice(self, cr, uid, invoice, our_invoice_address, our_vat_id):
        inv = minidom.Document()
        #  Add inv header
        invoice_el = inv.createElement("invoice")
        inv.appendChild(invoice_el)

        invoice_el.setAttribute("generator_info", invoice.company_id.name)
        invoice_el.setAttribute("generating_system", "OpenERP")
        invoice_el.setAttribute("description", "DATEV Import invoices")
        invoice_el.setAttribute("version", "3.0")
        invoice_el.setAttribute("xml_data", "Kopie nur zur Verbuchung berechtigt nicht zum Vorsteuerabzug") # new in v3
        invoice_el.setAttribute("xsi:schemaLocation","http://xml.datev.de/bedi/tps/invoice/v030 Belegverwaltung_online_invoice_v030.xsd")
        invoice_el.setAttribute("xmlns","http://xml.datev.de/bedi/tps/invoice/v030")
        invoice_el.setAttribute("xmlns:xsi","http://www.w3.org/2001/XMLSchema-instance")

    # invoice_info part
#        if not invoice.partner_id.vat:
#            raise osv.except_osv(_('Data Insufficient !'), _('You have to fill the VAT id for partner of invoice %s!')%invoice.number)
#        if not invoice.address_invoice_id:
#            raise osv.except_osv(_('Data Insufficient !'), _('You have to fill the address for partner of invoice %s!')%invoice.number)

        if invoice.type in ['out_invoice','in_invoice']:
            invoice_type = "Rechnung"
            invoice_sign = 1
            drawee_no = False
        else:
            invoice_type = "Gutschrift/Rechnungskorrektur"
            invoice_sign = -1
            drawee_no = self.refunded_inv_search(cr, uid, invoice)

        if invoice.type in ['out_invoice','out_refund']:
            we_are_supplier = True
            recipient_address_obj = invoice.address_invoice_id
            recipient_vat_id = invoice.partner_id.vat
            issuer_address_obj = our_invoice_address
            issuer_vat_id = our_vat_id
            # remember about vat_no
        else:
            we_are_supplier = False
            issuer_address_obj = invoice.address_invoice_id
            issuer_vat_id = invoice.partner_id.vat
            recipient_address_obj = our_invoice_address
            recipient_vat_id = our_vat_id
            # remember about vat_no

        invoice_info = inv.createElement("invoice_info")
        invoice_el.appendChild(invoice_info)
        invoice_info.setAttribute("invoice_type", invoice_type)
        invoice_info.setAttribute("invoice_date", invoice.date_invoice)
        # Delivery date
        delivery_date = False

        if invoice.type in ['in_refund','out_refund']:
            delivery_date = invoice.date_invoice
        else:
            if invoice.type == 'out_invoice':
                if self.pool.get("sale.order"):
#                    logging.getLogger('DATEV EXPORT').warn("Pickings"+str(is_so))
                    cr.execute("SELECT p.id, max(p.date) FROM stock_picking as p \
                                LEFT JOIN sale_order as s \
                                    ON (p.sale_id = s.id) \
                                    LEFT JOIN sale_order_invoice_rel as i \
                                        ON (s.id = i.order_id) \
                                WHERE (i.invoice_id = %s) AND (p.state = 'done') \
                                GROUP BY p.id",(invoice.id,))
                    res = cr.fetchone()
                    if res:
                        delivery_date = res[1]
                        delivery_date = delivery_date[0:10]
#                    logging.getLogger('DATEV EXPORT').warn("Pickings"+str(delivery_date))
            else:
                if self.pool.get("purchase.order"):
#                    logging.getLogger('DATEV EXPORT').warn("Pickings"+str(is_so))
                    cr.execute("SELECT p.id, max(p.date) FROM stock_picking as p \
                                LEFT JOIN purchase_order as po \
                                    ON (p.purchase_id = po.id) \
                                    LEFT JOIN purchase_invoice_rel as i \
                                        ON (po.id = i.purchase_id) \
                                WHERE (i.invoice_id = %s) AND (p.state = 'done') \
                                GROUP BY p.id",(invoice.id,))
                    res = cr.fetchone()
                    if res:
                        delivery_date = res[1]  #self.pick_done_last(cr, uid, picking_ids)  # search for last done pick list
                        delivery_date = delivery_date[0:10]  # datetime.strftime(last_date, '%Y-%m-%d')
        if not delivery_date:
            delivery_date = invoice.date_invoice

        invoice_info.setAttribute("delivery_date",  delivery_date)
        invoice_info.setAttribute("invoice_id",invoice.number)   # its our number, In ver 6 it is account move number too.
        drawee_no and invoice_info.setAttribute("drawee_no",drawee_no)

    #invoice_party part
        invoice_party = inv.createElement("invoice_party")
        invoice_el.appendChild(invoice_party)
        recipient_vat_id and invoice_party.setAttribute("vat_id",recipient_vat_id)
        party_address = inv.createElement("address")
        invoice_party.appendChild(party_address)
        self.set_address(cr, uid, party_address, recipient_address_obj)

        supplier_party = inv.createElement("supplier_party")
        invoice_el.appendChild(supplier_party)
        issuer_vat_id and supplier_party.setAttribute("vat_id",issuer_vat_id)
        supp_address = inv.createElement("address")
        supplier_party.appendChild(supp_address)
        self.set_address(cr, uid, supp_address, issuer_address_obj)
        if invoice.partner_bank_id:
            account = inv.createElement("account")
            supplier_party.appendChild(account)
            invoice.partner_bank_id.acc_number and account.setAttribute("bank_account", invoice.partner_bank_id.acc_number)
            invoice.partner_bank_id.bank.country.code and account.setAttribute("bank_country", invoice.partner_bank_id.bank.country.code)
            invoice.partner_bank_id.bank.code and account.setAttribute("bank_code", invoice.partner_bank_id.bank.code)
            account.setAttribute("bank_name", invoice.partner_bank_id.bank.name)     # Mandatory when bank exist
            invoice.partner_bank_id.iban and account.setAttribute("bank_iban", invoice.partner_bank_id.iban)
        booking_info_bp = inv.createElement("booking_info_bp")
        booking_info_bp.setAttribute("bp_account_no", invoice.account_id.code or "")
        if we_are_supplier:
            invoice_party.appendChild(booking_info_bp)
        else:
            supplier_party.appendChild(booking_info_bp)

        tax_rates = []   # creating a list of tax_rates because tax rates are not in tax_lines
        for line in invoice.invoice_line:
            if not line.invoice_line_tax_id or line.invoice_id.amount_tax == 0:
                tax_rate = 0
#                tax_amount = False
            else:
                tax_rate = line.invoice_line_tax_id[0].amount
                tax_rate = abs(tax_rate * 100)
            if not tax_rate in tax_rates:        
                tax_rates.append(tax_rate)

        if invoice.payment_term:
            total = invoice.amount_total * invoice_sign
            residual = total
            current_amount = 0
            for pay_term_line in invoice.payment_term.line_ids:    # TODO check if payment done date and amount fields should be added.
                payment_conditions = inv.createElement("payment_conditions")
                invoice_el.appendChild(payment_conditions)
                payment_conditions.setAttribute("currency",invoice.currency_id.name)
                pay_term_line_date_due = self.compute_date_due(cr, uid, pay_term_line, date_ref=invoice.date_invoice)
                payment_conditions.setAttribute("due_date",pay_term_line_date_due)
                payment_conditions.setAttribute("payment_conditions_text",pay_term_line.name[:60]) # Mandatory when payment term
                self.include_discount_line(cr, uid, invoice, pay_term_line, payment_conditions)


        #               Add line entries

        for line in invoice.invoice_line:
            self.include_invoice_line(cr, uid, line, inv, invoice_el, invoice_sign)

        #            Add invoice footer and close invoice xml file

        total_amount = inv.createElement("total_amount")
        invoice_el.appendChild(total_amount)
        total_amount.setAttribute("net_total_amount","%.2f"%(invoice.amount_untaxed * invoice_sign))
        total_amount.setAttribute("currency",invoice.currency_id.name)
        total_amount.setAttribute("total_gross_amount_excluding_third-party_collection","%.2f"%(invoice.amount_total * invoice_sign))

        if invoice.amount_tax == 0.0:
            tax_line = inv.createElement("tax_line")
            total_amount.appendChild(tax_line)
            tax_line.setAttribute("currency",invoice.currency_id.name)
            tax_line.setAttribute("gross_price_line_amount","%.2f"%(invoice.amount_total * invoice_sign))
            tax_line.setAttribute("tax", "0.00")
            tax_line.setAttribute("net_price_line_amount","%.2f"%(invoice.amount_untaxed * invoice_sign))
#            tax_line.setAttribute("tax_amount","0.00")
        else:
            for tax in invoice.tax_line:
                tax_line = inv.createElement("tax_line")
                total_amount.appendChild(tax_line)
                line_rate = self.tax_rate_find(cr, uid, tax, tax_rates)
                tax_line.setAttribute("tax", "%.2f"%(line_rate))              #   End of tax rate calculation
                tax_line.setAttribute("tax_amount","%.2f"%(tax.amount * invoice_sign))
                tax_line.setAttribute("net_price_line_amount","%.2f"%(tax.base * invoice_sign))
                tax_line.setAttribute("currency",invoice.currency_id.name)
                tax_line.setAttribute("gross_price_line_amount","%.2f"%((tax.base+tax.amount) * invoice_sign))

        inv_xml= inv.toprettyxml(indent="\t", newl="\n", encoding = "utf-8")
        self.check_xml_file(cr, uid, inv_xml, doc_name = invoice.number)
        return self.toprettyxml_fixed(cr, uid, inv_xml)

# main Wizard method (called from interface)
    def generate_zip(self, cr, uid, invoice_ids = [], context=None):
        if context is None:
            context = {}

#    def generate_zip(self, cr, uid, ids, context=None):
        logging.getLogger('DATEV EXPORT').warn("Beginning of generate_zip"+str(context))
        inv_obj = self.pool.get('account.invoice')
        if invoice_ids:
            active_ids = invoice_ids   # invoices selected by options
        else:
            active_ids = context and context.get('active_ids', [])    # invoices selected by selection in tree or form
        active_ids = inv_obj.search(cr, uid, [('id','in',active_ids),('state','in',['paid','open'])])
#        active_ids =[14]
        if len(active_ids) == 0:
            raise osv.except_osv(_('No active invoice in selection !'), _("Only invoices in state 'Open' or 'Paid' can be exported !"))
        invoices = inv_obj.browse(cr, uid, active_ids, context=context)

        company = invoices[0].company_id
        res =  self.pool.get('res.partner').address_get(cr, uid, [company.partner_id.id], ['invoice'])
        our_invoice_addr_id = res['invoice']
        our_invoice_address = self.pool.get('res.partner.address').browse(cr, uid, our_invoice_addr_id)
#        if not company.partner_id.vat:
#            raise osv.except_osv(_('Data Insufficient !'), _('You have to fill the VAT id for your company!'))
#        our_vat_id = company.partner_id.vat
        our_vat_id = False

        s=StringIO.StringIO()
#        s='xml.zip'   #StringIO.StringIO()
        zip = zipfile.ZipFile(s, 'w')

        doc = minidom.Document()
#               Add doc header 
        archive = self.include_doc_header(cr, uid, doc, company)
        content = doc.createElement("content")
        archive.appendChild(content)
  
        for invoice in invoices:
            inv_number = invoice.number.replace('/','')
#           Add invoice xml file
            inv_xml = self.include_invoice(cr, uid, invoice, our_invoice_address, our_vat_id)
            self.add_to_zip(cr, uid, inv_number+".xml", inv_xml, zip)

#            Add invoice entries to document.xml
            document = doc.createElement("document")
            content.appendChild(document)  
            if invoice.type in ['out_invoice','out_refund']:
#                desc = "Ausgangssrechnung"
                type = "Outgoing"
                doctype = "2"
#               Add invoice picture file
                ok, inv_pic = self.create_report(cr, uid, [invoice.id])
                if ok:
                    fname = inv_number + ".pdf"
                    self.add_to_zip(cr, uid, fname, inv_pic, zip)
            else:
#                desc = "Eingangsrechnung"
                type = "Incoming"
                doctype = "2"
#               Add invoice picture file of any name if exists
                ok = False
                ok, fname, inv_pic = self.get_attachment(cr, uid, invoice)
                if ok:
                    fname = inv_number+"_"+fname
                    self.add_to_zip(cr, uid, fname, inv_pic, zip)

#            document.setAttribute("type",doctype)  # Datev ver 3
            self.createTextElement(cr, uid, doc, document, "description", invoice.number)  # changed in version 3
#            self.createTextElement(cr, uid, doc, document, "keywords", "Mit Positionsbetragsverbuchung")  # ???? check if good
            if not invoice.address_invoice_id or not invoice.address_invoice_id.name:
                raise osv.except_osv(_('Data Insufficient !'), _('You have to fill the address for partner of invoice %s. The partner address has to have official company name!')%invoice.number)

            self.createTextElement(cr, uid, doc, document, "keywords", invoice.address_invoice_id.name + ", " + invoice.number)
            extension = doc.createElement("extension")
            document.appendChild(extension)
            extension.setAttribute("xsi:type","Invoice")
            extension.setAttribute("datafile",inv_number+".xml")
            property = doc.createElement("property")
            extension.appendChild(property)
            property.setAttribute("key","InvoiceType")
            property.setAttribute("value",type)
            if ok:
                extension = doc.createElement("extension")
                document.appendChild(extension)
                extension.setAttribute("xsi:type","File")
                extension.setAttribute("name",fname)
          
#        Close doc file
        doc_xml= doc.toprettyxml(indent="\t", newl="\n", encoding = "utf-8")
        doc_xml= self.toprettyxml_fixed(cr, uid, doc_xml)   #, newl="\n", encoding = "utf-8")
        self.check_xml_file(cr, uid, doc_xml, doc_name = "Document.xml", doc = True)
        self.add_to_zip(cr, uid, "document.xml", doc_xml, zip)

        zip.close()
        zip_file = base64.encodestring(s.getvalue())
        s.close()
#        ret= {
#            'state':'get',
#            'export_file': base64.encodestring(s.getvalue()),
#            'name': 'xml.zip',
#            }
#        return self.write(cr, uid, ids, ret, context=context)
        logging.getLogger('DATEV EXPORT').warn("End of generat_zip"+str(context))
        return zip_file    # ret['export_file']  #self.write(cr, uid, ids, ret, context=context)

    def add_to_zip(self,cr,uid,name,data,zip):
        info = zipfile.ZipInfo(name, date_time=time.localtime(time.time()))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 2175008768
        if not data:
            data = ''
        zip.writestr(info, data)
        return True

    _defaults = { 
        'filename': lambda *a: datetime.now().strftime('%Y_%m_%d_%H_%M')+'_xml.zip',
        'file': lambda self, cr, uid, context: self.generate_zip(cr, uid, context = context),
    }


    # for in invoices
    def get_attachment(self, cr, uid, invoice):
        attachment_obj = self.pool.get('ir.attachment')
        attachment_id = attachment_obj.search(cr, uid, [('res_model','=','account.invoice'),('res_id','=',invoice.id),('type','=','binary')])
        if len(attachment_id):
            attachment = attachment_obj.browse(cr, uid, attachment_id[0])
            result = base64.decodestring(attachment.datas)
            return (True, attachment.datas_fname, result) #ret_file_name)
        return (False, False, "No file")
    
    # for out invoices
    def create_report(self, cr, uid, ids):
        if not ids:
            return (False, Exception('Report name and Resources ids are required !!!'))
        try:
#            ret_file_name = '/tmp/'+file_name+'.pdf'
            service = netsvc.LocalService("report.account.invoice");
            (result, format) = service.create(cr, uid, ids, {}, {})
#            fp = open(ret_file_name, 'wb+');
#            fp.write(result);
#            fp.close();
        except Exception,e:
            print 'Exception in create report:',e
            return (False, str(e))
        return (True, result) #ret_file_name)

    def check_xml_file(self, cr, uid, xml_file, doc_name, doc = False):
# TODO take the xsd from url online
        if doc:
            f_schema = tools.file_open('Document_v030.xsd',subdir='addons/datev_export/xsd_files')
        else:
            f_schema = tools.file_open('Belegverwaltung_online_invoice_v030.xsd',subdir='addons/datev_export/xsd_files')
        schema_doc = etree.parse(f_schema)
        schema = etree.XMLSchema(schema_doc)
        parser = etree.XMLParser(schema = schema)
        try:
            doc = etree.fromstring(xml_file, parser)
        except etree.XMLSyntaxError as e:
#            e = unicode(str(e), "ascii")
#            logging.getLogger('DATEV EXPORT').warn("XSD message " + str(e))
            raise osv.except_osv(_('Wrong Data in XML file!'), _("Try to solve the problem with '%s' according to message below:\n\n")%doc_name+ str(e))
        return True

datev_export()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

