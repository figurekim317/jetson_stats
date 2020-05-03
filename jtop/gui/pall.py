# -*- coding: UTF-8 -*-
# This file is part of the jetson_stats package (https://github.com/rbonghi/jetson_stats or http://rnext.it).
# Copyright (c) 2019 Raffaello Bonghi.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import curses
from curses.textpad import rectangle
from .jtopgui import Page
# Graphics elements
from .jtopguilib import (linear_gauge,
                         size_min,
                         label_freq)
# Menu GUI pages
from .jtopguimenu import (plot_watts,
                          compact_info,
                          plot_temperatures,
                          plot_CPUs)
# Actual variable printed
# LIST_PRINT = ['CPU', 'MTS', 'RAM', 'IRAM', 'SWAP', 'EMC', 'GR3D', 'TEMP', 'WATT', 'FAN', 'APE', 'NVENC', 'NVDEC', 'MSENC']


class ALL(Page):

    def __init__(self, stdscr, jetson, refresh):
        super(ALL, self).__init__("ALL", stdscr, jetson, refresh)

    def draw(self, key):
        """
            Update screen with values
        """
        # Screen size
        height, width, first = self.size_page()
        line_counter = first + 1
        # Plot Status CPU
        line_counter = plot_CPUs(self.stdscr, line_counter, self.jetson.stats['CPU'], width)
        # Plot MTS
        if 'MTS' in self.jetson.stats:
            line_counter += 1
            self.stdscr.addstr(line_counter, 0, "MTS ", curses.color_pair(5))
            # Show FG linear gauge
            linear_gauge(self.stdscr, offset=line_counter, start=4, size=width // 2 - 2,
                         name='FG',
                         value=self.jetson.stats['MTS']['fg'],
                         color=curses.color_pair(5))
            # Show BG linear gauge
            linear_gauge(self.stdscr, offset=line_counter, start=2 + width // 2, size=width // 2 - 2,
                         name='BG',
                         value=self.jetson.stats['MTS']['bg'],
                         color=curses.color_pair(5))
        # RAM linear gauge info
        line_counter += 1
        ram_status = self.jetson.stats['RAM']
        lfb_status = self.jetson.stats['RAM']['lfb']
        szw, divider, unit = size_min(ram_status['tot'], start=ram_status['unit'])
        # lfb label
        percent = "{use:2.1f}{unit}/{tot:2.1f}{unit}B".format(use=ram_status['use'] / divider, unit=unit, tot=szw)
        label_lfb = "(lfb {nblock}x{size}{unit}B)".format(nblock=lfb_status['nblock'],
                                                          size=lfb_status['size'],
                                                          unit=lfb_status['unit'])
        # Plot Linear Gauge
        linear_gauge(self.stdscr, offset=line_counter, size=width,
                     name='Mem',
                     value=int(ram_status['use'] / float(ram_status['tot']) * 100.0),
                     label=label_lfb,
                     percent=percent,
                     color=curses.color_pair(6))
        # IRAM linear gauge info
        if 'IRAM' in self.jetson.stats:
            iram_status = self.jetson.stats['IRAM']
            line_counter += 1
            szw, divider, unit = size_min(iram_status['tot'], start=iram_status['unit'])
            # lfb label
            percent = "{use:2.1f}{unit}/{tot:2.1f}{unit}B".format(use=iram_status['use'] / divider, unit=unit, tot=szw)
            label_lfb = "(lfb {size}{unit}B)".format(size=iram_status['lfb']['size'],
                                                     unit=iram_status['lfb']['unit'])
            linear_gauge(self.stdscr, offset=line_counter, size=width,
                         name='Imm',
                         value=int(iram_status['use'] / float(iram_status['tot']) * 100.0),
                         label=label_lfb,
                         percent=percent,
                         color=curses.color_pair(6))
        # SWAP linear gauge info
        line_counter += 1
        swap_status = self.jetson.stats.get('SWAP', {})
        swap_cached = swap_status.get('cached', {})
        szw, divider, unit = size_min(swap_status['tot'], start=swap_status['unit'])
        # lfb label
        percent = "{use:2.1f}{unit}/{tot:2.1f}{unit}B".format(use=swap_status['use'] / divider, unit=unit, tot=szw)
        label_lfb = "(cached {size}{unit}B)".format(size=swap_cached.get('size', '0'),
                                                    unit=swap_cached.get('unit', ''))
        linear_gauge(self.stdscr, offset=line_counter, size=width,
                     name='Swp',
                     value=int(swap_status.get('use', 0) / float(swap_status.get('tot', 1)) * 100.0),
                     label=label_lfb,
                     percent=percent,
                     status='ON' if swap_status else 'OFF',
                     color=curses.color_pair(6))
        # EMC linear gauge info
        line_counter += 1
        emc = self.jetson.stats.get('EMC', {})
        linear_gauge(self.stdscr, offset=line_counter, size=width,
                     name='EMC',
                     value=emc.get('val', 0),
                     status='ON' if emc else 'SUDO SUGGESTED',
                     label=label_freq(emc),
                     color=curses.color_pair(6))
        # GPU linear gauge info
        line_counter += 2
        gpu = self.jetson.stats.get('GR3D', {})
        linear_gauge(self.stdscr, offset=line_counter, size=width,
                     name='GPU',
                     value=gpu.get('val', 0),
                     label=label_freq(gpu),
                     status='ON' if gpu else 'SUDO SUGGESTED',
                     color=curses.color_pair(6))
        # Status disk
        line_counter += 1
        disk_status = self.jetson.disk
        linear_gauge(self.stdscr, offset=line_counter, size=width,
                     name='Dsk',
                     value=int(float(disk_status['used']) / float(disk_status['total']) * 100.0),
                     percent="{0:2.1f}GB/{1:2.1f}GB".format(disk_status['used'], disk_status['total']),
                     type_bar="#",
                     color=curses.color_pair(3))
        # Last part of information
        rectangle(self.stdscr, line_counter + 1, 0, height - 2, width - 1)
        mini_menu = 1
        mini_menu += 1 if self.jetson.stats['TEMP'] else 0
        mini_menu += 1 if self.jetson.stats['WATT'] else 0
        column_width = (width) // (mini_menu)
        # Plot compact info
        compact_info(self.stdscr, 0, line_counter + 1, column_width + 2, height - line_counter - 3, self.jetson)
        # Plot temperatures
        if self.jetson.stats['TEMP']:
            self.add_line(line_counter + 1, column_width + 2, height - (line_counter + 1) - 1)
            plot_temperatures(self.stdscr, column_width + 2, line_counter + 1, column_width - 4, height - line_counter - 3, self.jetson)
        # plot watts
        if self.jetson.stats['WATT']:
            self.add_line(line_counter + 1, 2 * column_width - 2, height - (line_counter + 1) - 1)
            plot_watts(self.stdscr, 2 * column_width - 1, line_counter + 1, column_width + 2, height - line_counter - 3, self.jetson)

    def add_line(self, pos_y, pos_x, height):
        """
        http://www.melvilletheatre.com/articles/ncurses-extended-characters/index.html
        """
        self.stdscr.addch(pos_y, pos_x, curses.ACS_TTEE)
        self.stdscr.vline(pos_y + 1, pos_x, curses.ACS_VLINE, height - 2)
        self.stdscr.addch(pos_y + height - 1, pos_x, curses.ACS_BTEE)
# EOF
