# -*- coding: utf-8 -*-

# Copyright 2013 Fanficdownloader team, 2018 FanFicFare team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import absolute_import
import logging
logger = logging.getLogger(__name__)

# py2 vs py3 transition

from .adapter_storiesonlinenet import StoriesOnlineNetAdapter

def getClass():
    return StoryRoomComAdapter

# Class name has to be unique.  Our convention is camel case the
# sitename with Adapter at the end.  www is skipped.
class StoryRoomComAdapter(StoriesOnlineNetAdapter):

    @classmethod
    def getSiteAbbrev(cls):
        return 'stryrm'

    @staticmethod # must be @staticmethod, don't remove it.
    def getSiteDomain():
        # The site domain.  Does have www here, if it uses it.
        return 'storyroom.com'

    @classmethod
    def getAcceptDomains(cls):
        return ['finestories.com',cls.getSiteDomain()]

    @classmethod
    def getConfigSections(cls):
        "Only needs to be overriden if has additional ini sections."
        return ['finestories.com',cls.getSiteDomain()]

    @classmethod
    def getSiteURLPattern(self):
        return r"https?://("+r"|".join([x.replace('.',r'\.') for x in self.getAcceptDomains()])+r")/(?P<path>s|n|library)/(storyInfo.php\?id=)?(?P<id>\d+)(?P<chapter>:\d+)?(?P<title>/.+)?((;\d+)?$|(:i)?$)?"
