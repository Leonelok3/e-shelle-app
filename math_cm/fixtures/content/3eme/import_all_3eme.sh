#!/bin/bash
# Import de tous les chapitres de 3ème dans la base de données
# Usage: bash math_cm/fixtures/content/3eme/import_all_3eme.sh

echo "=== Import 3ème — MathCM ==="

# NB: ch01 s'appelle ch01_lecons.json mais est de type cours_complet
FILES=(
  "math_cm/fixtures/content/3eme/ch01_lecons.json"
  "math_cm/fixtures/content/3eme/ch02_complet.json"
  "math_cm/fixtures/content/3eme/ch03_complet.json"
  "math_cm/fixtures/content/3eme/ch04_complet.json"
  "math_cm/fixtures/content/3eme/ch05_complet.json"
  "math_cm/fixtures/content/3eme/ch06_complet.json"
  "math_cm/fixtures/content/3eme/ch07_complet.json"
  "math_cm/fixtures/content/3eme/ch08_complet.json"
  "math_cm/fixtures/content/3eme/ch09_complet.json"
  "math_cm/fixtures/content/3eme/ch10_complet.json"
  "math_cm/fixtures/content/3eme/ch11_complet.json"
  "math_cm/fixtures/content/3eme/ch12_complet.json"
  "math_cm/fixtures/content/3eme/ch13_complet.json"
  "math_cm/fixtures/content/3eme/ch14_complet.json"
  "math_cm/fixtures/content/3eme/ch15_complet.json"
)

for FILE in "${FILES[@]}"; do
  echo ""
  echo ">>> Import: $FILE"
  python manage.py import_content --file "$FILE"
done

echo ""
echo "=== Terminé ! ==="
