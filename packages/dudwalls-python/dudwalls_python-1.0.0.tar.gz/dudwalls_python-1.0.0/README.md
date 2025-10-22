# Dudwalls Python SDK

Official Python SDK for Dudwalls NoSQL Database.

## Installation

```bash
pip install dudwalls-python
```

## Quick Start

```python
from dudwalls import Dudwalls
import os

# Initialize with your API key
db = Dudwalls(os.getenv('DUDWALLS_API_KEY'))

# Get a collection
users = db.collection('myapp', 'users')

# Insert a document
user = users.insert_one({
    'name': 'John Doe',
    'email': 'john@example.com'
})

# Find documents
all_users = users.find()
```

## API Reference

### Constructor
```python
Dudwalls(api_key, base_url='https://dudwalls.me/api/dudwalls')
```

### Methods
- `get_databases()` - Get all databases
- `create_database(name)` - Create new database
- `collection(database, collection)` - Get collection instance

### Collection Methods
- `find(query=None)` - Find documents
- `find_one(doc_id)` - Find document by ID
- `insert_one(document)` - Insert single document
- `insert_many(documents)` - Insert multiple documents
- `update_one(doc_id, update)` - Update document
- `delete_one(doc_id)` - Delete document
- `count()` - Count documents

## License

MIT
