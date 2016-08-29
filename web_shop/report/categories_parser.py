# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2012 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
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

from universal_parser import uniparser

class Parser(uniparser):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, 1, name, context)
        self.localcontext.update({'categ_count_get':self._categ_count_get,
                                  })

    def _categ_count_get(self, categ_ids, brand_id):
        #{% with categ_products = len(search_ids('product.product',[('prim_sales_category_id', '=', categ.id),('sale_ok', '=', True),'|',('shop_ids', 'in', [int(context.get('shop_id', 1))]),('shop_ids', '=', False)])) %}\
        categ_mod = self.pool.get('product.sales_category')
        prod_mod = self.pool.get('product.product')
        domain = [('sale_ok', '=', True),'|',('shop_ids', '=', self.shop_id),('shop_ids', '=', False)]
        domain += brand_id and [('brandname', '=', brand_id)] or []
        res = {}
        for categ in categ_ids:
            sale_categs = categ_mod.search(self.cr, self.uid, [('id', 'child_of', [categ.id])])
            p_count = prod_mod.search(self.cr, 1, ['|',('prim_sales_category_id', 'in', sale_categs), ('sales_category_ids', 'in', sale_categs)] + domain, count=True)
            res[categ.id] = p_count
        return res
