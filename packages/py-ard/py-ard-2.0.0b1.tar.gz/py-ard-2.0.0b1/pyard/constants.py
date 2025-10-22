#
#    py-ard
#    Copyright (c) 2023 Be The Match operated by National Marrow Donor Program. All Rights Reserved.
#
#    This library is free software; you can redistribute it and/or modify it
#    under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 3 of the License, or (at
#    your option) any later version.
#
#    This library is distributed in the hope that it will be useful, but WITHOUT
#    ANY WARRANTY; with out even the implied warranty of MERCHANTABILITY or
#    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
#    License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this library;  if not, write to the Free Software Foundation,
#    Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA.
#
#    > http://www.fsf.org/licensing/licenses/lgpl.html
#    > http://www.opensource.org/licenses/lgpl-license.php
#
import re

DEFAULT_CACHE_SIZE = 1_000

HLA_regex = re.compile("^HLA-")

VALID_REDUCTION_TYPES = ("G", "P", "lg", "lgx", "W", "exon", "U2", "S")
expression_chars = ("N", "Q", "L", "S")
# List of P and G characters
P_and_G_chars = ("P", "G")

# Loci with G group data
# Retrieved from lgx_group
# sqlite> select distinct(substr(allele, 1, instr(allele, '*') - 1)) from lgx_group;
G_GROUP_LOCI = (
    "A",
    "B",
    "C",
    "DMA",
    "DMB",
    "DOA",
    "DOB",
    "DPA1",
    "DPB1",
    "DQA1",
    "DQB1",
    "DRA",
    "DRB1",
    "DRB3",
    "DRB4",
    "DRB5",
    "E",
    "F",
    "G",
)
