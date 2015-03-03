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

from openerp.osv import fields,osv
import openerp.tools as tools


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
                    c.date_deadline,
                    count(id) as nbr_cases,

                    c.date_open as opening_date,
                    c.date_closed as date_closed,

                    c.date_last_stage_update as date_last_stage_update,

                    c.user_id,
                    c.probability,
                    c.stage_id,
                    c.type,
                    c.company_id,
                    c.priority,
                    c.section_id,
                    c.campaign_id,
                    c.source_id,
                    c.medium_id,
                    c.partner_id,
                    c.partner_name,
                    c.company_ext,
                    c.country_id,
                    c.planned_revenue as planned_revenue,
                    c.planned_revenue*(c.probability/100) as probable_revenue,
                    c.create_date as create_date,
                    extract('epoch' from (c.date_closed-c.create_date))/(3600*24) as  delay_close,
                    abs(extract('epoch' from (c.date_deadline - c.date_closed))/(3600*24)) as  delay_expected,
                    extract('epoch' from (c.date_open-c.create_date))/(3600*24) as  delay_open
                FROM
                    crm_lead c
                WHERE c.active = 'true'
                GROUP BY c.id
            )""")

crm_lead_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
