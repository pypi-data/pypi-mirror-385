from dataclasses import dataclass
from argparse import ArgumentParser
import os

from wizlib.command import WizCommand
from wizlib.stream_handler import StreamHandler
from wizlib.config_handler import ConfigHandler

from vernum.scheme import Scheme
from vernum.error import VerNumError


class VerNumCommand(WizCommand):

    default = 'full'
    # handlers = [StreamHandler, ConfigHandler]

    @property
    def scheme(self):
        name = self.app.config.get('vernum-scheme') or 'patch'
        scheme = Scheme.family_member('name', name)
        if not scheme:
            raise VerNumError(f"Invalid scheme '{name}'")
        return scheme
