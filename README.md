# Septim Tools v2.0

Outil Discord en Python complet - 28 fonctionnalites en menu interactif.

## Contenu du ZIP

| Fichier              | Description                                    |
| -------------------- | ---------------------------------------------- |
| `septim_tools.py`    | Script principal avec menu interactif          |
| `config.json`        | Configuration (token, message par defaut, delai) |
| `install.bat`        | Installation auto des dependances (Windows)    |
| `README.md`          | Ce fichier                                     |

## Installation

### Dans le fichier
1. Double-cliquez sur `install.bat`
2. Patientez la fin de l'installation

### Manuelle (tous OS)
```bash
pip install requests colorama
```

## POUR CONFIGURER LE TOOLS 

Editez `config.json` :

```json
{
  "token": "VOTRE_TOKEN_DISCORD",
  "message": "Message par defaut pour DM all friends",
  "delay_seconds": 3
}
```

| Champ          | Description                                                |
| -------------- | ---------------------------------------------------------- |
| `token`        | Votre token Discord                                        |
| `message`      | Message par defaut suggere dans certaines fonctionnalites  |
| `delay_seconds`| Delai par defaut anti rate-limit                           |

## Lancement

```bash
python septim_tools.py
```

tools menu 

## Liste complete des 28 fonctionnalites

### Messagerie & DM
1.  **DM all friends** - Envoyer un message a tous vos amis
2.  **DM aleatoire a tous les amis** - Choisir aleatoirement parmi plusieurs messages
3.  **Spam DM (un user)** - Envoyer N fois le meme message a un utilisateur
4.  **Envoyer un fichier en DM** - Joindre une image / fichier
5.  **Ghost ping** - Mention puis suppression instantanee
6.  **Auto-react messages** - Reagir aux N derniers messages d'un salon
7.  **Nettoyer mes messages** - Supprimer vos messages dans un salon

### Amis
8.  **Add friends (par IDs)** - Envoyer des demandes via une liste d'IDs
9.  **Add all server** - Envoyer une demande d'ami a TOUS les membres d'un serveur (via search API, fonctionne avec user token)
10. **Remove all friends** - Supprimer tous vos amis (confirmation requise)
11. **Block all friends** - Bloquer tous vos amis (confirmation requise)
12. **Unblock all** - Debloquer tous les utilisateurs bloques

### Serveurs
13. **Leave all servers** - Quitter tous vos serveurs (confirmation requise)
14. **Rejoindre un serveur (invite)** - Via un code d'invitation
15. **Info serveur (par ID)** - Afficher les details d'un serveur
16. **Pseudo tous serveurs (nick)** - Changer votre nickname sur tous les serveurs

### Compte
17. **Changer statut** - Online / Idle / DND / Invisible
18. **Custom status text** - Statut personnalise
19. **Changer pseudo (username)** - Necessite votre mot de passe
20. **Changer bio** - Bio de profil
21. **Changer avatar** - Depuis un fichier png/jpg/gif local
22. **Info compte (token info)** - Affiche les infos liees au token

### DMs & Channels
23. **Close all DM channels** - Fermer toutes vos conversations DM
24. **Lister mes DMs ouverts** - Liste avec les IDs

### Export & Recherche
25. **Exporter liste amis** -> `friends_export.json`
26. **Exporter liste serveurs** -> `servers_export.json`
27. **Exporter historique DM** -> `dm_<channel>.json`
28. **Info utilisateur (par ID)** - Recherche un utilisateur par son ID

## Fonctionnalites techniques

- Banner ASCII en degrade Bleu Fonce -> Bleu Ciel (ANSI 256 colors)
- Verification automatique du token au lancement
- Gestion automatique des rate limits (retry-after)
- Menu interactif en 2 colonnes
- Confirmations pour les actions destructives
- Pause apres chaque action pour lire le resultat
- Aucune dependance lourde (juste `requests` + `colorama`)

## Requis

- Python 3.8+
- Connexion Internet
- Packages : `requests`, `colorama`

## Astuces

- Pour quitter une action en cours : `Ctrl+C` (revient au menu)
- Les exports JSON sont sauves dans le dossier du script
- Le delai par defaut est lu depuis `config.json`, mais modifiable a chaque action

---

**Septim Tools v2.0**
