# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2012 by Wilbert Berendsen
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
Export to Music XML
Uses lxml.etree to create the XML document
"""

from __future__ import unicode_literals

import sys
    
from lxml import etree


class create_musicXML():
	""" creates the XML-file from the source code according to the Music XML standard """

	def __init__(self):
		""" creates the basic structure of the XML without any music 
		TODO: 
		set doctype	
		"""
		self.root = etree.Element("score-partwise", version="3.0")
		identification = etree.SubElement(self.root, "identification")
		encoding = etree.SubElement(identification, "encoding")
		software = etree.SubElement(encoding, "software")
		software.text = "Frescobaldi"
		encoding_date = etree.SubElement(encoding, "encoding-date")
		import datetime
		encoding_date = str(datetime.date.today())
		self.partlist = etree.SubElement(self.root, "part-list")
		self.part_count = 1		
	
	##
	# Building the basic Elements
	##
		
	def create_part(self, name):
		""" create a new part """
		part = etree.SubElement(self.partlist, "score-part", id="P"+str(self.part_count))
		partname = etree.SubElement(part, "part-name")
		partname.text = name
		self.current_part = etree.SubElement(self.root, "part", id="P"+str(self.part_count))
		self.part_count +=1
		self.bar_nr = 1
		
	def create_measure(self):
		""" create new measure """
		self.current_bar = etree.SubElement(self.current_part, "measure", number=str(self.bar_nr))
		self.bar_nr +=1	
		
	##
	# High-level node creation
	##
	
	def new_note(self, pitch, org_len, durtype, divs):
		""" create all nodes needed for a note. """
		self.create_note()
		self.add_pitch(pitch[0], pitch[1], pitch[2])
		duration = divs*4/int(org_len)
		self.add_div_duration(duration)
		self.add_duration_type(durtype)
		if pitch[1]:
			self.add_accidental(pitch[1])
			
	def tuplet_note(self, fraction, org_len, ttype, divs):
		""" convert current note to tuplet """
		a = divs*4*int(fraction[1])
		b = int(org_len)*int(fraction[0])
		duration = a/b
		self.change_div_duration(duration)
		self.add_time_modify(fraction)
		if ttype:
			self.add_notations()
			self.add_tuplet_type(ttype)
		
	def new_bar_attr(self, clef, mustime, key, mode, divs):
		""" create all bar attributes set. """
		self.create_bar_attr()
		if divs:
			self.add_divisions(divs)
		if key>=0:
			self.add_key(key, mode)
		if mustime:
			self.add_time(mustime[0], mustime[1])
		if clef:
			self.add_clef(clef[0], clef[1])
			
	def create_new_node(self, parentnode, nodename, txt):
		""" The Music XML language is extensive. 
		This function can be used to create 
		a non basic node not covered elsewhere in this script. 
		TODO: add attributes		
		"""
		new_node = etree.SubElement(parentnode, nodename)
		new_node.text = str(txt)
		
	##
	# Help functions
	##
	
	
	##
	# Low-level node creation
	##
		
	def create_note(self):
		""" create new note """
		self.current_note = etree.SubElement(self.current_bar, "note")
		
	def add_pitch(self, step, alter, octave):
		""" create new pitch """
		pitch = etree.SubElement(self.current_note, "pitch")
		stepnode = etree.SubElement(pitch, "step")
		stepnode.text = str(step)
		if alter:
			altnode = etree.SubElement(pitch, "alter")
			altnode.text = str(alter)
		octnode = etree.SubElement(pitch, "octave")
		octnode.text = str(octave)
		
	def add_accidental(self, alter):
		""" create accidental """
		acc = etree.SubElement(self.current_note, "accidental")
		if alter>0:		
			acc.text = "sharp"
		else:
			acc.text = "flat"
		
	def add_div_duration(self, divdur):
		""" create new duration """
		self.duration = etree.SubElement(self.current_note, "duration")
		self.duration.text = str(divdur)
		
	def change_div_duration(self, newdura):
		""" set new duration when tuplet """
		self.duration.text = str(newdura)
		
	def add_duration_type(self, durtype):
		""" create new type """
		typenode = etree.SubElement(self.current_note, "type")
		typenode.text = str(durtype)
		
	def add_notations(self):
		self.current_notation = etree.SubElement(self.current_note, "notations")
		
	def add_time_modify(self, fraction):
		""" create time modification """
		timemod_node = etree.SubElement(self.current_note, "time-modification")
		actual_notes = etree.SubElement(timemod_node, "actual-notes")
		actual_notes.text = fraction[0]
		norm_notes = etree.SubElement(timemod_node, "normal-notes")
		norm_notes.text = fraction[1]
		
	def add_tuplet_type(self, ttype):
		""" create tuplet with type attribute """
		tuplet = etree.SubElement(self.current_notation, "tuplet", type=ttype)		
		
	def create_bar_attr(self):
		""" create node attributes """
		self.bar_attr = etree.SubElement(self.current_bar, "attributes")
		
	def add_divisions(self, div):
		division = etree.SubElement(self.bar_attr, "divisions")
		division.text = str(div)
		
	def add_key(self, key, mode):
		keynode = etree.SubElement(self.bar_attr, "key")
		fifths = etree.SubElement(keynode, "fifths")
		fifths.text = str(key)
		modenode = etree.SubElement(keynode, "mode")
		modenode.text = str(mode)
		
	def add_time(self, beats, beat_type):
		timenode = etree.SubElement(self.bar_attr, "time")
		beatnode = etree.SubElement(timenode, "beats")
		beatnode.text = str(beats)
		typenode = etree.SubElement(timenode, "beat-type")
		typenode.text = str(beat_type)
		
	def add_clef(self, sign, line):
		clefnode = etree.SubElement(self.bar_attr, "clef")
		signnode = etree.SubElement(clefnode, "sign")
		signnode.text = str(sign)
		linenode = etree.SubElement(clefnode, "line")
		linenode.text = str(line)	
		
	##
	# Create XML document
	##
		
	def create_xmldoc(self):
		""" output etree as a XML document """
		return etree.tostring(self.root, pretty_print=True, xml_declaration=True, encoding='UTF-8')



