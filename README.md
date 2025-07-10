# Caplogy

Application de découverte et de partage de contenus pédagogiques intégrant Moodle et Nextcloud.

---

## 1. Introduction

L'application **Caplogy** a pour objectif de centraliser et d'enrichir la découverte de contenus pédagogiques issus de **Moodle**, tout en permettant la gestion et le partage de fichiers via **Nextcloud**.

## 2. Objectifs

* **Faciliter la navigation** entre catégories et cours Moodle
* **Associer un logo** à chaque catégorie (identité visuelle des établissements)
* **Intégrer un accès et un partage** simple des fichiers via Nextcloud
* **Offrir un back‑office minimal** pour les administrateurs (gestion des utilisateurs, catégories, logos)

## 3. Périmètre du projet

### Utilisateurs

* **Administrateurs** : création de catégories, gestion des logos, gestion des utilisateurs
* **Utilisateurs simples** : navigation, consultation, partage de fichiers

### Fonctionnalités hors scope

* Gestion avancée des droits sur Moodle
* Édition de contenu Moodle (hors navigation)

## 4. Spécifications fonctionnelles

1. **Gestion des utilisateurs**

   * Connexion / déconnexion (authentification via LDAP)
   * Gestion localisée des rôles (admin, user)

2. **Navigation Moodle**

   * Liste des catégories principales
   * Visualisation du nombre de cours et de sous‑catégories
   * Liste des cours d'une catégorie
   * Détail des sections & modules d'un cours

3. **Personnalisation des catégories**

   * Création de catégories Moodle depuis l'application
   * Association d'un logo (upload, modification, suppression)

4. **Intégration Nextcloud**

   * Consultation d'un répertoire Nextcloud prédéfini
   * Téléversement de fichiers dans Nextcloud
   * Partage de fichiers (génération de lien)

## 5. Spécifications techniques

* **Backend :** Django 5.2.3 (Python)
* **Frontend :** Django Templates + CSS/JS minimal
* **Base de données :** SQLite
* **Gestion d'environnement :** python-dotenv
* **APIs :** Moodle REST, Nextcloud WebDAV & OCS-API

**Organisation du code :**

* Application `caplogy_app` (views, modèles, formulaires)
* Services dédiés : `moodle_api`, `nextcloud_api`, `user_service`
* Répertoires `static/` & `media/`

## 6. Architecture

* **Couche présentation :** Templates Django
* **Couche métier :** Vues + services
* **Couche données :** Modèles Django (UserProfile, SchoolImage)
* **Intégrations externes :**

  * Moodle via Web Services
  * Nextcloud via WebDAV & OCS

## 7. Contraintes et exigences

* **Sécurité :**

  * Stockage des secrets dans `.env`
  * Utilisation du protocole HTTPS
  * Gestion des sessions Django & protection CSRF
* **Performance :**

  * Mise en cache des catégories et cours
* **Compatibilité :**

  * Navigateurs récents
  * Responsive design (desktop & tablette)

## 8. Tests et validation

* **Tests unitaires** : services, modèles
* **Tests d'intégration** : workflow d’authentification, navigation
* **Recette fonctionnelle** : avec l'équipe pédagogique

## 9. Déploiement

* **Environnements :** dev, staging, production
* **Mode de déploiement :** Docker ou serveur WSGI
* **CI/CD :** GitHub Actions (lint, tests)

## 11. Livrables

* Code source complet
* Documentation technique & guide utilisateur
