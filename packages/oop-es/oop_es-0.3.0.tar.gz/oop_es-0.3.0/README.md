# OOP ES - OOP Event sourcing

### WARNING

Not yet finished

### What is this

Just another implementation of event sourcing in Python. For now, it can handle commands, emit/save events,
manage read models.

### Installation

```
pip install oop-es
```

### Postgres adapter

Use `pip install oop-es[pg]` instead. Use [this script](./oop_es_pg/tests/integration/init.sql) to init the tables.
You can rename the `events` or use a custom schema, just pass the table name during the `PostgresEventStore` 
initialization.

### Usage

Check the `example` folder

### TODO

- [ ] add Projector into the example to illustrate how do views (read-models) work
- [ ] snapshotting
- [ ] upcasting
- [ ] better docs
- [ ] metadata collection