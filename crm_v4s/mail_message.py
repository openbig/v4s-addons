# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Module crm_v4s
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
import time
from tools.translate import _
import binascii
import tools
from openerp import SUPERUSER_ID
from mail.mail_message import format_date_tz, truncate_text

class mail_message(osv.osv):
    _inherit = "mail.message"
    

    def _get_display_text(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        tz = context.get('tz')
        result = {}

        # Read message as UID 1 to allow viewing author even if from different company
        for message in self.browse(cr, SUPERUSER_ID, ids):
            msg_txt = ''
            if message.email_from:
                msg_txt += _('%s Email from %s: \n Subject: %s \n\t') % (message.user_id.name or '/', format_date_tz(message.date, tz), message.subject)
                if message.body_text:
                    msg_txt += truncate_text(message.body_text)
            else:
                msg_txt = (message.user_id.name or '/') + _(' Note from ') + format_date_tz(message.date, tz) + ':\n\t'
                msg_txt += (message.subject or '')
            result[message.id] = msg_txt
        return result
    
    _columns = {
        'display_text': fields.function(_get_display_text, method=True, type='text', size="512", string='Display Text'),
    }
