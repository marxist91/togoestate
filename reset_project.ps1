# ================================
# Script de reset complet Django
# ================================

Write-Host "=== Nettoyage des migrations ==="

# Supprimer les migrations (sauf __init__.py)
Get-ChildItem -Path "agencies\migrations" -Recurse -Include *.py,*.pyc | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item -Force
Get-ChildItem -Path "accounts\migrations" -Recurse -Include *.py,*.pyc | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item -Force
Get-ChildItem -Path "listings\migrations" -Recurse -Include *.py,*.pyc | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item -Force

Write-Host "=== Suppression de la base SQLite ==="

# Supprimer la base SQLite si elle existe
if (Test-Path "db.sqlite3") {
    Remove-Item "db.sqlite3" -Force
    Write-Host "Base SQLite supprimée."
} else {
    Write-Host "Pas de base SQLite trouvée."
}

Write-Host "=== Recréation des migrations ==="

# Recréer les migrations propres
python manage.py makemigrations agencies accounts listings

Write-Host "=== Application des migrations ==="

# Appliquer les migrations
python manage.py migrate

Write-Host "=== Chargement des données géographiques ==="

# Charger le fixture des localisations
python manage.py loaddata togo_locations.json

Write-Host "=== Création d'un superuser (si nécessaire) ==="

# Proposer la création d'un superuser
python manage.py createsuperuser

Write-Host "=== Reset terminé avec succès 🚀 ==="