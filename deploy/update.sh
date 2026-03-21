#!/bin/bash
##############################################################################
#  update.sh — Mise à jour du code en production (sans coupure)
#  Exécuter : sudo bash update.sh
##############################################################################
set -e

APP_USER="eshelle"
APP_DIR="/home/$APP_USER/app"

echo "→ Pull du code..."
sudo -u $APP_USER git -C "$APP_DIR" pull origin main

echo "→ Installation des nouvelles dépendances..."
sudo -u $APP_USER "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt" -q

echo "→ Migrations..."
sudo -u $APP_USER "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" migrate --noinput

echo "→ Collecte des statiques..."
sudo -u $APP_USER "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" collectstatic --noinput

echo "→ Rechargement Gunicorn (gracieux)..."
systemctl reload eshelle 2>/dev/null || systemctl restart eshelle

echo "✅ Mise à jour terminée — aucune coupure de service."
