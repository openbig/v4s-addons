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

from osv import osv
from osv import fields
#import captcha
from tools.translate import _
import xmlrpclib
import md5
import time
import random

import tools
from tools import config
import netsvc

from jera.jera import PASSWORD_LENGTH, PASSWORD_CHARS

def _lang_get(self, cr, uid, context=None):
    obj = self.pool.get('res.lang')
    ids = obj.search(cr, uid, [('translatable','=',True)])
    res = obj.read(cr, uid, ids, ['code', 'name'], context=context)
    res = [(r['code'], r['name']) for r in res]
    return res

class jera_register_config(osv.osv):
    _name = 'jera.config'
    _inherit = 'jera.config'
    _description = 'JERA parmission configuration'

    _columns = {
        'group_ids':fields.many2many('res.groups', 'jconfig_groups_rel', 'jconfig_id', 'group_id', 'Groups for new users'),
        
    }

jera_register_config()

class jera_users(osv.osv):
    _name = 'jera.users'
    _inherit = ['jera.users','captcha.captcha']
    _description = 'JERA Registration'
    _rec_name = 'name'

    def name_get(self, cr, uid, ids, context={}):
        res = []
        for user in self.read(cr, uid, ids, ['name','login'], context, load='_classic_write'):
            res.append((user['id'], user.get('name',False) or user['login']))
        return res

    def _remove_overdue_register(self, cr, uid, context={}):
        user_obj = self.pool.get('res.users')
        cr.execute("DELETE \
                    FROM jera_users \
                    WHERE create_date <= (now() - interval '1 hours') and user_id is null"
                   ) # users connections where registration is interrupted (delete now)

        cr.execute("SELECT Users.id \
                    FROM jera_users Jusers, res_users Users \
                    WHERE Jusers.create_date <= (now() - interval '1 days') and Users.id=Jusers.user_id and \
		                    (SELECT Users.active FROM res_users Users WHERE Users.id=Jusers.user_id) = false \
                    GROUP BY Users.id \
                    HAVING count(Users.id)=1"
                   ) # only not active users created by Joomla site with overdue registration
        user_ids = cr.fetchall()
        user_obj.unlink(cr, uid, user_ids, context=context)
        return True

    def read(self,cr, uid, ids, fields=None, context=None, load='_classic_read'):
        def override(o):
            if uid != 1:
                if 'password' in o: o['password'] = '********'
                if 'password_verify' in o: o['password_verify'] = '********'
            return o

        result = super(jera_users, self).read(cr, uid, ids, fields, context, load)
        if isinstance(ids, (int, long)):
            result = override(result)
        else:
            result = map(override, result)
        return result

    _columns = {
        'name': fields.char('User Name', size=64, select=True, help="The new user's real name"),
        #'login': fields.char('Login', size=64, required=True, help="Used to log into the system"),
        #'password': fields.char('Password', size=64, invisible=True, required=True),
        'password_verify': fields.char('Verify Password', size=64, invisible=True),
        'context_lang': fields.selection(_lang_get, 'Language', help="Sets the language for the user interface"),
        #'captcha':fields.binary('Captcha', help="Click on image to refresh"),
        #'captcha_code':fields.char('Captcha code', size=16),
        #'captcha_code_verify':fields.char('Captcha code Type characters you see', size=16),
        'confirmed': fields.related('user_id','active', type='boolean', string='Confirmed'),
        'hash':fields.char('Hash', size=64),
        
    }

    _defaults = {
        #'captcha': _get_captcha,
        #'captcha_code': _get_captcha_code,
        'confirmed':False,
    }

jera_users()

class jera_register(osv.osv_memory):
    _name = 'jera.register'
    _inherit = 'captcha.captcha'

    def raise_error(self, cr, uid, obj, msg_header, msg, context={}):
        obj.write({'code_verify':False,'password_verify':False}, context=context)
        raise osv.except_osv(msg_header, msg)

    def _send_email(self, cr, uid, juser_id, user_email, confirm_hash, context={}):
        jera_host = context.get('jera_host')
        report_context = context.copy()
        report_context.update({'joomla_hostname':jera_host,'confirm_hash':confirm_hash})
        email_server = self.pool.get('ir.mail_server')
        ir_obj = self.pool.get('ir.actions.report.xml')
        report_xml_ids = ir_obj.search(cr, uid, [('report_name', '=', 'html_confirm_register')], context=report_context)
        report_xml = ir_obj.browse(cr, uid, report_xml_ids[0], context=report_context)

        data = {'model': 'jera.users', 'id': juser_id, 'report_type': 'aeroo', 'in_format': 'genshi-raw'}
        body_text = netsvc.Service._services['report.html_confirm_register'].create(cr, 1, [juser_id], data, context=report_context)[0]

        subject = 'Account registration on the %s' % jera_host
        ir_mail_server = self.pool.get('ir.mail_server')
        headers = {'Content-type':'text/html; charset=utf-8'}
        msg = ir_mail_server.build_email(email_from=config.get('email_from',) or 'mail@alistek.com',
                                         email_to=[user_email],
                                         subject=subject,
                                         body=body_text.decode("UTF-8"),
                                         subtype='html',
                                         headers=headers)
        return ir_mail_server.send_email(cr, uid, msg, context=context)

    def jera_request_register_user(self, cr, uid, ids, context=None):
        this = self.browse(cr, 1, ids, context=context)[0] # read can only admin!
        jconfig_obj = self.pool.get('jera.config')
        juser_obj = self.pool.get('jera.users')
        jera_host = context.get('jera_host')
        config_id = jconfig_obj.search(cr, 1, [('hostname','=',jera_host)], context=context)
        if not config_id:
            self.raise_error(cr, uid, this, _('System Error!'), _('Configuration for site "%s" is not defined!') % jera_host, context=context)
        jera_config = jconfig_obj.read(cr, 1, config_id[0], ['login','password','hostname','port','ssl','trans_login','group_ids','handler'], context=context)
        if not jera_config['hostname']:
            self.raise_error(cr, uid, this, _('Server error!'), _('Not configured Joomla connection!'), context=context)
        try:
            this.password.encode('ascii')
        except UnicodeEncodeError, e:
            password_ascii_error = True
        else:
            password_ascii_error = False
        #if not this.code_verify or this.code_verify.lower()!=this.code_by_sid:
        if not this.check_captcha(context=context): # in context must be sid (session ID)
            self.raise_error(cr, uid, this, _('Input error!'), _('The captcha code is invalid!'), context=context)
        elif password_ascii_error:
            self.raise_error(cr, uid, this, _('Input error!'), _("Password cannot contain non latin letters!"), context=context)
        elif this.password!=this.password_verify:
            self.raise_error(cr, uid, this, _('Input error!'), _('The password verify is false!'), context=context)
        elif juser_obj.search(cr, 1, [('email','=',this.email),('confirmed','=',True)], context=context):
            self.raise_error(cr, uid, this, _('Input error!'), _('Account with email "%s" already exist!') % this.email, context=context)
        else:
            self.clear_captcha(cr, uid, context) # in context must be sid (session ID)
            #del self._jdata[context.get('jera_sid')]['captcha'] # delete captcha data for the current session

        user_obj = self.pool.get('res.users')

        #jconfig_ids = jconfig_obj.search(cr, 1, [])
        #group_ids = jconfig_obj.read(cr, uid, config_id[0], ['group_ids'], context=context)['group_ids']

        new_user_data = {
            'name':this.name,
            'login':this.login,
            'password':jera_config['trans_login'] and this.password or reduce(lambda a,b:a+b, map(chr, random.sample(PASSWORD_CHARS, PASSWORD_LENGTH))),
            'email':this.email,
            'user_email':this.email,
            'context_lang':this.context_lang,
            'groups_id':[(6,0,jera_config['group_ids'])],
            'active': False,
        }

        ##### password crypting for joomla site #####
        #salt = self.pool.get('captcha.captcha').gen_random_code(32)
        salt = self.gen_random_code(32)
        crypt = md5.new(this.password+salt).hexdigest()
        #############################

        try:
            new_user_id = user_obj.create(cr, 1, new_user_data, context=context)
        except Exception, e:
            cr.commit()
            this.write({'code_verify':False,'password':False,'password_verify':False}, context=context)
            raise e

        server = jconfig_obj.make_xmlrpc_object(jera_config['hostname'], jera_config['port'], jera_config['ssl'], jera_config['handler'])
        server.jera.createUser(jera_config['login'], jera_config['password'], this.login, this.name.encode("UTF-8"), crypt+':'+salt, this.email, this.context_lang.replace('_','-'))

        confirm_hash = self.gen_random_code(32)
        ##### E-mail sending #####
        juser_data = self.copy_data(cr, 1, this.id, context=context)
        juser_data.update({'user_id':new_user_id,'hash':confirm_hash,'auto':True,'config_id':config_id[0]})
        juser_id = juser_obj.create(cr, 1, juser_data, context=context)

        self._send_email(cr, uid, juser_id, this.email, confirm_hash, context=context)
        ##########################

        done_msg = _('Account registration was successfully done.')+' '+_('To e-mail %s was sent a link that you have to confirm registration.') % '<strong>%s</strong>' % this.email

        this.unlink(context)
        return "message", done_msg

    def jera_request_confirm_register(self, cr, uid, ids, confirm_hash, context=None):
        done_msg = _('Account <strong>"%s"</strong> registration was successfully confirmed. You can login.')
        jconfig_obj = self.pool.get('jera.config')
        jera_host = context.get('jera_host')
        config_id = jconfig_obj.search(cr, 1, [('hostname','=',jera_host)], context=context)
        jera_config = jconfig_obj.read(cr, 1, config_id[0], ['login','password','hostname','port','ssl','trans_login','group_ids','handler'], context=context)
        server = jconfig_obj.make_xmlrpc_object(jera_config['hostname'], jera_config['port'], jera_config['ssl'], jera_config['handler'])
        for juser in self.pool.get('jera.users').browse(cr, 1, ids, context=context):
            if not juser.confirmed and juser.hash==confirm_hash:
                juser.user_id.write({'active':True}, context=context)
                server.jera.unblockUser(jera_config['login'], jera_config['password'], juser.login)
                juser.write({'hash':False}, context=context)
                return "message", done_msg % juser.name

        return True

    def read(self,cr, uid, ids, fields=None, context=None, load='_classic_read'):
        def override(o):
            if uid != 1:
                if 'password' in o: o['password'] = False
                if 'password_verify' in o: o['password_verify'] = False
                if 'code_verify' in o: o['code_verify'] = False
            return o

        result = super(jera_register, self).read(cr, uid, ids, fields, context, load)
        if not result:
            return False
        if isinstance(ids, (int, long)):
            result = override(result)
        else:
            result = map(override, result)
        return result

    _columns = {
        'name': fields.char('User Name', size=64, select=True, help="The new user's real name"),
        'login': fields.char('Login', size=64, required=True, help="Used to log into the system"),
        'password': fields.char('Password', size=64, invisible=True, required=True),
        'password_verify': fields.char('Verify Password', size=64, invisible=True),
        'context_lang': fields.selection(_lang_get, 'Language', help="Sets the language for the user interface"),
        'hash':fields.char('Hash', size=64),
        'email': fields.char('Email', size=64, requred=True),
        
    }
    
jera_register()

