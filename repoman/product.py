"""
A product is a special package which is collection of
packages prepared together into a logical application.

For Fermi, this includes ScienceTools and GlastRelease.
"""

from .package import Package
from .manifest import find_manifest, read_manifest
import logging
import re

logger = logging.getLogger(__name__)


class Product(Package):

    def read_manifest(self):
        manifest_path = find_manifest(self.path)
        return read_manifest(manifest_path)

    # FIXME: Write this
    # def find_latest_tag(self):
    #     tags = self.repo.tags
    #
    # def find_head_tag(self):
    #     tags = self.repo.tags
    #
    # def find_last(self):
    #     head_pattern = re.compile(self.name + '-HEAD-1-\d*:')
    #     tags = self.repo.tags
    #     heads = [tag.name for tag in tags if re.findall(head_pattern, tag.name)]
    #     if not heads:
    #         logger.error("no match found")
    #         return ""
    #
    #     nhead = 0
    #     for h in heads:
    #         mobj = self.numPat.search(h)
    #         if int(mobj.group(1)) > nhead:
    #             nhead = int(mobj.group(1))
    #     return self.name + '-HEAD-1-' + str(nhead)


