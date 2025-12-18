#!/bin/bash
echo "Creazione black-list di esempio..."

PREFIXES=("02" "06" "0289" "0645")

for prefix in "${PREFIXES[@]}"; do
    echo "Aggiunta prefisso: $prefix"
    sudo blacklist-cli add-prefix "$prefix"
done

echo ""
echo "✓ Black-list di esempio creata"
echo "Per vedere: sudo blacklist-cli list"
