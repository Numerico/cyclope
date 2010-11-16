#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2010 Código Sur - Nuestra América Asoc. Civil / Fundación Pacificar.
# All rights reserved.
#
# This file is part of Cyclope.
#
# Cyclope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cyclope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.comments.forms import CommentForm
from captcha.fields import CaptchaField

class CommentFormWithCaptcha(CommentForm):
    url = forms.URLField(label=_("Website or Blog"), required=False)
    captcha = CaptchaField(label=_("Security code"))

    def clean(self):

        # captcha_ input only exists when the user is authenticated
        if 'captcha_' in self.data:
            if 'captcha' in self._errors:
                self._errors.pop('captcha')
        return self.cleaned_data
