from typing import Optional, Tuple
import argparse
import re


def valid_proxy_line(proxy):
    part = proxy.partition(" ")

    if part[1] == "":
        return (part[0], "")

    return (part[0], part[2].lstrip())


def valid_proxy_file(proxies):
    ret = []
    for line in proxies.split("\n"):
        line = line.strip()
        if line == "":
            continue
        ret.append(valid_proxy_line(line))
    return ret


def valid_proxy(src):
    if src[:1] == "@":
        filename = src[1:]
        if filename == "-":
            filename = "/dev/stdin"
        with open(filename, "r") as f:
            data = f.read()
        return valid_proxy_file(data)

    return valid_proxy_file(src)


def valid_header_line(header):
    part = header.partition(":")

    if part[1] == "" and ((name := header[-1:]) == ";"):
        return (name.rstrip(), "")

    if part[1] == "" or not re.fullmatch(r"[a-zA-Z0-9#$%^&*+/`~_|.?'-]+", part[0]):
        raise argparse.ArgumentTypeError('Invalid header "{}"'.format(header))
    return (part[0], part[2].lstrip())


def valid_header_file(headers):
    ret = []
    for line in headers.split("\n"):
        line = line.strip()
        if line == "":
            continue
        ret.append(valid_header_line(line))
    return ret


def valid_header(src):
    if src[:1] == "@":
        filename = src[1:]
        if filename == "-":
            filename = "/dev/stdin"
        with open(filename, "r") as f:
            data = f.read()
        return valid_header_file(data)

    return valid_header_file(src)


def valid_cookie_line(cookie):
    part = cookie.partition("=")

    if part[1] == "":
        raise argparse.ArgumentTypeError('Invalid cookie "{}"'.format(cookie))
    return (part[0], part[2].lstrip())


def valid_cookie_file(cookies):
    ret = []
    for line in cookies.replace("\n", ";").split(";"):
        line = line.strip()
        if line == "":
            continue
        ret.append(valid_cookie_line(line))
    return ret


def valid_cookie(src):
    if src.find("=") == -1:
        filename = src[1:]
        if filename == "-":
            filename = "/dev/stdin"
        with open(filename, "r") as f:
            data = f.read()
        return valid_cookie_file(data)
    return valid_cookie_file(src)
    if r is None:
        raise argparse.ArgumentTypeError('Invalid cookie "{}"'.format(src))


def valid_browser(browser):
    browser = browser.strip()

    def err():
        raise argparse.ArgumentTypeError('no such browser "{}"'.format(browser))

    if (
        browser == ""
        or not browser[:1].islower()
        or browser
        in (
            "all_browsers",
            "base64",
            "json",
            "http",
            "load",
            "shutil",
            "sqlite3",
            "struct",
            "subprocess",
            "sys",
            "tempfile",
            "lz4",
            "glob",
            "os",
            "configparser",
            "contextlib",
            "open_dbus_connection",
            "unpad",
        )
    ):
        err()

    import browser_cookie3

    try:
        return getattr(browser_cookie3, browser)
    except AttributeError:
        err()


def valid_time(time):
    time = time.strip()

    suffix = time[-1:]
    weight = 1
    if not suffix.isdigit():
        time = time[:-1]
        match suffix:
            case "s":
                weight = 1
            case "m":
                weight = 60
            case "h":
                weight = 3600
            case "d":
                weight = 24 * 3600
            case _:
                raise argparse.ArgumentTypeError(
                    'incorrect time format "{}"'.format(time)
                )
    try:
        num = float(time)
    except ValueError:
        raise argparse.ArgumentTypeError('incorrect time format "{}"'.format(time))

    if num < 0:
        raise argparse.ArgumentTypeError('incorrect time format "{}"'.format(time))

    return num * weight


def valid_timeout(format):
    def check_time(time):
        time = time.strip()
        if time == "" or time == "-":
            return None
        return valid_time(time)

    times = format.split(".")
    timesl = len(times)
    try:
        if timesl == 1:
            return check_time(times[0])
        elif timesl == 2:
            return (check_time(times[0]), check_time(times[1]))
    except argparse.ArgumentTypeError as e:
        raise argparse.ArgumentTypeError(
            "incorrect timeout format: " + str.join(" ", e.args)
        )

    raise argparse.ArgumentTypeError(
        'incorrect timeout format "{}": too many values', format
    )


def arg_name(name, rename: list[Tuple[str]]) -> Optional[Tuple[str, bool]]:
    if name is None:
        return
    for i in rename:
        l = len(i)
        if l < 1 or l > 2:
            assert 0

        if i[0] != name:
            continue

        if l == 1:
            return
        else:
            return i[1], True
    return name, False


def args_longarg(arg: str, prefix: str, rename: list[Tuple[str]]):
    if (r := arg_name(arg, rename)) is None:
        return
    longarg = "--"
    if r[1]:
        return longarg + r[0]
    if len(prefix) > 0:
        longarg += prefix + "-"
    longarg += r[0]
    return longarg


def args_shortarg(
    shortarg: Optional[str], noshortargs: Optional[list[str]], rename: list[Tuple[str]]
) -> Optional[str]:
    if noshortargs:
        return
    if (r := arg_name(shortarg, rename)) is None:
        return
    return "-" + r[0]


def rename_normalize(rename):
    for i, j in enumerate(rename):
        if isinstance(j, str):
            val = j.lstrip("-")
            rename[i] = (val,)
        else:
            rename[i] = tuple([k.lstrip("-") for k in j])


def args_section(
    parser,
    name: str = "Request settings",
    noshortargs: bool = False,
    rename: list[Tuple[str, str] | Tuple[str] | str] = [],
    prefix: str = "",
):
    section = parser.add_argument_group(name)

    rename_normalize(rename)

    def add(shortarg, longarg, help, **kwargs):
        shortarg = args_shortarg(shortarg, noshortargs, rename)
        longarg = args_longarg(longarg, prefix, rename)

        if shortarg is None and longarg is None:
            return

        r = shortarg if shortarg is not None else longarg

        help = help.replace("{.}", r)

        a = [i for i in (shortarg, longarg) if i is not None]
        section.add_argument(*a, help=help, **kwargs)

    add(
        "w",
        "wait",
        "Set waiting time for each request",
        metavar="TIME",
        type=valid_time,
    )
    add(
        "W",
        "wait-random",
        "Set random waiting time for each request to be from 0 to TIME",
        metavar="TIME",
        type=valid_time,
    )
    add(
        "r",
        "retry",
        "Set number of retries for failed request to NUM",
        metavar="NUM",
        type=int,
    )
    add(
        None,
        "retry-delay",
        "Set interval between each retry",
        metavar="TIME",
        type=valid_time,
    )
    add(
        None,
        "retry-all-errors",
        "Retry no matter the error",
        action="store_true",
    )
    add(
        "m",
        "timeout",
        "Set request timeout, if in TIME format it'll be set for the whole request. If in TIME,TIME format first TIME will specify connection timeout, the second read timeout. If set to '-' timeout is disabled",
        metavar="TIMEOUT",
        type=valid_timeout,
    )
    add(
        "k",
        "insecure",
        "Ignore ssl errors",
        action="store_false",
    )
    add(
        "L",
        "location",
        "Allow for redirections, can be dangerous if credentials are passed in headers",
        action="store_true",
    )
    add(
        None,
        "max-redirs",
        "Set the maximum number of redirections to follow",
        metavar="NUM",
        type=int,
    )
    add(
        "A",
        "user-agent",
        "Sets custom user agent",
        metavar="UA",
        type=str,
    )
    add(
        "x",
        "proxy",
        "Use the specified proxy, can be used multiple times. If set to URL it'll be used for all protocols, if in PROTOCOL URL format it'll be set only for given protocol, if in URL URL format it'll be set only for given path. If first character is '@' then proxies are read from file",
        metavar="PROXY",
        action="extend",
        type=valid_proxy,
    )
    add(
        "H",
        "header",
        "Set curl style header, can be used multiple times e.g. {.} 'User: Admin' {.} 'Pass: 12345', if first character is '@' then headers are read from file e.g. {.} @file",
        metavar="HEADER",
        type=valid_header,
        action="extend",
    )
    add(
        "b",
        "cookie",
        "Set curl style cookie, can be used multiple times e.g. {.} 'auth=8f82ab' {.} 'PHPSESSID=qw3r8an829', without '=' character argument is read as a file",
        metavar="COOKIE",
        type=valid_cookie,
        action="extend",
    )
    add(
        "B",
        "browser",
        "Get cookies from specified browser e.g. {.} firefox",
        metavar="BROWSER",
        type=valid_browser,
    )

    return section


def finish_proxies(proxies):
    ret = {}
    if proxies is None:
        return ret

    all_protocols = ["http", "https", "ftp", "sftp", "ftps"]

    for name, value in proxies:
        if value == "":
            for i in all_protocols:
                if ret.get(i) is not None:
                    ret[i] = name
        elif (x := name.lower()) in all_protocols:
            ret[x] = value
        else:
            ret[name] = value
    return ret


def finish_cookies(cookies):
    ret = {}
    if cookies is None:
        return ret

    for name, value in cookies:
        ret[name] = value
    return ret


def finish_headers(headers, cookies):
    ret = {}
    if headers is None:
        return ret

    for name, value in headers:
        name = name.lower()
        if ret.get(name) is None:
            ret[name] = value
        else:
            ret[name] += "," + value

    cookie = [value for name, value in headers if name.lower() == "cookie"]

    ret.pop("cookie", None)

    if len(cookie) == 0:
        return ret
    cookies.update(finish_cookies(valid_cookie_file(cookie[0])))
    return ret


def args_session(
    session,
    args,
    prefix: str = "",
    rename: list[Tuple[str, str] | Tuple[str] | str] = [],
    **settings,
):
    prefix = prefix.replace("-", "_")
    rename_normalize(rename)

    def argval(name: str):
        if (r := arg_name(name, rename)) is None:
            return
        name = r[0]
        if not r[1] and len(prefix) > 0 and len(name) > 1:
            return getattr(args, prefix + "_" + name)
        else:
            return getattr(args, name)

    settings["proxies"] = finish_proxies(argval("proxy"))
    settings["cookies"] = finish_cookies(argval("cookie"))
    settings["headers"] = finish_headers(argval("header"), settings["cookies"])

    def setarg(longarg: str, shortarg: str = None, dest: str = None):
        name = longarg
        if (value := argval(name)) is None:
            if (value := argval(shortarg)) is None:
                return

        if dest is not None:
            name = dest
        settings[name] = value

    setarg("timeout")
    setarg("insecure", dest="verify")
    setarg("location", dest="allow_redirects")
    setarg("max_redirs", dest="max_redirects")
    setarg("retry")
    setarg("retry_delay")
    setarg("retry_all_errors")
    setarg("wait")
    setarg("wait_random")
    setarg("user_agent")
    setarg("browser")

    session.set_settings(settings, remove=False)
