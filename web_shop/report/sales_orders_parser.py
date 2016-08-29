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

from report import report_sxw

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, 1, name, context)
        self.context = context
        self.localcontext.update({ 'format_price': self._format_price,
                                   'sid':context.get('jera_sid'),
                                   'get_name_spec':self._get_name_spec,
                                   'j_anonym':'JERA Anonymous'})

    def _get_name_spec(self, obj):
        lang = self.context['lang'] or self.context['user_lang']
        return self.pool.get(obj._table_name).name_get(self.cr, 1, [obj.id], {'lang':lang})[0][1]
    
    def _format_price(self, price):
        amount, currency = price
        return self.localcontext.get('formatLang')(amount) + '&nbsp;' + currency.symbol
