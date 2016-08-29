# -*- encoding: utf-8 -*-

{
    "name" : "JERA Contact Us module provides \"Contact Us\" form on Joomla! based web site.",
    "version" : "1.0",
    "description" : """A lead is a possible business partner or customer. As the initial contact it is the first step in the sales cycle.
However, the most common problem is that this information too often gets lost by not registering it with CRM software.
JERA Contact us module provides entry point for this information from Joomla! based web-site directly to OpenERP.

No more manual copying & synchronising with external software, it directly records the enquiry in your OpenERP CRM.

Features:
===============================================================
* Collect CRM Leads from your Joomla! based web page;
* Integrated with OpenERP's CRM module;
* Captcha protected realtime on-line forms;
* Seamless sales team and category integration;
* Predefined vertical and horizontal forms;
* Optional custom forms;
* Joomla! component and module display support;
* Language integration - transparent OpenERP translations;
* Pre-definable default values;
* Multi-company support;
* Multi-site support;
* Anonymous and/or registered form submit;

This module depends on JERA Framework, an OpenERP<->Joomla! real-time on-line connector.

For more information visit: 
http://www.alistek.com

Enquire by email:
info@alistek.com

Or voice call:
+371 67964296""",
    "author" : "Alistek Ltd.",
    "website" : "http://www.alistek.com",
    "category" : "Generic Modules/CRM & SRM",
    "url" : "http://www.alistek.com",
    "depends" : ['base', 'captcha', 'jera', 'crm'],
    "init_xml" : [],
    "update_xml" : ['jera_install_action.xml',
                    'data/jera_contactus_data.xml',
                    'jera_contactus_views.xml'],
    "demo_xml" : [],
    "license" : "GPL-3",
    "installable" : True,
    "active" : False,

}
