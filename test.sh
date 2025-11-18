#!/bin/bash

FILE="in.json"
URL="https://www.consorciorandon.com.br/localize/buscacidadesunidades"

for id in $(awk '{for(i=2;i<=NF;i+=2) print $i}' "$FILE"); do
    echo "Sending request for ID: $id"
    curl -s "$URL" --data-raw "estados_id=$id"
    echo -e "\n---\n"
done

