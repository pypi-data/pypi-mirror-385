#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
#

""" Metadata retriever """

try:
    from nxstools import nxsfileinfo
    nxsfileinfo.Metadata.metadata
    NXSMETA = True
except Exception:
    NXSMETA = False


class Options(object):
    "metadata options"

    def __init__(self):
        #: (:obj:`str`) names of field or group attributes separated by ,
        self.attrs = None
        #: (:obj:`str`) names of field or group attributes
        #               to be hidden separated by ,
        self.nattrs = 'nexdatas_source,nexdatas_strategy,units'
        #: (:obj:`str`) field names of more dimensional datasets to be shown
        self.values = ""
        #: (:obj:`str`) postfix to be added to NeXus group name
        self.group_postfix = ""
        #: (:obj:`str`) ames of entry NX_class to be shown separated by ,
        self.entryclasses = "NXentry"
        #: (:obj:`str`) experiment techniques
        self.technuques = None
        #: (:obj:`str`) relative path between beamtime dir and scan dir
        self.relpath = ""
        #: (:obj:`str`) owner group
        self.ownergroup = None
        #: (:obj:`str`) access  groups
        self.accessgroups = None
        #: (:obj:`str`) ames of entry NX_class to be shown separated by ,
        self.entrynames = ""
        #: (:obj:`bool`) do not store NXentry as scientificMetadata
        self.rawscientific = False
        #: (:obj:`str`) dataset pid
        self.pid = None
        #: (:obj:`str`) DOOR proposal as SciCat proposal option
        self.pap = False
        #: (:obj:`str`) beamtime id
        self.beamtimeid = None
        #: (:obj:`bool`) generate pid with uuid
        self.puuid = False
        #: (:obj:`bool`) generate pid with file name
        self.pfname = False
        #: (:obj:`str`) beamtime metadata file
        self.beamtimemeta = None
        #: (:obj:`str`) scientific metadata file
        self.scientificmeta = None
        #: (:obj:`str`) output scicat metadata file
        self.output = None
        #: (:obj:`list` < :obj:`str`>) list of file names
        self.args = ['']
        #: (:obj:`bool`) empty units flag
        self.emptyunits = False
        #: (:obj:`str`) file format
        self.fileformat = 'nxs'


class Metadata(object):
    """ NeXus data writer
    """

    def __init__(self, root):
        """constructor

        :param root: filewriter root
        :type root: :class:`nxstools.FileWriter.FTGroup`)
        """
        self.__root = root

    def get(self, **args):
        """ retrieves metatadata


        :param args: options of nxsfileinfo command
        :type args: :class:`nxswriter.Metadata.Options`)
        :rtype: :obj:`str`
        :returns: JSON metadata string
        """
        options = Options()
        for ky, vl in args.items():
            setattr(options, ky, vl)
        return nxsfileinfo.Metadata.metadata(self.__root, options)
