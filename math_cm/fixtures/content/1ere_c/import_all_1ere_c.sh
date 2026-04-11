#!/bin/bash
# Import de tous les chapitres de 1ère C dans la base de données
# Usage: bash math_cm/fixtures/content/1ere_c/import_all_1ere_c.sh

echo "=== Import 1ère C — MathCM ==="

# Étape 1 : créer la classe et les chapitres
echo ""
echo ">>> Setup chapitres 1ère C"
venv/bin/python manage.py import_content --file "math_cm/fixtures/content/1ere_c/setup_chapitres_1ere_c.json"

FILES=(
  "math_cm/fixtures/content/1ere_c/ch01_complet.json"
  "math_cm/fixtures/content/1ere_c/ch02_complet.json"
  "math_cm/fixtures/content/1ere_c/ch03_complet.json"
  "math_cm/fixtures/content/1ere_c/ch04_complet.json"
  "math_cm/fixtures/content/1ere_c/ch05_complet.json"
  "math_cm/fixtures/content/1ere_c/ch06_complet.json"
  "math_cm/fixtures/content/1ere_c/ch07_complet.json"
  "math_cm/fixtures/content/1ere_c/ch08_complet.json"
  "math_cm/fixtures/content/1ere_c/ch09_complet.json"
  "math_cm/fixtures/content/1ere_c/ch10_complet.json"
  "math_cm/fixtures/content/1ere_c/ch11_complet.json"
  "math_cm/fixtures/content/1ere_c/ch12_complet.json"
  "math_cm/fixtures/content/1ere_c/ch13_complet.json"
  "math_cm/fixtures/content/1ere_c/ch14_complet.json"
  "math_cm/fixtures/content/1ere_c/ch15_complet.json"
)

for FILE in "${FILES[@]}"; do
  echo ""
  echo ">>> Import: $FILE"
  venv/bin/python manage.py import_content --file "$FILE"
done

echo ""
echo "=== Terminé ! 15 chapitres 1ère C importés ==="
