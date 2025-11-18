#!/bin/bash

ORIGINAL_FILE="in.json"
INPUT_FILE="estados.txt"
OUTPUT_FILE="random.csv"
BASE_URL="https://www.consorciorandon.com.br"
CIDADES_ENDPOINT="$BASE_URL/localize/buscacidadesunidades"
UNIDADES_ENDPOINT="$BASE_URL/localize/buscaunidades"

# Converter arquivo original para formato correto
cat "$ORIGINAL_FILE" | tr ' ' '\n' | paste - - > "$INPUT_FILE"

# Cabeçalho do CSV
echo "nome,endereco,cidade,estado,pagina" > "$OUTPUT_FILE"

while read -r sigla id; do
    echo "Processando estado: $sigla (ID: $id)"

    cidades_json=$(curl -s "$CIDADES_ENDPOINT" --data-raw "estados_id=$id")

    cidades=$(echo "$cidades_json" | jq -r '.[] | "\(.cidades_id) \(.nome)"')

    if [ -z "$cidades" ]; then
        echo "Nenhuma cidade encontrada para $sigla"
        continue
    fi

    while read -r cidade_id cidade_nome; do
        echo "  Cidade: $cidade_nome (ID: $cidade_id)"

        unidades_json=$(curl -s "$UNIDADES_ENDPOINT" --data-raw "estado=$id&cidade=$cidade_id")

        unidades=$(echo "$unidades_json" | jq -r --arg cidade "$cidade_nome" --arg estado "$sigla" --arg homepage "$BASE_URL" \
            '.[] | "\(.nome),\(.endereco),\($cidade),\($estado),\(.pagina // $homepage)"')

        if [ -n "$unidades" ]; then
            echo "$unidades" >> "$OUTPUT_FILE"
        fi
    done <<< "$cidades"

done < "$INPUT_FILE"

echo "Arquivo CSV gerado: $OUTPUT_FILE"
