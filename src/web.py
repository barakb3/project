import click
from flask import Flask
from pathlib import Path


_INDEX_HTML = '''
<html>
    <head>
        <title>Brain Computer Interface</title>
    </head>
    <body>
        <ul>
            {users}
        </ul>
    </body>
</html>
'''
_USER_LINE_HTML = '''
<li><a href="/users/{user_id}">user {user_id}</a></li>
'''

_USER_HTML = '''
<html>
    <head>
        <title>Brain Computer Interface: User {id}</title>
    </head>
    <body>
        <table>
            {thoughts}
        </table>
    </body>
</html>
'''
_THOUGHT_LINE_HTML = '''
<tr><td>{time_stamp}</td><td>{thought}</td></tr>
'''


website = Flask(__name__)


def get_users(data_dir: str) -> list:
    data_dir_path = Path(data_dir)
    users = []
    for user_dir in data_dir_path.iterdir():
        users.append(_USER_LINE_HTML.format(user_id=user_dir.name))
    return users


@click.command()
@click.argument("address")
@click.argument("data_dir", type=click.Path(exists=True))
def run_webserver(address: str, data_dir: str):
    """
    Creates a web page for the server that serves some data directory in which
    the user numbers can be found, and each one of them holds the thoughts of
    this user.
    Currently works only for at most 5 users.

    :param address: A host and a port, e.g.: 127.0.0.1:5000.
    :type address: str
    :param data_dir: A path to the data directory the server will serve.
    :type data_dir: str ot Path-like objects

    """
    @website.route("/")
    def index():
        users = get_users(data_dir=data_dir)
        index_html = _INDEX_HTML.format(users="\n".join(users))
        return index_html

    @website.route("/users/1")
    def user1():
        user_dir_path = Path(data_dir) / "1"
        thoughts = []
        for thought_file in user_dir_path.iterdir():
            thoughts.append(_THOUGHT_LINE_HTML
                            .format(
                                    time_stamp=thought_file.name[0:10] + " "
                                    + thought_file.name[11:13] + ":"
                                    + thought_file.name[14:16] + ":"
                                    + thought_file.name[17:19],
                                    thought=thought_file.read_text())
                            )
        user_html = _USER_HTML.format(id="1", thoughts="\n".join(thoughts))
        return user_html

    @website.route("/users/2")
    def user2():
        user_dir_path = Path(data_dir) / "2"
        thoughts = []
        for thought_file in user_dir_path.iterdir():
            thoughts.append(_THOUGHT_LINE_HTML
                            .format(
                                    time_stamp=thought_file.name[0:10] + " "
                                    + thought_file.name[11:13] + ":"
                                    + thought_file.name[14:16] + ":"
                                    + thought_file.name[17:19],
                                    thought=thought_file.read_text())
                            )
        user_html = _USER_HTML.format(id="2", thoughts="\n".join(thoughts))
        return user_html

    @website.route("/users/3")
    def user3():
        user_dir_path = Path(data_dir) / "3"
        thoughts = []
        for thought_file in user_dir_path.iterdir():
            thoughts.append(_THOUGHT_LINE_HTML
                            .format(
                                    time_stamp=thought_file.name[0:10] + " "
                                    + thought_file.name[11:13] + ":"
                                    + thought_file.name[14:16] + ":"
                                    + thought_file.name[17:19],
                                    thought=thought_file.read_text())
                            )
        user_html = _USER_HTML.format(id="3", thoughts="\n".join(thoughts))
        return user_html

    @website.route("/users/4")
    def user4():
        user_dir_path = Path(data_dir) / "4"
        thoughts = []
        for thought_file in user_dir_path.iterdir():
            thoughts.append(_THOUGHT_LINE_HTML
                            .format(
                                    time_stamp=thought_file.name[0:10] + " "
                                    + thought_file.name[11:13] + ":"
                                    + thought_file.name[14:16] + ":"
                                    + thought_file.name[17:19],
                                    thought=thought_file.read_text())
                            )
        user_html = _USER_HTML.format(id="4", thoughts="\n".join(thoughts))
        return user_html

    @website.route("/users/5")
    def user5():
        user_dir_path = Path(data_dir) / "5"
        thoughts = []
        for thought_file in user_dir_path.iterdir():
            thoughts.append(_THOUGHT_LINE_HTML
                            .format(
                                    time_stamp=thought_file.name[0:10] + " "
                                    + thought_file.name[11:13] + ":"
                                    + thought_file.name[14:16] + ":"
                                    + thought_file.name[17:19],
                                    thought=thought_file.read_text())
                            )
        user_html = _USER_HTML.format(id="5", thoughts="\n".join(thoughts))
        return user_html

    ip, port = address.split(":", 1)
    website.run(host=ip, port=int(port))
