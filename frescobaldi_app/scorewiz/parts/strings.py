# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2011 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
String part types.
"""

import __builtin__

import ly.dom

from . import _base
from . import register


class StringPart(_base.SingleVoicePart):
    """Base class for string part types."""


class Violin(StringPart):
    @staticmethod
    def title(_=__builtin__._):
        return _("Violin")
    
    @staticmethod
    def short(_=__builtin__._):
        return _("abbreviation for Violin", "Vl.")

    midiInstrument = 'violin'


class Viola(StringPart):
    @staticmethod
    def title(_=__builtin__._):
        return _("Viola")
    
    @staticmethod
    def short(_=__builtin__._):
        return _("abbreviation for Viola", "Vla.")
    
    midiInstrument = 'viola'
    clef = 'alto'
    octave = 0


class Cello(StringPart):
    @staticmethod
    def title(_=__builtin__._):
        return _("Cello")
    
    @staticmethod
    def short(_=__builtin__._):
        return _("abbreviation for Cello", "Cl.")
    
    midiInstrument = 'cello'
    clef = 'bass'
    octave = -1


class Contrabass(StringPart):
    @staticmethod
    def title(_=__builtin__._):
        return _("Contrabass")
    
    @staticmethod
    def short(_=__builtin__._):
        return _("abbreviation for Contrabass", "Cb.")
    
    midiInstrument = 'contrabass'
    clef = 'bass'
    octave = -1


class BassoContinuo(Cello):
    @staticmethod
    def title(_=__builtin__._):
        return _("Basso Continuo")
    
    @staticmethod
    def short(_=__builtin__._):
        return _("abbreviation for Basso Continuo", "B.c.")
    
    # TODO: reimplement build() to add a figures line
    

register(
    lambda: _("Strings"),
    [
        Violin,
        Viola,
        Cello,
        Contrabass,
        BassoContinuo,
    ])




