import json
import os
import shutil
import threading
import sublime
from urllib.request import urlopen, Request
import re

API_BASE_URL = "https://api.gitsecure.dev/v1"


def get_token_path():
    path = sublime.cache_path()
    token_path = os.path.join(path, "wasps")
    return token_path


def create_token(text):
    token_path = get_token_path()
    file = os.path.join(token_path, "token.txt")
    os.makedirs(token_path, exist_ok=True)

    with open(file, "w", encoding="utf-8") as f:
        f.write(text)


def remove_token():
    token_path = get_token_path()
    shutil.rmtree(token_path, ignore_errors=True)


def get_token() -> str:
    token_path = get_token_path()

    try:
        file = os.path.join(token_path, "token.txt")
        with open(file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def post(url_path: str, body: dict):
    token = get_token()
    params = json.dumps(body).encode("utf8")
    req = Request(
        url=API_BASE_URL + url_path,
        data=params,
        headers={
            "content-type": "application/json",
            "Authorization": "Token %s" % token,
        },
    )

    try:
        res = urlopen(req).read().decode("utf-8")
        return json.loads(res)
    except Exception as err:
        return {"message": str(err)}


def security_review(body: dict):
    return post("/wasps/review/", body)


def token_present() -> bool:
    return get_token() != ""


def build_result_list(title, items):
    if not items:
        return ""

    text = """<h3>%s</h3>""" % title
    for item in items:
        text += """<code style="color: red">* %s</code><br>""" % item["title"]
        text += """line number: %s<br>""" % item["line_no"]
        text += """Key type: %s<br>""" % item["key_type"]
        text += (
            """Severity: <code style="background-color: brown; color: white; padding: 2px">%s</code><br>"""
            % item["severity"].upper()
        )
        text += (
            """<h4>Vulnerable line</h4><p style="background-color: brown; color: white; padding: 2px; margin: 2px;">%s</p>"""
            % item["secret"]
        )
        text += "<p>%s</p>" % item["description"]

    return text


def show_scan_result(window, url, data):
    result = post(url, data)

    if "message" in result:
        output = result["message"]
    else:
        output = build_result_list("Vulnerable code", result["vulnerability_scanner"])
        output += build_result_list("Secret leak", result["secret_scanner"])

    window.new_html_sheet("Wasps Scanner result", output)


def show_review_result(window, url, data):
    result = post(url, data)

    if "message" in result:
        output = result["message"]
    else:
        output = result["code_review"]
        output = re.sub(r"\\*\\*(:.*?)\\*\\*", "<strong>\1</strong><br>", output)
        output = re.sub(r"\*(:.*?)\*", "<strong>\1</strong>", output)
        output = output.replace("\n\n", "<br><br>")

    window.new_html_sheet("Wasps Review result", output)
