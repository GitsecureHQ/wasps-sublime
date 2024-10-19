import os
import sys
from threading import Thread
import sublime
import sublime_plugin
import random
from .wasps import utils as ut
import json

actions = [
    "Wasps - AI Code Review",
    "Wasps - Security Review",
]


class SecurityReviewCommand(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        view = self.window.active_view()

        if not ut.token_present():

            window.status_message(
                "Please enter a token or visit https://gitsecure.dev to get a token"
            )
            return

        file_name = view.file_name().replace("\\", "/")
        file_name = os.path.basename(file_name)

        x, y = view.visible_region().to_tuple()
        x = 0
        x, y = sorted((x, y))

        region = sublime.Region(x, y)
        content = view.substr(region)

        data = {"content": content, "filename": file_name}
        window.status_message(
            "Please wait up to a minute while Wasps analyze your code ..."
        )

        Thread(
            target=ut.show_scan_result,
            args=(window, "/integration/wasp/scanner/", data),
        ).start()


class AiCodeReviewCommand(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        view = self.window.active_view()

        if not ut.token_present():

            window.status_message(
                "Please enter a token or visit https://gitsecure.dev to get a token"
            )
            return

        file_name = view.file_name().replace("\\", "/")
        file_name = os.path.basename(file_name)
        x, y = view.sel()[0].to_tuple()
        x, y = sorted((x, y))

        if x == y:
            x = 0

        region = sublime.Region(x, y)
        content = view.substr(region)

        data = {"content": content, "filename": file_name}
        window.status_message("Please wait while wasps review your code ...")

        Thread(
            target=ut.show_review_result,
            args=(window, "/integration/wasp/review/", data),
        ).start()


class ApiKeyCommand(sublime_plugin.WindowCommand):
    def run(self):
        initial_text = ut.get_token()

        if not initial_text:
            ut.remove_token()

        self.window.show_input_panel(
            "Enter your Wasps API Key: ", initial_text, self.on_done, None, None
        )

    def on_done(self, text: str):
        ut.create_token(text)
