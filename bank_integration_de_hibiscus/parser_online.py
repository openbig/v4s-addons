# -*- encoding: utf-8 -*-
##############################################################################
#
#  Copyright (C) 2012 OpenGLOBE (<http://www.openglobe.pl>).
#  All Rights Reserved
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from tools.translate import _
from osv import osv, fields
import time
from datetime import datetime
from tools import ustr   #gg change
import netsvc

'''
FOR IMPORT 

Inherit this class and add parser as a method. 
 The names of the methods will be selection for wizards.
 You have to return a list of following data:
result = {

 For Bank Statement:
name  (system will check if statement name is unique).
date
balance_start     - can be filled or left for manual entry
balance_end_real  - can be filled or left for manual entry
currency

For bank Statement lines:

name (communication) *
date *
amount *
type
partner_name *   If address cannot be resolved put everything to partner_name
partner_address_name, 
partner_street, If full address cannot be resolved put everything in street
partner_street2, 
partner_zip, 
partner_city, 
partner_country

bank_account_iban
    * or
bank_account
    and
bank_bic
    or
bank_code

ref    - ref and note is used for searching for invoice number in some configuration option.
note *  Put whole line here
sequence
}
'''

class bank_parsers(osv.osv_memory):
    _inherit = "bank.parsers"
    
    def parser_selection(self, cr, uid, context=None):
        res = super(bank_parsers, self).parser_selection(cr, uid, context=context)
#        res.append(('hibi_csv','Hibiscus CSV Parser'))   # selection must be exactly the same as method name.
        res.append(('hibi_ol','Hibiscus OnLine Parser'))   # selection must be exactly the same as method name.
        return res   # [('hibiscus_csv_parser','Hibiscus CSV Parser'),]
#        return res += [ ('hibiscus_csv_parser','Hibiscus CSV Parser'),] 

    #checking for new or modified bank mapping details
    def hibi_ol_import(self, cr, uid, wizard, context=None):
        if not wizard.banking_settings_id.hibiscus_account_id:
             raise osv.except_osv('Error!','You have to set Hibiscus Account ID in Import Settings using Import Hbiscus Accounts Wizard.')
        hibiscus_tools_obj = self.pool.get('hibiscus.tools')
        config = wizard.banking_settings_id
        server = hibiscus_tools_obj.get_server(cr, uid, config.hibiscus_server, config.hibiscus_user, config.hibiscus_password, \
                            config.hibiscus_port, config.hibiscus_secure)
        hibiscus_account_id = wizard.banking_settings_id.hibiscus_account_id
        date_from = wizard.date_from and datetime.strptime(wizard.date_from, "%Y-%m-%d").strftime("%d.%m.%Y") or ""
        date_to = wizard.date_to and datetime.strptime(wizard.date_to, "%Y-%m-%d").strftime("%d.%m.%Y") or ""

        args = {"konto_id":hibiscus_account_id}
        if date_from:
            args["datum:min"] = date_from  
        if date_to:
            args["datum:max"] = date_to 
        arg = (args,)
        try:
            file_data = getattr(server,'hibiscus.xmlrpc.umsatz.list')(*arg)
#            file_data = getattr(server,'hibiscus.xmlrpc.ueberweisung.find')(*arg)
        except Exception, e:
            raise osv.except_osv(_('Error!'),_('Cannot import Hibiscus bank statement: %s')%e)
                #self.report.append('ERROR: Unable to update record ['+str(id2)+']:'+str(value.get('name', '?')))
#        logger = netsvc.Logger()
#        logger.notifyChannel("warning", netsvc.LOG_WARNING,"File data %s"%str(file_data))
        if not file_data:
            return False
        lines = file_data  #.split('\n')
#        lines = file_data.split('\n')
        if not len(lines[1]):
            return False
#        quotechar = '"'
        delimiter = ':'
        first_line = lines[1]  #.replace(quotechar,'')

#  1      map.put("id", u.getID());

#  0      map.put("konto_id", u.getKonto().getID());
#  1      map.put("empfaenger_name", StringUtil.notNull(u.getGegenkontoName()));
#  2      map.put("empfaenger_konto", StringUtil.notNull(u.getGegenkontoNummer()));
#  3      map.put("empfaenger_blz", StringUtil.notNull(u.getGegenkontoBLZ()));
#  4      map.put("art", StringUtil.notNull(u.getArt()));
#  5      map.put("betrag", HBCI.DECIMALFORMAT.format(u.getBetrag()));
#  6      map.put("valuta", DateUtil.format(u.getValuta()));
#  7      map.put("datum", DateUtil.format(u.getDatum()));
#  8      map.put("zweck", VerwendungszweckUtil.toString(u, " "));
#  9      map.put("saldo", StringUtil.notNull(Double.valueOf(u.getSaldo())));
# 10     map.put("primanota", StringUtil.notNull(u.getPrimanota()));
# 11      map.put("customer_ref", StringUtil.notNull(u.getCustomerRef()));
# 12      map.put("kommentar", StringUtil.notNull(u.getKommentar()));
#      if (kat != null) {
# 13        map.put("umsatz_typ", kat.getName());
        first_line_data = first_line.split(delimiter)
        balance_start = float(first_line_data[9].replace(".","").replace(",","."))  # zwischensumme - balance after first line
        balance_start -=  float(first_line_data[5].replace(".","").replace(",","."))   #  amount of first line

        result = {}
# TODO name ????
        result['name'] = '/'  #  (system will check if statement name is unique).
        result['date'] =  time.strftime('%Y-%m-%d')
        result['balance_start'] = balance_start
        result['balance_end_real'] = False   # Will be entered after last loop
        result['currency'] = False #'EUR'    # to check if the same as in bank statement journal (which is taken from defaults)
        result['home_bank_account_iban'] = wizard.banking_settings_id.partner_account_id.iban
        result['home_bank_account'] = wizard.banking_settings_id.partner_account_id.acc_number
        result['home_bank_swift'] = False
        result['home_bank_code'] = wizard.banking_settings_id.partner_account_id.bank.code

        seq = 1
        last_balance = 0
        for line in lines:
            if not len(line):
                break
            data = line.split(delimiter)
#            for idx, value in enumerate(data):
#                data[idx] = data[idx].replace(quotechar,'')                
            val={}
# TODO How to recognize the IBAN ??
# TODO How to recognize the bank cost operations ??
            val['name'] = data[10]  # (communication - primanota
            val['date'] = datetime.strptime(data[7], "%d.%m.%Y").strftime("%Y-%m-%d") 
            val['amount'] = float(data[5])    #.replace(".","").replace(",","."))
            val['type'] = 'general'  # 'customer' or 'supplier', 'bank' Bank has to be converted to General after calculation.
            val['partner_name'] = data[1]
            val['partner_address_name'] = False
            val['partner_street'] = False
            val['partner_street2'] = False
            val['partner_zip'] = False
            val['partner_city'] = False
            val['partner_country'] = False
            val['partner_bank_account_iban'] = False  # No spaces inside !!
            val['partner_bank_account'] = data[2]
            val['partner_bank_swift'] = False
            val['partner_bank_code'] = data[3]
            val['ref'] = ustr(data[11])
            val['sequence'] = seq
            val['note'] =  ustr( "Primanota: :" + data[10]  \
                          +"\nKonto: " + data[0]  \
                          +"\nEmpfanger: " + data[1]  \
                          +"\nEmpfanger konto: " + data[2]  \
                          +"\nEmpfanger konto BLZ: " + data[3]  \
                          +"\nArt: " +  data[4]  \
                          +"\nSaldo: " +  data[9]  \
                          +"\nValuta: " +  data[6]  \
                          +"\nReferenz: " +  data[11]  \
                          +"\nUmsatz typ: " +  data[13]  \
                          +"\nZweck: " +  data[8]  \
                          +"\nKommentar: " + data[12]  \
                    )
#                          "\nZweck 2: " +  data[10] + \
#                          "\nWeitere Zweck: " + data[16]

            last_balance = data[9]
            seq += 1
            result['lines'].append(val)
        result['balance_end_real'] = float(last_balance.replace(".","").replace(",","."))
        return [result]

    def hibi_ol_export(self, cr, uid, p_order_id, context=None):
        logger = netsvc.Logger()
        if not p_order_id:
            return False
        result = False
        pay_order = self.pool.get('payment.order').browse(cr, uid, p_order_id, context)
        config = pay_order.mode.banking_settings_id
        hibiscus_tools_obj = self.pool.get('hibiscus.tools')
#        url = hibiscus_tools_obj.get_url(cr, uid, config.server, config.user, config.password, config.port, config.secure)
#        server = hibiscus_tools_obj.get_server(url)
        server = hibiscus_tools_obj.get_server(cr, uid, config.hibiscus_server, config.hibiscus_user, config.hibiscus_password, \
                            config.hibiscus_port, config.hibiscus_secure)
        hibiscus_account_id = config.hibiscus_account_id
        data = ""
        fixed_date = pay_order.date_prefered == "fixed" and pay_order.date_scheduled
        for line in pay_order.line_ids:
            date = fixed_date or pay_order.date_prefered == "due" and line.ml_maturity_date or line.date
            date = date and datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y") 
            kontonummer = line.bank_id.state == 'iban' and line.bank_id.iban or line.bank_id.acc_number
            amount = line.amount_currency
            verwendungszweck = [
                                    "Your ref " + (line.ml_inv_ref and line.ml_inv_ref.reference or "NONREF"),   # zweck1
                                    "Our ref " + (line.name or "NONREF"),          # zweck2
                                ]
            if line.communication:   # zweck3
                verwendungszweck.append(line.communication)
            if line.communication2:   # zweck4
                verwendungszweck.append(line.communication2)
            if amount < 0:
                testschluessel = "05"
            else:
                testschluessel = "51"
            arg = ({ "konto" : hibiscus_account_id,        # kontoID
                    "kontonummer" : kontonummer,                      # kto
                    "blz" : line.bank_id.bank.code,     # blz
                    "name" : line.partner_id.name,       # name
                    "betrag" : line.amount_currency + 0.0,   #.replace(".",","),   # betrag
                    "termin" : date,   # termin
                    "textschluessel" : testschluessel,
                    "verwendungszweck" : verwendungszweck,
            },)
#            logger.notifyChannel("warning", netsvc.LOG_WARNING,"In transfer %s"%str(arg))
            if amount < 0:
                result = getattr(server,'hibiscus.xmlrpc.lastschrift.create')(*arg)
            else:
                result = getattr(server,'hibiscus.xmlrpc.ueberweisung.create')(*arg)
#                result = getattr(server,'hibiscus.xmlrpc.ueberweisung.createParams')
            if result:
                raise osv.except_osv(_('Error!'),_(result.encode('UTF-8')))
            data += ustr(arg)
        return data
bank_parsers()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
