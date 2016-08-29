##############################################################################
#
# Copyright (c) 2008-2013 Alistek Ltd. (http://www.alistek.com) All Rights Reserved.
#                    General contacts <info@alistek.com
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

from osv import osv,fields
import xmlrpclib
from socket import error
import md5
import random
from tools.translate import _
import time, datetime
import netsvc
import base64

DEF_HTTP_PORT = 80
DEF_HTTPS_PORT = 443
PASSWORD_LENGTH=16
PASSWORD_CHARS=range(48,57)+range(65,91)+range(97,122)

JRELEASE_HANDLERS = {'1.5':"xmlrpc/index.php",'1.6':"index.php?option=com_jera&task=service&lang=en"}

class jera_config(osv.osv):
    _name = 'jera.config'
    _description = 'JERA connection configuration'
    _rec_name = 'hostname'

    def __init__(self, pool, cr):
        super(jera_config, self).__init__(pool, cr)
        self._DEF_HTTP_PORT = DEF_HTTP_PORT
        self._DEF_HTTPS_PORT = DEF_HTTPS_PORT

    def jera_search(self, cr, uid, act_type, act_id, custom_domain='[]', search=[], variables={}, model=None, context={}):
        if act_type=='ir.actions.act_window':
            fields = ['domain','context','res_model']
        elif act_type=='ir.actions.report.xml':
            fields = ['domain','model']
        if not model:
            act = self.pool.get(act_type).read(cr, 1, int(act_id), fields)
            context_str = act.get('context') or '{}'
            domain_str = act.get('domain') or '[]'
            model = act.get('model') or act.get('res_model')
        else:
            context_str = '{}'
            domain_str = '[]'
        variables['uid'] = uid
        variables['user'] = self.pool.get('res.users').browse(cr, 1, uid, context=context)
        variables['section_id'] = False
        variables['context'] = context
        context.update(eval(context_str, variables))
        variables['context'] = context
        domain = eval(domain_str+'+('+(custom_domain or '[]')+' or [])', variables)
        domain += search or []
        res = self.pool.get(model).search(cr, uid, domain, context=context)
        limit = context.get('jera_limit')
        limitstart = context.get('jera_limitstart',0)
        return limit and {'part_ids':res[limitstart:limit+limitstart], 'total':len(res)} or {'part_ids':res,'total':len(res)}

    def jera_name_search(self, cr, uid, act_type, act_id, name='', operator='ilike', \
                custom_domain='[]', custom_context='{}', drilldown_context='{}', limit=50, sort='newest', \
                    model=None, only_ids=False, context={}):
        if act_type=='ir.actions.act_window':
            fields = ['domain','context','res_model']
        elif act_type=='ir.actions.report.xml':
            fields = ['domain','model']
        variables = {
            'uid': uid,
            'user': self.pool.get('res.users').browse(cr, 1, uid, context=context),
            'section_id': False,
            'context': context,
        }
        if not model:
            act = self.pool.get(act_type).read(cr, 1, int(act_id), fields)
            context_str = act.get('context') or '{}'
            context.update(eval(context_str, variables))
            variables['context'] = context
            context.update(eval(custom_context, variables))
            variables['context'] = context
            domain_str = act.get('domain') or '[]'
            model = act.get('model') or act.get('res_model')
            domain = eval(domain_str+'+('+(custom_domain or '[]')+' or [])', variables)
        else:
            context.update(eval(custom_context or '{}', variables))
            variables['context'] = context
            domain = eval(custom_domain or '[]', variables)
        obj = self.pool.get(model)
        res = obj.name_search(cr, uid, name, domain, operator, context, limit=limit)
        if res and not only_ids:
            dd_context = eval(drilldown_context, variables)
            ctx = dd_context or context
            itemid = ctx.get('itemid',ctx.get('Itemid',False))
            perm_res = obj.perm_read(cr, uid, map(lambda a: a[0], res), context=context, details=False)
            res = dict(res)
            perm_res = map(lambda r: {'id':r['id'], 'name':res[r['id']], 'created':r['create_date'], 'itemid':itemid}, perm_res)
            if sort in ('newest', 'oldest'):
                reverse = False
                perm_res.sort(key=lambda a: a['created'], reverse=sort=='newest')
            else:
                perm_res.sort(key=lambda a: a['name'])
            res = perm_res
        limit = context.get('jera_limit')
        limitstart = context.get('jera_limitstart',0)
        if only_ids:
            res = map(lambda r: r[0],res)
        return limit and {'part_ids':res[limitstart:limit+limitstart], 'total':len(res)} or res

    def jera_read(self, cr, uid, model, ids, fields, context={}):
        if not ids:
            return False
        colors_expr = context.get('_colors')
        rows = self.pool.get(model).read(cr, uid, ids, fields, context=context)
        if colors_expr:
            colors = dict([a.split(':') for a in colors_expr.split(';') if a])
            variables = {'uid':uid,
                         'user':self.pool.get('res.users').browse(cr, 1, uid, context=context),
                         'context':context,
                         'time':time,
                         'datetime':datetime,
                         'current_date':time.strftime('%Y-%m-%d'),
                        }
            for row in rows:
                for c in colors:
                    row_copy = row.copy()
                    row_copy.update(variables)
                    if(eval(colors[c], row_copy)):
                        row['_color'] = c
                        break
        return rows

    def jera_colors_eval(self, cr, uid, colors_expr, model, ids, context={}):
        rows = self.pool.get(model).read(cr, uid, ids, context=context, load="_classic_write")
        variables = {'uid':uid,
                     'user':self.pool.get('res.users').browse(cr, 1, uid, context=context),
                     'context':context,
                     'time':time,
                     'datetime':datetime,
                     'current_date':time.strftime('%Y-%m-%d'),
                    }
        res = {}
        colors = dict([a.split(':') for a in colors_expr.split(';') if a])
        for row in rows:
            row.update(variables)
            for c in colors:
                if(eval(colors[c], row)):
                    res[str(row['id'])] = c
                    break
        return res

    def jera_get_report(self, cr, uid, model, report_name, ids, context={}):
        data = {'model': model, 'id': ids[0], 'report_type': 'aeroo', 'in_format': 'genshi-raw'}
        res = netsvc.Service._services['report.%s' % report_name].create(cr, uid, ids, data, context=context)
        return {'result':base64.encodestring(res[0]),'format':res[1]}

    def jera_get_report_stylesheet(self, cr, uid, report_name, context={}):
        report_obj = self.pool.get('ir.actions.report.xml')
        report_id = report_obj.search(cr, uid, [('report_name','=',report_name)], context=context)
        report = report_obj.browse(cr, 1, report_id[0], context=context)
        if report.styles_mode=='global':
            stylesheet = self.pool.get('res.users').browse(cr, 1, uid, context=context).company_id.stylesheet_id
        elif report.styles_mode=='specified':
            stylesheet = report.stylesheet_id
        else:
            stylesheet = False
        return stylesheet and stylesheet.report_styles or False

    def name_get(self, cr, uid, ids, context={}):
        res = []
        for cfg in self.read(cr, uid, ids, ['name',self._rec_name], context, load='_classic_write'):
            res.append((cfg['id'], cfg.get('name',False) or cfg[self._rec_name]))
        return res

    _columns = {
        'name':fields.char('Name', size=64),
        'hostname':fields.char('Host', size=64, required=True, help='Host name where joomla site is located'),
        'port': fields.integer('Port'),
        'ssl':fields.boolean('SSL'),
        'version':fields.char('Joomla version', size=16),
        'handler':fields.char('Joomla xmlrpc handler', size=16),
        'login':fields.char('Username', size=64, required=True, help='User in joomla site'),
        'password':fields.char('Password', size=64, required=True, help='User password in joomla site'),
        'group_ids':fields.many2many('res.groups', 'jconfig_groups_rel', 'jconfig_id', 'group_id', 'Groups for new users'),
        'trans_login':fields.boolean('Transparent login', help="Allow directly login in OpenERP system for new created JERA users"),
        'company_id': fields.many2one('res.company', 'Company'),
        'active':fields.boolean('Active'),
        
    }

    def make_xmlrpc_uri(self, hostname, port=None, ssl=False, jrelease='1.5'):
        data = {'hostname':str(hostname),'handler':JRELEASE_HANDLERS.get(jrelease,"xmlrpc/index.php")} # str(hostname) required for correct server proxy URL
        if ssl:
            data['proto']="https"
            data['port']=port and port or self._DEF_HTTPS_PORT
            uri = "%(proto)s://%(hostname)s:%(port)s/%(handler)s"
        else:
            data['proto']="http"
            if port and port!=self._DEF_HTTP_PORT:
                data['port'] = port
                uri = "%(proto)s://%(hostname)s:%(port)s/%(handler)s"
            else:
                uri = "%(proto)s://%(hostname)s/%(handler)s"
            #data['port']=port and port or self._DEF_HTTP_PORT
        return uri % data

    def make_xmlrpc_object(self, hostname, port=None, ssl=False, jhandler='1.5'):
        #data = {'hostname':str(hostname),'jhandler':jhandler} # str(hostname) required for correct server proxy URL
        #if ssl:
        #    data['proto']="https"
        #    data['port']=port and port or self._DEF_HTTPS_PORT
        #    uri = "%(proto)s://%(hostname)s:%(port)s/%(handler)s"
        #else:
        #    data['proto']="http"
        #    if port and port!=self._DEF_HTTP_PORT:
        #        data['port'] = port
        #        uri = "%(proto)s://%(hostname)s:%(port)s/%(handler)s"
        #    else:
        #        uri = "%(proto)s://%(hostname)s/%(handler)s"
            #data['port']=port and port or self._DEF_HTTP_PORT
        #uri = "%(proto)s://%(hostname)s/index.php?option=com_jera&task=service"
        uri = self.make_xmlrpc_uri(hostname, port, ssl, jhandler)
        return xmlrpclib.ServerProxy(uri, encoding='UTF-8', allow_none=True)

    def check_xmlrpc_connection(self, hostname, port=None, ssl=False, jrelease='1.5'):
        uri = self.make_xmlrpc_uri(hostname, port, ssl, jrelease)
        server = xmlrpclib.ServerProxy(uri, encoding='UTF-8', allow_none=True)
        #data = {'hostname':str(hostname),'handler':jhandler}
        #if ssl:
        #    data['proto']="https"
        #    data['port']=port and port or self._DEF_HTTPS_PORT
        #    uri = "%(proto)s://%(hostname)s:%(port)s/%(handler)s"
        #else:
        #    data['proto']="http"
        #    if port and port!=self._DEF_HTTP_PORT:
        #        data['port']=port and port or self._DEF_HTTP_PORT
        #        uri = "%(proto)s://%(hostname)s:%(port)s/%(handler)s"
        #    else:
        #        uri = "%(proto)s://%(hostname)s/%(handler)s"
            #data['port']=port and port or self._DEF_HTTP_PORT
        try:
            methods_list = server.system.listMethods()
        except Exception, e:
            raise osv.except_osv(_('Warning!'), _('XML-RPC services is not enabled on the host: "%s"') % uri)
        if not filter(lambda mtehod: mtehod.startswith('jera.'), methods_list):
            raise osv.except_osv(_('Warning!'), _('XML-RPC - JERA plugin is not enabled on the host: "%s"') % uri)
        return True

    def check_joomla_version(self, login, password, hostname, port=None, ssl=False):
        for release in JRELEASE_HANDLERS:
            uri = self.make_xmlrpc_uri(hostname, port, ssl, release)
            server = xmlrpclib.ServerProxy(uri, encoding='UTF-8', allow_none=True)
            try:
                return server.jera.getJVersion(login, password), release
            except xmlrpclib.ProtocolError, e:
                continue
        return False, '1.5'

    def check_and_create_juser(self, cr, uid, login, password, data, jusers_id, hostname, port=None, ssl=False, jrelease='1.5'):
        uri = self.make_xmlrpc_uri(hostname, port, ssl, jrelease)
        server = xmlrpclib.ServerProxy(uri, encoding='UTF-8', allow_none=True)
        res = server.jera.getUser(login, password, data['login'])
        if not server.jera.getUser(login, password, data['login']):
            user = self.pool.get('res.users').browse(cr, uid, data['user_id'])
            user_password = data['password'] or user.password
            salt = reduce(lambda a,b:a+b, map(chr, random.sample(PASSWORD_CHARS, 32)))
            crypt = md5.new(user_password+salt).hexdigest()

            jera_user_id = server.jera.createUser(login, password,
                                   data['login'],
                                   data.get('name',user.name),
                                   crypt+':'+salt, data['email'],
                                   data.get('context_lang',user.context_lang).replace('_','-')
                           )
            server.jera.unblockUser(login, password, data['login'])
            self.pool.get('jera.users').write(cr, uid, jusers_id, {'password':user_password})
            return jera_user_id
        return True

    _defaults = {
        'active': True,
        'port':DEF_HTTP_PORT,
    }

jera_config()

class jera_users(osv.osv):
    '''
    JERA users
    '''
    _name = 'jera.users'
    _rec_name = 'login'
    _description = 'JERA users'

    def __init__(self, pool, cr):
        super(jera_users, self).__init__(pool, cr)

        self._PASSWORD_LENGTH = PASSWORD_LENGTH
        self._PASSWORD_CHARS = PASSWORD_CHARS
   #     self._jdata = {}
   #     self._rec_name = 'login'
   #     ##### Set Joomla login data #####
   #     self._jera_configs = {}
   #     try:
   #         ids = self.search(cr, 1, [])
   #     except Exception, e:
   #         cr.rollback()
   #         print e
   #     else:
   #         for juser in self.browse(cr, 1, ids):
   #             if juser.config_id:
   #                 self._jera_configs[juser.id] = {
   #                     'joomla_hostname':juser.config_id.hostname,
   #                     'joomla_login':juser.config_id.login,
   #                     'joomla_password':juser.config_id.password,
   #                 }
   #             else:
   #                 self._jera_configs[juser.id] = {
   #                     'joomla_hostname':False,
   #                     'joomla_login':False,
   #                     'joomla_password':False,
   #                 }
   #     #############################
    
    _columns = {
        'login':fields.char('Joomla User', size=64, required=True, help="The new user's login"),
        'password':fields.char('Joomla User Password', size=64, invisible=True, required=False),
        'user_id':fields.many2one('res.users', 'OpenERP User', required=False, ondelete='cascade'),
        #'email': fields.related('user_id','user_email', type='char', string='Email', size=64, required=True),
        'email': fields.char('Email', size=64, requred=True),
        'config_id':fields.many2one('jera.config', 'JERA connection configuration'),
        'auto':fields.boolean('Auto Create'),
        'create_ip_address':fields.char('IP Address', size=16, required=False, readonly=True, help="IP Address from which the user was registered."),
        
    }

    def _get_default_config(self, cr, uid, context={}):
        res = self.pool.get('jera.config').search(cr, 1, [], context=context)
        return res and res[0] or False

    _defaults = {
        'config_id': _get_default_config,
        'auto': True,
    }

    def change_user(self, cr, uid, ids, *args):
        args = list(args)

        user_id = args.pop(0)
        if not user_id:
            return {'value':{}}
        user = self.pool.get('res.users').read(cr, uid, user_id, ['login','user_email','name','context_lang'])
        data = {}
        for field in ['login','user_email','name','context_lang']:
            if not args:
                break
            value = args.pop(0)
            if not value:
                data[field.replace('user_','')] = user[field]
        return {'value':data}

    def jera_user_login(self, cr, uid, user, hostname, context={}):
        ids = self.search(cr, uid, [('login','=',user),('config_id.hostname','=',hostname)], context=context)
        if ids:
            juser = self.browse(cr, uid, ids[0], context=context)
            juser.user_id.write({'date':time.strftime("%Y-%m-%d %H:%M:%S")})
            return True
        else:
            return False

    def jera_user_exist(self, cr, uid, user, hostname, context={}):
        return bool(self.search(cr, uid, [('login','=',user),('config_id.hostname','=',hostname)], context=context))

    def synchronize_jera_user(self, cr, uid, data, hostname, context={}):
        user_obj = self.pool.get('res.users')
        lang = data.get('language','en_US') or 'en_US'
        lang = lang in ('en-GB','') and 'en_US' or lang.replace('-','_')
        config_id = self.pool.get('jera.config').search(cr, uid, [('hostname','=',hostname)], context=context)
        if config_id:
            config = self.pool.get('jera.config').read(cr, uid, config_id[0], ['trans_login','group_ids','company_id'], context=context, load="_classic_write")
            trans_login = config['trans_login']
            partner_id = self.pool.get('res.partner').search(cr, 1, [('ref','=','JERA')], context=context)
            address_id = self.pool.get('res.partner.address').create(cr, 1, {'name':data['fullname'],
                                                                               'email':data['email'],
                                                                               'company_id':config['company_id'],
                                                                               'partner_id':partner_id and partner_id[0] or False},
                                                                    context=context)
            user_id = user_obj.create(cr, 1, {'name':data['fullname'],
                                      'login':data['username'],
                                      'context_lang':lang,
                                      'password':trans_login and data['password'] or reduce(lambda a,b:a+b, map(chr, random.sample(self._PASSWORD_CHARS, self._PASSWORD_LENGTH))),
                                      'groups_id':[(6,0,config['group_ids'])],
                                      'company_id':config['company_id'],
                                      'address_id':address_id,
                                      'site_id':config_id[0],
                                      }, context=context)
            if user_id:
                context['joomla_user_exist'] = True
                return self.create(cr, uid, {'login':data['username'],
                                             'email':data['email'],
                                             'user_id':user_id,
                                             'config_id':config_id[0],
                                             'password':data['password'],
                                             'name':data['fullname'],
                                             'context_lang':lang,
                                             'auto':context.get('auto'),
                                             'create_ip_address':context.get('ipaddress'),
                                             }, context=context)
        else:
            return False

    def write(self, cr, uid, ids, vals, context=None):
        if 'confirmed' in vals:
            jera_config_obj = self.pool.get('jera.config')
            r = self.read(cr, uid, ids[0], ['config_id','login','auto'], context=context)
            if 'auto' in vals and vals['auto'] or 'auto' not in vals and r['auto']:
                jera_config = jera_config_obj.read(cr, uid, vals.get('config_id',r['config_id'][0]), ['login','password','hostname','port','ssl','handler'], context=context)
                server = jera_config_obj.make_xmlrpc_object(jera_config['hostname'], jera_config['port'], jera_config['ssl'], jera_config['handler'])
                if vals['confirmed']:
                    server.jera.unblockUser(jera_config['login'], jera_config['password'], vals.get('login',r['login']))
                else:
                    server.jera.blockUser(jera_config['login'], jera_config['password'], vals.get('login',r['login']))
        res = super(jera_users, self).write(cr, uid, ids, vals, context)
        return res

    def create(self, cr, uid, vals, context={}):
        res_id = super(jera_users, self).create(cr, uid, vals, context)
        if not (vals.get('auto') or context.get('auto')):
            return res_id
        if 'user_id' in vals and 'config_id' in vals and not context.get('joomla_user_exist'):
            jera_config_obj = self.pool.get('jera.config')
            jera_config = jera_config_obj.read(cr, uid, vals['config_id'], ['login','password','hostname','port','ssl','handler'], context=context)
            if not jera_config['hostname'] or not jera_config['login'] or not jera_config['password']:
                raise osv.except_osv(_('Error!'), _("Can't connect to JERA. Please define connection."))
            server = jera_config_obj.make_xmlrpc_object(jera_config['hostname'], jera_config['port'], jera_config['ssl'], jera_config['handler'])
            user = self.pool.get('res.users').browse(cr, uid, vals['user_id'], context=context)

            password = vals['password'] or user.password
            salt = reduce(lambda a,b:a+b, map(chr, random.sample(self._PASSWORD_CHARS, 32)))
            crypt = md5.new(password+salt).hexdigest()

            try:
                jera_user_id = server.jera.createUser(jera_config['login'],
                                       jera_config['password'],
                                       vals['login'],
                                       vals.get('name',user.name),
                                       crypt+':'+salt, vals['email'],
                                       vals.get('context_lang',user.context_lang).replace('_','-')
                                    )
                if user.active and jera_user_id:
                    server.jera.unblockUser(jera_config['login'], jera_config['password'], vals['login'])
            except xmlrpclib.Fault, e:
                if e.faultCode==801:
                    raise osv.except_osv(_(e.faultString), _("Please check connection data."))
                else:
                    raise osv.except_osv(_("Error!"), _(e.faultString))
            except error, e:
                raise osv.except_osv(_("Error %s") % e.errno, _(e.strerror))

        return context.get('jera_return') and jera_user_id or res_id

    def unlink(self, cr, uid, ids, context=None):
        jera_config_obj = self.pool.get('jera.config')
        for juser in self.browse(cr, uid, ids, context=context):
            jera_config = jera_config_obj.read(cr, uid, juser.config_id.id, ['login','password','hostname','port','ssl','handler'], context=context)
            server = jera_config_obj.make_xmlrpc_object(jera_config['hostname'], jera_config['port'], jera_config['ssl'], jera_config['handler'])
            try:
                if juser.login in ('admin','jera_anonymous'):
                    continue
                try:
                    jera_removed = server.jera.removeUser(jera_config['login'], jera_config['password'], juser.login)
                except Exception, e:
                    print e
                #if not jera_removed:
                #    raise osv.except_osv(_("Error!"), _("Cannot delete Joomla user! Username: %s; Connection: %s.") % (juser.login, jera_config['hostname']))
            except IOError, e:
                print e
        return super(jera_users, self).unlink(cr, uid, ids, context=context)

    #def _load_jconnect_data(self, host, login, password):
    #    self._joomla_hostname = str(host)
    #    self._joomla_login = login
    #    self._joomla_password = password
    #    return True

    def get_openerp_user(self, cr, uid, name, password, hostname):
        crypt, salt = password.split(':')
        cr.execute("""
                    SELECT password
                    FROM jera_users
                    WHERE login = %s and config_id in (SELECT id FROM jera_config WHERE hostname=%s)
                   """, (name,hostname))
        j_user = cr.dictfetchone()
        if j_user:
            testcrypt = md5.new(j_user['password']+salt).hexdigest()
            if testcrypt==crypt:
                cr.execute("""
                            SELECT A.login, A.password
                            FROM res_users A
                            WHERE id = (SELECT B.user_id
                                FROM jera_users B
                                WHERE B.login = %s and B.config_id in (SELECT C.id FROM jera_config C WHERE C.hostname=%s))
                           """, (name,hostname))
                return cr.fetchone()
        else:
            raise osv.except_osv(_('Warning!'), _('The user "%s" does not exist with site "%s"') % (name,hostname))
        return False

    def _check_login(self, cr, uid, ids):
        user = self.read(cr, uid, ids[0], ['login','config_id'], load='_classic_write')
        if self.search(cr, uid, [('login','=',user['login']),('config_id','=',user['config_id']),('id','not in',ids)]):
            return False
        return True

    def _check_email(self, cr, uid, ids):
        user = self.read(cr, uid, ids[0], ['email','config_id'], load='_classic_write')
        if self.search(cr, uid, [('email','=',user['email']),('config_id','=',user['config_id']),('id','not in',ids)]):
            return False
        return True

    _constraints = [
            (_check_login, 'You cannot have two users with the same login!', ['login']),
            (_check_email, 'You cannot have two users with the same email!', ['email']),
        ]

jera_users()

class users(osv.osv):
    _name = 'res.users'
    _inherit = 'res.users'
    
    def unlink(self, cr, uid, ids, context=None):
        juser_obj = self.pool.get('jera.users')
        for user_id in ids:
            juser_id = juser_obj.search(cr, uid, [('user_id','=',user_id)], context=context)
            if juser_id:
                juser = juser_obj.unlink(cr, uid, juser_id, context=context)
        return super(users, self).unlink(cr, uid, ids, context=context)

    _columns = {
        'site_id':fields.many2one('jera.config', 'Created by JERA'),
        'address_id': fields.many2one('res.partner.address', 'Address'),
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context={}, count=False):
        if not context.get('show_all'):
            args.extend([('site_id','=',False)])
        res = super(users, self).search(cr, uid, args, offset, limit, order, context, count)
        return res

users()

def get_active_module(self, cr, uid, context={}):
    res = self.pool.get('ir.module.module').search(cr, uid, [('name','=',context.get('module_name'))], context=context)
    return res and res[0] or False

########## Jera Users ##########

user_profiles_columns = {
    'module_id':fields.many2one('ir.module.module', 'Module', required=True),
    'name': fields.char('User Name', size=64, select=True, help="The new user's real name"),
    'login':fields.char('Joomla User', size=64, required=True, help="The new user's login"),
    'password':fields.char('Joomla User Password', size=64, required=True),
    'user_id':fields.many2one('res.users', 'OpenERP User', required=True, ondelete='set null'),
    'email': fields.char('Email', size=64, required=True),
}

class jera_user_profiles(osv.osv):
    _name = 'jera.user.profiles'
    _description = 'Profiles for JERA users'
    _rec_name = 'login'
    
    _columns = user_profiles_columns

jera_user_profiles()

class jera_user_profiles_temp(osv.osv_memory):
    _name = 'jera.user.profiles.temp'

    _columns = {
        'realid': fields.integer('Real profile Id'),
        'install_id':fields.many2one('jera.installer.action', 'Install Id'),
        'install':fields.boolean('Install'),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name','=','jera.user.profiles.form')], context=context)
        view = self.pool.get('jera.user.profiles').fields_view_get(cr, uid, view_ids[0], view_type, context, toolbar, submenu)
        #res = super(jera_user_profiles_temp, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        return view

    _columns.update(user_profiles_columns)
    _defaults = {
        'module_id': get_active_module,
        'install': True,
    }

jera_user_profiles_temp()

########## Jera Actions ##########

def get_action_name(self, cr, uid, ids, field, arg=None, context={}):
    res = {}
    for p in self.browse(cr, uid, ids, context):
        res[p.id] = p.action_id.name
    return res

def _get_jera_actions(self, cr, uid, context={}):
    obj = self.pool.get('jera.action.profiles')
    module_name = context.get('module_name')
    domain = module_name and [('module_id.name','=',module_name)] or []
    ids = obj.search(cr, uid, domain)
    actions = obj.browse(cr, uid, ids, context)
    return [(False,'')]+[(str(a.id), a.name or a.action_id.name or a.action_id.res_model) for a in actions if a]

action_profiles_columns = {
    'name':fields.char('Profile name', size=64, required=False, readonly=False),
    #'action_id':fields.many2one('ir.actions.actions', 'Action', required=True),
    'action_id': fields.reference('Action', 
        selection=[
            ('ir.actions.act_window', 'ir.actions.act_window'),
            ('ir.actions.report.xml', 'ir.actions.report.xml'),
            
        ], size=128, required=True, _classic_read=True),
    'action_name': fields.function(get_action_name, method=True, type='char', string='Action Name'),
    'module_id':fields.many2one('ir.module.module', 'Module', required=True),
    'alias':fields.char('Alias', size=64, required=False, readonly=False),
    'domain':fields.text('Domain', required=False, readonly=False),
    'context':fields.text('Context', required=False, readonly=False),
    'used_user':fields.selection([
        ('default',_('Default')),
        ('anonymous',_('Anonymous')),
        ('custom',_('Custom')),
        
    ],'User'),
    'user_id':fields.many2one('jera.user.profiles', 'Jera user', required=False),
    'r_metainfo':fields.selection([
        ('never','Never'),
        ('html','HTML'),
        ('xhtml','XHTML'),
        
    ],'Use meta info'),
    'id_security':fields.selection([
        ('none','None (Plain)'),
        ('signed','Signed (MD5 Hash)'),
        
    ],'Apply id security'),
    'searchable':fields.boolean('Searchable'),
    'search_area':fields.boolean('As Separate Search Area'),
    'dd_action_id': fields.selection(_get_jera_actions, 'Drillldown action'),
}

action_profiles_defaults = {
    'r_metainfo': 'never',
    'used_user': 'default',
    'id_security': 'none',
}


class jera_action_profiles(osv.osv):
    '''
    JERA actions profiles
    '''
    _name = 'jera.action.profiles'
    _description = 'Profiles for JERA actions'

    def name_get(self, cr, uid, ids, context={}):
        res = []
        for jera_act in self.browse(cr, uid, ids, context):
            res.append((jera_act.id, jera_act.name or jera_act.action_id.name or jera_act.action_id.res_model))
        return res

    _columns = action_profiles_columns
    _defaults = action_profiles_defaults

jera_action_profiles()

class jera_action_profiles_temp(osv.osv_memory):
    _name = 'jera.action.profiles.temp'

    _columns = {
        'realid': fields.integer('Real profile Id'),
        'install_id':fields.many2one('jera.installer.action', 'Install Id'),
        'install':fields.boolean('Install'),
        
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name','=','jera.action.profiles.form')], context=context)
        view = self.pool.get('jera.action.profiles').fields_view_get(cr, uid, view_ids[0], view_type, context, toolbar, submenu)
        #res = super(jera_action_profiles_temp, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        #res['arch'] = view['arch']
        return view

    _columns.update(action_profiles_columns)
    _defaults = {
        'module_id': get_active_module,
        'install': True,
    }
    _defaults.update(action_profiles_defaults)

jera_action_profiles_temp()

########## Jera Menus ##########

menu_profiles_columns = {
    'name':fields.char('Title', size=256, required=True),
    'module_id':fields.many2one('ir.module.module', 'Module', required=True),
    'layout':fields.selection([
        ('list',_('List')),
        ('form',_('Form')),
        
    ],'Layout', select=True),
    'published':fields.boolean('Published'),
    'parent_id':fields.many2one('jera.menu.profiles', 'Parent Menu'),
    'access':fields.selection([
        ('0',_('Public')),
        ('1',_('Registered')),
        ('2',_('Special')),
        
    ],'Access', required=True),

    'action_id': fields.selection(_get_jera_actions, 'Action Profile', required=True),
    'user_id':fields.many2one('jera.user.profiles', 'Jera user', required=False),
    'used_user':fields.selection([
        ('default','Default'),
        ('anonymous','Anonymous'),
        ('custom','Custom'),
        
    ],'User Usage'),
    'dd_action_id': fields.selection(_get_jera_actions, 'Drillldown action'),
    'dd_click':fields.selection([
        ('0',_('Single')),
        ('1',_('Double')),
        
    ],'Drilldown click'),
    'show_search':fields.selection([
        ('0',_('Hide')),
        ('1',_('Show')),
        ('2',_('Manual')),
        
    ],'Search Panel', select=True),
    'custom_search_fields': fields.text('Custom Search Fields'),
    
}
menu_profiles_defaults = {
    'layout':'list',
    'access': '0',
    'dd_click': '1',
    'show_search':'0',
    'published':True,
    'used_user': 'default',
}

class jera_menu_profiles(osv.osv):
    _name = 'jera.menu.profiles'
    _description = 'Profiles for JERA menu'

    _columns = menu_profiles_columns
    _defaults = menu_profiles_defaults

jera_menu_profiles()

class jera_menu_profiles_temp(osv.osv_memory):
    _name = 'jera.menu.profiles.temp'

    _columns = {
        'realid': fields.integer('Real profile Id'),
        'install_id':fields.many2one('jera.installer.action', 'Install Id'),
        'install':fields.boolean('Install'),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name','=','jera.menu.profiles.form')], context=context)
        view = self.pool.get('jera.menu.profiles').fields_view_get(cr, uid, view_ids[0], view_type, context, toolbar, submenu)
        #res = super(jera_menu_profiles_temp, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        #res['arch'] = view['arch']
        return view

    _columns.update(menu_profiles_columns)
    _defaults = {
        'module_id': get_active_module,
        'install': True,
    }
    _defaults.update(menu_profiles_defaults)

jera_menu_profiles_temp()

########## Jera Modules ##########

module_profiles_columns = {
    'name':fields.char('Title', size=256, required=True),
    'module_id':fields.many2one('ir.module.module', 'Module', required=True),
    'position':fields.selection([
        ('left','left'),
        ('right','right'),
        ('top','top'),
        ('bottom','bottom'),
        
    ],'Position', required=True),
    'access':fields.selection([
        ('0',_('Public')),
        ('1',_('Registered')),
        ('2',_('Special')),
        
    ],'Access', required=True),
    'showtitle':fields.boolean('Show Title'),
    'published':fields.boolean('Published'),
    'menus':fields.selection([
        ('all',_('All')),
        ('none',_('None')),
        ('select',_('Select Menu Item(s)')),
        
    ],'Menus'),
    'menu_ids':fields.many2many('jera.menu.profiles', 'jera_module_menu_rel', 'module_id', 'menu_id', 'Menu Selection'),

    'action_id': fields.selection(_get_jera_actions, 'Action Profile', required=True),
    'user_id':fields.many2one('jera.user.profiles', 'Jera user', required=False),
    'used_user':fields.selection([
        ('default','Default'),
        ('anonymous','Anonymous'),
        ('custom','Custom'),
        
    ],'User Usage'),
    'layout':fields.selection([
        ('list',_('List')),
        ('form',_('Form')),
        
    ],'Layout', select=True),

    'cache':fields.selection([
        ('0',_('No Caching')),
        ('1',_('Use Global')),
        
    ],'Cahce'),
    'cache_time': fields.integer('Cache Time', help="The period of time in seconds before the Module is re-cached"),
    
}

module_profiles_defaults = {
    'layout':'form',
    'access': '0',
    'published':True,
    'showtitle':False,
    'cache':'0',
    'cache_time':900,
    'position':'left',
    'menus':'all',
    'used_user': 'default',
}

class jera_module_profiles(osv.osv):
    _name = 'jera.module.profiles'
    _description = 'Profiles for JERA module'
    
    _columns = module_profiles_columns
    _defaults = module_profiles_defaults

jera_module_profiles()

class jera_module_profiles_temp(osv.osv_memory):
    _name = 'jera.module.profiles.temp'

    _columns = {
        'realid': fields.integer('Real profile Id'),
        'install_id':fields.many2one('jera.installer.action', 'Install Id'),
        'install':fields.boolean('Install'),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name','=','jera.module.profiles.form')], context=context)
        view = self.pool.get('jera.module.profiles').fields_view_get(cr, uid, view_ids[0], view_type, context, toolbar, submenu)
        #res = super(jera_module_profiles_temp, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        return view

    _columns.update(module_profiles_columns)
    _defaults = {
        'module_id': get_active_module,
        'install': True,
    }
    _defaults.update(module_profiles_defaults)

jera_module_profiles_temp()

##############################

class report_xml(osv.osv):
    _name = 'ir.actions.report.xml'
    _inherit = 'ir.actions.report.xml'

    _columns = {
        'domain':fields.char('Domain Value', size=250),
        
    }

report_xml()

