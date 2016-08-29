# -*- encoding: utf-8 -*-
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

from report import report_sxw

class uniparser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.context = context
        self.uri = self.context.get('uri', {})
        self.cookies = self.context.get('cookie', {})
        self.shop_id = int(context.get('shop_id', '1'))
        self.categ_id = self.uri.get('categ_id')
        self.categ_id = self.categ_id and self.categ_id.isdigit() and int(self.uri.get('categ_id')) or False
        self.brand_id = self.uri.get('brand_id')
        self.brand_id = self.brand_id and self.brand_id.isdigit() and int(self.uri.get('brand_id')) or False
        super(uniparser, self).__init__(cr, 1, name, context)
        self.uid = uid
        self.localcontext.update({
                                  'price_get':self._price_get,
                                  'format_price': self._format_price,
                                  'cookies': self.cookies,
                                  'referer': context.get('referer',{}),
                                  'show_count': bool(int(context.get('show_count','0'))),
                                  'uri': self.uri,
                                  'shop_id': self.shop_id,
                                  'categ_id': self.categ_id,
                                  'brand_id': self.brand_id,
                                  'context': context})
    
    def _price_get(self, product_ids):
        result = {}
        plist_mod = self.pool.get('product.pricelist')
        shop_mod = self.pool.get('sale.shop')
        cache_mod = self.pool.get('product.listprice_cache')
        user_mod = self.pool.get('res.users')
        user = user_mod.browse(self.cr, 1, self.uid, context=self.context)
        shop_obj = shop_mod.browse(self.cr, 1, self.context.get('shop_id'))
        position_id = False
        pricelist_id = False
        if not self.context.get('guest'):
            partner_id = user.address_id.partner_id
            pricelist_id = partner_id.property_product_pricelist and partner_id.property_product_pricelist.id or False
            position_id = partner_id.property_account_position and partner_id.property_account_position.id or False
        if not position_id:
            position_id = shop_obj.position_default_id and shop_obj.position_default_id.id or False
        if not pricelist_id:
            pricelist_id = shop_obj.pricelist_id and shop_obj.pricelist_id.id or False
        result = cache_mod.price_get(self.cr, self.uid, product_ids, pricelist_id, position_id=position_id, date=False)
        return result
    
    def _format_price(self, price):
        amount, currency = price
        return self.localcontext.get('formatLang')(amount) + ' ' + currency.symbol

