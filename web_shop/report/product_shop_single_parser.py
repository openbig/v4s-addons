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
        self.localcontext.update({
                                  'product_available': self._product_available,
                                  'text_to_html': self._text_to_html,
                                  })
    
    def _text_to_html(self, text):
        return '\n'.join([ '<p>%s</p>' % line for line in text.splitlines() ])

    def _product_available(self, id):
        product_obj = self.pool.get('product.product')
        c = self.context.copy()
        c.update({'states':('done',), 'what':('in','out')})
        stock = product_obj.get_product_available(self.cr, 1, [id], context=c)
        return stock.get(id, 0.0)

