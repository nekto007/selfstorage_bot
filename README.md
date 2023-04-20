## Установка

```bash
git clone https://github.com/nekto007/selfstorage_bot.git
cd selfstorage_bot
```

### 1. Install requirements

```bash
pip install -r requirements.txt
```
### 2. Run the migration to configure the SQLite database:

```bash
python3 manage.py migrate
```

### 3. Create a superuser to gain access to the admin panel:

```bash
python3 manage.py createsuperuser
```


### 4. Creation of initial data:

```bash
python3 db_init.py
```

### 5. Starts the admin panel:

```bash
python3 manage.py runserver
```

The address of the admin panel: [admin_panel](http://127.0.0.1:8000/admin/).