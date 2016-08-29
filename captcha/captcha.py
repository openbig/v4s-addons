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

from osv import osv, fields
import Image, ImageFont, ImageDraw
import random, math
import base64
from tools import config
import os, sys

if sys.platform=='win32':
    def_font_path = "C:/windows/fonts/ArialBlack.ttf"
else:
    def_font_path = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf"

try:
    from cStringIO import StringIO
except ImportError, e:
    from StringIO import StringIO

class captcha_captcha(osv.osv):
    '''
    Captcha data
    '''
    _name = 'captcha.captcha'
    _description = 'Captcha data'
    _rec_name = 'code'

    _foreground_color = (49,157,28)
    _background_color = (221, 221, 221)
    _allowed_symbols = "23456789abcdegifjkpqsvxyz" #alphabet without similar symbols (o=0, 1=l)

    def __init__(self, pool, cr):
        super(captcha_captcha, self).__init__(pool, cr)
        self._jdata = {}
        self_obj = self.pool.get('captcha.captcha')
        try:
            captcha_ids = self_obj.search(cr, 1, [])
            # Load font
            self._font_file = False
            ad = os.path.abspath(os.path.join(config['root_path'], u'addons'))
            mod_path_list = map(lambda m: os.path.abspath(m.strip()), config['addons_path'].split(','))
            mod_path_list.append(ad)

            for mod_path in mod_path_list:
                font_file = mod_path+os.path.sep+"captcha"+os.path.sep+"font26.ttf"
                if os.path.lexists(font_file):
                    if os.path.isfile(def_font_path):
                        self._font = ImageFont.truetype(def_font_path, 22)
                    else:
                        self._font = ImageFont.truetype(font_file, 22)
                    break
        except Exception, e:
            cr.rollback()
            print e
        else:
            try:
                for captcha in self_obj.read(cr, 1, captcha_ids, ['sid','code']):
                    self._jdata[captcha['sid']] = {'captcha':{'code':captcha['code']}}
            except Exception, e:
                cr.rollback()
                print e

    def _get_captcha(self, cr, uid, context={}):
        sid = context.get('jera_sid')
        return self._jdata.get(sid, {}).get('captcha', {}).get('img', False)

    def _get_captcha_code(self, cr, uid, context={}):
        sid = context.get('jera_sid')
        return self._jdata.get(sid, {}).get('captcha', {}).get('code', False)

    def jera_request_reload_captcha(self, cr, uid, context=None):
        sid = context.get('jera_sid')
        img, code = self.get_captcha_store(cr, uid, sid=sid)
        captcha = {'code':code,'img':img}
        self._jdata[sid] = {'captcha':captcha}
        return captcha['img']

    def check_captcha(self, cr, uid, ids, context):
        for captcha in self.browse(cr, uid, ids, context=context):
            if captcha.code_verify and captcha.code_verify.lower()==self._get_captcha_code(cr, uid, context=context):
                return True
        return False

    def clear_captcha(self, cr, uid, context):
        del self._jdata[context.get('jera_sid')]['captcha'] # delete captcha data for the current session
        return True

    def read(self,cr, uid, ids, fields=None, context=None, load='_classic_read'):
        def override(o):
            if uid != 1:
                if 'code' in o: o['code'] = '********'
                if 'code_by_sid' in o: o['code_by_sid'] = '********'
            return o

        result = super(captcha_captcha, self).read(cr, uid, ids, fields, context, load)
        if not result:
            return False
        if isinstance(ids, (int, long)):
            result = override(result)
        else:
            result = map(override, result)
        return result
    
    _columns = {
        'captcha':fields.binary('Captcha', help="Click on image to refresh"),
        'code':fields.char('Code', size=16, required=False),
        'code_verify':fields.char('Captcha code Type characters you see', size=16),
        'sid':fields.char('Session Id', size=256),
        #'datetime': fields.datetime('Date'),
    }

    def _MultiWave(self, img):
        width, height = img.size
        img2 = Image.new("RGB",img.size, self._background_color)
        # частоты
        rand1 = random.randint(750000, 1200000) / 10000000.0
        rand2 = random.randint(750000, 1200000) / 10000000.0
        rand3 = random.randint(750000, 1200000) / 10000000.0
        rand4 = random.randint(750000, 1200000) / 10000000.0
        # фазы
        rand5 = random.randint(0, 31415926) / 10000000.0
        rand6 = random.randint(0, 31415926) / 10000000.0
        rand7 = random.randint(0, 31415926) / 10000000.0
        rand8 = random.randint(0, 31415926) / 10000000.0
        # амплитуды
        rand9 = random.randint(330, 420) / 110.0
        rand10 = random.randint(330, 450) / 100.0

        for x in range(width):
            for y in range(height):
                # координаты пикселя-первообраза.
                sx = x + ( math.sin(x * rand1 + rand5) + math.sin(y * rand3 + rand6) ) * rand9
                sy = y + ( math.sin(x * rand2 + rand7) + math.sin(y * rand4 + rand8) ) * rand10

                # первообраз за пределами изображения
                if sx<0 or sy<0 or sx>=width-1 or sy>=height-1:
                    continue
                else: # цвета основного пикселя и его 3-х соседей для лучшего антиалиасинга
                    color=(reduce(lambda a,b:a*b, img.getpixel((sx, sy))) >> 16) & 0xFF
                    color_x=(reduce(lambda a,b:a*b, img.getpixel((sx+1, sy))) >> 16) & 0xFF
                    color_y=(reduce(lambda a,b:a*b, img.getpixel((sx, sy+1))) >> 16) & 0xFF
                    color_xy=(reduce(lambda a,b:a*b, img.getpixel((sx+1, sy+1)))) & 0xFF

                # сглаживаем только точки, цвета соседей которых отличается
                if color==255 and color_x==255 and color_y==255 and color_xy==255:
                    continue
                elif color==0 and color_x==0 and color_y==0 and color_xy==0:
                    newred = self._foreground_color[0]
                    newgreen = self._foreground_color[1]
                    newblue = self._foreground_color[2]
                else:
                    frsx=sx-int(sx) #отклонение координат первообраза от целого
                    frsy=sy-int(sy)
                    frsx1=1-frsx
                    frsy1=1-frsy

                    # вычисление цвета нового пикселя как пропорции от цвета основного пикселя и его соседей
                    newcolor = ( color * frsx1 * frsy1 +
                                     color_x  * frsx  * frsy1 +
                                     color_y  * frsx1 * frsy  +
                                     color_xy * frsx  * frsy )
                    if newcolor>255:
                        newcolor=255
                    newcolor=newcolor/255
                    newcolor0=1-newcolor

                    newred=int(newcolor0 * self._foreground_color[0] + newcolor * self._background_color[0])
                    newgreen=int(newcolor0 * self._foreground_color[1] + newcolor * self._background_color[1])
                    newblue=int(newcolor0 * self._foreground_color[2] + newcolor * self._background_color[2])

                img2.putpixel( (x, y), (newred, newgreen, newblue) )
        return img2


    def gen_random_code(self, length=5):
        #char_range = range(48,57)+range(97,122)#+range(65,91)
        char_range = map(lambda a: ord(a), self._allowed_symbols)
        password = ''
        random.seed()
        while(length):
            password += chr(random.choice(char_range))
            length -= 1
        return password

    def get_captcha(self, length=5):
        size_x = 46
        size_y = 26*length

        self._foreground_color = (random.randint(0,80), random.randint(0,80), random.randint(0,80))
        self._background_color = (random.randint(220,255), random.randint(220,255), random.randint(220,255))

        captcha = Image.new("RGB",(size_y,size_x), "#ffffff")
        draw_captcha = ImageDraw.Draw(captcha)
        captcha_code = self.gen_random_code()

        # Load font
        #ad = os.path.abspath(os.path.join(config['root_path'], u'addons'))
        #mod_path_list = map(lambda m: os.path.abspath(m.strip()), config['addons_path'].split(','))
        #mod_path_list.append(ad)

        #for mod_path in mod_path_list:
        #    font_file = mod_path+os.path.sep+"captcha"+os.path.sep+"font26.ttf"
        #    if os.path.lexists(font_file):
        #        font = ImageFont.truetype(font_file, 22)
        #        break

        draw_captcha.setfont(self._font)
        draw_captcha.text((12,12), captcha_code, fill=self._foreground_color)

        st_io = StringIO()
        captcha = self._MultiWave(captcha)
        captcha.save(st_io, "PNG")
        return base64.encodestring(st_io.getvalue()), captcha_code

    def get_captcha_store(self, cr, uid, length=5, sid=None):
        captcha_img, captcha_code = self.get_captcha(length)
        cr.execute("DELETE FROM captcha_captcha WHERE extract(day from current_date-create_date)>0")
        if sid:
            ids = self.pool.get('captcha.captcha').search(cr, 1, [('sid','=',sid)])
            if ids:
                self.pool.get('captcha.captcha').write(cr, 1, ids, {'code':captcha_code})
            else:
                self.pool.get('captcha.captcha').create(cr, 1, {'code':captcha_code,'sid':sid})
        return captcha_img, captcha_code

    _defaults = {
        'captcha': _get_captcha,
        'code': _get_captcha_code,
    }    

captcha_captcha()

