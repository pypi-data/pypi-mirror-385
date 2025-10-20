import logging
import random
import string
import hashlib
from markdownify import markdownify as md
import warnings
from bs4 import MarkupResemblesLocatorWarning

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
logger = logging.getLogger("default")


def replace_all(text, list_char, replacement):
    for i in list_char:
        text = text.replace(i, replacement)
    return text


def clean_str(name, replace_dots=False):
    replacement_list = ["-", " ", ",", "."] if replace_dots else ["-", " ", ","]
    return replace_all(name, replacement_list, "_")


def clean_name(name, prefix="", replace_dots=False):
    name = clean_str(name, replace_dots)
    if name and name[0].isdigit():
        name = "id_" + name
    elif name[0].isdigit() == "_":
        name = name[1:]
    return name


def generate_id(name=None, length=18):
    if name:
        h = hashlib.blake2b(digest_size=length)
        h.update(name.encode("utf-8") if isinstance(name, str) else name)
        return h.hexdigest()
    else:
        return "".join(
            random.choices(
                string.ascii_lowercase + string.digits + string.ascii_uppercase,
                k=length,
            )
        )


def get_rand_name(name=None, length=8):
    return "n" + generate_id(name=name, length=length)


# the soup.text strips off the html formatting also
def remove_html(string):

    if " " in string:
        text = md(
            string,
            strip=["img", "table", "a"],
            strong_em_symbol="*",
            escape_underscores=False,
            escape_asterisks=False,
            bullets=["-", "*"],
        )

        return text
    return string
