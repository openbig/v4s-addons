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

from osv import fields,osv
import tools


class crm_lead_report(osv.osv):
    """ CRM Lead Analysis """
    _inherit = "crm.lead.report"

    _columns = {
        'nbr': fields.integer('# Opportunities', readonly=True),
        'partner_name': fields.char("Customer Name", size=64, readonly=True, select=1),
        'company_ext' : fields.char('Company Name', size=128, readonly=True),
    }
    
    def init(self, cr):

        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'crm_lead_report')
        cr.execute("""
            CREATE OR REPLACE VIEW crm_lead_report AS (
                SELECT
                    id,

                    to_char(c.date_deadline, 'YYYY') as deadline_year,
                    to_char(c.date_deadline, 'MM') as deadline_month,
                    to_char(c.date_deadline, 'YYYY-MM-DD') as deadline_day,

                    to_char(c.create_date, 'YYYY') as creation_year,
                    to_char(c.create_date, 'MM') as creation_month,
                    to_char(c.create_date, 'YYYY-MM-DD') as creation_day,

                    to_char(c.date_open, 'YYYY-MM-DD') as opening_date,
                    to_char(c.date_closed, 'YYYY-mm-dd') as date_closed,

                    c.state,
                    c.user_id,
                    c.probability,
                    c.stage_id,
                    c.type,
                    c.company_id,
                    c.priority,
                    c.section_id,
                    c.channel_id,
                    c.type_id,
                    c.categ_id,
                    c.partner_id,
                    c.partner_name,
                    c.company_ext,
                    c.country_id,
                    c.planned_revenue,
                    c.planned_revenue*(c.probability/100) as probable_revenue,
                    1 as nbr,
                    (SELECT count(id) FROM mail_message WHERE model='crm.lead' AND res_id=c.id AND email_from is not null) AS email,
                    date_trunc('day',c.create_date) as create_date,
                    extract('epoch' from (c.date_closed-c.create_date))/(3600*24) as  delay_close,
                    abs(extract('epoch' from (c.date_deadline - c.date_closed))/(3600*24)) as  delay_expected,
                    extract('epoch' from (c.date_open-c.create_date))/(3600*24) as  delay_open
                FROM
                    crm_lead c
                WHERE c.active = 'true'
            )""")

crm_lead_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
