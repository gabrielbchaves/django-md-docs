# Endpoints

## GET /api/items/

Returns a list of items.

```json
[
  {"id": 1, "name": "Item A"},
  {"id": 2, "name": "Item B"}
]
```

## POST /api/items/

Creates a new item.

| Field | Type | Required |
|---|---|---|
| `name` | string | yes |
