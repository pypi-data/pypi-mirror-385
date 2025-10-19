# Zentropy Client

Python client for the Zentropy key-value server.

## Example

```python
from zentropy import Client

z = Client(host='127.0.0.1', port=6383, password='')
z.set('foo', 'bar')
print(z.get('foo'))
z.close()
