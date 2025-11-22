# Aplikacja webowa flask

## System webowy umożliwiający prowadzenie bloga z przepisami oraz udostępniający możliwość interkacji użytkowników z danymi przepisami (oceny, komentarze)

## Stack technologiczny
W skład aplikacji na chwilę obecną wchodzi:
- **Backend:** Python, Flask, Flask-Login, Flask-Admin, Flask-SQLAlchemy  
- **Frontend:** HTML, CSS, JavaScript, szablony Jinja2  
- **Baza danych:** PostgreSQL
- **DevOps:** Docker, Docker Compose, CI Workflow do automatycznej weryfikacji buildów 

## Kluczowe funkcjonalności
Aplikacja na chwilę obecną umożliwia:
- dodawanie przepisów
- administracje zawartością strony poprzez panel administratora
- logowanie i uwierzytelnianie z użyciem **Flask-Login**

## Uruchomienie aplikacji
Po pobraniu repozytorium należy:
1. Utworzyć plik .env ze zmiennymi środowiskowymi 
```env
ADMIN_USERNAME
ADMIN_PASSWORD
ADMIN_EMAIL
SECRET_KEY
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
POSTGRES_HOST
POSTGRES_PORT
```

2. Uruchomić docker-compose z użyciem komendy: ```docker-compose up --build```


3. W celu wypełnienia strony danymi należy wykorzystać skrpyt **populate_data.py**:
 - otwórz okno terminala (cmd)
 - wejdź do kontenera z aplikacją ```docker exec -it app bash```
 - uruchom skrypt zasilający bazę danych ```python3 -m populate_data.populate_data```

Aplikacja zostanie uruchomiona na localhoście pod adresem http://127.0.0.1:5000

## Źródło danych
Przepisy, instrukcje i zdjęcia pochodzą z API **[TheMealDB](https://www.themealdb.com)**.

Na potrzeby projektu dane zmodyfikowane.

