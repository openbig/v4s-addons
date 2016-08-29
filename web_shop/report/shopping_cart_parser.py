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
import time

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.context = context
        super(Parser, self).__init__(cr, 1, name, context)
        if context.get('guest'):
            user = self.pool.get('res.users').browse(cr, 1, uid, context=context)
            domain = [('state','=','draft'),('origin','=',context.get('jera_sid')),('partner_id','=',user.address_id.partner_id.id)]
        else:
            domain = [('state','=','draft'),('origin','=',context.get('jera_sid'))]
        self.localcontext.update({'shop_id': 1,
                                  'sid':context.get('jera_sid'),
                                  'format_price': self._format_price,
                                  'context': self.context,
                                  'domain': domain})
        
    def _format_price(self, price):
        amount, currency = price
        return self.localcontext.get('formatLang')(amount) + '&nbsp;' + currency.symbol

