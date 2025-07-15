from ldap3 import Server, Connection, ALL, NTLM
import sys

# Config AD
AD_SERVER = 'ldaps://10.3.0.107'  # LDAPS (SSL)
AD_DOMAIN = 'CAPLOGY'                # NetBIOS name
AD_USER = 'CAPLOGY\\t.frescaline'  # ou juste 'monutilisateur' avec NTLM
AD_PASSWORD = '&NC$U&QS*8cbiy'

# Connexion LDAPS (port 636, SSL)
server = Server(AD_SERVER, get_info=None, use_ssl=True)
conn = Connection(server, user=AD_USER, password=AD_PASSWORD, authentication=NTLM)

if conn.bind():
    print("✅ Authentifié avec succès (LDAPS)")
else:
    print("❌ Échec d’authentification (LDAPS)")
    print(f"LDAP result: {conn.result}")
    print(f"LDAP last error: {conn.last_error}")
    print(f"User utilisé: {AD_USER}")
    print(f"Serveur: {AD_SERVER}")

conn.unbind()
