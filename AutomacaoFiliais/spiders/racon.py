  echo "Nome,Endereco,Cidade,Estado,Pagina" &&
  curl 'https://www.racon.com.br/unidades-racon-get' \
    -H 'accept: */*' \
    -H 'accept-language: pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7' \
    -H 'content-type: application/json' \
    -b 'PHPSESSID=93ac5572beb968c4ba5496880e1f2383; _gcl_au=1.1.747371674.1763132959; _fbp=fb.2.1763132958974.59471855424324368; _ga=GA1.1.797803532.1763132959; cookie_consent_user_consent_token=iWbzLUQuyfiY; cookie_consent_user_accepted=true; cookie_consent_level=%7B%22strictly-necessary%22%3Atrue%2C%22functionality%22%3Atrue%2C%22tracking%22%3Atrue%2C%22targeting%22%3Atrue%7D; XSRF-TOKEN=eyJpdiI6Iis5WFI0aWpXR2NrYkVGOEF5d05mWFE9PSIsInZhbHVlIjoiK3FvQS9CZVhZelAwQ1ZQVHNTaEE2dlc1SkkyQ2k3UGV3WXpTbWtTcGUwK2o5NFcyRFc5cjBBWHY5SDZwcDVVSW9SRVdCN1FmRnhKelFrLzZqTW43RHFkN0pXYTJkSm1qYmd6TDRMN2VNTVJGbWZ3NEFPZC91Q0NoWEY0T0ExRHEiLCJtYWMiOiI0ODYyMTdkOGNmOTNiM2ZjNmExOWY4ZTJjOTBiYTY5Mzc5YjUyY2RhNDYxYzM1M2JmNDRlZTczMmE4M2I4ZGE3IiwidGFnIjoiIn0%3D; racon_consorcios_session=eyJpdiI6InBYSHNjVUtrQVNUNjJEZXk2b0dWSnc9PSIsInZhbHVlIjoiUUswZWdYVlFOZE0vc1JPZlNUcFFJTkVSbFhwM1ExcUJJT25HWjBTZGNJRlZXZDFxSlp2LzcwbUpMZjdkaTB2MFBSeW01SDNkbUtpbTA3UXU1WTYwaVNsRlJpTzExQW9RVUI0eWdXek1vUERIMytITzJMU1ptMW5maytLcFQ0cTUiLCJtYWMiOiIwYjNmYTgyYmNlMGNlYWJlNDFjMDU1NWYxYjZkYTk5OGJjZWQ1OTlkNjQyOWY3NjgwZWJkMmZiMjdiZGY4Y2NkIiwidGFnIjoiIn0%3D; _ga_L7N2GXCLP2=GS2.1.s1763132959$o1$g1$t1763133207$j60$l0$h1920624584' \
    -H 'dnt: 1' \
    -H 'origin: https://www.racon.com.br' \
    -H 'priority: u=1, i' \
    -H 'referer: https://www.racon.com.br/unidades' \
    -H 'sec-ch-ua: "Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
    -H 'sec-ch-ua-mobile: ?0' \
    -H 'sec-ch-ua-platform: "Linux"' \
    -H 'sec-fetch-dest: empty' \
    -H 'sec-fetch-mode: cors' \
    -H 'sec-fetch-site: same-origin' \
    -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36' \
    -H 'x-csrf-token: 4YMjALjtpXKqOzasvfaHqoJWqBnkTtk7JjuQ7oHE' \
    --data-raw '' |
  jq -r '
    .data
    | select(type=="array")[]
    | [
        .title,
        (.address | (split(", ") | {
          endereco: (.[0] | split(" , ")[0]),
          cidade: (.[1] | split(" - ")[0]),
          estado: (.[1] | split(" - ")[1])
        } | .endereco, .cidade, .estado)),
        .link
      ]
    | @csv
  '
) > racon.csv

