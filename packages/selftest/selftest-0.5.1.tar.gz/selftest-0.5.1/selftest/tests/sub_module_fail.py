## begin license ##
#
# "selftest": a simpler test runner for python
#
# Copyright (C) 2022-2023 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "selftest"
#
# "selftest" is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# "selftest" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "selftest".  If not, see <http://www.gnu.org/licenses/>.
#
## end license ##

import selftest

test = selftest.get_tester(__name__)


@test
def tiedeldom():
    assert 42 == 43, "fail I will"
