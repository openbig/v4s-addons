# -*- encoding: utf-8 -*-

from osv import osv,fields
from tools.translate import _

class jera_contactus(osv.osv_memory):
    '''Contact Us'''
    _name = 'jera.contactus'
    _inherit = 'captcha.captcha'
    _description = "Contact Us"
    _rec_name = 'partner_name'

    def jera_request_send_message(self, cr, uid, ids, context=None):
        result = None
        this = self.browse(cr, 1, ids)[0]
        if this.check_captcha(context=context):
            self.clear_captcha(cr, 1, context=context)
            lead_obj = self.pool.get('crm.lead')
            new_lead_data = {'partner_name': this.partner_name,
                             'contact_name': this.contact_name,
                             'optin': this.optin,
                             'optout': this.optin == False and True,
                             'phone': this.phone,
                             'name': this.name,
                             'description': this.description,
                             'categ_id': this.category,
                             'email_from': this.email_from,
                             'channel_id': context.get('channel_id', False),
                             'company_id': context.get('company_id', False),
                             'section_id': context.get('section_id', False),
                             'type_id': context.get('campaign_id', False),
                             'stage_id': context.get('stage_id', False),
                             'priority': context.get('priority', False),
                            }
            lead_obj.create(cr, 1, new_lead_data, context=context)
            return "message", _('Your enquiry is successfully registered!')
        else:
            this.write({'code_verify':False})
            raise osv.except_osv(_('Captcha Input Error'), _('Please enter the characters displayed in the box. If you are unable to see the text clearly, you may click image for a new code.'))

    def _get_categories(self, cr, uid, context={}):
        obj = self.pool.get('crm.case.categ')
        ids = obj.search(cr, 1, ['|',('section_id','=',context.get('section_id', False)),('section_id','=',False), ('object_id.model', '=', 'crm.lead')])
        res = obj.read(cr, 1, ids, ['id', 'name'], context)
        return [(r['id'], r['name']) for r in res]

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if not context:
            context = {}
        if context.get('view_name', False):
            view_obj = self.pool.get('ir.ui.view')
            ids = view_obj.search(cr, 1, [('name', '=', context.get('view_name', ''))])
            if ids:
                return super(jera_contactus, self).fields_view_get(cr, 1, ids[0], view_type, context, toolbar, submenu)
        return super(jera_contactus, self).fields_view_get(cr, 1, view_id, view_type, context, toolbar, submenu)

    _columns = {
        'partner_name': fields.char('Company', size=200, required=False, readonly=False, translate=False, help=''),
        'contact_name': fields.char('Name', size=200, required=False, readonly=False, translate=False, help=''),
        'category': fields.selection(_get_categories, 'Category', size=64, required=False, readonly=False, translate=False, help=''),
        'optin': fields.boolean('Opt-in', readonly=False, help=''),
        'phone': fields.char('Phone', size=64, required=False, readonly=False, translate=False, help=''),
        'description': fields.text('Message', readonly=False, translate=False, help=''),
        'email_from': fields.char('E-mail', size=64, required=False, readonly=False, translate=False, help=''),
        'name': fields.char('Subject', size=64, required=False, readonly=False, translate=False, help=''),
    }

    _defaults = {
        'optin': lambda *a: True,
    }

jera_contactus()

