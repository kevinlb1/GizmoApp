import os

from .emmie_server import create_app

app = create_app(shell_variant=os.getenv("EMMIE_SHELL"))
