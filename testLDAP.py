from ldap3 import Server, Connection, ALL, NTLM

# Config AD
AD_SERVER = 'ldap://caplogy.local'  # ou IP
AD_DOMAIN = 'CAPLOGY'                # NetBIOS name
AD_USER = 'CAPLOGY\\t.frescaline'  # ou juste 'monutilisateur' avec NTLM
AD_PASSWORD = '&NC$U&QS*8cbiy'

# Connexion
server = Server(AD_SERVER, get_info=None)
conn = Connection(server, user=AD_USER, password=AD_PASSWORD, authentication=NTLM)

if conn.bind():
    print("✅ Authentifié avec succès")
else:
    print("❌ Échec d’authentification")

conn.unbind()
