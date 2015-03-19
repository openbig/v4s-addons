# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#
#    Module is copyrighted by OpenGLOBE (www.openglobe.pl)
#    with the same rules as OpenObject and Odoo.
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

{
    'name': 'Stock Picking Type Edit',
    'version': '0.01 (8.0)',
    'author': 'OpenGLOBE.pl',
    'website': 'http://www.openglobe.pl',
    'category': 'Warehouse Management',
    'sequence': 8,
    'summary': 'Inventory, Logistic, Storage',
    'images': [
    ],
    'depends': [
        'stock',
    ],
    'description': """
Stock Picking Type Changes:
==========================

This module allows to hide picking type, and to choose them in warehouse.
    """,
    'data': [
        'stock_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'qweb': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
