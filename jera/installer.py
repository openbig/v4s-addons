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

from osv import fields
from osv import osv
import random
import xmlrpclib
from tools.translate import _
from jera import DEF_HTTP_PORT, DEF_HTTPS_PORT, PASSWORD_LENGTH, PASSWORD_CHARS

class jera_installer(osv.osv_memory):
    _name = 'jera.installer'
    _inherit = 'res.config.installer'
    _rec_name = 'hostname'

    def _get_configs(self, cr, uid, context={}):
        obj = self.pool.get('jera.config')
        ids = obj.search(cr, uid, [('active','=',True)])
        ids.extend(obj.search(cr, uid, [('active','=',False)]))
        configs = obj.read(cr, uid, ids, ['name', 'hostname'], context)
        res = [(-1, _('- Create new -'))]
        res.extend([(r['id'], r['name'] or r['hostname']) for r in configs])
        return res

    def change_jera_config(self, cr, uid, ids, jera_config):
        data = {}
        if not jera_config:
            return {'value':{}}
        elif jera_config == -1:
            data = {'name':False,
                    'hostname':False,
                    'login':False,
                    'password':False,
                    'active':True,
                    'port':DEF_HTTP_PORT,
                    'ssl':False,
                    'version':False,
                    'trans_login':False,
                    'group_ids':[],
                    'company_id':self.pool.get('res.users').read(cr, uid, uid, ['company_id'], load='_classic_write')['company_id']
                    }
        else:
            data = self.pool.get('jera.config').read(cr, uid, jera_config, 
                ['name','hostname','login','password','description','active','port','ssl','trans_login','group_ids','company_id','version'])
            del data['id']
        return {'value':data}

    def change_ssl(self, cr, uid, ids, ssl, port):
        data = {}
        if not ssl and port in [DEF_HTTP_PORT,DEF_HTTPS_PORT]:
            data['port'] = DEF_HTTP_PORT
        elif ssl and port in [DEF_HTTP_PORT,DEF_HTTPS_PORT]:
            data['port'] = DEF_HTTPS_PORT
        return {'value':data}

    _columns = {
        'name':fields.char('Name', size=64),
        'hostname':fields.char('Host', size=64, required=True, help='Host name where joomla site is located. Must match with DNS name configuration for the site.'),
        'port': fields.integer('Port', required=True),
        'ssl':fields.boolean('SSL'),
        'version':fields.char('Joomla version', size=16),
        'handler':fields.char('Joomla xmlrpc handler', size=16),
        'login':fields.char('Username', size=64, required=True, help='User in joomla site'),
        'password':fields.char('Password', size=64, required=True, help='User password in joomla site'),
        'jera_config': fields.selection(_get_configs, 'JERA connection configuration', required=True),
        'description':fields.text('Description', readonly=True),
        'group_ids':fields.many2many('res.groups', 'jinstaller_groups_rel', 'jconfig_id', 'group_id', 'Groups for new users'),
        'trans_login':fields.boolean('Transparent login', help="Allow directly login in OpenERP system for new created JERA users"),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'active':fields.boolean('Active'),
    }

    def default_get(self, cr, uid, fields, context=None):
        jconfig_obj = self.pool.get('jera.config')
        data = super(jera_installer, self).default_get(cr, uid, fields, context=context)
        ids = jconfig_obj.search(cr, uid, [], context=context)
        data['company_id'] = self.pool.get('res.users').read(cr, uid, uid, ['company_id'], context=context, load='_classic_write')['company_id']
        if ids:
            data['jera_config'] = ids[0]
            res = self.change_jera_config(cr, uid, [], ids[0])['value']
        #    res = jconfig_obj.read(cr, uid, ids[0], ['hostname','login','password','description'], context=context)
        #    del res['id']
            data.update(res)
        else:
            data['jera_config'] = -1
        return data

    def execute(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        jconfig_obj = self.pool.get('jera.config')
        jusers_obj = self.pool.get('jera.users')
        users_obj = self.pool.get('res.users')
        res = self.read(cr, uid, ids, context=context, load='_classic_write')[0]

        jversion, jhandler_key = jconfig_obj.check_joomla_version(res['login'],res['password'],res['hostname'],res['port'],res['ssl'])
        res['version'] = jversion
        res['handler'] = jhandler_key

        jconfig_obj.check_xmlrpc_connection(res['hostname'],res['port'],res['ssl'],jhandler_key) # check the xmlrpc server workability
        config_id = int(res['jera_config'])

        del res['id'], res['jera_config']
        res['group_ids'] = [(6,0,res['group_ids'])]
        if config_id==-1:
            config_id = jconfig_obj.create(cr, uid, res, context=context)
        else:
            jconfig_obj.write(cr, uid, config_id, res, context=context)
        jusers_ids = jusers_obj.search(cr, uid, [('login','=','jera_anonymous'),('config_id','=',config_id)], context=context)
        anonymous = users_obj.search(cr, uid, [('login','=','jera_anonymous')], context=context)
        #if not anonymous:
        password = reduce(lambda a,b:a+b, map(chr, random.sample(PASSWORD_CHARS, PASSWORD_LENGTH)))
        address = self.pool.get('res.partner.address').search(cr, uid, [('partner_id.ref','=','JERA')], context=context)
        #user_id = users_obj.create(cr, uid, {'login':'jera_anonymous',
        #                                       'name':'JERA Anonymous',
        #                                       'email':'jera@alistek.com',
        #                                       'password':password,
        #                                       'groups_id':[(6,0,self.pool.get('res.groups').search(cr, uid, [('name','=','JERA')], context=context))],
        #                                       'address_id':address and address[0] or False
        #                                       }, context=context)
        user_id = anonymous[0]
        users_obj.write(cr, uid, user_id, {'password':password,
                                                     #'groups_id':[(6,0,self.pool.get('res.groups').search(cr, uid, [('name','=','JERA')], context=context))],
                                                     'address_id':address and address[0] or False
                                                    }, context=context)
        #else:
        #    user_id = anonymous[0]
        juser_data = {
            'login':'jera_anonymous',
            'name':'JERA Anonymous',
            'email':'jera@alistek.com',
            'password':password,
            'user_id':user_id,
        }
        if not jusers_ids:
            juser_data['auto'] = True
            juser_data['config_id'] = config_id
            jusers_obj.create(cr, uid, juser_data, context=context)
        else:
            jconfig_obj.check_and_create_juser(cr, uid, res['login'],
                                                        res['password'],
                                                        juser_data, jusers_ids[0],
                                                        res['hostname'],
                                                        res['port'],
                                                        res['ssl'],
                                                        jhandler_key)
        #self.pool.get('jera.users')._load_jconnect_data(res['hostname'],res['login'],res['password'])

    _defaults = {
        'description' : _("Here you can configure OpenERP connection to Joomla site where is installed JERA component")
    }

jera_installer()

