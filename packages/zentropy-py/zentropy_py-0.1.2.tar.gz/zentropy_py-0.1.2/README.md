# Zentropy Python Client

A lightweight Python client for **[Zentropy](https://github.com/mailmug/zentropy)** — a fast, Redis-like key-value store with authentication, Unix socket support, and a simple text-based protocol.

---

## 🚀 Installation

Install from **PyPI**:

```bash
pip install zentropy-py
```

## 🧠 Usage
### Basic Example

```python
from zentropy import Client

client = Client(password="testpass")

client.set("foo", "bar")
print(client.get("foo"))  # Output: bar

client.close()
```

## 🔐 Authentication
```python
client = Client(host='127.0.0.1', port=6383, password='password here')
```

## ⚙️ Supported Commands

| Method            | Command  | Description                 |
| ----------------- | -------- | --------------------------- |
| `auth(password)`  | `AUTH`   | Authenticate the connection |
| `set(key, value)` | `SET`    | Set a key-value pair        |
| `get(key)`        | `GET`    | Retrieve a value            |
| `delete(key)`     | `DELETE` | Remove a key                |
| `exists(key)`     | `EXISTS` | Check if a key exists       |
| `ping()`          | `PING`   | Test connectivity           |
| `close()`         | –        | Close the connection        |


## Example

```python
client.set("hello", "world")
print(client.exists("hello"))  # True
print(client.get("hello"))     # "world"
client.delete("hello")
```


### 🤝 Contributing

Contributions are welcome! 🎉