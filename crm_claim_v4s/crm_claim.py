# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Module crm_claim_v4s
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

from osv import fields, osv
from datetime import datetime
from crm import crm
import time
from crm import wizard

from tools.translate import _
import binascii
import tools


class crm_claim(osv.osv):
    """
    Crm claim
    """
    _inherit = "crm.claim"
    
    _columns = {
        'purchase_id': fields.many2one('purchase.order', 'Procurement Order'), # x_beschaffungsauftrag
        'credit_date': fields.char('Credit Note-Nr. / Date', size=64), # x_creditnote
        'credit_amount': fields.float('Credit Note Amount in $'), # x_creditnotebetrag
        'spare_outstanding': fields.boolean('Spare Outstanding'), # x_ersatzlieferung
        
        'defect_desc': fields.char('Defect Decription', size=64), # x_defektbeschreibung
        'defect_date': fields.date('Defect Date'), # x_defekteingang
        
        'defect_is_replacement': fields.boolean('Replacement of Sieve'), # x_entnahme
        'defect_obtain': fields.boolean(''), # x_erhalten
        
        'defect_substitute01': fields.many2one('product.product', 'Substitute for Customer 01'), # x_ersatzkunde01
        'defect_substitute02': fields.many2one('product.product', 'Substitute for Customer 02'), # x_ersatzkunde02
        
        'defect_susbstitute_supplier01': fields.many2one('product.product', 'Substitute from Supplier 01'), # x_ersatzlieferant01
        'defect_susbstitute_supplier02': fields.many2one('product.product', 'Substitute from Supplier 02'), # x_ersatzlieferant02
        
        'replacement_lot01': fields.many2one('stock.production.lot', 'Replacement Lot by Customer 01'), # x_ersatzlotkunde 01
        'replacement_lot02': fields.many2one('stock.production.lot', 'Replacement Lot by Customer 02'), # x_ersatzlotkunde 02
        
        'replacement__lot_supplier01': fields.many2one('stock.production.lot', 'Replacement Lot from Supplier 01'), # x_ersatzlotlieferant 01
        'replacement__lot_supplier02': fields.many2one('stock.production.lot', 'Replacement Lot from Supplier 02'), # x_ersatzlotlieferant 02
        
        'defective_product01': fields.many2one('product.product', 'Defective Instrument 01'), # x_defekt01
        'defective_product02': fields.many2one('product.product', 'Defective Instrument 02'), # x_defekt02
        
        'defect_lot01': fields.many2one('stock.production.lot', 'Defective Instrument - Lot 01'), # x_defektlot02
        'defect_lot02': fields.many2one('stock.production.lot', 'Defective Instrument - Lot 02'), # x_defektlot02
        
        'warranty': fields.date('Warranty'), # x_garantie
        'invoice_number': fields.char('Invoice Number', size=64), # x_invoice
        'invoice_amount': fields.float('Invoice Amount in $'), # x_invoicebetrag
        
        'partner_id': fields.many2one('res.partner', 'Customer'), # x_kunde
        'supplier_id': fields.many2one('res.partner', 'Supplier'), #x_lieferant
        
        'delivery_number': fields.char('Delivery Number', size=256), # x_lieferschein
        'defect_location': fields.char('Defect Location', size=256), # x_ort
        'obtain_per': fields.boolean('Obtain PER'), # x_per
        'invoice_id': fields.many2one('account.invoice', 'Invoice'), # x_rechnung
        'invoice_amount02': fields.float('Invoice Amount in €'), # x_rechnungsbetrag
        'rga_number': fields.char('RGA Nr.', size=256), # x_rga
        
        'sale_order_id': fields.many2one('sale.order', 'Sale Order'), # x_verkaufsauftrag
        'wa_to_supplier': fields.date('WA to Supplier'), # x_walieferant
        'we_from_supplier': fields.date('WE from Supplier'), #x_welieferant
    }
    
crm_claim()   