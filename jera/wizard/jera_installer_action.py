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
import netsvc
import xmlrpclib
from socket import error
from tools.translate import _
from jera.jera import DEF_HTTP_PORT, DEF_HTTPS_PORT

class jera_installer_action(osv.osv_memory):
    _name = 'jera.installer.action'

    def _get_configs(self, cr, uid, context={}):
        obj = self.pool.get('jera.config')
        ids = obj.search(cr, uid, [])
        configs = obj.read(cr, uid, ids, ['name', 'hostname'], context)
        return [(r['id'], r['name'] or r['hostname']) for r in configs]

    _columns = {
        'jera_user_ids':fields.one2many('jera.user.profiles.temp', 'install_id', 'Users'),
        'jera_action_ids':fields.one2many('jera.action.profiles.temp', 'install_id', 'Actions'),
        'jera_menu_ids':fields.one2many('jera.menu.profiles.temp', 'install_id', 'Menus'),
        'jera_module_ids':fields.one2many('jera.module.profiles.temp', 'install_id', 'Modules'),
        'config': fields.selection(_get_configs, 'Site'),
        'messages': fields.text('Messages'),
        'state':fields.selection([
            ('site','Sites'),
            ('user','Users'),
            ('action','Actions'),
            ('menu','Menus'),
            ('module','Modules'),
            ('install','Install'),
            ('done','Done'),
            
        ],'State', select=True, readonly=True),
        'states_seq':fields.serialized('Installation states sequence'),
        'states_prev':fields.serialized('List of previous state'),
        
    }

    _defaults = {
        'state': 'site',
        'states_seq': [],
        'states_prev': [],
    }

    def default_get(self, cr, uid, fields, context=None):
        states_seq = context.get('states_seq',[])
        user_prof_obj = self.pool.get('jera.user.profiles')
        action_prof_obj = self.pool.get('jera.action.profiles')
        menu_prof_obj = self.pool.get('jera.menu.profiles')
        module_prof_obj = self.pool.get('jera.module.profiles')
        data = super(jera_installer_action, self).default_get(cr, uid, fields, context=context)
        user_prof_ids = user_prof_obj.search(cr, uid, [('module_id.name','=',context.get('module_name'))], context=context)
        action_prof_ids = action_prof_obj.search(cr, uid, [('module_id.name','=',context.get('module_name'))], context=context)
        menu_prof_ids = menu_prof_obj.search(cr, uid, [('module_id.name','=',context.get('module_name'))], context=context)
        module_prof_ids = module_prof_obj.search(cr, uid, [('module_id.name','=',context.get('module_name'))], context=context)
        if 'user' in states_seq:
            user_res = []
            for user_profile in user_prof_obj.read(cr, uid, user_prof_ids, context=context):
                user_profile['realid'] = user_profile['id']
                del user_profile['id']
                user_res.append(user_profile)
            data['jera_user_ids'] = user_res
        if 'action' in states_seq:
            action_res = []
            for action_profile in action_prof_obj.read(cr, uid, action_prof_ids, context=context):
                action_profile['realid'] = action_profile['id']
                del action_profile['id']
                action_res.append(action_profile)
            data['jera_action_ids'] = action_res
        if 'menu' in states_seq:
            menu_res = []
            for menu_profile in menu_prof_obj.read(cr, uid, menu_prof_ids, context=context):
                menu_profile['realid'] = menu_profile['id']
                del menu_profile['id']
                menu_res.append(menu_profile)
            data['jera_menu_ids'] = menu_res
        if 'module' in states_seq:
            module_res = []
            for module_profile in module_prof_obj.read(cr, uid, module_prof_ids, context=context):
                module_profile['realid'] = module_profile['id']
                del module_profile['id']
                module_res.append(module_profile)
            data['jera_module_ids'] = module_res
        data['messages'] = context.get('messages',False)
        data['states_seq'] = states_seq # this field will be as list
        data['states_prev'] = [] # this field will be as list
        return data

    def action_back(self, cr, uid, ids, context={}):
        this = self.browse(cr, uid, ids[0], context=context)
        states_seq = this.states_seq
        states_prev = this.states_prev
        states_seq.insert(0,this.state)
        new_state = states_prev.pop()
        return this.write({'state':new_state, 'states_seq':states_seq, 'states_prev':states_prev}, context=context)

    def action_next(self, cr, uid, ids, context={}):
        this = self.browse(cr, uid, ids[0], context=context)
        states_seq = this.states_seq
        states_prev = this.states_prev
        if this.state=='site':
            jera_config_obj = self.pool.get('jera.config')
            jera_config = jera_config_obj.browse(cr, uid, int(this.config), context=context)
            if not jera_config.hostname or not jera_config.login or not jera_config.password:
                raise osv.except_osv(_('Error!'), _("Can't connect to JERA. Please define connection."))
            jera_config_obj.check_xmlrpc_connection(jera_config.hostname,jera_config.port,jera_config.ssl,jera_config.handler) # check the xmlrpc server workability
            server = jera_config_obj.make_xmlrpc_object(jera_config.hostname, jera_config.port, jera_config.ssl, jera_config.handler)
            try:
                res = server.jera.testConnect(jera_config.login, jera_config.password)
            except xmlrpclib.Fault, e:
                raise osv.except_osv(_('Error!'), e.faultString)
            except error, e:
                raise osv.except_osv(_("Error %s") % e.errno, _(e.strerror))
            except Exception, e:
                raise osv.except_osv(_('Error!'), e)
        states_prev.append(this.state)
        if not states_seq:
            report = 'Ready to be install'
            return this.write({'state':'install','messages':report, 'states_seq':states_seq, 'states_prev':states_prev}, context=context)
        else:
            state = states_seq.pop(0)
            return this.write({'state':state, 'states_seq':states_seq, 'states_prev':states_prev}, context=context)

    def createJeraAction(self, cr, uid, server, jera_config, act_profile, user_id, dd_action_id=False, context={}):
        action_data = self.pool.get(act_profile.action_id.type).read(cr, uid, act_profile.action_id.id, ['name','type','report_name'], context=context)
        del action_data['id']
        #user_id = False
        #if act_profile.user_id:
        #    jera_user = server.jera.getUser(jera_config.login, jera_config.password, act_profile.user_id.login)
        #    user_id = int(jera_user['id'])
        action_data.update({
            'action_id':act_profile.action_id.id,
            #'alias':act_profile.alias,
            'domain':act_profile.domain,
            'context':act_profile.context,
            'r_metainfo':act_profile.r_metainfo,
            'user_id':user_id,
            'searchable':act_profile.searchable,
            'search_area':act_profile.search_area,
            'dd_action_id':dd_action_id,
        })
        if act_profile.alias:
            action_data['alias'] = act_profile.alias
        return server.jera.createAction(jera_config.login, jera_config.password, action_data)

    def createJeraMenu(self, cr, uid, server, jera_config, menu_profile, user_id, act_id, dd_action_id=False, context={}):
        #user_id = False
        #if menu_profile.user_id:
        #    jera_user = server.jera.getUser(jera_config.login, jera_config.password, menu_profile.user_id.login)
        #    user_id = int(jera_user['id'])
        menu_data = {
            'menutype':'mainmenu',
            'name':menu_profile.name,
            'link':'index.php?option=com_jera&view=jera&layout=%s' % menu_profile.layout,
            'type':'component',
            'published':menu_profile.published,
            'access':menu_profile.access,
            'params':{
                    'id':act_id,
                    'user':user_id,
                    'dd_action_id':dd_action_id,
                    'dd_click':menu_profile.dd_click,
                    'show_search':menu_profile.show_search,
                    'custom_search_fields':menu_profile.custom_search_fields,
                },
            'home':False,
            'parent':False,

        }
        return server.jera.createMenuItem(jera_config.login, jera_config.password, menu_data)

    def createJeraModule(self, cr, uid, server, jera_config, module_profile, user_id, act_id, menu_ids_dict=[], context={}):
        menu_ids = []
        #user_id = False
        #if module_profile.user_id:
        #    jera_user = server.jera.getUser(jera_config.login, jera_config.password, module_profile.user_id.login)
        #    user_id = int(jera_user['id'])
        if module_profile.menus=='select' and module_profile.menu_ids:
            menu_ids = map(lambda mod: menu_ids_dict[mod.id], module_profile.menu_ids)
        module_data = {
            'module':'mod_jera',
            'client_id':0,
            'title':module_profile.name,
            'position':module_profile.position,
            'published':module_profile.published,
            'access':module_profile.access,
            'showtitle':module_profile.showtitle,
            'menus':module_profile.menus,
            'selections':menu_ids,
            'params':{
                    'id':act_id,
                    'user':user_id,
                    'layout':module_profile.layout,
                    'cache':module_profile.cache,
                    'cache_time':module_profile.cache_time,
                },

        }
        return server.jera.createModule(jera_config.login, jera_config.password, module_data)


    def process(self, cr, uid, ids, context={}):
        this = self.browse(cr, uid, ids[0], context=context)
        jera_config_obj = self.pool.get('jera.config')
        jera_config = jera_config_obj.browse(cr, uid, int(this.config), context=context)
        server = jera_config_obj.make_xmlrpc_object(jera_config.hostname, jera_config.port, jera_config.ssl, jera_config.handler)

        jera_users_dict = {0:False}
        jera_actions_dict = {0:False}
        jera_menus_dict = {0:False}
        try:
            context['jera_return'] = True
            for user_profile in this.jera_user_ids:
                if not user_profile.install:
                    continue
                user_data = {
                    'name':user_profile.name,
                    'user_id':user_profile.user_id.id,
                    'login':user_profile.login,
                    'password':user_profile.password,
                    'email':user_profile.email,
                    'config_id':int(this.config),
                }
                jera_user_id = self.pool.get('jera.users').create(cr, uid, user_data, context=context)
                if jera_user_id:
                    jera_users_dict[user_profile.realid] = jera_user_id
            for act_profile in this.jera_action_ids:
                if not act_profile.install:
                    continue
                user_id = False
                if act_profile.used_user=='anonymous':
                    jera_anonymous = server.jera.getUser(jera_config.login, jera_config.password, 'jera_anonymous')
                    user_id = jera_anonymous and jera_anonymous['id'] or False
                elif act_profile.used_user=='custom' and act_profile.user_id:
                    user_id = jera_users_dict.get(act_profile.user_id.id,False)
                dd_action_id = jera_actions_dict.get(int(act_profile.dd_action_id),False)
                jera_action_id = self.createJeraAction(cr, uid, server, jera_config, act_profile, user_id, dd_action_id, context=context)
                if jera_action_id:
                    jera_actions_dict[act_profile.realid] = jera_action_id
            for menu_profile in this.jera_menu_ids:
                if not menu_profile.install:
                    continue
                user_id = False
                if menu_profile.used_user=='anonymous':
                    jera_anonymous = server.jera.getUser(jera_config.login, jera_config.password, 'jera_anonymous')
                    user_id = jera_anonymous and jera_anonymous['id'] or False
                elif act_profile.used_user=='custom' and act_profile.user_id:
                    user_id = jera_users_dict.get(menu_profile.user_id.id,False)
                act_id = jera_actions_dict.get(int(menu_profile.action_id),False)
                dd_action_id = jera_actions_dict.get(int(menu_profile.dd_action_id),False)
                jera_menu_id = self.createJeraMenu(cr, uid, server, jera_config, menu_profile, user_id, act_id, dd_action_id, context=context)
                if jera_menu_id:
                    jera_menus_dict[menu_profile.realid] = jera_menu_id
            for module_profile in this.jera_module_ids:
                if not module_profile.install:
                    continue
                user_id = False
                if module_profile.used_user=='anonymous':
                    jera_anonymous = server.jera.getUser(jera_config.login, jera_config.password, 'jera_anonymous')
                    user_id = jera_anonymous and jera_anonymous['id'] or False
                elif act_profile.used_user=='custom' and act_profile.user_id:
                    user_id = jera_users_dict.get(module_profile.user_id.id,False)
                act_id = jera_actions_dict.get(int(module_profile.action_id),False)
                jera_module_id = self.createJeraModule(cr, uid, server, jera_config, module_profile, user_id, act_id, jera_menus_dict, context=context)

        except xmlrpclib.Fault, e:
            raise osv.except_osv(_("Error!"), _(e.faultString))
        except error, e:
            raise osv.except_osv(_("Error %s") % e.errno, _(e.strerror))

        return this.write({'state':'done','messages':'Installation complete'}, context=context)

jera_installer_action()

