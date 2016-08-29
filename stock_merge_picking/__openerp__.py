# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP Module
#    
#    Copyright (C) 2010-2011 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
#
##############################################################################
#
#    Merge Picking up to v5 of OpenERP was written by Axelor, www.axelor.com
#    This is a complete rewrite.
#
##############################################################################
{
    'name' : 'Merge Picking',
    'version' : '6.0',
    'author' : 'Marco Dieckhoff (Bremskerl)',
    'website' : 'www.bremskerl.com',
    'depends' : ['stock'],
    'category' : 'Warehouse',
    'description': """
This module allows you to manually merge stock pickings (Incoming Shipments, Delivery Orders, Internal Moves).
    """,
    'init_xml' : [],
    'demo_xml' : [],
    'update_xml' : ['view/stock_view.xml', 'wizard/merge_picking_view.xml'],
    'active': False,
    'installable': True
}
