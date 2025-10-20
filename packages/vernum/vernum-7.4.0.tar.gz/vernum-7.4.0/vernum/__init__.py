import re

from wizlib.app import WizApp
from wizlib.stream_handler import StreamHandler
from wizlib.config_handler import ConfigHandler
from wizlib.ui_handler import UIHandler

from vernum.command import VerNumCommand

FORMAT = re.compile(r"^v?(\d+)\.(\d+)\.(?:(\d+)|beta(\d+)|alpha(\d+))$")


class VerNumApp(WizApp):

    base = VerNumCommand
    name = 'vernum'
    handlers = [StreamHandler, ConfigHandler, UIHandler]
