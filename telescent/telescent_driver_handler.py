#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from common.configuration_parser import ConfigurationParser
from common.driver_handler_base import DriverHandlerBase
from common.xml_wrapper import XMLWrapper
from resource_info2 import ResourceInfo2

class TelescentDriverHandler(DriverHandlerBase):
    def __init__(self):
        DriverHandlerBase.__init__(self)

        self._ctag = 1
        self._switch_name = ''
        self._switch_size = 0
        self._mapping_info = dict()

        self._resource_info = None

        self._port = ConfigurationParser.get("driver_variable", "connection_port")

        self._service_mode = ConfigurationParser.get("driver_variable", "service_mode")
        self._port_logical_mode = ConfigurationParser.get("driver_variable", "port_mode")
        self._custom_port_pairing = ConfigurationParser.get("driver_variable", "custom_port_pairing")

    def log(self, s):
        with open(r'c:\temp\telescent.log', 'a') as f:
            f.write(s + '\n')
            
    def login(self, address, username, password, command_logger=None):
        self.log('login')
        self.log('address=' + str(address))
        self.log('username=' + str(username))
        self.log('password=' + str(password))
        self.log('port=' + str(self._port))
        self.log('prompt=' + str(self._prompt))

        self._session.connect(address, username, password, port=self._port, re_string=self._prompt)

    def get_resource_description(self, address, command_logger=None):
        switchfamily = ConfigurationParser.get("driver_variable", "switch_family")
        switchmodel = ConfigurationParser.get("driver_variable", "switch_model")
        bladefamily = ConfigurationParser.get("driver_variable", "blade_family")
        blademodel = ConfigurationParser.get("driver_variable", "blade_model")
        portfamily = ConfigurationParser.get("driver_variable", "port_family")
        portmodel = ConfigurationParser.get("driver_variable", "port_model")

        sw = ResourceInfo2('', address, switchfamily, switchmodel, serial=address)

        switchstate = self._session.send_command('switchstate', re_string=self._prompt)
        switchstate = re.sub(r'.\[\d+m', '', switchstate)
        self.log('CLEANED SWITCH STATE: (((' + switchstate + ')))')

        outaddr2inaddrstatus = {}
        max_global_row = -1
        for line in switchstate.split('\n'):
            line = line.strip()
            matches = re.search(r"R(?P<global_row>\d+)#"
                                r"(?P<state>[a-zA-Z])"
                                r"\s+(?P<status0>[a-zA-Z]+)(?P<addr0>\d+)"
                                r"\s+(?P<status1>[a-zA-Z]+)(?P<addr1>\d+)"
                                r"\s+(?P<status2>[a-zA-Z]+)(?P<addr2>\d+)"
                                r"\s+(?P<status3>[a-zA-Z]+)(?P<addr3>\d+)"
                                r"\s+(?P<status4>[a-zA-Z]+)(?P<addr4>\d+)"
                                r"\s+(?P<status5>[a-zA-Z]+)(?P<addr5>\d+)"
                                r"\s+(?P<status6>[a-zA-Z]+)(?P<addr6>\d+)"
                                r"\s+(?P<status7>[a-zA-Z]+)(?P<addr7>\d+)"
                                r"\s+(?P<status8>[a-zA-Z]+)(?P<addr8>\d+)"
                                r"\s+(?P<status9>[a-zA-Z]+)(?P<addr9>\d+)"
                                r"\s+(?P<status10>[a-zA-Z]+)(?P<addr10>\d+)"
                                r"\s+(?P<status11>[a-zA-Z]+)(?P<addr11>\d+)"
                                , line, re.DOTALL)
            if matches:
                d = matches.groupdict()
                global_row = int(d['global_row'])
                for col in range(0, 12):
                    outaddr = global_row*12 + col
                    inaddr = d['addr' + str(col)]
                    instatus  = d['status' + str(col)]
                    outaddr2inaddrstatus[outaddr] = (inaddr, instatus)
                if global_row > max_global_row:
                    max_global_row = global_row

        for module in range(0, (max_global_row + 1) / 8):
            bladeserial = address + '/' + str(module)
            blade = ResourceInfo2('module%0.2d' % (module), str(module), bladefamily, blademodel, serial=bladeserial)
            for row in range(0,8):
                for col in range(0, 12):
                    portname = 'row_%d_col_%0.2d' % (row, col)
                    portaddr = '%d,%d' % (row, col)
                    absaddr = (module * 8 + row) * 12 + col
                    if absaddr in outaddr2inaddrstatus and outaddr2inaddrstatus[absaddr][1].startswith('A'):
                        connaddr = int(outaddr2inaddrstatus[absaddr][0])
                        connglobrow = connaddr / 12
                        connmodule = connglobrow / 8
                        connrow = connglobrow % 8
                        conncol = connaddr % 12
                        mappath = '%s/%d/%d,%d' % (address, connmodule, connrow, conncol)
                    else:
                        mappath = None
                    # mappath = None
                    # todo Warning "An item with the same key has already been added." caused by nonblank mappath
                    portserial = address + '/' + str(module) + '/' + portaddr
                    blade.subresources.append(ResourceInfo2(portname, portaddr, portfamily, portmodel, map_path=mappath, serial=portserial))
            sw.subresources.append(blade)

        self.log('resource info xml: (((' + sw.to_string() + ')))')

        return XMLWrapper.parse_xml(sw.to_string())

    def map_uni(self, src_port, dst_port, command_logger=None):
        a = ','.join(src_port[1:])
        b = ','.join(dst_port[1:])
        self.log('map_uni ' + a + ' ' + b)
        out = ''
        out += self._session.send_command('unlock --force -in ' + a, re_string=self._prompt)
        out += self._session.send_command('unlock --force -out ' + b, re_string=self._prompt)
        out += self._session.send_command('connect --force -in ' + a + ' -out ' + b, re_string=self._prompt)
        if 'Exception' in out or 'ERROR' in out:
            raise Exception('Error: ' + out)

    def map_bidi(self, src_port, dst_port, command_logger=None):
        a = ','.join(src_port[1:])
        b = ','.join(dst_port[1:])
        self.log('map_bidi ' + a + ' ' + b)
        out = ''
        out += self._session.send_command('unlock --force ' + a, re_string=self._prompt)
        out += self._session.send_command('unlock --force ' + b, re_string=self._prompt)
        out += self._session.send_command('connect --force ' + a + ' ' + b, re_string=self._prompt)
        if 'Exception' in out or 'ERROR' in out:
            raise Exception('Error: ' + out)

    def map_clear_to(self, src_port, dst_port, command_logger=None):
        a = ','.join(src_port[1:])
        b = ','.join(dst_port[1:])
        self.log('map_clear_to ' + a + ' ' + b)
        out = ''
        # out += self._session.send_command('unlock --force -in ' + a, re_string=self._prompt)
        # out += self._session.send_command('unlock --force -out ' + b, re_string=self._prompt)
        out += self._session.send_command('unlock --force ' + a, re_string=self._prompt)
        out += self._session.send_command('unlock --force ' + b, re_string=self._prompt)
        out += self._session.send_command('unallocate --force -in ' + a, re_string=self._prompt)
        out += self._session.send_command('unallocate --force -out ' + b, re_string=self._prompt)
        if 'Exception' in out or 'ERROR' in out:
            raise Exception('Error: ' + out)

    def map_clear(self, src_port, dst_port, command_logger=None):
        a = ','.join(src_port[1:])
        b = ','.join(dst_port[1:])
        self.log('map_clear ' + a + ' ' + b)
        out = ''
        out += self._session.send_command('unlock --force ' + a, re_string=self._prompt)
        out += self._session.send_command('unlock --force ' + b, re_string=self._prompt)
        out += self._session.send_command('unallocate --force ' + a, re_string=self._prompt)
        out += self._session.send_command('unallocate --force ' + b, re_string=self._prompt)
        if 'Exception' in out or 'ERROR' in out:
            raise Exception('Error: ' + out)

    def set_speed_manual(self, src_port, dst_port, speed, duplex, command_logger=None):
        self.log('1')
        # command_logger.log('1')

    def get_attribute_value(self, address, attribute_name, command_logger=None):
        self.log('1')
        # command_logger.log('1')
        return XMLWrapper.parse_xml('<Attribute Name="' + attribute_name + '" Type="String" Value="fake_value"/>')


if __name__ == '__main__':
    from cloudshell.core.logger.qs_logger import get_qs_logger

    gglass = TelescentDriverHandler()
    plogger = get_qs_logger('Autoload', 'Telescent', 'Telescent')
    gglass.login('10.11.34.218:9861', 'quali', 'aoeu1234', plogger)
    gglass.get_resource_description('10.11.34.218', plogger)
