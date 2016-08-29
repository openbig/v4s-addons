# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2013 Alistek Ltd. (http://www.alistek.com) All Rights Reserved.
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
# as published by the Free Software Foundation; either version 3
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
from tools.translate import _

from PIL import Image
import base64
import StringIO
import md5

class sale_shop(osv.osv):
    _name = 'sale.shop'
    _inherit = 'sale.shop'

    _columns = {
        'available_products': fields.selection([('sel_and_all',_('Selected and Other Products')),
('sel_only',_('Selected Products Only'))], 'Available Products', size=64, required=False, readonly=False, translate=False, help=''),
        'position_default_id': fields.many2one('account.fiscal.position', 'Default Fiscal Position', domain="[('company_id','in',('company_id', False))]", ondelete='set null', required=False, readonly=False, help='Default fiscal position for anonymous price calculations with included taxes.'),
    }

    _defaults = {
        'available_products': 'sel_and_all',
    }

sale_shop()

class product_image(osv.osv):
    '''Product Image'''
    _name = 'product.image'
    _description = "Product Image"

    def _get_params(self, cr, uid, ids, fields, arg=None, context={}):
        res = {}
        #return res
        for p in self.browse(cr, uid, ids, context):
            record_template = { 'thumb_size_x': -1,
                                'thumb_size_y': -1,
                                'midsize_size_x': -1,
                                'midsize_size_y': -1,
                                'large_size_x': -1,
                                'large_size_y': -1,
                                'fullscale_size_x': -1,
                                'fullscale_size_y': -1 }
            imgbuf = p.image_thumb
            if imgbuf:
                img = Image.open(StringIO.StringIO(base64.decodestring(imgbuf)))
                record_template['thumb_size_x'], record_template['thumb_size_y'] = img.size
                del img
            imgbuf = p.image_midsize
            if imgbuf:
                img = Image.open(StringIO.StringIO(base64.decodestring(imgbuf)))
                record_template['midsize_size_x'], record_template['midsize_size_y'] = img.size
                del img
            imgbuf = p.image_large
            if imgbuf:
                img = Image.open(StringIO.StringIO(base64.decodestring(imgbuf)))
                record_template['large_size_x'], record_template['large_size_y'] = img.size
                del img
            imgbuf = p.image_fullscale
            if imgbuf:
                img = Image.open(StringIO.StringIO(base64.decodestring(imgbuf)))
                record_template['fullscale_size_x'], record_template['fullscale_size_y'] = img.size
                del img
            res[p.id] = record_template
    #            if not self.pool.get(p.object._table_name).search(cr, uid, [('id','=',p.object.id)]):
    #                res[p.id]['name'] = _('Error')+'! '+_('No value')
    #                res[p.id]['state'] = False
    #            else:
    #                name = p.object and p.object.name_get(context=context) or False
    #                res[p.id]['name'] = name and name[0][1] or _('Value can not display')
        return res

    def _generate(self, cr, uid, img_id=False, vals={}, context=None):
        def process_image(source_image, size_x, size_y):
            thumbnail = source_image.copy()
            thumbnail.thumbnail([size_x,size_y], Image.ANTIALIAS)
            output = StringIO.StringIO()
            thumbnail.save(output, source_image.format, quality=90)
            return  base64.encodestring(output.getvalue())
        
        if img_id:
            p = self.browse(cr, uid, img_id, context)
            image_fullscale = vals.get('image_fullscale') or p.image_fullscale or False
            thumb_gen = p.thumb_gen
            midsize_gen = p.midsize_gen
            large_gen = p.large_gen
        else:
            image_fullscale = vals.get('image_fullscale')
            thumb_gen = vals.get('thumb_gen', True)
            midsize_gen = vals.get('midsize_gen', True)
            large_gen = vals.get('large_gen', True)
        if not image_fullscale: return vals
        data = base64.decodestring(image_fullscale)
        img = Image.open(StringIO.StringIO(data))
        vals['fullscale_md5'] = md5.new(data).hexdigest()
        if thumb_gen:
            vals['image_thumb'] = process_image(img, 75, 75)
        if midsize_gen:
            vals['image_midsize'] = process_image(img, 120, 120)
        if large_gen:
            vals['image_large'] = process_image(img, 300, 300)
        return vals

    def on_change_image(self, cr, uid, id, field_changed, image_data, context=None):
        res = {}
        if image_data:
            data = base64.decodestring(image_data)
            try:
                img = Image.open(StringIO.StringIO(data))
            except IOError, e:
                raise osv.except_osv(_('Input error!'), e)
            res[field_changed+'_size_x'], res[field_changed+'_size_y'] = img.size
        else:
            res[field_changed+'_size_x'] = res[field_changed+'_size_y'] = -1
        return {'value':res}

    def write(self, cr, uid, ids, vals, context=None):
        for img_id in ids:
            vals = self._generate(cr, uid, img_id, vals, context)
            for image in ['fullscale', 'large', 'midsize', 'thumb']:
                size = self.on_change_image(cr, uid, ids, image, vals.get('image_'+image), context)
                vals.update(size['value'])
            res = super(product_image, self).write(cr, uid, ids, vals, context)
        return res

    def create(self, cr, uid, vals, context={}):
        vals = self._generate(cr, uid, False, vals, context)
        for image in ['fullscale', 'large', 'midsize', 'thumb']:
            size = self.on_change_image(cr, uid, False, image, vals.get('image_'+image), context)
            vals.update(size['value'])
        res_id = super(product_image, self).create(cr, uid, vals, context)
        return res_id

    def _regenerate(self, cr, uid, context={}):
        ids = self.search(cr, uid, [], context=context)
        self.write(cr, uid, ids, {}, context=context)
        return True

    _columns = {
        'image_thumb': fields.binary('Thumbnail Image', required=False, readonly=False, help=''),
        'image_midsize': fields.binary('Midsize Image', required=False, readonly=False, help=''),
        'image_fullscale': fields.binary('Full Scale Image', required=False, readonly=False, help=''),
        'product_id': fields.many2one('product.product', 'Product', domain="[]", ondelete='set null', required=False, readonly=False, help='', select=True),
        'sequence': fields.integer('Sequence', required=False, readonly=False, help=''),
        'autocreated': fields.boolean('Autocreated', readonly=False, help='Designates, that whole record is generated automatically or imported from external data source.'),
        'thumb_gen': fields.boolean('Auto Generate', readonly=False, help='Designates, that thumbnail to be generated from higher resolution image if available.'),
        'midsize_gen': fields.boolean('Auto Generate', readonly=False, help='Designates, that midsized image to be generated from higher resolution image if available.'),
        'thumb_size_x': fields.integer('Width', required=False, readonly=True, help=''),
        'thumb_size_y': fields.integer('Height', required=False, readonly=True, help=''),
        'midsize_size_x': fields.integer('Width', required=False, readonly=True, help=''),
        'midsize_size_y': fields.integer('Height', required=False, readonly=True, help=''),
        'fullscale_size_x': fields.integer('Width', required=False, readonly=True, help=''),
        'fullscale_size_y': fields.integer('Height', required=False, readonly=True, help=''),
        'fullscale_md5': fields.char('MD5 (Fullscale)', size=32, required=False, readonly=False, translate=False, help='', select=True),
        'image_large': fields.binary('Large Image', required=False, readonly=False, help=''),
        'large_size_x': fields.integer('Width', required=False, readonly=True, help=''),
        'large_size_y': fields.integer('Height', required=False, readonly=True, help=''),
        'large_gen': fields.boolean('Auto Generate', readonly=False, help=''),
    }

    _defaults = {
        'midsize_gen': lambda *a: True,
        'large_gen': lambda *a: True,
        'thumb_gen': lambda *a: True,
        'sequence': lambda *a: 99,
    }

product_image()

class product_brandname(osv.osv):
    '''Brandname'''
    _name = 'product.brandname'
    _description = "Brandname"

    _columns = {
        'name': fields.char('Name', size=128, required=True, readonly=False, translate=True, help='', select=True),
        'code': fields.char('Code', size=16, required=False, readonly=False, translate=False, help='', select=True),
        'logo_image': fields.binary('Logo', required=False, readonly=False, help=''),
    }

product_brandname()

class product_sales_category(osv.osv):
    '''Sale Categories'''
    _name = 'product.sales_category'
    _description = "Sale Categories"
    _parent_name = 'parent_id'

    _columns = {
        'name': fields.char('Name', size=256, required=True, readonly=False, translate=True, help=''),
        'parent_id': fields.many2one('product.sales_category', 'Parent Category', domain="[]", ondelete='cascade', required=False, readonly=False, help=''),
        'description': fields.text('Description', readonly=False, translate=True, help=''),
        'publish': fields.boolean('Publish', readonly=False, help=''),
        'type': fields.selection([('normal',_('Normal')),
('view',_('View'))], 'Type', size=64, required=False, readonly=False, translate=False, help=''),
    }

    _defaults = {
        'publish': lambda *a: True,
    }

product_sales_category()

class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context={}, count=False):
        shop_id = context and context.get('shop',context.get('shop_id',False)) or False
        if shop_id:
            available_products = self.pool.get('sale.shop').read(cr, 1, shop_id, ['available_products'], context=context)['available_products']
            if available_products=='sel_only':
                domain = [('shop_ids', 'in', [shop_id])]
            elif available_products=='sel_and_all':
                domain = ['|',('shop_ids', '=', shop_id),('shop_ids', '=', False)]
            args.extend(domain)
    
        res = super(product_product, self).search(cr, uid, args, offset, limit, order, context, count)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
        records = self.read(cr, uid, ids, \
                ['to_recalc_price_cache','sale_ok'], context=context)
        if 'sale_ok' not in vals:
            sale_ok_ids = [r['id'] for r in records if r['sale_ok']]
        elif vals['sale_ok']:
            sale_ok_ids = ids
        else:
            return super(product_product, self).write(cr, uid, ids, vals, context)
        if 'to_recalc_price_cache' in vals and not vals['to_recalc_price_cache']:
            return super(product_product, self).write(cr, uid, ids, vals, context)
        check_fields = [
            'categ_id',
            'standard_price',
            'list_price',
            'price_margin',
            'price_extra',
            'uos_id',
            'uom_id',
            'uos_coeff',
            'company_id',
        ]
        ids_remaind = ids
        is_changed = set(check_fields)-set(vals.keys())!=set(check_fields)
        if (vals.get('sale_ok') or is_changed) and sale_ok_ids:
            vals_copy = vals.copy()
            vals_copy['to_recalc_price_cache'] = True
            super(product_product, self) \
                    .write(cr, uid, sale_ok_ids, vals_copy, context)
            ids_remaind = list(set(ids)-set(sale_ok_ids))
        if ids_remaind:
            super(product_product, self) \
                    .write(cr, uid, ids_remaind, vals, context)
        return True

    def _deferred_price_recalculation(self, cr, uid, context={}):
        pp_cache_obj = self.pool.get('product.listprice_cache')
        ids_to_recalc = self.search(cr, uid, [('to_recalc_price_cache','=',True)], context=context)
        products = self.browse(cr, uid, ids_to_recalc, context=context)
        pricelist_ids = self.pool.get('product.pricelist').search(cr, uid, [('type','=','sale')], context=context)
        position_ids = self.pool.get('account.fiscal.position').search(cr, uid, [], context=context)

        for pricelist_id in pricelist_ids:
            for position_id in position_ids:
                pp_cache_obj.price_batch_recalc(cr, uid, products, pricelist_id, position_id, context=context)
        self.write(cr, uid, ids_to_recalc, {'to_recalc_price_cache':False}, context=context)
        return True

    _columns = {
        'image_ids': fields.one2many('product.image', 'product_id', 'Product Images', readonly=False, help=''),
        'brandname': fields.many2one('product.brandname', 'Brandname', domain="[]", ondelete='set null', required=False, readonly=False, help=''),
        'shop_ids': fields.many2many('sale.shop', 'sale_shop_product_product_rel', 'product_product1_id', 'sale_shop2_id', 'Shops', domain="[]", readonly=False, help=''),
        'prim_sales_category_id': fields.many2one('product.sales_category', 'Primary Sales Category', domain="[('type', '=', 'normal')]", ondelete='set null', required=False, readonly=False, help=''),
        'sales_category_ids': fields.many2many('product.sales_category', 'product_sales_category_product_product_rel', 'product_product1_id', 'product_sales_category2_id', 'Additional Sales Categories', oldname='oth_sales_category_id', domain="[('type', '=', 'normal')]", readonly=False, help=''),
        'cross_selling_product_ids': fields.many2many('product.product', 'cross_selling_product_product_rel', 'product_product1_id', 'product_product2_id', 'Cross-Selling', domain="[]", readonly=False, help=''),
        'up_selling_product_ids': fields.many2many('product.product', 'up_selling_product_product_rel', 'product_product1_id', 'product_product2_id', 'Up-Selling', domain="[]", readonly=False, help=''),
        'related_product_ids': fields.many2many('product.product', 'related_product_product_rel', 'product_product1_id', 'product_product2_id', 'Related Products', domain="[]", readonly=False, help=''),
        'ean13': fields.char('EAN13', size=13, required=False, readonly=False, translate=False, help='', select=True),
        'default_code': fields.char('Reference', size=64, required=False, readonly=False, translate=False, help='', select=True),
        'paywithatweet_code': fields.char('Pay with a Tweet Code', size=64, required=False, readonly=False, translate=False, help='Code (id) for the \'Pay with a Tweet\' online service.\nFor more information refer: http://www.paywithatweet.com'),
        'to_recalc_price_cache': fields.boolean('Recalculate cached price', readonly=False, help=''),
    }

product_product()

class product_feature_group(osv.osv):
    '''Feature Group'''
    _name = 'product.feature_group'
    _description = "Feature Group"

    _columns = {
        'name': fields.char('Name', size=128, required=False, readonly=False, translate=True, help=''),
    }

product_feature_group()

class product_feature_definition(osv.osv):
    '''Feature'''
    _name = 'product.feature_definition'
    _description = "Feature"

    _columns = {
        'name': fields.char('Name', size=128, required=False, readonly=False, translate=True, help=''),
        'group_id': fields.many2one('product.feature_group', 'Feature Group', domain="[]", ondelete='set null', required=False, readonly=False, help=''),
        'description': fields.text('Description', readonly=False, translate=True, help=''),
    }

product_feature_definition()

