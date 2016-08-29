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
import xmlrpclib
from socket import error
import md5
import random
from tools.translate import _

class jera_user_mirror_wizard(osv.osv_memory):
    _name = 'jera.user_mirror_wizard'
    _description = 'Copy user from OpenERP to Joomla'
    _rec_name = 'user_id'

    def _get_configs(self, cr, uid, context={}):
        obj = self.pool.get('jera.config')
        ids = obj.search(cr, uid, [])
        configs = obj.read(cr, uid, ids, ['name', 'hostname'], context)
        return [(r['id'], r['name'] or r['hostname']) for r in configs]

    def change_user(self, cr, uid, ids, user_id):
        data = {}
        if not user_id:
            return {'value':{}}

        data['email'] = self.pool.get('res.users').read(cr, uid, user_id, ['user_email'])['user_email']
        return {'value':data}

    _columns = {
        'user_id':fields.many2one('res.users', 'User', required=True),
        'new_password':fields.char('New Password', size=32),
        'email':fields.char('Email', size=128, required=True),
        'state':fields.selection([
            ('draft','Draft'),
            ('done','Done'),
            
        ],'State', select=True, readonly=True),
        'note': fields.text('Notes'),
        'config': fields.selection(_get_configs, 'Site'),
        
    }

    def gen_random_code(self, length=5):
        allowed_symbols = "23456789abcdegifjkpqsvxyz"
        char_range = map(lambda a: ord(a), allowed_symbols)
        password = ''
        random.seed()
        while(length):
            password += chr(random.choice(char_range))
            length -= 1
        return password

    def mirror_user(self, cr, uid, ids, context=None):
        jera_user_obj = self.pool.get('jera.users')
        this = self.browse(cr, uid, ids)[0]
        password = this.new_password or this.user_id.password
        juser_data = {'login':this.user_id.login,
                      'password':password,
                      'user_id':this.user_id.id,
                      'email':this.email,
                      'config_id': this.config
                     }

        ctx = context.copy()
        ctx['auto'] = True
        juser_id = jera_user_obj.create(cr, uid, juser_data, context=ctx)
        self.write(cr, uid, ids, {'state':'done','note':'The user "%s" is successfully copied to Joomla and ready for use.' % this.user_id.name}, context=context)
        
        return True

    def back(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft','user_id':False,'new_password':False,'email':False,'note':False}, context=context)
        return True

    _defaults = {
        'state': 'draft',
    }

jera_user_mirror_wizard()

