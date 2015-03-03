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
        self.localcontext.update({
            'payment_agencies': self._get_payment_agencies(cr, uid, context=context),
            'get_partner': self._get_partner(cr, context=context), # for the partner access without rights
        })

    def _get_partner(self, cr, context={}):
        def get_partner(partner_id):
            return self.pool.get('res.partner').browse(cr, 1, partner_id, context=context)
        return get_partner

    def _get_payment_agencies(self, cr, uid, context={}):
        pa_obj = self.pool.get('payment.agency.config')
        pa_ids = pa_obj.search(cr, uid, [], context=context)
        data = pa_obj.read(cr, uid, pa_ids, ['name','button_url','logo','code','currency_ids'], context=context)
        return data
