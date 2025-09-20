"""Create symlinks for package versions"""

# Standard
import string
import random
import os

# Rez
from rez.release_hook import ReleaseHook
from rez.system import system
from rez.utils.logging_ import print_error
from rez.utils.scope import scoped_formatter
from rez.vendor.schema.schema import Or


class HHSymlinkReleaseHook(ReleaseHook):

    schema_dict = {}

    @classmethod
    def name(cls):
        return "hh_symlink"

    def __init__(self, source_path):
        super(HHSymlinkReleaseHook, self).__init__(source_path)

    def post_release(self,
                     user,
                     install_path,
                     variants,
                     release_message=None,
                     changelog=None,
                     previous_version=None,
                     **kwargs):

        pck_name = self.package.name
        pck_version = str(self.package.version)

        pck_dir = os.path.join(install_path, pck_name)

        latest_dir = os.path.join(pck_dir, "latest")
        current_dir = os.path.join(pck_dir, "current")

        # -----------------------------------------
        # Create "latest" symlink
        # -----------------------------------------
        print()
        print("--------------------hh_symlink - release hook--------------------")

        if os.path.islink(latest_dir):
            # NOTE: If symlink already exists and we are forcing its recreation,
            # one the safest ways to do so, although still open for some rare
            # race conditions, is to create a temp symlink pointing to path
            # and rename afterwards.
            rnd_str = [random.choice(string.ascii_letters + string.digits) for n in range(6)]
            temp_link = latest_dir + "_" + "".join(rnd_str)

            os.symlink(pck_version, temp_link)
            os.rename(temp_link, latest_dir)
        else:
            os.symlink(pck_version, latest_dir)

        # -----------------------------------------
        # Create "current" symlink (if not there)
        # -----------------------------------------
        if not os.path.islink(current_dir):
            os.symlink("latest", current_dir)


def register_plugin():
    return HHSymlinkReleaseHook
