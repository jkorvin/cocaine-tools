#
# Copyright (c) 2013+ Evgeny Safronov <division494@gmail.com>
# Copyright (c) 2013+ Anton Tiurin <noxiouz@yandex.ru>
# Copyright (c) 2011-2014 Other contributors as noted in the AUTHORS file.
#
# This file is part of Cocaine-tools.
#
# Cocaine is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Cocaine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import time

from cocaine.services import Service, Locator
from cocaine.exceptions import ConnectionError, ConnectionRefusedError, ServiceError

from cocaine.tools import actions
from cocaine.tools.actions import app
from cocaine.tools.actions import profile
from cocaine.tools.actions import runlist
from cocaine.tools.actions import common

from nose import tools


@tools.raises(ConnectionRefusedError, ConnectionError)
def test_storage_bad_address():
    st = actions.Storage()
    st.connect(port=10055)


def test_list():
    st = Service("storage")
    result = actions.List("apps", ["app"], st).execute().wait(4)
    assert isinstance(result, (list, tuple)), result


def test_specific():
    st = Service("storage")
    actions.Specific(st, "entity", "name")


@tools.raises(ValueError)
def test_specific_unspecified_name():
    st = Service("storage")
    actions.Specific(st, "entity", "")


def test_isJsonValid():
    valid = "{}"
    invalid = ":dsdll"
    assert actions.isJsonValid(valid)
    assert not actions.isJsonValid(invalid)


# @tools.raises(Exception)
# def test_view():
#     st = Service("storage")
#     view = actions.View(st, "profile", "TEST2", "profiles")
#     data = view.execute().wait(1)
#     assert data is not None, data


class TestAppActions(object):
    def __init__(self):
        self.storage = Service("storage")
        self.node = Service("node")
        self.locator = Locator()

    def test_app_list(self):
        listing = app.List(self.storage).execute().wait(4)
        assert isinstance(listing, (list, tuple))

    def test_app_start(self):
        name = "random_name"
        result = app.Start(self.node, name,
                           "random_profile").execute().wait(4)
        assert isinstance(result, dict) and name in result

    def test_app_stop(self):
        name = "random_name"
        result = app.Stop(self.node,
                          name).execute().wait(4)
        assert isinstance(result, dict) and name in result

    def test_restart(self):
        name = "random_name"
        profile_name = "random_profile"
        result = app.Restart(self.node, self.locator,
                             name, profile_name,
                             self.storage).execute().wait(4)

        assert len(result) == 2 and name in result[0] and name in result[1], result

    def test_NodeInfo(self):
        n = common.NodeInfo(self.node, self.locator, self.storage)
        result = n.execute().wait(100)
        assert isinstance(result, dict) and "apps" in result

    # def test_remove(self):
    #     name = "blabla"
    #     app.Remove(self.storage, name).execute().wait(1)


class TestProfileActions(object):
    def __init__(self):
        self.storage = Service("storage")
        self.node = Service("node")

    def test_profile(self):
        name = "dummy_profile_name %d" % time.time()
        dummy_profile = {"aaa": [1, 2, 3]}
        profile.Upload(self.storage, name, dummy_profile).execute().wait(4)

        listing = profile.List(self.storage).execute().wait(4)
        assert isinstance(listing, (list, tuple)), listing
        assert name in listing

        pr = profile.View(self.storage, name).execute().wait(4)
        assert pr == dummy_profile

        profile.Remove(self.storage, name).execute().wait(4)
        try:
            profile.View(self.storage, name).execute().wait(4)
        except ServiceError:
            pass


class TestRunlistActions(object):
    def __init__(self):
        self.storage = Service("storage")

    def test_runlist(self):
        name = "dummy_runlist %d" % time.time()
        app_name = "test_app"
        profile_name = "test_profile"
        dummy_runlist = {app_name: profile_name}
        runlist.Upload(self.storage, name, dummy_runlist).execute().wait(4)

        listing = runlist.List(self.storage).execute().wait(4)
        assert isinstance(listing, (list, tuple)), listing
        assert name in listing

        res = runlist.View(self.storage, name).execute().wait(4)
        assert isinstance(res, dict), res
        assert res == dummy_runlist, res

        runlist.Remove(self.storage, name).execute().wait(4)
        try:
            runlist.View(self.storage, name).execute().wait(4)
        except ServiceError:
            pass

        runlist.Create(self.storage, name).execute().wait(4)
        res = runlist.View(self.storage, name).execute().wait(4)
        assert res == {}, res

        res = runlist.AddApplication(self.storage, name, app_name, profile_name, force=True).execute().wait(4)
        assert isinstance(res, dict), res
        assert "added" in res, res
        assert app_name == res["added"]["app"] and profile_name == res["added"]["profile"], res

        res = runlist.RemoveApplication(self.storage, name, app_name).execute().wait(4)
        assert isinstance(res, dict), res
