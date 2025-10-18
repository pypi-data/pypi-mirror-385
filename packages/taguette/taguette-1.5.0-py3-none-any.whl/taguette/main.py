import argparse
import asyncio
import base64
import gettext
import importlib_resources
import locale
import logging
import os
import prometheus_client
import re
import secrets
import string
import subprocess
import sys
import tornado.ioloop
from urllib.parse import urlparse
import webbrowser

import taguette
from . import exact_version
from . import database
from .web import make_app


logger = logging.getLogger(__name__)


PROM_VERSION = prometheus_client.Gauge('version', "Application version",
                                       ['version'])


def prepare_db(database):
    # Windows paths kinda look like URLs, but aren't
    if sys.platform == 'win32' and re.match(r'^[a-zA-Z]:\\', database):
        logger.info("Database URL recognized as Windows path")
        url = None
    else:
        url = urlparse(database)
    if url is not None and url.scheme:
        # Full URL: use it, create path if sqlite
        db_url = database
        if url.scheme == 'sqlite' and url.path.startswith('/'):
            os.makedirs(os.path.dirname(url.path[1:]), exist_ok=True)
    else:
        # Path: create it, turn into URL
        database = os.path.expanduser(database)
        if os.path.dirname(database):
            os.makedirs(os.path.dirname(database), exist_ok=True)
        db_url = 'sqlite:///' + database
        logger.info("Turning database path into URL: %s", db_url)
    return db_url


def get_join_url(app):
    url = 'http://localhost'
    if app.config['PORT'] != 80:
        url += ':%d' % app.config['PORT']
    if app.config['BASE_PATH'] not in ('', '/'):
        url += '/' + app.config['BASE_PATH'].strip('/')
    url += '/'
    token = app.single_user_token
    if token:
        url += '?token=%s' % token
    return url


def default_config(output):
    if output is None:
        out = sys.stdout
    else:
        out = open(output, 'w')
    out.write('''\
# This is the configuration file for Taguette
# It is a Python file, so you can use the full Python syntax

# Name of this server
NAME = "Misconfigured Taguette Server"

# Address and port to listen on
BIND_ADDRESS = "0.0.0.0"
PORT = 7465

# Base path of the application
BASE_PATH = "/"

# The domain of the application (used in emails)
DOMAIN = ""

# A unique secret key that will be used to sign cookies
SECRET_KEY = "{secret}"

# Database to use
# This is a SQLAlchemy connection URL; refer to their documentation for info
# https://docs.sqlalchemy.org/en/latest/core/engines.html
# If using SQLite3 on Unix, note the 4 slashes for an absolute path
# (keep 3 before a relative path)
DATABASE = "sqlite:////non/existent/taguette/database.sqlite3"

# Redis instance for live collaboration
# This is not required if using a single server, collaboration will still work
#REDIS_SERVER = 'redis://localhost:6379'

# Address to send system emails from
EMAIL = "Misconfigured Taguette Server <taguette@example.com>"

# Terms of service (HTML file)
TOS_FILE = 'tos.html'
# If set to None, no terms of service link will be displayed anywhere
#TOS_FILE = None

# Extra footer at the bottom of every page
#EXTRA_FOOTER = """
#  | This instance of Taguette is managed by Example University.
#  Please <a href="mailto:it@example.org">email IT</a> with any questions.
#"""

# Default language
DEFAULT_LANGUAGE = 'en_US'

# SMTP server to use to send emails
MAIL_SERVER = {{
    "ssl": False,
    "host": "localhost",
    "port": 25,
}}

# Whether users must explicitly accept cookies before using the website
COOKIES_PROMPT = False

# Whether new users can create an account
REGISTRATION_ENABLED = True

# Whether users can import projects from SQLite3 files
SQLITE3_IMPORT_ENABLED = True

# Set this to true if you are behind a reverse proxy that sets the
# X-Forwarded-For header.
# Leave this at False if users are connecting to Taguette directly
X_HEADERS = False

# Time limits for converting documents
CONVERT_TO_HTML_TIMEOUT = 3 * 60  # 3min for importing document into Taguette
CONVERT_FROM_HTML_TIMEOUT = 3 * 60  # 3min for exporting from Taguette

# If you want to export metrics using Prometheus, set a port number here
#PROMETHEUS_LISTEN = "0.0.0.0:9101"

# If you want to report errors to Sentry, set your DSN here
#SENTRY_DSN = "https://<key>@sentry.io/<project>"
'''.format(secret=base64.b64encode(os.urandom(30)).decode('ascii')))
    if output is not None:
        out.close()


DEFAULT_CONFIG = {
    'MULTIUSER': True,
    'BIND_ADDRESS': '0.0.0.0',
    'BASE_PATH': '',
    'EXTRA_FOOTER': None,
    'REGISTRATION_ENABLED': True,
    'REDIS_SERVER': None,
    'SQLITE3_IMPORT_ENABLED': True,
    'DEFAULT_LANGUAGE': 'en_US',
    'CONVERT_FROM_HTML_TIMEOUT': 3 * 60,
    'CONVERT_TO_HTML_TIMEOUT': 3 * 60,
    'OPF_OUT_SIZE_LIMIT': 5000000,  # 5 MB
    'HTML_OUT_SIZE_LIMIT': 2000000,  # 2 MB
}

REQUIRED_CONFIG = [
    'NAME', 'PORT', 'SECRET_KEY', 'DATABASE', 'TOS_FILE', 'DOMAIN',
    'X_HEADERS', 'EMAIL', 'MAIL_SERVER', 'COOKIES_PROMPT',
]


async def _set_password(user):
    import getpass
    try:
        passwd = getpass.getpass("Enter password for user %r: " % user.login)
    except (OSError, EOFError):
        character_set = (
            string.ascii_lowercase
            + string.ascii_uppercase
            + string.digits
        )
        passwd = ''.join(secrets.choice(character_set) for _ in range(16))
        logger.warning(
            "Can't prompt for a password, setting admin password to: %s",
            passwd,
        )
    await user.set_password(passwd)


def main():
    logging.root.handlers.clear()
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s: %(message)s")
    locale.setlocale(locale.LC_ALL, '')
    lang = locale.getlocale()[0]
    lang = [lang] if lang else []
    d = importlib_resources.files('taguette').joinpath('l10n')
    trans = gettext.translation('taguette_main', d, lang, fallback=True)
    taguette._trans = trans
    _ = trans.gettext

    if sys.platform == 'win32' and sys.version_info >= (3, 8):
        # https://github.com/tornadoweb/tornado/issues/2608
        try:
            from asyncio import WindowsSelectorEventLoopPolicy
        except ImportError:
            pass
        else:
            policy = asyncio.get_event_loop_policy()
            if not isinstance(policy, WindowsSelectorEventLoopPolicy):
                asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    toplevel = os.path.dirname(os.path.dirname(__file__))
    if os.path.exists(os.path.join(toplevel, '.git')):
        try:
            version = subprocess.check_output(
                ['git', '--git-dir=.git', 'describe'],
                cwd=toplevel,
                stderr=subprocess.PIPE,
            ).decode('utf-8').strip()
        except (OSError, subprocess.CalledProcessError):
            logger.info("Can't get version from Git, using version=%s",
                        exact_version())
        else:
            logger.info("Running from Git repository, using version=%s",
                        version)
            if version.startswith('v'):
                taguette._exact_version = version[1:]
    else:
        logger.info("Not a Git repository, using version=%s", exact_version())
    PROM_VERSION.labels(exact_version()).set(1)

    if sys.platform == 'win32':
        import ctypes.wintypes

        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None,
                                               SHGFP_TYPE_CURRENT, buf)

        default_db = os.path.join(buf.value, 'Taguette', 'taguette.sqlite3')
        default_db_show = os.path.join(os.path.basename(buf.value),
                                       'Taguette', 'taguette.sqlite3')
    else:
        data = os.environ.get('XDG_DATA_HOME')
        if not data:
            data = os.path.join(os.environ['HOME'], '.local', 'share')
            default_db_show = '$HOME/.local/share/taguette/taguette.sqlite3'
        else:
            default_db_show = '$XDG_DATA_HOME/taguette/taguette.sqlite3'
        default_db = os.path.join(data, 'taguette', 'taguette.sqlite3')

    parser = argparse.ArgumentParser(
        description="Document tagger for qualitative analysis",
    )
    parser.add_argument('--version', action='version',
                        version='taguette version %s' % exact_version())
    parser.add_argument('-p', '--port', default='7465',
                        help=_("Port number on which to listen"))
    parser.add_argument('-b', '--bind', default='127.0.0.1',
                        help=_("Address to bind on"))
    parser.add_argument('--browser', action='store_true', default=True,
                        help=_("Open web browser to the application"))
    parser.add_argument('--no-browser', action='store_false', dest='browser',
                        help=_("Don't open the web browser"))
    parser.add_argument('--debug', action='store_true', default=False,
                        help=argparse.SUPPRESS)
    parser.add_argument('--database', action='store',
                        default=default_db,
                        help=_("Database location or connection string, for "
                               "example 'project.db' or "
                               "'postgresql://me:pw@localhost/mydb' "
                               "(default: %(default)r)") %
                        dict(default=default_db_show))
    parser.add_argument('--set-umask', action='store', dest='umask',
                        default="077",
                        help=_("Set the file creation mask (umask) on systems "
                               "that support it."))
    parser.add_argument('--dont-set-umask', action='store_const', dest='umask',
                        const=None,
                        help=_("Don't change umask on startup"))
    parser.set_defaults(
        func=None,  # Function to run instead of default, e.g. migrate, server
        func1=None,  # Run immediately, e.g. before anything is logged
    )

    subparsers = parser.add_subparsers(title=_("additional commands"),
                                       metavar='', dest='cmd')

    parser_migrate = subparsers.add_parser('migrate',
                                           help=_("Manually trigger a "
                                                  "database migration"))
    parser_migrate.add_argument('revision', action='store', default='head',
                                nargs=argparse.OPTIONAL)
    parser_migrate.set_defaults(func=lambda args: database.migrate(
        prepare_db(args.database),
        args.revision,
    ))

    parser_config = subparsers.add_parser(
        'default-config',
        help=_("Print the default server configuration"))
    parser_config.add_argument('--output', '-o', action='store', nargs=1,
                               help=_("Output to this file rather than "
                                      "stdout"))
    parser_config.set_defaults(func1=lambda args: default_config(args.output))

    parser_server = subparsers.add_parser(
        'server',
        help=_("Run in server mode, suitable for a multi-user deployment"))
    parser_server.add_argument('config_file',
                               help=_("Configuration file for the server. The "
                                      "default configuration can be generated "
                                      "using the `default-config` command"))

    args = parser.parse_args()

    if args.func1:
        args.func1(args)
        sys.exit(0)

    if args.umask is not None:
        if not re.match(r'^[0-7][0-7][0-7]$', args.umask):
            print(_("Invalid umask: %(arg)s") % dict(arg=args.umask),
                  file=sys.stderr, flush=True)
            sys.exit(2)
        logger.info("Setting umask to %s", args.umask)
        os.umask(int(args.umask, 8))

    if args.func:
        args.func(args)
        sys.exit(0)

    if args.cmd == 'server':
        # Set configuration from config file
        config = {}
        config_file = os.path.abspath(args.config_file)
        with open(config_file) as fp:
            code = compile(fp.read(), config_file, 'exec')
        exec(code, config)
        config = dict(
            DEFAULT_CONFIG,
            **config
        )
        missing = False
        for key in REQUIRED_CONFIG:
            if key not in config:
                print(_("Missing required configuration variable %(var)s") %
                      dict(var=key),
                      file=sys.stderr, flush=True)
                missing = True
        if missing:
            sys.exit(2)

        if config['BASE_PATH'] and config['BASE_PATH'][0] != '/':
            print(_("Invalid BASE_PATH"))
            sys.exit(2)
        config['BASE_PATH'] = config['BASE_PATH'].strip('/')
        if config['BASE_PATH']:
            config['BASE_PATH'] = '/' + config['BASE_PATH']

        if not config['DOMAIN']:
            print(_("Invalid DOMAIN"))
            sys.exit(2)
    else:
        if args.debug:
            # Use a deterministic secret key, to avoid it changing during
            # auto-reload and such
            secret = 'debug'
        else:
            secret = os.urandom(30).decode('iso-8859-15')

        # Set configuration from command-line
        config = dict(
            DEFAULT_CONFIG,
            MULTIUSER=False,
            DOMAIN='localhost:' + str(int(args.port)),
            BIND_ADDRESS=args.bind,
            X_HEADERS=False,
            SQLITE3_IMPORT_ENABLED=True,
            PORT=int(args.port),
            DATABASE=prepare_db(args.database),
            TOS_FILE=None,
            SECRET_KEY=secret,
            COOKIES_PROMPT=False,
            HTML_OUT_SIZE_LIMIT=5000000,  # 5 MB
        )

    if 'PROMETHEUS_LISTEN' in config:
        p_addr = None
        p_port = config['PROMETHEUS_LISTEN']
        if isinstance(p_port, str):
            if ':' in p_port:
                p_addr, p_port = p_port.split(':')
                p_addr = p_addr or None
            p_port = int(p_port)
        logger.info("Starting Prometheus exporter on port %d", p_port)
        prometheus_client.start_http_server(p_port, p_addr)

    if 'SENTRY_DSN' in config:
        import sentry_sdk
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.tornado import TornadoIntegration
        logger.info("Initializing Sentry")
        sentry_sdk.init(
            dsn=config['SENTRY_DSN'],
            integrations=[TornadoIntegration(), SqlalchemyIntegration()],
            ignore_errors=[KeyboardInterrupt],
            release='taguette@%s' % exact_version(),
        )

    app = make_app(config, debug=args.debug)
    app.listen(config['PORT'], address=config['BIND_ADDRESS'],
               xheaders=config.get('X_HEADERS', False))
    loop = tornado.ioloop.IOLoop.current()

    db = app.DBSession()
    admin = db.query(database.User).get('admin')
    if admin is None:
        logger.warning("Creating user 'admin'")
        admin = database.User(login='admin')
        if config['MULTIUSER']:
            loop.run_sync(lambda: _set_password(admin))
        db.add(admin)
        db.commit()
    elif config['MULTIUSER'] and not admin.hashed_password:
        loop.run_sync(lambda: _set_password(admin))
        db.commit()
    db.close()

    if args.debug:
        logger.warning("Debug mode is ON")
        asyncio.get_event_loop().set_debug(True)

    url = get_join_url(app)
    print(_("\n    Taguette %(version)s is now running. You can connect to it "
            "using this link:\n\n    %(url)s\n") %
          dict(url=url, version=exact_version()), flush=True)

    if args.browser and not args.debug:
        loop.call_later(0.01, webbrowser.open, url)

    loop.start()


if __name__ == '__main__':
    main()
