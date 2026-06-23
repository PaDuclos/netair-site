#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apercu.py — Aperçu EN DIRECT des fiches techniques.

But : modifier le contenu d'une fiche (le formulaire produits/<nom>.json) et voir
le résultat se mettre à jour TOUT SEUL dans le navigateur, sans relancer de commande.

Comment ça marche :
  1. on lance un petit serveur local (cette fenêtre) ;
  2. le navigateur s'ouvre sur la fiche ;
  3. on édite le formulaire produits/<nom>.json dans un éditeur de texte, on ENREGISTRE ;
  4. la fiche est régénérée et le navigateur se rafraîchit automatiquement.

Le rafraîchissement automatique est ajouté « à la volée » (uniquement à l'écran) :
les fichiers de fiches livrés ne sont JAMAIS modifiés → le test d'identité NETPLY
reste valable.

Usage :
    python3 apercu.py            # surveille toutes les fiches + page d'accueil avec la liste
    python3 apercu.py netplan    # ouvre directement la fiche NETPLAN

Pour arrêter : fermer cette fenêtre, ou faire Ctrl+C.
"""

import glob
import http.server
import json
import os
import socketserver
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
PRODUITS = os.path.join(ROOT, "produits")
FICHES = os.path.abspath(os.path.join(ROOT, "..", "Fiches_Netair"))
PORT_BASE = 8765

# Compteur de version : incrémenté à chaque régénération. Le navigateur le surveille
# (via /__reload) et se recharge dès qu'il change.
_version = 0
_lock = threading.Lock()

# Script de rafraîchissement auto, injecté À LA VOLÉE (jamais écrit sur le disque).
RELOAD_JS = (
    "<script>(function(){var v=null;setInterval(function(){"
    "fetch('/__reload').then(function(r){return r.text();}).then(function(t){"
    "if(v===null){v=t;return;}if(t!==v){location.reload();}})"
    ".catch(function(){});},800);})();</script>"
)


def bouton_modifier(slug):
    """Bouton flottant « Modifier le texte » : ouvre le formulaire du produit dans
    l'éditeur de texte du Mac (via /__edit). Rien si le produit est inconnu."""
    if not slug:
        return ""
    return (
        "<div style=\"position:fixed; right:18px; bottom:18px; z-index:99999;"
        " font-family:Helvetica,Arial,sans-serif;\">"
        "<button onclick=\"fetch('/__edit?slug=" + slug + "')"
        ".then(function(r){return r.text();}).then(function(t){"
        "var m=document.getElementById('__msg');m.textContent=t;m.style.display='block';"
        "setTimeout(function(){m.style.display='none';},6000);});\""
        " style=\"background:#0F3261; color:#fff; border:none; border-radius:9px;"
        " padding:12px 17px; font-size:14px; font-weight:700; cursor:pointer;"
        " box-shadow:0 3px 10px rgba(15,50,97,.35);\">&#9998; Modifier le texte</button>"
        "<div id=\"__msg\" style=\"display:none; margin-top:9px; background:#fff;"
        " color:#0F3261; border:1px solid #E2E8F0; border-radius:9px; padding:10px 13px;"
        " font-size:12.5px; line-height:1.45; max-width:250px;"
        " box-shadow:0 3px 10px rgba(0,0,0,.18);\"></div></div>"
    )


def injection(slug):
    """Contenu ajouté avant </body> : bouton « Modifier » + rafraîchissement auto."""
    return (bouton_modifier(slug) + RELOAD_JS).encode("utf-8")


def produits():
    """slug -> {path, nom, fichier html attendu} pour chaque formulaire produit."""
    out = {}
    for p in sorted(glob.glob(os.path.join(PRODUITS, "*.json"))):
        if os.path.basename(p) == "_gabarit_ref.json":
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
            out[d["slug"]] = {
                "path": p,
                "nom": d["nom"],
                "file": f"Fiche technique {d['nom']}.html",
            }
        except Exception:
            pass
    return out


def regen(json_path):
    """Régénère la fiche d'un formulaire et incrémente la version (déclenche le refresh)."""
    global _version
    nom = os.path.basename(json_path)
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "generer.py"), json_path],
        cwd=ROOT, capture_output=True, text=True,
    )
    with _lock:
        _version += 1
    if r.returncode == 0:
        print(f"  ✅ {nom} régénéré — l'aperçu se rafraîchit tout seul")
    else:
        print(f"  ⚠️  Souci avec {nom} (la fiche n'a pas pu être régénérée) :")
        print("     " + (r.stderr.strip().replace("\n", "\n     ") or "(pas de détail)"))


def watcher():
    """Surveille produits/*.json et régénère la fiche dès qu'un formulaire est enregistré."""
    mtimes = {}
    for p in glob.glob(os.path.join(PRODUITS, "*.json")):
        try:
            mtimes[p] = os.path.getmtime(p)
        except OSError:
            pass
    while True:
        time.sleep(0.7)
        for p in glob.glob(os.path.join(PRODUITS, "*.json")):
            if os.path.basename(p) == "_gabarit_ref.json":
                continue
            try:
                m = os.path.getmtime(p)
            except OSError:
                continue
            if p not in mtimes:
                mtimes[p] = m
                continue
            if m != mtimes[p]:
                mtimes[p] = m
                print(f"\n✏️  Modification enregistrée : {os.path.basename(p)}")
                regen(p)


def page_accueil():
    """Page d'accueil listant les fiches disponibles (liens cliquables)."""
    items = []
    for slug, info in sorted(produits().items(), key=lambda kv: kv[1]["nom"]):
        href = "/" + urllib.parse.quote(info["file"])
        existe = os.path.isfile(os.path.join(FICHES, info["file"]))
        etat = "" if existe else ' <span style="color:#b08900;">(fiche pas encore générée)</span>'
        items.append(
            f'<li style="margin:6px 0;"><a href="{href}" '
            f'style="color:#0070C8; text-decoration:none; font-weight:600;">'
            f'{info["nom"]}</a>{etat}</li>'
        )
    return (
        "<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'>"
        "<title>Aperçu fiches Netair</title></head>"
        "<body style=\"font-family:Helvetica,Arial,sans-serif; max-width:640px; "
        "margin:40px auto; color:#0F3261; padding:0 20px;\">"
        "<h1 style='font-size:22px;'>Aperçu des fiches techniques Netair</h1>"
        "<p style='color:#4A5E7A;'>Cliquez une fiche pour l'ouvrir. Modifiez le "
        "formulaire <code>produits/&lt;nom&gt;.json</code> et enregistrez : la fiche "
        "se mettra à jour toute seule à l'écran.</p>"
        f"<ul style='list-style:none; padding:0; font-size:16px;'>{''.join(items)}</ul>"
        "</body></html>"
    ).encode("utf-8")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=FICHES, **k)

    def log_message(self, *a):
        pass  # silence : on garde la fenêtre lisible

    def _send(self, data, ctype="text/html; charset=utf-8"):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/__reload":
            with _lock:
                self._send(str(_version).encode(), "text/plain")
            return
        if self.path.startswith("/__edit"):
            self._edit()
            return
        if self.path in ("/", "/index.html"):
            self._send(page_accueil())
            return
        rel = urllib.parse.unquote(self.path.split("?")[0]).lstrip("/")
        full = os.path.join(FICHES, rel)
        if full.endswith(".html") and os.path.isfile(full):
            slug = {info["file"]: s for s, info in produits().items()}.get(rel)
            inj = injection(slug)
            data = open(full, "rb").read()
            if b"</body>" in data:
                data = data.replace(b"</body>", inj + b"</body>", 1)
            else:
                data = data + inj
            self._send(data)
            return
        super().do_GET()  # images, assets, etc.

    def _edit(self):
        """Ouvre le formulaire <slug>.json dans l'éditeur de texte du Mac (TextEdit)."""
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        slug = (q.get("slug") or [None])[0]
        info = produits().get(slug)
        if not info:
            self._send("Formulaire introuvable.".encode("utf-8"), "text/plain; charset=utf-8")
            return
        try:
            subprocess.Popen(["open", "-t", info["path"]])  # -t : éditeur de texte par défaut
            msg = ("Le formulaire s'est ouvert dans l'éditeur de texte. "
                   "Modifiez le texte entre guillemets, enregistrez (Cmd+S), "
                   "puis revenez ici : la fiche se met à jour toute seule.")
        except Exception as e:
            msg = "Impossible d'ouvrir l'éditeur automatiquement : " + str(e)
        self._send(msg.encode("utf-8"), "text/plain; charset=utf-8")


def main():
    arg = sys.argv[1].lower().lstrip("-") if len(sys.argv) > 1 else None
    cible = "/"
    prods = produits()
    if arg:
        if arg in prods:
            cible = "/" + urllib.parse.quote(prods[arg]["file"])
        else:
            print(f"⚠️  Produit « {arg} » inconnu. Ouverture de la liste complète.")

    # Trouve un port libre (au cas où 8765 serait déjà pris).
    httpd = None
    port = PORT_BASE
    for port in range(PORT_BASE, PORT_BASE + 20):
        try:
            httpd = socketserver.TCPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if httpd is None:
        print("❌ Impossible d'ouvrir un port local. Fermez les autres aperçus et réessayez.")
        sys.exit(1)

    threading.Thread(target=watcher, daemon=True).start()
    url = f"http://localhost:{port}{cible}"
    print("=" * 58)
    print("  APERÇU EN DIRECT DES FICHES TECHNIQUES NETAIR")
    print("=" * 58)
    print(f"  Adresse : {url}")
    print("  Éditez un fichier produits/<nom>.json, enregistrez (Cmd+S),")
    print("  la fiche se met à jour toute seule dans le navigateur.")
    print("  Pour arrêter : fermez cette fenêtre (ou Ctrl+C).")
    print("=" * 58)
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Aperçu arrêté.")


if __name__ == "__main__":
    main()
