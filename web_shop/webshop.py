# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2013 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
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

from osv import fields,osv
import netsvc
import time
import random
from tools.translate import _

class sale_shop(osv.osv):
    _name = 'sale.shop'
    _inherit = 'sale.shop'

    _columns = {
        'catalog_layout': fields.selection([('vertical_list',_('Vertical List')),
('grid',_('Grid'))], 'Catalog Layout', size=64, required=False, readonly=False, translate=False, help=''),
    }

    _defaults = {
        'catalog_layout': 'vertical_list',
    }

sale_shop()

class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'

    def jera_request_add_so_line(self, cr, uid, ids, context=None):
        """
        This function add sales order line.
        If need to define quentity then passed in the context "qty" value
        """
        so_obj = self.pool.get('sale.order')
        fpos_mod = self.pool.get('account.fiscal.position')
        wf_service = netsvc.LocalService("workflow")
        user = self.pool.get('res.users').browse(cr, 1, uid, context=context)
        if not user.address_id:
            raise osv.except_osv('Warning!', 'Cannot add sales order line. User has no address!')
        partner_id = user.address_id.partner_id.id

        domain = context.get('guest') and [('state','=','draft'),('origin','=',context.get('jera_sid'))] or \
            [('state','=','draft'),('partner_id','=',user.address_id.partner_id and user.address_id.partner_id.id),('origin','=',context.get('jera_sid'))]
        so_ids = so_obj.search(cr, uid, domain)
        if so_ids:
            so_id = so_ids[0]
            so = so_obj.browse(cr, uid, so_id, context=context)
            so_changes = so_obj.onchange_partner_id(cr, 1, so_ids, partner_id)['value']
            if so.partner_id!=partner_id:
                so_changes['partner_id'] = partner_id
            if so.user_id!=uid:
                so_changes['user_id'] = uid
            if so_changes:
                so.write(so_changes, context=context)
            for sol in so.order_line:
                if sol.product_id and sol.product_id.id in ids:
                    so.write({'order_line':[(1,sol.id,{'product_uom_qty':sol.product_uom_qty+context.get('qty',1)})]}, context=context)
                    return True
            line_vals = self.pool.get('sale.order.line').product_id_change(cr, 1, False, so.pricelist_id.id, ids[0], 1, partner_id=so.partner_id.id)['value']
            line_vals['product_uom_qty'] = context.get('qty',1)
            line_vals['product_id'] = ids[0]
            product = self.browse(cr, uid, line_vals['product_id'], context=context)
            taxes_ids = fpos_mod.map_tax(cr, 1, so.fiscal_position, product.taxes_id)
            line_vals['tax_id'] = [(6,0,taxes_ids)]

            so.write({'order_line':[(0,0,line_vals)]}, context=context)
        else:
            vals = so_obj.onchange_partner_id(cr, 1, so_ids, partner_id)['value']
            vals['shop_id'] = int(context.get('shop_id'))
            if vals['user_id']==uid:
                vals['user_id'] = False
            vals.update(so_obj.onchange_shop_id(cr, 1, so_ids, vals['shop_id'])['value'])
            vals['origin'] = context.get('jera_sid')
            if user.address_id.partner_id.name=='JERA Anonymous' or not vals['payment_term']:
                shop = self.pool.get('sale.shop').browse(cr, uid, vals['shop_id'], context=context)
                vals['payment_term'] = shop.payment_default_id.id
            if user.address_id.partner_id.name!='JERA Anonymous' and \
                    'section_id' in so_obj._columns.keys() and 'section_id' in user.address_id.partner_id._columns.keys():
                vals['section_id'] = user.address_id.partner_id.section_id
            vals['partner_id'] = partner_id
            vals['user_id'] = uid
            vals['order_policy'] = 'prepaid'
            line_vals = self.pool.get('sale.order.line').product_id_change(cr, 1, False, vals['pricelist_id'], ids[0], 1, partner_id=vals['partner_id'])['value']
            line_vals['product_uom_qty'] = context.get('qty',1)
            line_vals['product_id'] = ids[0]
            product = self.browse(cr, uid, line_vals['product_id'], context=context)
            fiscal_position = vals['fiscal_position'] and fpos_mod.browse(cr, 1, vals['fiscal_position'], context=context) or False
            taxes_ids = fpos_mod.map_tax(cr, 1, fiscal_position, product.taxes_id)
            line_vals['tax_id'] = [(6,0,taxes_ids)]

            vals['order_line'] = [(0,0,line_vals)]
            so_id = so_obj.create(cr, uid, vals, context=context)
        return True

    def jera_request_remove_so_line(self, cr, uid, ids, context=None):
        so_line_obj = self.pool.get('sale.order.line')
        order = so_line_obj.browse(cr, uid, ids[0], context=context).order_id
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if context['jera_sid']!=order.origin:
            raise osv.except_osv('Access Error!', 'You can not delete this item!') 
        all_so_line_ids = map(int, order.order_line)
        so_line_obj.unlink(cr, uid, ids, context=context)
        if not bool(set(all_so_line_ids).difference(set(ids))):
            self.pool.get('sale.order').unlink(cr, uid, [order.id], context=context)
            return True
        return True
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context={}, count=False):
        uri = context.get('uri', {})
        sttime = time.time()
        brand_id = uri.get('brand_id','').isdigit() and int(uri.get('brand_id')) or False
        categ_id = uri.get('categ_id','').isdigit() and int(uri.get('categ_id')) or False
        if not categ_id and context.get('default_categ_id'):
            categ_id = context.get('default_categ_id') > 0 and context.get('default_categ_id') or False
        if categ_id:
            categ_mod = self.pool.get('product.sales_category')
            sale_categs = categ_mod.search(cr, 1, [('id', 'child_of', [categ_id])])
            args += categ_id and ['|',('prim_sales_category_id', 'in', sale_categs), ('sales_category_ids', 'in', sale_categs)] or []
        args += brand_id and [('brandname', '=', brand_id)] or []
        res = super(product_product, self).search(cr, 1, args, offset, limit, order, context, count)
        orderby = uri.get('order_by');
        if orderby and res:
            orderlist = orderby and orderby.split(',') or False
            orderclean = []
            for field_bit in orderlist:
                order_item = field_bit.split('.')
                field = len(order_item) >= 1 and order_item[0] or False
                order = len(order_item) == 2 and order_item[1].upper() in ['ASC','DESC'] and order_item[1].upper() or 'ASC'
                if field:
                    orderclean.append({'field':field, 'order':order})
            for order_item in orderclean:
                if order_item.get('field') == 'listprice':
                    position_id = False
                    pricelist_id = False
                    user_mod = self.pool.get('res.users')
                    shop_mod = self.pool.get('sale.shop')
                    shop_obj = shop_mod.browse(cr, 1, context.get('shop_id'))
                    if not context.get('guest'):
                        partner_id = user.address_id.partner_id
                        pricelist_id = partner_id.property_product_pricelist and partner_id.property_product_pricelist.id or None
                        position_id = partner_id.property_account_position and partner_id.property_account_position.id or None
                    if not position_id:
                        position_id = shop_obj.position_default_id and shop_obj.position_default_id.id or None
                    if not pricelist_id:
                        pricelist_id = shop_obj.pricelist_id and shop_obj.pricelist_id.id or None
                    if pricelist_id:
                        cr.execute('SELECT product_id \
                        FROM product_listprice_cache \
                        WHERE product_id IN %s \
                        AND pricelist_id = %s \
                        AND position_id IS NOT DISTINCT FROM %s \
                        AND date_valid IS NULL \
                        ORDER BY price ' + order_item.get('order'),
                        (tuple(res), pricelist_id, position_id))
                        res = [ seq[0] for seq in cr.fetchall() ]
        return res
        
product_product()

class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'

    def jera_request_set_active(self, cr, uid, ids, context=None):
        current_active = self.search(cr, uid, [('origin','=',context.get('jera_sid')),('origin','<>',False)], context=context)
        if current_active:
            self.write(cr, uid, current_active, {'origin':False}, context=context)
        self.write(cr, uid, ids, {'origin':context.get('jera_sid')}, context=context)
        return True

    def change_origin_by_sid(self, cr, uid, sid, new_origin, username, context=None):
        user_obj = self.pool.get('res.users')
        jera_user_obj = self.pool.get('jera.users')
        user = user_obj.browse(cr, uid, uid)
        if user.login=='jera_service':
            jera_user_ids = jera_user_obj.search(cr, uid, [('login','=',username)])
            if jera_user_ids:
                ids = self.search(cr, 1, [('origin','=',sid),('partner_id.ref','=','JERA')], context=context)
                if ids:
                    change_user = jera_user_obj.browse(cr, uid, jera_user_ids[0])
                    change_value = self.onchange_partner_id(cr, 1, ids[0], change_user.user_id.address_id.partner_id.id)['value']
                    change_value['partner_id'] = change_user.user_id.address_id.partner_id.id
                    change_value['origin'] = new_origin
                    self.write(cr, 1, ids, change_value, context=context)
                return ids
            else:
                return -2
        else:
            return -1

sale_order()

class webshop_checkout(osv.osv_memory):
    _name = 'webshop.checkout'
    _description = 'Checkout'

    def default_get(self, cr, uid, fields, context=None):
        data = super(webshop_checkout, self).default_get(cr, uid, fields, context=context)
        states_seq = context.get('states_seq',[])
        if not states_seq:
            return data
        order_obj = self.pool.get('sale.order')
        user = self.pool.get('res.users').browse(cr, 1, uid, context=context)
        domain = context.get('guest') and [('state','=','draft'),('origin','=',context.get('jera_sid'))] or \
            [('state','=','draft'),('partner_id','=',user.address_id.partner_id and user.address_id.partner_id.id)]
        order_id = order_obj.search(cr, uid, domain, context=context)
        if order_id:
            order = order_obj.browse(cr, 1, order_id[0], context=context)
            if not filter(lambda line: line.product_id and line.product_id.type!='service', order.order_line):
                if 'shipp_info' in states_seq:
                    states_seq.pop(states_seq.index('shipp_info'))
                if 'shipp_method' in states_seq:
                    states_seq.pop(states_seq.index('shipp_method'))
            state = states_seq.pop(0)
            if not context.get('guest') and state=='method':
                state = states_seq.pop(0)
            if not context.get('guest') and state=='bill_info':
                customer = order.partner_id
                if order_id and customer.ref!="JERA" and user.address_id.partner_id.ref!="JERA":
                    state = states_seq and states_seq.pop(0) or 'done'
            if not context.get('guest') and state=='bill_company':
                if order_id and customer.ref!="JERA" and user.address_id.partner_id.ref!="JERA":
                    state = states_seq and states_seq.pop(0) or 'done'
            data['so_id'] = order_id[0]
            data['state'] = state
            data['states_seq'] = states_seq # this field will be as list
            data['states_prev'] = [] # this field will be as list
        else:
            data['so_id'] = False
            data['state'] = 'stop'
            data['states_seq'] = []
            data['states_prev'] = []
        return data

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        res = super(webshop_checkout, self).read(cr, uid, ids, fields, context)
        if 'so_id' in fields:
            os_obj = self.pool.get('sale.order')
            if type(res)==list:
                for r in res:
                    if r['so_id'] and not os_obj.search(cr, uid, [('id','=',r['so_id'][0])], context=context):
                        r['so_id'] = False
                        r['state'] = 'stop'
            else:
                if res['so_id'] and not os_obj.search(cr, uid, [('id','=',res['so_id'][0])], context=context):
                    res['so_id'] = False
                    res['state'] = 'stop'
        return res

    def _delivery_variants(self, cr, uid, context={}):
        active_id = context.get('active_id', False)
        carrier_obj = self.pool.get('delivery.carrier')
        grid_obj=self.pool.get('delivery.grid')
        ids = carrier_obj.search(cr, uid, [], context=context)
        res = []
        if active_id and self.exists(cr, uid, active_id):
            this = self.browse(cr, uid, active_id, context=context)
            user = self.pool.get('res.users').browse(cr, 1, uid, context=context)
            if this.is_shipping_address:
                prefix = ""
                delivery_address = context.get('guest') and this or user.address_id
            else:
                prefix = "shipping_"
                delivery_address = this
            def grid_get(ids, this, order):
                for carrier in carrier_obj.browse(cr, uid, ids, context=context):
                    for grid in carrier.grids_id:
                        country_ids = map(lambda g: g.id, grid.country_ids)
                        if country_ids and not getattr(this, prefix+"country_id").id in country_ids:
                            continue
                        if grid.zip_from and (getattr(this, prefix+"zip") or '')< grid.zip_from:
                            continue
                        if grid.zip_to and (getattr(this, prefix+"zip") or '')> grid.zip_to:
                            continue
                        yield grid.id, carrier.name, grid_obj.get_price(cr, uid, grid.id, order, time.strftime('%Y-%m-%d'), context)

            domain = context.get('guest') and [('state','=','draft'),('origin','=',context.get('jera_sid'))] or \
                    [('state','=','draft'),('partner_id','=',user.address_id.partner_id and user.address_id.partner_id.id)]
            order_id = self.pool.get('sale.order').search(cr, uid, domain, context=context)
            if order_id:
                context['order_id'] = order_id[0]

                order = self.pool.get('sale.order').browse(cr, uid, order_id[0], context=context)
                currency = order.pricelist_id.currency_id.name or ''
                carrier_grids = list(grid_get(ids, delivery_address, order))
                
                res = [(r[0], r[1]+' ('+(str(r[2]))+' '+currency+')') for r in carrier_grids]

        return res
    
    _columns = {
        'name':fields.char('Last Name', size=64),
        'first_name':fields.char('First Name', size=64),
        'company_name':fields.char('Company', size=64),
        'email': fields.char('E-Mail', size=240),
        'address': fields.char('Street', size=128),
        'city': fields.char('City', size=128),
        'zip': fields.char('Zip', size=24),
        'ref':fields.char('Reference', size=64),
        'vat':fields.char('VAT', size=32),
        'country_id': fields.many2one('res.country', 'Country'),
        'phone': fields.char('Phone', size=64),
        'fax': fields.char('Fax', size=64),
        'method':fields.selection([
            ('guest','Checkout as Guest'),
            ('login','Already registered'),
            ('register','Register'),
            
        ],'Checkout Method'),
        'is_shipping_address':fields.boolean('Same as billing address'),
        'shipping_name':fields.char('Last Name', size=64),
        'shipping_first_name':fields.char('First Name', size=64),
        'shipping_address': fields.char('Street', size=128),
        'shipping_country_id': fields.many2one('res.country', 'Country'),
        'shipping_city': fields.char('City', size=128),
        'shipping_zip': fields.char('Zip', size=24),
        'shipping_phone': fields.char('Phone', size=64),
        'carrier_id': fields.selection(_delivery_variants, 'Delivery Method'),
        'so_id': fields.many2one('sale.order', 'Sale Order'),

        'state':fields.selection([
            ('method','Checkout Method'),
            ('register','Register'),
            ('bill_info','Billing Inforamtion'),
            ('bill_company','Billing Company'),
            ('shipp_info','Shipping Information'),
            ('shipp_method','Shipping Method'),
            ('pay_info','Payment Information'),
            ('done','Done'),
            ('stop','Stop'),
            
        ],'State', select=True, readonly=True),
        'states_seq':fields.serialized('Next states sequence'),
        'states_prev':fields.serialized('Previous states sequence'),
        
    }

    def _set_random_password(self, cr, uid, user_id):
        user_obj = self.pool.get('res.users')
        jera_users_obj = self.pool.get('jera.users')
        user = user_obj.browse(cr, uid, user_id)
        if not user.password:
            password = ''.join(map(chr, random.sample(jera_users_obj._PASSWORD_CHARS, jera_users_obj._PASSWORD_LENGTH)))
            user.write({'password':password})
        return True

    def confirm(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0], context=context)
        this.so_id
        states_prev = this.states_prev
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, 1, uid, context=context)
        address_obj = self.pool.get('res.partner.address')
        grid_obj = self.pool.get('delivery.grid')
        order_obj = self.pool.get('sale.order')
        domain = context.get('guest') and [('state','=','draft'),('origin','=',context.get('jera_sid'))] or \
                [('state','=','draft'),('partner_id','=',user.address_id.partner_id and user.address_id.partner_id.id)]
        order_id = order_obj.search(cr, uid, domain, context=context)
        if order_id:
            lang = context.get('lang','en_US')
            lang_id = self.pool.get('res.lang').search(cr, uid, [('code','=',lang)], context=context)
            web_shop_admin_id = user_obj.search(cr, 1, [('login','=','web_shop_admin')], context=context)[0] # get web shop administrator Id
            order = order_obj.browse(cr, uid, order_id[0], context=context)
            partner_id = order.partner_id.id
            if 'bill_info' in states_prev:
                address = {
                    'street':this.address,
                    'country_id':this.country_id and this.country_id.id or False,
                    'company_id':False,
                    'phone':this.phone,
                    'fax':this.fax,
                    'email':this.email,
                    'city':this.city,
                    'zip':this.zip,
                    'type':'default',
                }
                address_id = address_obj.create(cr, web_shop_admin_id, address, context=context)
                partner_name = this.company_name or this.first_name+' '+this.name
                partner_id = self.pool.get('res.partner').create(cr, web_shop_admin_id, {
                                                            'name':partner_name,
                                                            'ref':this.ref,
                                                            'vat':this.vat,
                                                            'company_id':False,
                                                            'address':[(6,0,[address_id])],
                                                            'lang':lang,
                                                            'property_payment_term':order.shop_id.payment_default_id.id,
                                                            'property_product_pricelist':order.shop_id.pricelist_id.id,
                                                        }, context=context)
                change_value = order_obj.onchange_partner_id(cr, 1, order_id, partner_id)['value']
                change_value['partner_id'] = partner_id
                order_obj.write(cr, uid, order_id, change_value, context=context)
                if context.get('guest'):
                    jera_users_obj = self.pool.get('jera.users')
                    config_id = self.pool.get('jera.config').search(cr, web_shop_admin_id, [('hostname','=',context['jera_host'])], context=context, limit=1)
                    if config_id:
                        config_id =  config_id[0]
                        config = self.pool.get('jera.config').read(cr, web_shop_admin_id, config_id, ['trans_login','group_ids','company_id'], context=context, load="_classic_write")
                        trans_login = config['trans_login']
                        login = ''.join(map(chr,random.sample(range(65,91)+range(97,122),8)))
                        password = ''.join(map(chr,random.sample(jera_users_obj._PASSWORD_CHARS,8)))
                        user_id = user_obj.create(cr, 1, {'name':partner_name,
                                                  'login':login,
                                                  'password':trans_login and password or \
                                                    ''.join(map(chr, random.sample(jera_users_obj._PASSWORD_CHARS, jera_users_obj._PASSWORD_LENGTH))),
                                                  'groups_id':[(6,0,config['group_ids'])],
                                                  'company_id':config['company_id'],
                                                  'context_lang':lang,
                                                  'address_id':address_id,
                                                  'active':False}, context=context)

                        confirm_hash = self.pool.get('captcha.captcha').gen_random_code(32)
                        ctx = context.copy()
                        ctx['auto'] = True
                        juser_id = jera_users_obj.create(cr, web_shop_admin_id, {'name':partner_name,
                                                  'login':login,
                                                  'password':password,
                                                  'user_id':user_id,
                                                  'hash':confirm_hash,
                                                  'email':this.email,
                                                  'config_id':config_id}, context=ctx)
                        self.pool.get('jera.register')._send_email(cr, uid, juser_id, this.email, confirm_hash, context=context) # E-mail sending

            elif not context.get('guest'):
                if order.partner_id.id!=user.address_id.partner_id.id:
                    change_value = order_obj.onchange_partner_id(cr, 1, order_id, user.address_id.partner_id.id)['value']
                    change_value['partner_id'] = user.address_id.partner_id.id
                    order.write(change_value, context=context)
            if 'shipp_info' in states_prev:
                if not this.is_shipping_address:
                    ship_address = {
                        'partner_id':partner_id,
                        'street':this.shipping_address,
                        'country_id':this.shipping_country_id.id,
                        'city':this.shipping_city,
                        'zip':this.shipping_zip,
                        'company_id':False,
                        'phone':this.shipping_phone,
                        'type':'delivery',
                    }
                    ship_address_id = address_obj.create(cr, web_shop_admin_id, ship_address, context=context)
                elif context.get('guest'):
                    ship_address = {
                        'street':this.address,
                        'country_id':this.country_id and this.country_id.id or False,
                        'city':this.city,
                        'zip':this.zip,
                        'phone':this.phone,
                    }
                    address_obj.write(cr, web_shop_admin_id, address_id, ship_address, context=context)
                    ship_address_id = address_id
                else:
                    ship_address_id = user.address_id.id

                change_value = order_obj.onchange_partner_id(cr, 1, order_id, partner_id)['value']
                change_value['partner_id'] = partner_id
                order_obj.write(cr, uid, order_id, change_value, context=context)

                if ship_address_id and this.carrier_id:
                    carrier_obj = self.pool.get('delivery.carrier')
                    ##### Search already added delivery methods and then delete them #####
                    carrier_ids = carrier_obj.search(cr, uid, [], context=context)
                    carrier_products = carrier_obj.read(cr, uid, carrier_ids, ['product_id'], context=context, load="_classic_write")
                    carrier_product_ids = map(lambda p: p['product_id'], carrier_products)
                    for sol in order.order_line:
                        if sol.product_id.id in carrier_product_ids:
                            sol.unlink(context=context)
                    order = order_obj.browse(cr, uid, order_id[0], context=context)
                    ####################################################################
                    grid_id = carrier_obj.grid_get(cr, 1, [this.carrier_id],ship_address_id)
                    if not grid_id:
                        raise osv.except_osv('Invalid action!', 'No delivery grid found!')
                    grid = grid_obj.browse(cr, uid, grid_id, context=context)
                    taxes = grid.carrier_id.product_id.taxes_id
                    fpos = order.fiscal_position or False
                    taxes_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes)
                    self.pool.get('sale.order.line').create(cr, uid, {
                        'order_id': order_id[0],
                        'name': grid.carrier_id.name,
                        'product_uom_qty': 1,
                        'product_uom': grid.carrier_id.product_id.uom_id.id,
                        'product_id': grid.carrier_id.product_id.id,
                        'price_unit': grid_obj.get_price(cr, uid, grid.id, order, time.strftime('%Y-%m-%d'), context),
                        'tax_id': [(6,0,taxes_ids)],
                        'type': 'make_to_stock',
                        'sequence':1000,
                    })
            return self.pool.get('payment.agency.config').confirm_order(cr, uid, order_id[0], context=context)
        else:
            raise osv.except_osv('Invalid action!', 'No sales order found!')
        return False

    def jera_request_action_next(self, cr, uid, ids, context={}):
        this = self.browse(cr, uid, ids[0], context=context)
        this.so_id
        states_prev = this.states_prev
        states_seq = this.states_seq
        to_write = {}
        if this.state=='shipp_method':
            if not this.carrier_id:
                raise osv.except_osv('Warning!', 'Please select delivery method.')
        if not states_seq and this.state!='done':
            states_prev.append(this.state)
            to_write['state'] = 'done'
            to_write['states_prev'] = states_prev
            return this.write(to_write, context=context)
        if not states_seq and this.state=='done':
            return self.confirm(cr, uid, ids, context=context)
        else:
            states_prev.append(this.state)
            next_state = states_seq.pop(0)
            if next_state=='bill_info':
                if not context.get('guest'):
                    user = self.pool.get('res.users').browse(cr, 1, uid, context=context)
                    domain = context.get('guest') and [('state','=','draft'),('origin','=',context.get('jera_sid'))] or \
                            [('state','=','draft'),('partner_id','=',user.address_id.partner_id and user.address_id.partner_id.id)]
                    order_obj = self.pool.get('sale.order')
                    order_id = order_obj.search(cr, uid, domain, context=context)
                    if order_id and order_obj.browse(cr, uid, order_id[0], context=context).partner_id.ref!="JERA":
                        next_state = states_seq.pop(0)
            if next_state=='shipp_method':
                context['active_id'] = ids[0]
                if not self.fields_get(cr, uid, 'carrier_id', context=context)['carrier_id']['selection']:
                    states_prev.pop()
                    states_seq.append(next_state)
                    raise osv.except_osv('Warning!', 'Order cannot be delivered to this address! Please check Country and/or Zip.')
            if this.state=='method' and this.method=='login':
                to_write['state'] = next_state
                to_write['states_prev'] = states_prev
                to_write['states_seq'] = states_seq
                this.write(to_write, context=context)
                return 'force_login;new_record'
            if this.state=='method' and this.method=='register':
                mod_obj = self.pool.get('ir.model.data')
                act_obj = self.pool.get('ir.actions.act_window')
                ref = mod_obj.get_object_reference(cr, uid, 'jera_register', 'action_jera_users_wizard')
                id = ref and ref[1] or False
                act_win = act_obj.read(cr, uid, [id])[0]
                return act_win

            to_write['states_prev'] = states_prev
            to_write['states_seq'] = states_seq
            to_write['state'] = next_state
            return this.write(to_write, context=context)

    def jera_request_action_back(self, cr, uid, ids, context={}):
        this = self.browse(cr, uid, ids[0], context=context)
        this.so_id
        if this.states_prev:
            prior_state = this.states_prev.pop()
            this.states_seq.insert(0,this.state)
            to_write = {'state':prior_state,'states_seq':this.states_seq,'states_prev':this.states_prev}
            return this.write(to_write, context=context)
        return True

    _defaults = {
        'state': 'checkout_method',
        'states_seq': [],
        'states_prev': [],
        'method':'guest',
    }

webshop_checkout()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

