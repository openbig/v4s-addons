# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2013 Alistek Ltd. (http://www.alistek.com) All Rights Reserved.
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
# as published by the Free Software Foundation; either version 3
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
from osv import osv,fields
from tools.translate import _

class product_listprice_cache(osv.osv):
    '''Listprice'''
    _name = 'product.listprice_cache'
    _description = "Listprice"
    _log_access = False

    def price_get(self, cr, uid, product_ids, pricelist_id, position_id=None, date=None, context={}):
        result = {}
        if not position_id:
            position_id = None
        if not date:
            cr.execute('SELECT product_id, price, currency_id \
            FROM product_listprice_cache WHERE product_id IN %s AND \
            pricelist_id = %s AND position_id IS NOT DISTINCT FROM %s AND date_valid is null;',
            (tuple(map(int, product_ids)), pricelist_id, position_id))
            records = cr.dictfetchall()
            currency_mod = self.pool.get('res.currency')
            for rec in records:
                currency_obj = currency_mod.browse(cr, 1, rec['currency_id'])
                result[rec['product_id']] = (rec['price'], currency_obj)
            resids = result.keys()
            if len(resids) < len(product_ids):
                tocalc = []
                for prod_id in product_ids:
                    if prod_id.id not in resids:
                        tocalc.append(prod_id)
                if tocalc:
                    calcres = self.price_calc(cr, uid,
                    tocalc, pricelist_id, position_id=position_id, date=date)
                    for prod in calcres.keys():
                        result[prod] = calcres[prod]
                        cr.execute('INSERT INTO product_listprice_cache \
                        (product_id, pricelist_id, price, currency_id, position_id)\
                        VALUES (%s, %s, %s, %s, %s)',
                        (prod, pricelist_id, calcres[prod][0], calcres[prod][1].id,
                        position_id))
        return result

    def price_calc(self, cr, uid, product_ids, pricelist_id, position_id=None, date=None, context={}):
        result = {}
        fpos_mod = self.pool.get('account.fiscal.position')
        plist_mod = self.pool.get('product.pricelist')
        tax_mod = self.pool.get('account.tax')
        pricelist_obj = pricelist_id and plist_mod.browse(cr, 1, pricelist_id) or False
        position_obj = position_id and fpos_mod.browse(cr, 1, position_id)
        if not pricelist_obj:
            for prod_id in product_ids:
                result[prod_id.id] = (0.0, False)
            return result
        currency_id = pricelist_obj.currency_id
        products = [ (prod_id.id, 1.0, None) for prod_id in product_ids ]
    
        # product.pricelist.version:
        pricelist_version_ids = [pricelist_id]
        plversions_search_args = [
            ('pricelist_id', 'in', pricelist_version_ids),
            '|',
            ('date_start', '=', False),
            ('date_start', '<=', date),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', date),
        ]
    
        plversion_ids = self.pool.get('product.pricelist.version').search(cr, uid, plversions_search_args)
        if len(pricelist_version_ids) == len(plversion_ids):
            prices = plist_mod.price_get_multi(cr, 1, pricelist_ids=[pricelist_id], products_by_qty_by_partner=products, context=context)
            for prod_id in product_ids:
                price = prices[prod_id.id][pricelist_id]
                tax_id = False
                if position_id:
                    tax_id = fpos_mod.map_tax(cr, 1, position_obj, prod_id.taxes_id)
                if tax_id:
                    price = tax_mod.compute_all(cr, 1, tax_mod.browse(cr, 1, tax_id), price, 1)['total_included']
                if price is not False:    
                    result[prod_id.id] = (price, currency_id)
        return result

    def price_batch_recalc(self, cr, uid, product_ids, pricelist_id, position_id=None, date=None, context={}):
        result = None
        #if not product_ids:
        #    prod_mod = self.pool.get('product.product')
        #    plist_mod = self.pool.get('product.pricelist')
        #    plist_obj = plist_mod.browse(cr, 1, [1], context=context)
        #    company_list = plist_obj.company_id and (plist_obj.company_id.id, False) or (False,)
        #    all_prod_ids = prod_mod.search(cr, 1, [('company_id','in', company_list)], limit=100, context=context)
        #    product_ids = prod_mod.browse(cr, 1, all_prod_ids, context=context)
        if product_ids:
            calcres = self.price_calc(cr, uid, product_ids, pricelist_id,
                position_id=position_id, date=date)
            for prod in calcres.keys():
                cr.execute('SELECT * FROM product_listprice_cache \
                WHERE product_id = %s AND pricelist_id = %s \
                AND position_id IS NOT DISTINCT FROM %s AND date_valid IS NULL',
                (prod, pricelist_id, position_id))
                qres = cr.dictfetchone()
                insnew = False
                if qres:
                    if qres.get('price') != calcres[prod][0] or qres.get('currency_id') != calcres[prod][1].id:
                        cr.execute('UPDATE product_listprice_cache \
                        SET date_valid = CURRENT_DATE WHERE id = %s',
                        (qres.get('id'),))
                        insnew = True
                else:
                    insnew = True
                if insnew:
                    cr.execute('INSERT INTO product_listprice_cache \
                    (product_id, pricelist_id, price, currency_id, position_id) \
                    VALUES (%s, %s, %s, %s, %s)',
                    (prod, pricelist_id, calcres[prod][0],
                    calcres[prod][1].id, position_id))
            cr.commit()
        return result

    def init_price_recalc(self, cr, uid, product_ids, pricelist_id, position_id=None, date=None, context={}):
        def _chunks(l, n):
            """ Yield successive n-sized chunks from l.
            """
            for i in xrange(0, len(l), n):
                yield l[i:i+n]
        result = None
        if not product_ids:
            prod_mod = self.pool.get('product.product')
            plist_mod = self.pool.get('product.pricelist')
            plist_obj = plist_mod.browse(cr, 1, [1], context=context)
            domain = []
            if plist_obj[0].company_id:
                domain = ['|',('company_id','=', False),('company_id','=', plist_obj[0].company_id.id)]
            all_prod_ids = prod_mod.search(cr, 1, domain, context=context)
            for batch_ids in _chunks(all_prod_ids, 100):
                product_ids = prod_mod.browse(cr, 1, batch_ids, context=context)
                self.price_batch_recalc(cr, uid, product_ids, pricelist_id, position_id=position_id, date=date, context=context)
        return result

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', domain="[]", ondelete='cascade', required=True, readonly=False, help='', select=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', domain="[('type','=','sale')]", ondelete='cascade', required=True, readonly=False, help='', select=True),
        'price': fields.float('Price', digits=(16,2), required=True, readonly=False, help=''),
        'currency_id': fields.many2one('res.currency', 'Currency', domain="[]", ondelete='cascade', required=False, readonly=False, help=''),
        'date_valid': fields.date('Valid Until', required=False, readonly=False, help=''),
        'position_id': fields.many2one('account.fiscal.position', 'Fiscal Position', domain="[]", ondelete='cascade', required=False, readonly=False, help='', select=True),
    }

product_listprice_cache()

