#!/usr/bin/env python3
"""
Septim Tools
Tools Discord en Python - 25 fonctionnalites
"""
import os
import sys
import re
import json
import time
import base64
import random
import string
import requests
from colorama import init, Fore, Style

init(autoreset=True)

API_BASE = "https://discord.com/api/v9"

# Bleu fonce -> bleu ciel (ANSI 256)
BLUE_GRADIENT = [17, 18, 19, 20, 26, 32, 39, 45, 51, 87, 123, 159, 195]

# Couleurs ANSI 256 pour les niveaux
C_BG_DEEP = 17     # bleu tres fonce
C_PRIMARY = 39     # bleu très claire
C_ACCENT = 51      # cyan
C_LIGHT = 195      # bleu tres clair
C_DIM = 244        # gris

# Symboles Unicode propres
SYM_OK = "✓"
SYM_ERR = "✗"
SYM_INFO = "▸"
SYM_WARN = "⚠"
SYM_BULLET = "●"
SYM_ARROW = "→"
SYM_PROMPT = "❯"


def c(code, text):
    """Wrap text in an ANSI 256 color."""
    return "\033[38;5;{}m{}\033[0m".format(code, text)


BANNER = r"""
   ____             _   _              _____           _     
  / ___|  ___ _ __ | |_(_)_ __ ___    |_   _|__   ___ | |___ 
  \___ \ / _ \ '_ \| __| | '_ ` _ \     | |/ _ \ / _ \| / __|
   ___) |  __/ |_) | |_| | | | | | |    | | (_) | (_) | \__ \
  |____/ \___| .__/ \__|_|_| |_| |_|    |_|\___/ \___/|_|___/
             |_|                                              
                      S E P T I M   T O O L S   
"""

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\n" + c(C_DIM, "  " + SYM_ARROW + " Entree pour revenir au menu..."))


def gradient_text(text, colors=BLUE_GRADIENT):
    out = ""
    for i, line in enumerate(text.split("\n")):
        color = colors[i % len(colors)]
        out += "\033[38;5;{}m{}\033[0m\n".format(color, line)
    return out


def hr(width=64, char="─", color=C_DIM):
    """Horizontal rule."""
    return c(color, char * width)


def section_header(title, color=C_ACCENT):
    """Section header with line and title."""
    line = "─" * 3 + " " + title + " "
    line += "─" * max(0, 64 - len(line))
    return c(color, line)


def ask(prompt, default=None):
    suffix = c(C_DIM, " [{}]".format(default)) if default is not None else ""
    raw = input(c(C_ACCENT, "  " + SYM_PROMPT + " ") + prompt + suffix + c(C_DIM, " : "))
    val = raw.strip()
    return val if val else (default or "")


def ask_int(prompt, default=1):
    raw = ask(prompt, str(default))
    try:
        return int(raw)
    except ValueError:
        return default


def ask_float(prompt, default=1.0):
    raw = ask(prompt, str(default))
    try:
        return float(raw)
    except ValueError:
        return default


def info(msg):
    print("  " + c(C_PRIMARY, SYM_INFO) + " " + msg)


def ok(msg):
    print("  " + c(C_ACCENT, SYM_OK) + " " + msg)


def warn(msg):
    print("  " + Fore.YELLOW + SYM_WARN + Style.RESET_ALL + " " + msg)


def err(msg):
    print("  " + Fore.LIGHTRED_EX + SYM_ERR + Style.RESET_ALL + " " + msg)


# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------
def load_config():
    if not os.path.exists(CONFIG_PATH):
        err("config.json introuvable.")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------
def get_headers(token):
    # X-Super-Properties : base64 d'un JSON decrivant le "navigateur".
    # Discord exige de plus en plus ce header pour les user tokens.
    super_props = base64.b64encode(json.dumps({
        "os": "Windows",
        "browser": "Chrome",
        "device": "",
        "system_locale": "fr-FR",
        "browser_user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "browser_version": "120.0.0.0",
        "os_version": "10",
        "referrer": "",
        "referring_domain": "",
        "referrer_current": "",
        "referring_domain_current": "",
        "release_channel": "stable",
        "client_build_number": 9999,
        "client_event_source": None,
    }).encode("utf-8")).decode("ascii")

    return {
        "Authorization": token,
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Origin": "https://discord.com",
        "Referer": "https://discord.com/channels/@me",
        "X-Discord-Locale": "fr",
        "X-Super-Properties": super_props,
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }


def normalize_token(raw):
    """Nettoie le token : enleve les espaces, guillemets, prefixes."""
    if not raw:
        return ""
    t = raw.strip()
    # Quotes
    for q in ('"', "'", "`"):
        if t.startswith(q) and t.endswith(q):
            t = t[1:-1]
    t = t.strip()
    # Prefixes courants colles par erreur
    for prefix in ("Bearer ", "bearer ", "Token ", "token "):
        if t.startswith(prefix):
            t = t[len(prefix):].strip()
    return t


def api_request(method, endpoint, token, **kwargs):
    url = API_BASE + endpoint
    headers = kwargs.pop("headers", get_headers(token))
    try:
        r = requests.request(method, url, headers=headers, timeout=20, **kwargs)
    except requests.RequestException as e:
        err("Erreur reseau : " + str(e))
        return None
    if r.status_code == 429:
        retry = 0
        try:
            retry = float(r.json().get("retry_after", 1))
        except Exception:
            retry = 1
        warn("Rate limit. Pause {:.1f}s...".format(retry))
        time.sleep(retry + 0.5)
        return api_request(method, endpoint, token, headers=headers, **kwargs)
    return r


def check_token(token):
    r = api_request("GET", "/users/@me", token)
    if r is None:
        err("Pas de reponse du serveur Discord (probleme reseau).")
        return None
    if r.status_code == 200:
        return r.json()
    # Diagnostic detaille
    try:
        body = r.json()
    except Exception:
        body = {"raw": r.text[:300]}
    err("Discord a refuse le token. HTTP {} - {}".format(r.status_code, body))
    if r.status_code == 401:
        warn("=> 401 Unauthorized : token invalide, expire, ou regenere.")
        warn("   Verifiez que vous avez bien colle le token COMPLET (pas tronque).")
        warn("   Re-recuperez le token depuis votre navigateur (Network tab).")
    elif r.status_code == 403:
        warn("=> 403 Forbidden : compte verrouille / IP bannie / captcha requis.")
    return None


# --------------------------------------------------------------------------
# Data getters
# --------------------------------------------------------------------------
def get_friends(token):
    r = api_request("GET", "/users/@me/relationships", token)
    if r is None or r.status_code != 200:
        return []
    return [rel for rel in r.json() if rel.get("type") == 1]


def get_all_relationships(token):
    r = api_request("GET", "/users/@me/relationships", token)
    if r is None or r.status_code != 200:
        return []
    return r.json()


def get_guilds(token):
    r = api_request("GET", "/users/@me/guilds", token)
    if r is None or r.status_code != 200:
        return []
    return r.json()


def get_dm_channels(token):
    r = api_request("GET", "/users/@me/channels", token)
    if r is None or r.status_code != 200:
        return []
    return r.json()


def open_dm(token, user_id):
    r = api_request("POST", "/users/@me/channels", token, json={"recipients": [user_id]})
    if r is not None and r.status_code in (200, 201):
        return r.json().get("id")
    return None


def send_message(token, channel_id, content):
    r = api_request("POST", "/channels/{}/messages".format(channel_id), token,
                    json={"content": content})
    return r is not None and r.status_code in (200, 201)


# --------------------------------------------------------------------------
# Features
# --------------------------------------------------------------------------
def feature_dm_all_friends(token, cfg):
    msg = ask("Message", cfg.get("message", ""))
    delay = ask_float("Delai entre DM (s)", cfg.get("delay_seconds", 3))
    if not msg:
        warn("Message vide. Annule.")
        return
    friends = get_friends(token)
    if not friends:
        warn("Aucun ami.")
        return
    info("{} amis. Demarrage...".format(len(friends)))
    sent, failed = 0, 0
    for i, f in enumerate(friends, 1):
        u = f.get("user", {})
        uid = u.get("id"); uname = u.get("username", "?")
        cid = open_dm(token, uid)
        if cid and send_message(token, cid, msg):
            ok("[{}/{}] {} -> envoye".format(i, len(friends), uname)); sent += 1
        else:
            err("[{}/{}] {} -> echec".format(i, len(friends), uname)); failed += 1
        time.sleep(delay)
    info("Termine : {} envoyes / {} echecs".format(sent, failed))


def feature_friend_request_by_ids(token):
    raw = ask("IDs utilisateurs (separes par virgule)")
    if not raw:
        return
    ids = [x.strip() for x in raw.split(",") if x.strip()]
    delay = ask_float("Delai (s)", 2)
    sent, failed = 0, 0
    for i, uid in enumerate(ids, 1):
        r = api_request("PUT", "/users/@me/relationships/{}".format(uid), token, json={})
        if r is not None and r.status_code in (200, 204):
            ok("[{}/{}] {} -> demande envoyee".format(i, len(ids), uid)); sent += 1
        else:
            err("[{}/{}] {} -> echec".format(i, len(ids), uid)); failed += 1
        time.sleep(delay)
    info("Termine : {} envoyes / {} echecs".format(sent, failed))


def feature_friend_request_in_guild(token):
    """Add all server : envoie une demande d'ami a TOUS les membres d'un serveur."""
    gid = ask("ID du serveur")
    if not gid:
        return
    max_members = ask_int("Nombre max de membres a contacter (0 = illimite)", 200)
    delay = ask_float("Delai entre demandes (s)", 2)
    dry = ask("Mode 'liste seulement' sans envoyer ? (o/N)", "n").lower().startswith("o")

    info("Verification de l'acces au serveur...")
    g_check = api_request("GET", "/guilds/{}".format(gid), token)
    if g_check is None:
        err("Pas de reponse du serveur Discord."); return
    if g_check.status_code == 404:
        err("Serveur introuvable. Vous n'etes pas membre ou ID invalide."); return
    if g_check.status_code != 200:
        err("Acces refuse : HTTP {} - {}".format(g_check.status_code, g_check.text[:200]))
        return
    g_data = g_check.json()
    ok("Serveur : " + c(C_LIGHT, g_data.get("name", "?")))

    info("Scan des membres via search API (a-z + 0-9)...")
    seen = {}
    queries = list(string.ascii_lowercase) + list(string.digits)
    search_works = False
    for q in queries:
        r = api_request(
            "GET",
            "/guilds/{}/members/search?query={}&limit=1000".format(gid, q),
            token,
        )
        if r is None:
            continue
        if r.status_code != 200:
            print("  " + c(C_DIM, "  search '{}' -> HTTP {} {}".format(
                q, r.status_code, r.text[:80])))
            continue
        search_works = True
        members = r.json()
        for m in members:
            u = m.get("user", {})
            uid = u.get("id")
            if not uid or u.get("bot"):
                continue
            if uid not in seen:
                seen[uid] = u
        print("  " + c(C_DIM, "  scan '{}' -> {} uniques jusqu'ici".format(q, len(seen))))
        if max_members and len(seen) >= max_members:
            break
        time.sleep(0.3)

    if not search_works:
        warn("La search API ne repond pas pour ce serveur.")
        warn("Tentative de fallback via /guilds/{id}/members ...")
        r = api_request("GET", "/guilds/{}/members?limit=1000".format(gid), token)
        if r is not None and r.status_code == 200:
            for m in r.json():
                u = m.get("user", {})
                uid = u.get("id")
                if not uid or u.get("bot"):
                    continue
                seen[uid] = u
        else:
            err("Fallback echec : HTTP {} {}".format(
                r.status_code if r else "?", r.text[:150] if r else ""))

    members = list(seen.values())
    if max_members:
        members = members[:max_members]

    if not members:
        err("Aucun membre detecte.")
        warn("Causes possibles :")
        warn("  - Serveur prive / pas la permission de voir les membres")
        warn("  - Token user requis (les tokens bot ne marchent pas pour cette fonction)")
        warn("  - Compte recemment cree (Discord limite l'API pour les nouveaux comptes)")
        return

    ok("{} membres uniques detectes.".format(len(members)))

    if dry:
        info("Mode liste seulement. Apercu :")
        for i, u in enumerate(members[:20], 1):
            print("  " + c(C_DIM, "{:>3}.".format(i)) + " " +
                  c(C_LIGHT, u.get("username", "?")) +
                  c(C_DIM, "  (id=" + u.get("id", "?") + ")"))
        if len(members) > 20:
            print("  " + c(C_DIM, "  ... et {} autres".format(len(members) - 20)))
        return

    info("Envoi des demandes d'ami...")
    sent, already, failed = 0, 0, 0
    for i, u in enumerate(members, 1):
        uid = u.get("id")
        uname = u.get("username", "?")
        # Methode moderne : PUT /users/@me/relationships/{id} avec body vide
        rr = api_request(
            "PUT",
            "/users/@me/relationships/{}".format(uid),
            token,
            json={},
        )
        if rr is None:
            err("[{}/{}] {} -> pas de reponse".format(i, len(members), uname))
            failed += 1
        elif rr.status_code in (200, 204):
            ok("[{}/{}] {} -> demande envoyee".format(i, len(members), uname))
            sent += 1
        elif rr.status_code == 400:
            # Souvent : deja amis, ou demande deja en cours, ou compte bloque
            try:
                body = rr.json()
                msg = body.get("message", "")
            except Exception:
                msg = rr.text[:100]
            print("  " + c(C_DIM, "[{}/{}] {} -> ignore : {}".format(
                i, len(members), uname, msg)))
            already += 1
        elif rr.status_code == 403:
            err("[{}/{}] {} -> 403 : DMs fermes ou bloque".format(i, len(members), uname))
            failed += 1
        elif rr.status_code == 429:
            warn("Rate limit. Augmente le delai.")
            failed += 1
        else:
            try:
                body = rr.json(); msg = body.get("message", rr.text[:100])
            except Exception:
                msg = rr.text[:100]
            err("[{}/{}] {} -> HTTP {} : {}".format(
                i, len(members), uname, rr.status_code, msg))
            failed += 1
        time.sleep(delay)

    print()
    info(c(C_LIGHT, "Bilan : {} envoyes / {} ignores (deja amis ?) / {} echecs sur {} membres.".format(
        sent, already, failed, len(members))))


def feature_remove_all_friends(token):
    if ask("Tapez OUI pour confirmer la suppression de TOUS les amis").upper() != "OUI":
        warn("Annule."); return
    friends = get_friends(token)
    delay = ask_float("Delai (s)", 1)
    removed = 0
    for i, f in enumerate(friends, 1):
        uid = f.get("user", {}).get("id")
        r = api_request("DELETE", "/users/@me/relationships/{}".format(uid), token)
        if r is not None and r.status_code in (200, 204):
            ok("[{}/{}] supprime".format(i, len(friends))); removed += 1
        time.sleep(delay)
    info("Termine : {} amis supprimes.".format(removed))


def feature_block_all_friends(token):
    if ask("Tapez OUI pour bloquer TOUS vos amis").upper() != "OUI":
        warn("Annule."); return
    friends = get_friends(token)
    delay = ask_float("Delai (s)", 1)
    blocked = 0
    for i, f in enumerate(friends, 1):
        uid = f.get("user", {}).get("id")
        r = api_request("PUT", "/users/@me/relationships/{}".format(uid), token,
                        json={"type": 2})
        if r is not None and r.status_code in (200, 204):
            blocked += 1; ok("[{}/{}] bloque".format(i, len(friends)))
        time.sleep(delay)
    info("Termine : {} bloques.".format(blocked))


def feature_unblock_all(token):
    rels = get_all_relationships(token)
    blocked = [r for r in rels if r.get("type") == 2]
    delay = ask_float("Delai (s)", 1)
    done = 0
    for i, b in enumerate(blocked, 1):
        uid = b.get("user", {}).get("id")
        r = api_request("DELETE", "/users/@me/relationships/{}".format(uid), token)
        if r is not None and r.status_code in (200, 204):
            done += 1; ok("[{}/{}] debloque".format(i, len(blocked)))
        time.sleep(delay)
    info("Termine : {} debloques.".format(done))


def feature_leave_all_servers(token):
    if ask("Tapez OUI pour quitter TOUS vos serveurs").upper() != "OUI":
        warn("Annule."); return
    guilds = get_guilds(token)
    delay = ask_float("Delai (s)", 2)
    left = 0
    for i, g in enumerate(guilds, 1):
        r = api_request("DELETE", "/users/@me/guilds/{}".format(g.get("id")), token)
        if r is not None and r.status_code in (200, 204):
            left += 1; ok("[{}/{}] quitte : {}".format(i, len(guilds), g.get("name", "?")))
        time.sleep(delay)
    info("Termine : {} serveurs quittes.".format(left))


def feature_close_all_dms(token):
    dms = get_dm_channels(token)
    delay = ask_float("Delai (s)", 1)
    closed = 0
    for i, d in enumerate(dms, 1):
        r = api_request("DELETE", "/channels/{}".format(d.get("id")), token)
        if r is not None and r.status_code in (200, 204):
            closed += 1; ok("[{}/{}] DM ferme".format(i, len(dms)))
        time.sleep(delay)
    info("Termine : {} DMs fermes.".format(closed))


def feature_set_status(token):
    print("  Statuts : 1) online  2) idle  3) dnd  4) invisible")
    c = ask_int("Choix", 1)
    mapping = {1: "online", 2: "idle", 3: "dnd", 4: "invisible"}
    status = mapping.get(c, "online")
    r = api_request("PATCH", "/users/@me/settings", token, json={"status": status})
    if r is not None and r.status_code == 200:
        ok("Statut change : " + status)
    else:
        err("Echec changement de statut.")


def feature_set_custom_status(token):
    text = ask("Texte du statut custom")
    payload = {"custom_status": {"text": text}} if text else {"custom_status": None}
    r = api_request("PATCH", "/users/@me/settings", token, json=payload)
    if r is not None and r.status_code == 200:
        ok("Statut custom mis a jour.")
    else:
        err("Echec.")


def feature_change_username(token):
    username = ask("Nouveau pseudo")
    password = ask("Mot de passe du compte (requis)")
    if not username or not password:
        warn("Champs requis."); return
    r = api_request("PATCH", "/users/@me", token,
                    json={"username": username, "password": password})
    if r is not None and r.status_code == 200:
        ok("Pseudo change.")
    else:
        err("Echec : " + (r.text if r else ""))


def feature_change_bio(token):
    bio = ask("Nouvelle bio (max 190)")
    r = api_request("PATCH", "/users/@me/profile", token, json={"bio": bio})
    if r is not None and r.status_code == 200:
        ok("Bio mise a jour.")
    else:
        err("Echec.")


def feature_change_avatar(token):
    path = ask("Chemin de l'image (png/jpg/gif)")
    if not os.path.exists(path):
        err("Fichier introuvable."); return
    ext = path.lower().split(".")[-1]
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif"}.get(ext, "image/png")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    data_uri = "data:{};base64,{}".format(mime, b64)
    r = api_request("PATCH", "/users/@me", token, json={"avatar": data_uri})
    if r is not None and r.status_code == 200:
        ok("Avatar change.")
    else:
        err("Echec.")


def feature_spam_dm(token):
    uid = ask("ID utilisateur cible")
    msg = ask("Message")
    count = ask_int("Nombre de messages", 5)
    delay = ask_float("Delai (s)", 2)
    if not uid or not msg:
        warn("Champs requis."); return
    cid = open_dm(token, uid)
    if not cid:
        err("Impossible d'ouvrir le DM."); return
    sent = 0
    for i in range(count):
        if send_message(token, cid, msg):
            sent += 1; ok("[{}/{}] envoye".format(i + 1, count))
        else:
            err("[{}/{}] echec".format(i + 1, count))
        time.sleep(delay)
    info("Termine : {} envoyes.".format(sent))


def feature_export_friends(token):
    friends = get_friends(token)
    out = []
    for f in friends:
        u = f.get("user", {})
        out.append({"id": u.get("id"), "username": u.get("username"),
                    "global_name": u.get("global_name")})
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "friends_export.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    ok("{} amis exportes -> {}".format(len(out), path))


def feature_export_servers(token):
    guilds = get_guilds(token)
    out = [{"id": g.get("id"), "name": g.get("name"), "owner": g.get("owner")} for g in guilds]
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "servers_export.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    ok("{} serveurs exportes -> {}".format(len(out), path))


def feature_export_dm_history(token):
    cid = ask("ID du DM channel (ou utilisez 'List DMs')")
    limit = ask_int("Nombre de messages a recuperer (max 100/page)", 100)
    if not cid:
        return
    all_msgs = []
    before = None
    while len(all_msgs) < limit:
        ep = "/channels/{}/messages?limit=100".format(cid)
        if before:
            ep += "&before=" + before
        r = api_request("GET", ep, token)
        if r is None or r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        all_msgs.extend(batch)
        before = batch[-1]["id"]
        if len(batch) < 100:
            break
    all_msgs = all_msgs[:limit]
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "dm_{}.json".format(cid))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(all_msgs, f, indent=2, ensure_ascii=False)
    ok("{} messages exportes -> {}".format(len(all_msgs), path))


def feature_user_info(token):
    uid = ask("ID utilisateur")
    if not uid:
        return
    r = api_request("GET", "/users/{}".format(uid), token)
    if r is None or r.status_code != 200:
        err("Utilisateur introuvable."); return
    u = r.json()
    print(Fore.LIGHTCYAN_EX + "\n  --- INFO UTILISATEUR ---")
    for k in ("id", "username", "global_name", "discriminator", "bot", "public_flags"):
        print("  {}: {}".format(k, u.get(k)))


def feature_server_info(token):
    gid = ask("ID du serveur")
    if not gid:
        return
    r = api_request("GET", "/guilds/{}".format(gid), token)
    if r is None or r.status_code != 200:
        err("Serveur introuvable / pas membre."); return
    g = r.json()
    print(Fore.LIGHTCYAN_EX + "\n  --- INFO SERVEUR ---")
    for k in ("id", "name", "owner_id", "member_count", "premium_tier", "verification_level"):
        print("  {}: {}".format(k, g.get(k)))


def feature_join_server(token):
    invite = ask("Code d'invitation (ex: abc123)")
    if not invite:
        return
    invite = invite.split("/")[-1]
    r = api_request("POST", "/invites/{}".format(invite), token, json={})
    if r is not None and r.status_code in (200, 201):
        ok("Serveur rejoint.")
    else:
        err("Echec : " + (r.text[:200] if r else ""))


def feature_auto_react(token):
    cid = ask("ID du channel")
    emoji = ask("Emoji (unicode ou name:id)")
    count = ask_int("Nombre de messages recents", 10)
    delay = ask_float("Delai (s)", 1)
    if not cid or not emoji:
        warn("Champs requis."); return
    r = api_request("GET", "/channels/{}/messages?limit={}".format(cid, min(count, 100)), token)
    if r is None or r.status_code != 200:
        err("Echec recuperation messages."); return
    msgs = r.json()
    from urllib.parse import quote
    enc = quote(emoji)
    done = 0
    for m in msgs:
        rr = api_request("PUT", "/channels/{}/messages/{}/reactions/{}/@me".format(
            cid, m["id"], enc), token, json={})
        if rr is not None and rr.status_code in (200, 204):
            done += 1; ok("Reaction ajoutee sur " + m["id"])
        time.sleep(delay)
    info("Termine : {} reactions.".format(done))


def feature_ghost_ping(token):
    cid = ask("ID du channel")
    uid = ask("ID utilisateur a mentionner")
    if not cid or not uid:
        return
    r = api_request("POST", "/channels/{}/messages".format(cid), token,
                    json={"content": "<@{}>".format(uid)})
    if r is None or r.status_code not in (200, 201):
        err("Echec envoi."); return
    mid = r.json().get("id")
    time.sleep(0.5)
    api_request("DELETE", "/channels/{}/messages/{}".format(cid, mid), token)
    ok("Ghost ping execute.")


def feature_clear_my_messages(token):
    cid = ask("ID du channel")
    limit = ask_int("Nombre max de messages a supprimer", 50)
    if not cid:
        return
    me = check_token(token)
    if not me:
        err("Token invalide."); return
    my_id = me["id"]
    r = api_request("GET", "/channels/{}/messages?limit={}".format(cid, min(limit, 100)), token)
    if r is None or r.status_code != 200:
        err("Echec recup messages."); return
    mine = [m for m in r.json() if m.get("author", {}).get("id") == my_id]
    deleted = 0
    for m in mine:
        rr = api_request("DELETE", "/channels/{}/messages/{}".format(cid, m["id"]), token)
        if rr is not None and rr.status_code in (200, 204):
            deleted += 1; ok("supprime " + m["id"])
        time.sleep(1)
    info("Termine : {} messages supprimes.".format(deleted))


def feature_token_info(token):
    user = check_token(token)
    if not user:
        err("Token invalide."); return
    print(Fore.LIGHTCYAN_EX + "\n  --- INFO COMPTE ---")
    for k in ("id", "username", "global_name", "email", "phone", "verified",
              "mfa_enabled", "premium_type", "locale"):
        v = user.get(k, "-")
        print("  {}: {}".format(k, v))


def feature_nickname_all_servers(token):
    nick = ask("Nouveau pseudo (vide = reset)")
    delay = ask_float("Delai (s)", 2)
    guilds = get_guilds(token)
    done = 0
    payload = {"nick": nick} if nick else {"nick": None}
    for i, g in enumerate(guilds, 1):
        r = api_request("PATCH", "/guilds/{}/members/@me".format(g.get("id")), token,
                        json=payload)
        if r is not None and r.status_code in (200, 204):
            done += 1; ok("[{}/{}] {} -> ok".format(i, len(guilds), g.get("name", "?")))
        time.sleep(delay)
    info("Termine : {} pseudos changes.".format(done))


def feature_send_attachment(token):
    uid = ask("ID utilisateur destinataire")
    path = ask("Chemin du fichier")
    if not uid or not os.path.exists(path):
        err("Champs invalides."); return
    cid = open_dm(token, uid)
    if not cid:
        err("DM impossible."); return
    h = get_headers(token); h.pop("Content-Type", None)
    with open(path, "rb") as f:
        files = {"file": (os.path.basename(path), f)}
        r = requests.post(API_BASE + "/channels/{}/messages".format(cid),
                          headers=h, files=files, timeout=60)
    if r.status_code in (200, 201):
        ok("Fichier envoye.")
    else:
        err("Echec : " + r.text[:200])


def feature_list_dms(token):
    dms = get_dm_channels(token)
    print(Fore.LIGHTCYAN_EX + "\n  --- DMs ouverts ---")
    for d in dms:
        recs = d.get("recipients", [])
        names = ", ".join([u.get("username", "?") for u in recs])
        print("  {}  ->  {}".format(d.get("id"), names))
    info("{} DMs.".format(len(dms)))


def feature_username_generator(token):
    """Generateur de pseudos 3-4 lettres avec verification de dispo."""
    print("  " + c(C_DIM, "Longueur 3 (rare/cher) ou 4 lettres ?"))
    length = ask_int("Longueur (3 ou 4)", 3)
    if length not in (3, 4):
        length = 3
    count = ask_int("Combien de pseudos disponibles veux-tu trouver ?", 10)
    delay = ask_float("Delai entre tests (s)", 1.0)
    mode = ask("Mode : (l)ettres / (a)lphanumerique / (n)umbers", "l").lower()
    sys_mode = ask("Iteration : (r)andom ou (s)ystematique a-z ?", "r").lower()

    if mode == "n":
        charset = string.digits
    elif mode == "a":
        charset = string.ascii_lowercase + string.digits
    else:
        charset = string.ascii_lowercase

    info("Recherche de pseudos {} caracteres dispo...".format(length))
    available = []
    tested_set = set()  # ne jamais re-tester le meme
    headers = get_headers(token)
    endpoint = "/unique-username/username-attempt-unauthed"

    def gen_random():
        return "".join(random.choice(charset) for _ in range(length))

    def gen_systematic():
        """Itere a-z, aa-zz, etc. dans l'ordre."""
        import itertools
        for combo in itertools.product(charset, repeat=length):
            yield "".join(combo)

    if sys_mode == "s":
        info("Mode systematique : {} combinaisons possibles.".format(len(charset) ** length))
        gen = gen_systematic()
    else:
        gen = None

    max_tests = max(2000, count * 300)
    tested = 0

    while len(available) < count and tested < max_tests:
        if sys_mode == "s":
            try:
                candidate = next(gen)
            except StopIteration:
                warn("Toutes les combinaisons testees.")
                break
        else:
            # Random mais sans repetition
            attempts = 0
            candidate = gen_random()
            while candidate in tested_set and attempts < 50:
                candidate = gen_random()
                attempts += 1

        if candidate in tested_set:
            continue
        tested_set.add(candidate)
        tested += 1

        try:
            r = requests.post(
                API_BASE + endpoint,
                headers=headers,
                json={"username": candidate},
                timeout=15,
            )
        except requests.RequestException as e:
            err("Reseau : " + str(e)); time.sleep(2); continue

        if r.status_code == 429:
            try:
                retry = float(r.json().get("retry_after", 3))
            except Exception:
                retry = 3
            warn("Rate limit, pause {:.1f}s...".format(retry))
            time.sleep(retry + 0.5)
            continue

        if r.status_code != 200:
            print("  " + c(C_DIM, "test {} -> HTTP {} {}".format(
                candidate, r.status_code, r.text[:60])))
            time.sleep(delay); continue

        try:
            data = r.json()
        except Exception:
            data = {}

        taken = data.get("taken", True)
        if not taken:
            ok("DISPO : " + c(C_LIGHT, candidate) + c(C_DIM, "  (test #" + str(tested) + ")"))
            available.append(candidate)
        else:
            print("  " + c(C_DIM, "  pris   : " + candidate + "  (#" + str(tested) + ")"))

        time.sleep(delay)

    if not available:
        warn("Aucun pseudo dispo trouve apres {} tests uniques.".format(tested))
        return

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "available_usernames.txt")
    with open(out_path, "a", encoding="utf-8") as f:
        for u in available:
            f.write(u + "\n")
    info("{} pseudos dispo sauves -> {}".format(len(available), out_path))

    if ask("Veux-tu en prendre un maintenant ? (o/N)", "n").lower().startswith("o"):
        choice = ask("Quel pseudo ?", available[0])
        password = ask("Mot de passe du compte (requis Discord)")
        if not password:
            warn("Mot de passe requis."); return
        r = api_request("PATCH", "/users/@me", token,
                        json={"username": choice, "password": password})
        if r is not None and r.status_code == 200:
            ok("Pseudo change : " + c(C_LIGHT, choice))
        else:
            err("Echec : HTTP {} - {}".format(
                r.status_code if r else "?",
                r.text[:200] if r else ""))


def feature_nitro_generator(token):
    """Generateur de codes Nitro avec verification multi-threadee.

    ATTENTION : Les codes Nitro Discord font 16 caracteres pour les classic gifts
    et 24 pour les anciens. Les chances de trouver un code valide en brute force
    sont astronomiquement faibles (~1 sur 10^20+). Cette fonction est fournie
    pour usage pedagogique / educatif.
    """
    warn("=" * 60)
    warn("ATTENTION : la probabilite de trouver un code valide est")
    warn("astronomiquement faible (de l'ordre de 1 sur 10^20).")
    warn("Cette fonction est fournie a titre experimental.")
    warn("=" * 60)
    print()

    if ask("Continuer quand meme ? (o/N)", "n").lower() != "o":
        info("Annule.")
        return

    print("  " + c(C_DIM, "Format de code :"))
    print("  " + c(220, "  1") + c(C_LIGHT, " Nitro 16 char ") + c(C_DIM, "(format moderne)"))
    print("  " + c(220, "  2") + c(C_LIGHT, " Nitro 24 char ") + c(C_DIM, "(ancien format)"))
    print("  " + c(220, "  3") + c(C_LIGHT, " Mixte 16+24   ") + c(C_DIM, "(alterne les deux)"))
    fmt = ask_int("Choix", 1)

    total_tests = ask_int("Nombre TOTAL de codes a tester (max 100000)", 5000)
    total_tests = min(total_tests, 100000)
    workers = ask_int("Threads paralleles (1-15, plus=plus vite)", 8)
    workers = max(1, min(workers, 15))
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "nitro_valid.txt")

    charset = string.ascii_letters + string.digits
    headers = get_headers(token)

    def gen_code():
        if fmt == 1:
            return "".join(random.choice(charset) for _ in range(16))
        if fmt == 2:
            return "".join(random.choice(charset) for _ in range(24))
        # mixte
        return "".join(random.choice(charset) for _ in range(random.choice([16, 24])))

    found = []
    tested_count = [0]
    start = time.time()
    lock_print = []

    def check_code(code):
        url = API_BASE + "/entitlements/gift-codes/{}?with_application=false&with_subscription_plan=true".format(code)
        try:
            r = requests.get(url, headers=headers, timeout=10)
        except requests.RequestException:
            return None
        tested_count[0] += 1
        if r.status_code == 200:
            try:
                data = r.json()
                # Valide
                return ("valid", code, data)
            except Exception:
                return ("valid", code, {})
        elif r.status_code == 429:
            try:
                retry = float(r.json().get("retry_after", 1))
            except Exception:
                retry = 1
            time.sleep(retry + 0.2)
            return ("ratelimit", code, None)
        return None

    info("Demarrage avec {} threads. Ctrl+C pour stopper.".format(workers))
    print()

    try:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=workers) as ex:
            batch_size = workers * 4
            remaining = total_tests
            while remaining > 0 and len(found) < 10:
                size = min(batch_size, remaining)
                codes = [gen_code() for _ in range(size)]
                futures = [ex.submit(check_code, c) for c in codes]
                for fut in as_completed(futures):
                    res = fut.result()
                    if res and res[0] == "valid":
                        code = res[1]
                        found.append(code)
                        print()
                        ok(c(C_LIGHT, "*** CODE VALIDE TROUVE ***  " + code))
                        ok("URL : https://discord.gift/" + code)
                        with open(save_path, "a", encoding="utf-8") as f:
                            f.write(code + "  (" + time.strftime("%Y-%m-%d %H:%M:%S") + ")\n")
                remaining -= size
                # Affichage progression
                elapsed = time.time() - start
                rate = tested_count[0] / elapsed if elapsed > 0 else 0
                sys.stdout.write("\r  " + c(C_DIM,
                    "  Tests: {} / {}  |  {:.1f}/s  |  {:.1f}s ecoule  |  trouves: {}     ".format(
                        tested_count[0], total_tests, rate, elapsed, len(found))))
                sys.stdout.flush()
    except KeyboardInterrupt:
        warn("\nInterrompu par l'utilisateur.")

    print()
    print()
    info("Termine : {} codes testes en {:.1f}s ({:.1f}/s)".format(
        tested_count[0], time.time() - start,
        tested_count[0] / max(time.time() - start, 0.01)))
    if found:
        ok("{} code(s) valide(s) trouve(s) ! Sauvegardes dans : {}".format(
            len(found), save_path))
        for fcode in found:
            print("  " + c(C_LIGHT, SYM_BULLET) + " https://discord.gift/" + fcode)
    else:
        warn("Aucun code valide trouve (statistiquement normal).")
        info("Math : 1 chance sur ~10^20 = il faudrait des milliards d'annees.")


def feature_set_hypesquad(token):
    """Assigne une maison HypeSquad (badge automatiquement debloque)."""
    print("  " + c(C_DIM, "Maisons HypeSquad disponibles :"))
    print("  " + c(220, "  1") + c(C_LIGHT, " Bravery   ") + c(C_DIM, "(violet)"))
    print("  " + c(220, "  2") + c(C_LIGHT, " Brilliance") + c(C_DIM, " (rose)"))
    print("  " + c(220, "  3") + c(C_LIGHT, " Balance   ") + c(C_DIM, "(vert)"))
    choice = ask_int("Choix (1/2/3)", 1)
    if choice not in (1, 2, 3):
        warn("Choix invalide."); return
    house_names = {1: "Bravery", 2: "Brilliance", 3: "Balance"}
    r = api_request("POST", "/hypesquad/online", token, json={"house_id": choice})
    if r is None:
        err("Pas de reponse Discord."); return
    if r.status_code in (200, 204):
        ok("Maison HypeSquad assignee : " + c(C_LIGHT, house_names[choice]))
        info("Le badge apparaitra sur ton profil dans quelques secondes.")
    else:
        err("Echec : HTTP {} - {}".format(r.status_code, r.text[:200]))


def feature_badges_guide(token):
    """Liste tous les badges Discord et explique comment obtenir chacun."""
    # Recupere les badges actuels du user
    me = check_token(token)
    flags = me.get("public_flags", 0) if me else 0

    # Mapping flag bits -> badge name (source: Discord API docs)
    FLAGS = [
        (1 << 0,  "Discord Employee",          "Reserve aux employes Discord (impossible)"),
        (1 << 1,  "Discord Partner",           "Etre partenaire Discord (programme officiel ferme/limite)"),
        (1 << 2,  "HypeSquad Events",          "Participer aux events Discord (rare)"),
        (1 << 3,  "Bug Hunter Level 1",        "Reporter des bugs valides sur Discord Beta"),
        (1 << 6,  "HypeSquad Bravery",         "AUTOMATISABLE : option 'HypeSquad badge' du menu"),
        (1 << 7,  "HypeSquad Brilliance",      "AUTOMATISABLE : option 'HypeSquad badge' du menu"),
        (1 << 8,  "HypeSquad Balance",         "AUTOMATISABLE : option 'HypeSquad badge' du menu"),
        (1 << 9,  "Early Supporter",           "Discontinue (badge avant oct 2018, impossible aujourd'hui)"),
        (1 << 14, "Bug Hunter Level 2",        "Bug Hunter avance (encore plus rare)"),
        (1 << 17, "Early Verified Bot Dev",    "Discontinue depuis 2020 (impossible)"),
        (1 << 18, "Discord Certified Mod",     "Programme arrete depuis dec 2022 (impossible)"),
        (1 << 22, "Active Developer",          "POSSIBLE : creer un bot, envoyer 1 commande slash, "
                                               "puis aller sur discord.com/developers/active-developer"),
    ]

    print()
    print(section_header("BADGES DE TON COMPTE", C_LIGHT))
    print()
    for bit, name, _ in FLAGS:
        has = (flags & bit) != 0
        symbol = c(C_ACCENT, SYM_OK) if has else c(C_DIM, "·")
        print("  " + symbol + " " + c(C_LIGHT if has else C_DIM, name))

    print()
    print(section_header("COMMENT OBTENIR CHAQUE BADGE", C_ACCENT))
    print()
    for _, name, how in FLAGS:
        print("  " + c(C_PRIMARY, SYM_BULLET) + " " + c(C_LIGHT, name))
        print("    " + c(C_DIM, how))
    print()

    print(section_header("BADGES NITRO (payants)", 220))
    print()
    nitro_badges = [
        ("Nitro",            "Abonnement Discord Nitro (9.99$/mois ou 99.99$/an)"),
        ("Nitro Basic",      "Discord Nitro Basic (2.99$/mois)"),
        ("Server Booster 1m+", "Booster un serveur pendant 1+ mois (necessite Nitro)"),
        ("Server Booster 24m", "Booster un serveur pendant 2 ans"),
        ("Legacy Username",  "Avoir change ton username avant le systeme pomelo"),
    ]
    for name, how in nitro_badges:
        print("  " + c(220, SYM_BULLET) + " " + c(C_LIGHT, name))
        print("    " + c(C_DIM, how))
    print()

    warn("RAPPEL : la plupart des badges Discord ne peuvent PAS etre obtenus via API.")
    warn("        Les seuls programmables sont les 3 HypeSquad (option dediee du menu).")


def feature_random_message_friends(token):
    """Envoie un message aleatoire (parmi une liste) a chaque ami."""
    raw = ask("Messages separes par |  (ex: Hi|Salut|Yo)")
    if not raw:
        return
    messages = [m.strip() for m in raw.split("|") if m.strip()]
    delay = ask_float("Delai (s)", 3)
    friends = get_friends(token)
    sent = 0
    for i, f in enumerate(friends, 1):
        msg = random.choice(messages)
        uid = f.get("user", {}).get("id")
        cid = open_dm(token, uid)
        if cid and send_message(token, cid, msg):
            sent += 1; ok("[{}/{}] -> envoye".format(i, len(friends)))
        time.sleep(delay)
    info("Termine : {} envoyes.".format(sent))


# --------------------------------------------------------------------------
# Menu
# --------------------------------------------------------------------------
# Menu : (categorie, label, fonction)
MENU = [
    ("Messagerie", "DM all friends",                 "feature_dm_all_friends"),
    ("Messagerie", "DM aleatoire (multi-messages)",  "feature_random_message_friends"),
    ("Messagerie", "Spam DM (un utilisateur)",       "feature_spam_dm"),
    ("Messagerie", "Envoyer un fichier en DM",       "feature_send_attachment"),
    ("Messagerie", "Ghost ping",                     "feature_ghost_ping"),
    ("Messagerie", "Auto-react messages",            "feature_auto_react"),
    ("Messagerie", "Nettoyer mes messages",          "feature_clear_my_messages"),
    ("Amis",       "Add friends (par IDs)",          "feature_friend_request_by_ids"),
    ("Amis",       "Add all server (tous membres)",  "feature_friend_request_in_guild"),
    ("Amis",       "Remove all friends",             "feature_remove_all_friends"),
    ("Amis",       "Block all friends",              "feature_block_all_friends"),
    ("Amis",       "Unblock all",                    "feature_unblock_all"),
    ("Serveurs",   "Leave all servers",              "feature_leave_all_servers"),
    ("Serveurs",   "Rejoindre un serveur (invite)",  "feature_join_server"),
    ("Serveurs",   "Info serveur (par ID)",          "feature_server_info"),
    ("Serveurs",   "Pseudo tous serveurs",           "feature_nickname_all_servers"),
    ("Compte",     "Changer statut",                 "feature_set_status"),
    ("Compte",     "Custom status text",             "feature_set_custom_status"),
    ("Compte",     "Changer pseudo (username)",      "feature_change_username"),
    ("Compte",     "Changer bio",                    "feature_change_bio"),
    ("Compte",     "Changer avatar",                 "feature_change_avatar"),
    ("Compte",     "Username generator (3-4 lettres)","feature_username_generator"),
    ("Compte",     "Nitro generator (brute force)",   "feature_nitro_generator"),
    ("Compte",     "HypeSquad badge (auto)",         "feature_set_hypesquad"),
    ("Compte",     "Guide tous les badges Discord",  "feature_badges_guide"),
    ("Compte",     "Info compte (token info)",       "feature_token_info"),
    ("DMs",        "Close all DM channels",          "feature_close_all_dms"),
    ("DMs",        "Lister mes DMs ouverts",         "feature_list_dms"),
    ("Export",     "Exporter liste amis",            "feature_export_friends"),
    ("Export",     "Exporter liste serveurs",        "feature_export_servers"),
    ("Export",     "Exporter historique DM",         "feature_export_dm_history"),
    ("Export",     "Info utilisateur (par ID)",      "feature_user_info"),
]

CAT_COLORS = {
    "Messagerie": 39,
    "Amis":       51,
    "Serveurs":   45,
    "Compte":     123,
    "DMs":        87,
    "Export":     159,
}


def render_header(user):
    """Barre de statut en haut du menu."""
    uname = user.get("username", "?")
    uid = user.get("id", "?")
    discord_tag = "@" + uname
    box_w = 64
    title = c(C_LIGHT, "  SEPTIM TOOLS")
    ver = c(C_DIM, " v2.0")
    user_line = c(C_ACCENT, SYM_BULLET) + " " + c(C_LIGHT, discord_tag) + c(C_DIM, "  id:" + uid)
    print(c(C_PRIMARY, "  ╔" + "═" * box_w + "╗"))
    print(c(C_PRIMARY, "  ║") + title + ver +
          " " * max(0, box_w - len("  SEPTIM TOOLS v2.0")) + c(C_PRIMARY, "║"))
    visible_len = len("  ● @" + uname + "  id:" + uid)
    print(c(C_PRIMARY, "  ║  ") + user_line +
          " " * max(0, box_w - 2 - visible_len) + c(C_PRIMARY, "║"))
    print(c(C_PRIMARY, "  ╚" + "═" * box_w + "╝"))


def render_menu(user):
    clear()
    print(gradient_text(BANNER))
    render_header(user)
    print()

    # Group by category in insertion order
    cats = []
    for cat, _, _ in MENU:
        if cat not in cats:
            cats.append(cat)

    idx = 1
    items_by_cat = {ca: [] for ca in cats}
    for cat, label, _ in MENU:
        items_by_cat[cat].append((idx, label))
        idx += 1

    # 2 columns of categories
    col_w = 36
    col1 = cats[:3]
    col2 = cats[3:]

    def cat_lines(cat_list):
        lines = []
        for ca in cat_list:
            color = CAT_COLORS.get(ca, C_ACCENT)
            lines.append(c(color, "  ┌─ " + ca + " " + "─" * (col_w - len(ca) - 5)))
            for n, lbl in items_by_cat[ca]:
                num = c(C_DIM, "{:>2}".format(n))
                arrow = c(color, " " + SYM_BULLET + " ")
                text = lbl if len(lbl) <= col_w - 6 else lbl[:col_w - 9] + "..."
                lines.append("  " + num + arrow + c(C_LIGHT, text))
            lines.append("")
        return lines

    L = cat_lines(col1)
    R = cat_lines(col2)
    height = max(len(L), len(R))
    while len(L) < height:
        L.append("")
    while len(R) < height:
        R.append("")
    for a, b in zip(L, R):
        # Pad left column to col_w + 4 (margin)
        # Stripping ANSI for length calc is complex; use simple pad
        pad = " " * max(0, col_w + 6 - _visible_len(a))
        print(a + pad + b)

    print()
    print("  " + c(196, "{:>2}".format(0)) + c(196, " " + SYM_BULLET + " ") +
          c(C_DIM, "Quitter"))
    print()


def _visible_len(s):
    """Approx visible length (strip ANSI escape sequences)."""
    return len(re.sub(r"\033\[[0-9;]*m", "", s))


def main():
    cfg = load_config()
    raw_token = cfg.get("token", "")
    token = normalize_token(raw_token)
    if not token or token == "YOUR_DISCORD_TOKEN_HERE":
        clear()
        print(gradient_text(BANNER))
        err("Token non configure dans config.json")
        input("\n  Entree pour quitter...")
        return

    if len(token) < 50:
        clear()
        print(gradient_text(BANNER))
        err("Token trop court ({} caracteres). Un token Discord fait ~70+ caracteres.".format(len(token)))
        warn("Verifiez que vous avez colle le TOKEN COMPLET dans config.json")
        input("\n  Entree pour quitter...")
        return

    clear()
    print(gradient_text(BANNER))
    info("Verification du token...")
    user = check_token(token)
    if not user:
        warn("")
        warn("Comment recuperer votre token Discord :")
        warn("  1) Ouvrez Discord dans Chrome/Firefox (pas l'app)")
        warn("  2) F12 -> Network")
        warn("  3) Cliquez sur un salon -> requete -> Headers -> 'authorization'")
        warn("  4) Copiez la valeur complete dans config.json")
        input("\n  Entree pour quitter...")
        return

    ok("Connecte : " + c(C_LIGHT, "@" + user.get("username", "?")) +
       c(C_DIM, "  id=" + user.get("id", "?")))
    time.sleep(1.1)

    while True:
        render_menu(user)
        choice = ask_int("Votre choix", 0)
        if choice == 0:
            clear()
            print(gradient_text(BANNER))
            print(c(C_ACCENT, "\n  " + SYM_BULLET + " A bientot.\n"))
            return
        if 1 <= choice <= len(MENU):
            cat, name, fname = MENU[choice - 1]
            clear()
            print(gradient_text(BANNER))
            print(section_header(cat + "  " + SYM_ARROW + "  " + name,
                                 CAT_COLORS.get(cat, C_ACCENT)))
            print()
            func = globals().get(fname)
            try:
                if fname == "feature_dm_all_friends":
                    func(token, cfg)
                else:
                    func(token)
            except KeyboardInterrupt:
                warn("Interrompu.")
            except Exception as e:
                err("Erreur inattendue : " + str(e))
            print()
            print(hr())
            pause()
        else:
            warn("Choix invalide.")
            time.sleep(0.6)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  " + c(220, SYM_WARN) + " Interrompu par l'utilisateur.\n")
