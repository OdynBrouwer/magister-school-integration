#!/usr/bin/python3
import re
import urllib.request
import urllib.parse
import http.cookiejar
from datetime import datetime, timezone, timedelta
import json
import sys
import os
import traceback
from pathlib import Path
import argparse

def dehtml(html):
    """
    convert html to somewhat readable text.
    """
    if html is None: return

    html = re.sub(r"</p>|<br>", "\n", html)
    html = re.sub(r"</td>\s*<td[^<>]*>", "\t", html)
    html = re.sub(r"</tr>", "\n", html)
    # special handling for <a href>: description first, then link.
    html = re.sub(r"<a[^<>]*\shref=([^<> ]+)[^<>]*>([^<>]*)</\s*a\s*>", lambda m:m[2]+' '+m[1]+' ', html, flags=re.DOTALL)
    html = re.sub(r"<\w[^<>]*\shref=([^<> ]+)[^<>]*>", lambda m:m[1] + ' ', html, flags=re.DOTALL)
    html = re.sub(r"<\w[^<>]*\ssrc=([^<> ]+)[^<>]*>", lambda m:m[1] + ' ', html, flags=re.DOTALL)
    html = re.sub(r"</?\w+[^<>]*>", "", html)
    html = re.sub(r"&nbsp;", " ", html)
    html = re.sub(r"\u00a0", " ", html)
    html = re.sub(r"&gt;", ">", html)
    html = re.sub(r"&lt;", "<", html)
    html = re.sub(r"&amp;", "&", html)
    # remove repeating links
    html = re.sub(r"""['"]?(http\S+?)['"]?(?:\s+['"]?\1['"]?)+""", lambda m:m[1], html, flags=re.DOTALL)
    html = re.sub(r"""['"]?(http\S+?)['"]?(?:\s+['"]?\1['"]?)+""", lambda m:m[1], html, flags=re.DOTALL)
    return html

def datum(ts):
    """
    Strip the date's to a more reasonable string.
    """
    if not ts:
        return "?"
    if m := re.split(r"[-T:Z.]", ts):
        # voorzichtig: m[-1] kan soms leeg zijn; oorspronkelijke code gebruikte m[:-1]
        try:
            y, mo, d, H, M, S, us = map(int, m[:-1])
            localtz = datetime(y, mo, d, H, M, S).astimezone().tzinfo
            t = datetime(y, mo, d, H, M, S, tzinfo=timezone.utc)
            t = t.astimezone(localtz)
            return f"{t:%Y-%m-%d %H:%M:%S}"
        except Exception:
            # fallback: return original prefix
            return ts[:19]

    return ts[:19]

def ymd(ts):
    """
    Return just the date
    """
    return datum(ts)[:10]

def utctime(ts):
    if m := re.split(r"[-T:Z.]", ts):
        y, mo, d, H, M, S = map(int, m[:-1])
        return datetime(y, mo, d, H, M, S, tzinfo=timezone.utc)

def deltaymd(years=0, days=0, weeks=0):
    t = datetime.now()
    if years:
        t += timedelta(days=365*years)
    elif days:
        t += timedelta(days=days)
    elif weeks:
        t += timedelta(weeks=weeks)
    return "%04d-%02d-%02d" % (t.year, t.month, t.day)

def infotstr(t):
    typenames = ["", "hw", "T!", "TT", "SO", "MO", "in", "aa"]
    if isinstance(t, int) and 0 <= t < len(typenames):
        return typenames[t]
    try:
        it = int(t)
        if 0 <= it < len(typenames):
            return typenames[it]
    except Exception:
        pass
    return "??"

class Magister:
    """
    object encapsulating all magister functionality.
    """
    def __init__(self, args):
        self.args = args
        self.xsrftoken = args.xsrftoken
        self.access_token = args.accesstoken
        self.magisterserver = args.magisterserver
        self.schoolserver = args.schoolserver
        self.cj = http.cookiejar.CookieJar()
        handlers = [urllib.request.HTTPCookieProcessor(self.cj)]
        if args.debug:
            handlers.append(urllib.request.HTTPSHandler(debuglevel=1))
        self.opener = urllib.request.build_opener(*handlers)

    def logprint(self, *args):
        # In JSON-modus altijd stil zijn; en alleen loggen als debug True.
        if not getattr(self.args, "debug", False) or getattr(self.args, "json", False):
            return
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # Verberg wachtwoorden en tokens in logs
                arg = re.sub(r'("password":\s*")[^"]*"', r'\1***"', arg)
                arg = re.sub(r'(access_token=)[^&\s]*', r'\1***', arg)
            safe_args.append(arg)
        print(*safe_args)

    def httpreq(self, url, data=None):
        """
        Generic http request function.
        Does a http-POST when the 'data' argument is present.

        Adds the nesecesary xsrf and auth headers.
        """
        self.logprint(">", url)
        hdrs = { }
        if data and type(data)==str:
            data = data.encode('utf-8')
        if data and data[:1] in (b'{', b'['):
            hdrs["Content-Type"] = "application/json"
        if self.xsrftoken:
            hdrs["X-XSRF-TOKEN"] = self.xsrftoken
        if self.access_token:
            hdrs['Authorization'] = 'Bearer ' + self.access_token
        req = urllib.request.Request(url, headers=hdrs)
        kwargs = dict()
        if data:
            kwargs["data"] = data
        try:
            response = self.opener.open(req, **kwargs)
        except urllib.error.HTTPError as e:
            self.logprint("!", str(e))
            response = e

        raw = response.read()
        ctype = response.headers.get("content-type", "")
        if "application/json" in ctype:
            js = json.loads(raw)
            # alleen loggen als debug én niet json-uitvoer
            if getattr(self.args, "debug", False) and not getattr(self.args, "json", False):
                self.logprint(js)
                self.logprint()
            return js
        # niet-json content
        if getattr(self.args, "debug", False) and not getattr(self.args, "json", False):
            self.logprint(raw)
            self.logprint()
        return raw

    def extractxsrf(self):
        """
        Find the XSRF token in the CookieJar
        """
        for c in self.cj:
            if c.name == "XSRF-TOKEN":
                return c.value

    def httpredirurl(self, url, data=None):
        """
        request 'url', obtaining both the final result, and final redirected-to URL.
        """
        self.logprint(">", url)
        hdrs = { }
        if data and data[:1] in (b'{', b'['):
            hdrs["Content-Type"] = "application/json"
        req = urllib.request.Request(url, headers=hdrs)
        kwargs = dict()
        if data:
            kwargs["data"] = data
        response = self.opener.open(req, **kwargs)
        raw = response.read()
        if getattr(self.args, "debug", False) and not getattr(self.args, "json", False):
            self.logprint(raw)
            self.logprint()
        return response.url, raw

    def extract_account_url(self, html):
        """
        Find the name of the account-XXXXX.js file.
        """
        if m := re.search(r'js/account-\w+\.js', html):
            return f"https://{self.magisterserver}/{m.group(0)}"

    def extract_authcode(self, js):
        """
        Extract the authCode from the 'account-XXXXX.js' file.

        This function handles only one of the type of account.js files.

        The other kind is not handled (yet), which stores the parts of the authcode
        string in separate variables and then using those vars instead of literal strings in the 'n' Array.
        """
        if m := re.search(r'\(\w=\["([0-9a-f",]+?)"\],\["([0-9",]+)"\]\.map', js):
            codes = m.group(1).split('","')
            idxes = [int(_) for _ in m.group(2).split('","')]
            return "".join(codes[_] for _ in idxes)

        if not getattr(self.args, "json", False):  # Alleen printen in niet-JSON modus
            print("Did not find encoded authcode, using default!")

        return self.args.authcode

    def extract_oidc_config(self, js):
        """
        Decode the javascript containing the oidc config.
        """
        cfg = dict()
        for line in re.split(r'[\r\n]+', js):
            if not line: continue
            if m := re.match(r'\s*(\w+):\s*(.*),?$', line):
                key, value = m.groups()
                value = re.sub(r'\' \+ window\.location\.hostname', f"{self.schoolserver}'", value)
                value = re.sub(r'\' \+ \'', "", value)
                if value == 'false':
                    value = False
                elif value == 'true':
                    value = True
                elif m2 := re.match(r'\'(.*)\',?$', value):
                    value = m2.group(1)
                cfg[key] = value;
        return cfg

    def login(self, username, password):
        """
        Authenticate to the magister server using username and password.
        """
        openidcfg = self.httpreq(f"https://{self.magisterserver}/.well-known/openid-configuration")
        if not openidcfg:
            if not getattr(self.args, "json", False):
                print("could not get magister openid config")
            return False
        oidcjs = self.httpreq(f"https://{self.schoolserver}/oidc_config.js")
        if not oidcjs:
            if not getattr(self.args, "json", False):
                print("could not get school config")
            return False
        oidccfg = self.extract_oidc_config(oidcjs.decode('utf-8'))

        params = dict(
            client_id= oidccfg["client_id"],
            redirect_uri= oidccfg["redirect_uri"],
            response_type= oidccfg["response_type"],
            scope= "openid profile",
            state= "11111111111111111111111111111111",
            nonce= "11111111111111111111111111111111",
            acr_values= oidccfg["acr_values"],
        )

        self.logprint("\n---- auth ----")

        # sets the XSRF-TOKEN cookie
        sessionurl, html = self.httpredirurl(openidcfg["authorization_endpoint"] + "?" + urllib.parse.urlencode(params))

        self.xsrftoken = self.extractxsrf()
        if self.args.verbose and not getattr(self.args, "json", False):
            print(f"-> xsrf = {self.xsrftoken}")

        self.logprint("\n---- account.js ----")
        accountjs_url = self.extract_account_url(html.decode('utf-8'))
        if not accountjs_url:
            if not getattr(self.args, "json", False):
                print("could not get account.js url")
            return False
        actjs = self.httpreq(accountjs_url)

        authcode = self.extract_authcode(actjs.decode('utf-8'))
        if self.args.verbose and not getattr(self.args, "json", False):
            print("-> authcode =", authcode)

        # extract sessionid from redirect-url
        qs = sessionurl[sessionurl.find('?')+1:]
        sessioninfo = urllib.parse.parse_qs(qs)

        self.logprint(sessioninfo)
        self.logprint()

        self.logprint("\n---- current ----")
        d = dict(
            sessionId= sessioninfo["sessionId"][0],
            returnUrl= sessioninfo["returnUrl"][0],
            authCode= authcode,
        )
        r = self.httpreq(f"https://{self.magisterserver}/challenges/current", json.dumps(d))

        d["username"] = username

        self.logprint("\n---- username ----")
        r = self.httpreq(f"https://{self.magisterserver}/challenges/username", json.dumps(d))
        if r.get('error'):
            if not getattr(self.args, "json", False):
                print("ERROR '%s'" % r['error'])
            return False

        d["password"] = password

        self.logprint("\n---- password ----")
        r = self.httpreq(f"https://{self.magisterserver}/challenges/password", json.dumps(d))

        if not r.get('redirectURL') or r.get('error'):
            if r.get('action'):
                if not getattr(self.args, "json", False):
                    print("'%s' requested -> visit website" % r['action'])
                return False
            if not getattr(self.args, "json", False):
                print("ERROR '%s'" % r.get('error'))
            return False

        self.logprint("\n---- callback ----")
        url, html = self.httpredirurl(f"https://{self.magisterserver}" + r["redirectURL"])
        if not getattr(self.args, "json", False):
            print(">>> Redirect URL after login:", url)

        if '#' not in url:
            if not getattr(self.args, "json", False):
                print("ERROR: Redirect URL does not contain a fragment (#). Login may have failed.")
                print(f"URL was: {url}")
            return False
        _, qs = url.split('#', 1)

        d = urllib.parse.parse_qs(qs)
        self.access_token = d["access_token"][0]
        if self.args.verbose and not getattr(self.args, "json", False):
            print(f" -> access = {self.access_token}")

        return True

    def req(self, *args):
        """
        Generic 'school' request method, converts and concats all argments automatically.
        With the last argument optionally a dict, when a querystring is needed.
        """
        tag = []
        for v in args:
            if type(v)==str and re.match(r'^[a-z]+$', v):
                tag.append(v)

        self.logprint(f"\n---- {'.'.join(tag)} ---")

        qs = ""
        if args and type(args[-1])==dict:
            querydict = args[-1]
            args = args[:-1]
            qs = "?" + urllib.parse.urlencode(querydict)

        path = "/".join(str(_) for _ in args)
        return self.httpreq(f"https://{self.schoolserver}/api/{path}{qs}")

    def getlink(self, link):
        """
        request the link specified in the 'link' dictionary.
        """
        if not link:
            return
        return self.httpreq(f"https://{self.schoolserver}{link['href']}")

def loadconfig(cfgfile):
    """
    Load config from .magisterrc
    """
    try:
        with open(cfgfile, 'r') as fh:
            txt = fh.read()
        txt = "[root]\n" + txt
        import configparser
        config = configparser.ConfigParser()
        config.read_string(txt)
        return config
    except FileNotFoundError:
        return None

def applyconfig(cfg, args):
    """
    Apply the configuration read from .magisterrc to the `args` dictionary,
    which is used to configure everything.
    """
    if not args.username and cfg:
        args.username = cfg.get('root', 'user')
    if not args.password and cfg:
        args.password = cfg.get('root', 'pass')
    if not args.schoolserver and cfg:
        args.schoolserver = cfg.get('root', 'school')
    if not args.authcode and cfg:
        args.authcode = cfg.get('root', 'authcode')

def apply_auth_config(cfg, args):
    if args.accesstoken:
        return
    exptime = utctime(cfg.get('root', 'expires')) if cfg else None
    if not exptime:
        return
    now = datetime.now().astimezone(timezone.utc)
    if exptime < now - timedelta(minutes=5):
        return
    args.accesstoken = cfg.get('root', 'accesstoken')

def store_access_token(cache: str, token: str) -> None:
    import base64
    import json
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)

    def base64url_decode(input):
        """Decode base64url (JWT-style) to bytes."""
        if isinstance(input, str):
            input = input.encode('ascii')
        rem = len(input) % 4
        if rem > 0:
            input += b'=' * (4 - rem)  # add padding
        return base64.b64decode(input.replace(b'-', b'+').replace(b'_', b'/'))

    try:
        f = token.split(".")
        if len(f) >= 2:
            # Decode the payload (f[1])
            payload = base64url_decode(f[1])
            j = json.loads(payload)
            exp = datetime.fromtimestamp(j["exp"], tz=timezone.utc)
        else:
            exp = now + timedelta(hours=1)
    except Exception:
        exp = now + timedelta(hours=1)

    with open(cache, "w+") as fh:
        print(f"expires={exp:%Y-%m-%dT%H:%M:%SZ}", file=fh)
        print(f"accesstoken={token}", file=fh)

def safe_datum_field(item, *keys):
    """Return first found datum from item for given keys (passes through datum())."""
    for k in keys:
        v = item.get(k)
        if v:
            return datum(v)
    return "?"

def main():
    parser = argparse.ArgumentParser(description='Magister info dump')
    parser.add_argument('--debug', '-d', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--json', action='store_true', help='output as JSON only')
    parser.add_argument('--config', help=argparse.SUPPRESS)
    parser.add_argument('--cache', help=argparse.SUPPRESS)
    parser.add_argument('--verbose', action='store_true')

    # 'internal' options.
    parser.add_argument('--xsrftoken', help=argparse.SUPPRESS)
    parser.add_argument('--accesstoken', help=argparse.SUPPRESS)
    parser.add_argument('--username', help=argparse.SUPPRESS)
    parser.add_argument('--password', help=argparse.SUPPRESS)
    parser.add_argument("--authcode", help=argparse.SUPPRESS)
    parser.add_argument('--schoolserver', help=argparse.SUPPRESS)
    parser.add_argument('--magisterserver', default='accounts.magister.net', help=argparse.SUPPRESS)
    args = parser.parse_args()

    if not args.config:
        script_dir = Path(__file__).parent
        local_config = script_dir / ".magisterrc"
        args.config = local_config if local_config.exists() else Path.home() / ".magisterrc"

    # Config laden - we doen dit eerst om username/schoolserver te krijgen voor cache naam
    cfg = None
    if args.config.exists():
        try:
            cfg = loadconfig(args.config)
            if cfg:
                applyconfig(cfg, args)
        except Exception as e:
            if not args.json:
                print(f"config: {e}")
    elif not args.json:
        print(f"Config file not found: {args.config}")

    # Cache naam bepalen - maak per schoolserver + username uniek om conflicts te voorkomen
    if not args.cache:
        script_dir = Path(__file__).parent
        cache_suffix = ""
        if args.schoolserver and args.username:
            # Sanitize filename characters
            safe_school = args.schoolserver.replace('.', '_').replace('@', '_').replace('/', '_')
            safe_user = args.username.replace('.', '_').replace('@', '_').replace('/', '_')
            cache_suffix = f"_{safe_school}_{safe_user}"

        cache_name = f".magister_auth_cache{cache_suffix}"
        local_cache = script_dir / cache_name
        args.cache = local_cache if local_cache.exists() else Path.home() / cache_name

    # Cache laden
    acfg = None
    if args.cache.exists():
        try:
            acfg = loadconfig(args.cache)
            if acfg:
                apply_auth_config(acfg, args)
        except Exception as e:
            if not args.json:
                print(f"cache: {e}")

    mg = Magister(args)

    if not args.accesstoken:
        if not mg.login(args.username, args.password):
            if not args.json:
                print("Login failed")
            return
        if not mg.access_token or mg.access_token == "":
            if not args.json:
                print("Login appeared to succeed, but no access token was received.")
            return
        store_access_token(args.cache, mg.access_token)

    # JSON output voor Home Assistant
    output_data = {
        "last_update": datetime.now().isoformat(),
        "kinderen": {},
        "cijfers": {},
        "absenties": {},
        "opdrachten": {},
        "studiewijzers": {},
        "activiteiten": {}
    }

    d = mg.req("account")

    # Check if account request was successful
    if not isinstance(d, dict) or "Persoon" not in d:
        if not args.json:
            print(f"ERROR: Could not get account info. Response: {d}")
        sys.exit(1)

    ouderid = d["Persoon"]["Id"]

    # Try to get children - will fail for student accounts
    try:
        k = mg.req("personen", ouderid, "kinderen")
    except Exception as e:
        # If request fails completely, treat as student account
        k = {"Fouttype": "OnvoldoendePrivileges"}

    # Check if student account (gets permission error)
    if k.get('Fouttype'):
        # Student account - use own ID as "kind"
        kinderen = [{
            "Id": d["Persoon"]["Id"],
            "Roepnaam": d["Persoon"].get("Roepnaam", ""),
            "Achternaam": d["Persoon"].get("Achternaam", ""),
            "Geboortedatum": d["Persoon"].get("Geboortedatum", ""),
            "Stamnummer": d["Persoon"].get("Stamnummer", "")
        }]
    else:
        # Parent account - use children list
        kinderen = k.get("Items", [])

    for kind in kinderen:
        kind_naam = f"{kind.get('Roepnaam', '')} {kind.get('Achternaam', '')}"
        kind_data = {
            "naam": kind_naam,
            "stamnummer": kind.get('Stamnummer', ''),
            "geboortedatum": kind.get('Geboortedatum', '')
        }
        kindid = kind["Id"]

        # Aanmeldingen
        x = mg.req("personen", kindid, "aanmeldingen")
        kind_data["aanmeldingen"] = [
            {
                "start": datum(item.get("Start")),
                "einde": datum(item.get("Einde")),
                "lesperiode": item.get("Lesperiode"),
                "studie": item.get("Studie", {}).get("Omschrijving", "") if item.get("Studie") else ""
            }
            for item in x.get("Items", [])
        ]

        # Rooster data: determine lesperiode as before
        start_date = deltaymd()
        end_date = deltaymd(weeks=+2)

        params = dict(van=start_date, tot=end_date)
        target_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        lesperiode = None

        for meld in x.get("Items", []):
            if "Start" not in meld or "Eind" not in meld:
                continue
            try:
                start_aanm = datetime.strptime(meld["Start"][:10], "%Y-%m-%d").date()
                einde_aanm = datetime.strptime(meld["Eind"][:10], "%Y-%m-%d").date()
            except Exception:
                continue
            if start_aanm <= target_date <= einde_aanm:
                omschrijving = meld.get("Omschrijving", "")
                lesperiode = omschrijving.split()[0] if omschrijving else None
                break

        if not lesperiode and x.get("Items"):
            last = x["Items"][-1]
            lesperiode = last.get("Lesperiode")

        if lesperiode:
            params["lesperiode"] = lesperiode

        afspraken = mg.req("personen", kindid, "afspraken", params)
        wijzigingen = mg.req("personen", kindid, "roosterwijzigingen", params)

        kind_data["afspraken"] = [
            {
                "start": datum(item.get("Start") or item.get("Datum")),
                "einde": datum(item.get("Einde") or item.get("Eind")),
                "type": infotstr(item.get("InfoType", 0)),
                "lokaal": item.get("Lokatie", ""),
                "omschrijving": item.get("Omschrijving", ""),
                "inhoud": dehtml(item.get("Inhoud", "")),
                "vak": item.get("Vak", ""),
                "is_huiswerk": item.get("InfoType", 0) == 1
            }
            for item in afspraken.get("Items", [])
        ]

        kind_data["wijzigingen"] = [
            {
                "start": safe_datum_field(item, "Start", "Datum"),
                "einde": safe_datum_field(item, "Eind", "Einde"),
                "type": infotstr(item.get("InfoType", 0)),
                "lokaal": item.get("Lokatie", ""),
                "omschrijving": item.get("Omschrijving", ""),
                "inhoud": dehtml(item.get("Inhoud", ""))
            }
            for item in wijzigingen.get("Items", [])
        ]

        # Tel statistieken
        vandaag = datetime.now().strftime('%Y-%m-%d')
        kind_data["aantal_afspraken_vandaag"] = len([
            a for a in kind_data["afspraken"]
            if a["start"].startswith(vandaag)
        ])
        kind_data["aantal_huiswerk"] = len([
            a for a in kind_data["afspraken"]
            if a["is_huiswerk"]
        ])

        # Volgende afspraak
        toekomstige_afspraken = [
            a for a in kind_data["afspraken"]
            if a["start"] > datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ]
        if toekomstige_afspraken:
            volgende = min(toekomstige_afspraken, key=lambda x: x["start"])
            kind_data["volgende_afspraak"] = volgende["start"]
            kind_data["volgende_vak"] = volgende.get("vak", "")
        else:
            kind_data["volgende_afspraak"] = "Geen"
            kind_data["volgende_vak"] = ""

        output_data["kinderen"][kind_naam] = kind_data

        # 🔥 Nieuw: haal extra data per kind
        # Cijfers
        c = mg.req("personen", kindid, "cijfers", "laatste", dict(top=50))
        output_data["cijfers"][kind_naam] = [
            {
                "vak": item.get("vak", {}).get("code", ""),
                "omschrijving": item.get("omschrijving", ""),
                "waarde": item.get("waarde", ""),
                "weegfactor": item.get("weegfactor", ""),
                "ingevoerd_op": datum(item.get("ingevoerdOp"))
            }
            for item in c.get("items", [])
        ]

        # Absenties
        abs_van = deltaymd(years=-1)
        abs_tot = deltaymd(weeks=+1)
        abs_data = mg.req("personen", kindid, "absenties", dict(van=abs_van, tot=abs_tot))
        output_data["absenties"][kind_naam] = [
            {
                "start": datum(item.get("Start")),
                "einde": datum(item.get("Eind")),
                "omschrijving": item.get("Omschrijving", ""),
                "afspraak": item.get("Afspraak", {}).get("Omschrijving", "")
            }
            for item in abs_data.get("Items", [])
        ]

        # Opdrachten
        opdr_data = mg.req("personen", kindid, "opdrachten")
        output_data["opdrachten"][kind_naam] = [
            {
                "titel": item.get("Titel", ""),
                "vak": item.get("Vak", ""),
                "inleveren_voor": datum(item.get("InleverenVoor")),
                "ingeleverd_op": datum(item.get("IngeleverdOp")),
                "omschrijving": dehtml(item.get("Omschrijving", ""))
            }
            for item in opdr_data.get("Items", [])
        ]

        # Activiteiten
        act_data = mg.req("personen", kindid, "activiteiten")
        output_data["activiteiten"][kind_naam] = [
            {
                "titel": item.get("Titel", ""),
                "zichtbaar_vanaf": datum(item.get("ZichtbaarVanaf")),
                "zichtbaar_tot": datum(item.get("ZichtbaarTotEnMet"))
            }
            for item in act_data.get("Items", [])
        ]

        # Studiewijzers
        swlist = mg.req("leerlingen", kindid, "studiewijzers")
        output_data["studiewijzers"][kind_naam] = []
        for sw in swlist.get("Items", []):
            switem = mg.req("leerlingen", kindid, "studiewijzers", sw["Id"])
            output_data["studiewijzers"][kind_naam].append({
                "titel": switem.get("Titel", ""),
                "van": datum(switem.get("Van")),
                "tot_en_met": datum(switem.get("TotEnMet")),
                "onderdelen": [
                    {
                        "titel": o.get("Titel", ""),
                        "omschrijving": dehtml(o.get("Omschrijving", ""))
                    }
                    for o in switem["Onderdelen"]["Items"]
                ]
            })

    print(json.dumps(output_data, ensure_ascii=False, separators=(',', ':')))

# Entry point
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # behoud originele error-logbestanden gedrag
        try:
            with open("/config/magister_error.log", "w") as f:
                f.write("FOUT IN MAGISTER SCRIPT:\n")
                f.write(str(e))
                f.write("\n\n")
                f.write(traceback.format_exc())
        except Exception:
            # als we niet naar /config kunnen schrijven, print kort naar stderr
            print("FOUT IN MAGISTER SCRIPT:", e, file=sys.stderr)
        sys.exit(1)
