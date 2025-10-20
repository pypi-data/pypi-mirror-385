# cartagon-monday-client

Cliente **Python** para integraciones con la **API GraphQL de Monday.com**.  
Incluye manejo de reintentos (HTTP 5xx, 403, 401/404 transitorios, `ComplexityException`), paginación con `items_page` → `next_items_page`, y utilidades de alto nivel para crear, actualizar y consultar ítems.

> **Requisitos**: Python **3.10+**

---

## Instalación

```bash
pip install cartagon-monday-client
```

Importación:

```python
from monday_client import MondayClient
```

---

## Inicio rápido

```python
from monday_client import MondayClient

token = "TU_API_TOKEN"
client = MondayClient(api_key=token)

# 1) Probar conexión
print(client.test_connection())  # True si la API responde y el token es válido

# 2) Listar tableros
boards = client.get_boards(limit=5, page=1)
for b in boards:
    print(f"{b['id']}: {b['name']}")

# 3) Obtener ítems de un tablero (paginación automática con cursor)
items = client.get_all_items(board_id=123456789, limit=100)
print("Total ítems:", len(items))

# 4) Crear un ítem con columnas en bruto
nuevo = client.create_item(
    board_id=123456789,
    item_name="Tarea de ejemplo",
    columns=[
        {"id": "status", "type": "status", "value": "Working on it"},
        {"id": "date", "type": "date", "value": {"date": "2025-09-25"}}
    ]
)
print("Ítem creado:", nuevo)

# 5) Crear un subítem
sub = client.create_subitem(
    parent_item_id=987654321,
    subitem_name="Subtarea",
    columns=[{"id": "text", "type": "text", "value": "Detalle"}]
)
print("Subítem:", sub)

# 6) Actualizar columna simple
upd1 = client.update_simple_column_value(
    item_id=987654321,
    board_id=123456789,
    column_id="text_column",
    value="Texto actualizado"
)
print("Update simple:", upd1)

# 7) Actualizar múltiples columnas
upd2 = client.update_multiple_column_values(
    item_id=987654321,
    board_id=123456789,
    columns=[
        {"id": "status", "type": "status", "value": "Done"},
        {"id": "priority", "type": "dropdown", "value": ["High"]}
    ]
)
print("Update múltiple:", upd2)

# 8) Filtrar ítems por valor de columna
results = client.get_items_by_column_value(
    board_id=123456789,
    column_id="status",
    value="Done",
    operator="any_of",
    limit=50
)
print("Resultados filtrados:", len(results))

# 9) Obtener un ítem por ID
item = client.get_item(item_id=987654321, columns_ids=["status", "text_column"])
print(item)
```

---

## API de `MondayClient`

### `execute_query(query: str, *, return_key: str | None = None, log_query_preview: bool = False) -> dict`
Ejecuta una query/mutación GraphQL y devuelve `data` (o `data[return_key]`).

---

### `test_connection() -> bool`
Consulta `me` y devuelve True si la API responde con un usuario válido.

---

### `get_boards(limit: int = 10, page: int = 1, fields: list[str] | str | None = None) -> list[dict]`
Devuelve tableros con paginación simple.  
- `fields` por defecto: `["id","name","workspace_id","state","board_kind"]`.

---

### `get_all_items(board_id: int, limit: int = 50, *, fields: list[str] | str | None = None, columns_ids: list[str] | None = None) -> list[dict]`
Devuelve **todos** los ítems de un tablero, paginando con `cursor`.  
- Si `fields` es None, usa `id`, `name` y `column_values { ALL_COLUMNS_FRAGMENT }`.  
- Si `columns_ids` se pasa, aplica filtro `ids:[...]` en `column_values`.

---

### `create_item(board_id: int, item_name: str, *, group_id: str | None = None, columns: list[dict] | dict | None = None, fail_on_duplicate: bool = True, create_labels_if_missing: bool = True, return_fields: list[str] | str | None = None) -> dict`
Crea un ítem.  
- Acepta `columns` en bruto y los normaliza con `create_column_values`.  
- `return_fields`: por defecto `"id"`.

---

### `create_subitem(parent_item_id: int, subitem_name: str, *, columns: list[dict] | dict | None = None, fail_on_duplicate: bool = True, create_labels_if_missing: bool = True, return_fields: list[str] | str | None = None) -> dict`
Crea un subítem bajo un ítem padre.  
- Acepta `columns` en bruto o dict ya renderizado.  
- `return_fields`: por defecto `"id"`.

---

### `update_simple_column_value(item_id: int, board_id: int, column_id: str, value: str, *, return_fields: list[str] | str | None = None) -> dict`
Actualiza **una** columna simple.  
- `value` es obligatorio; usa `""` para limpiar.  
- Si la columna espera JSON, pásalo serializado como string (ej: `'{"date":"2025-09-25"}'`).

---

### `update_multiple_column_values(item_id: int, board_id: int, columns: list[dict] | dict, *, fail_on_duplicate: bool = True, create_labels_if_missing: bool = True, return_fields: list[str] | str | None = None) -> dict`
Actualiza **varias columnas** en un único llamado.  
- Normaliza `columns` con `create_column_values`.  
- Internamente hace doble `json.dumps` para `column_values`.  

---

### `get_items_by_column_value(board_id: int, column_id: str, value: str, fields: list[str] | None = None, operator: str = "any_of", limit: int = 200) -> list[dict]`
Filtra ítems por valor en una columna, con `query_params.rules`.  
- Pagina con `cursor` hasta agotar resultados.  
- Soporta operadores: `any_of`, `not_any_of`, `is_empty`, `contains_text`, `greater_than`, `between`, etc.

---

### `get_item(item_id: int, columns_ids: list[str] | None = None) -> dict`
Obtiene un ítem por ID.  
- Limita columnas si pasas `columns_ids`.  

---

### Otras utilidades
- `board_columns(board_id: int)`: devuelve columnas de un board.  
- `item_columns(item_id: int)`: columnas de un ítem.  
- `subitems_columns(board_id: int)`: columnas de subitems de un board.  
- `delete_item(item_id: int)`: elimina un ítem.  
- `create_item_update(item_id: str, body: str, mention_user: list[dict] = [])`: crea un update en un ítem.  
- `create_column_values(columns: list[dict], fail_on_duplicate: bool = True) -> dict`: helper para normalizar `column_values`.

---

## Manejo de errores

- **Errores retriables**: HTTP 5xx, 403, 401/404 transitorios, `ComplexityException`.  
- **Errores no retriables**: otros GraphQL (ej. `InvalidBoardIdException`).  
- Si se agotan reintentos → `MondayAPIError("Max retries reached")`.

---

## Licencia

**MIT** — ver archivo `LICENSE`.

---

## Enlaces

- PyPI: https://pypi.org/project/cartagon-monday-client/
- Repo: (añade aquí la URL de tu repositorio)
