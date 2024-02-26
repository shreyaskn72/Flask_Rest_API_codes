# Internally calling an api


In this Example endpoint2 `/internal_call` internally calls endpoint1 `/hello`


## Endpoint1

### `/hello` [POST]


### Example JSON Payload

```json
{
    "Name": "Shreyas"
}
```

### Example CURL Command

```bash
curl --location 'http://127.0.0.1:5000/hello' \
--header 'Content-Type: application/json' \
--data '{
    "Name": "Shreyas"
}'
```

## Endpoint2

### `/internal_call` [POST]

### Example JSON Payload

```json
{
    "Name": "Shreyas",
    "City": "Bengaluru"
}
```

### Example CURL Command

```bash
curl --location 'http://127.0.0.1:5000/internal_call' \
--header 'Content-Type: application/json' \
--data '{
    "Name": "Shreyas",
    "City": "Bengaluru"
}'
```
