## Activar venv en el backend e instalar requeriments necesarios
source ~/Multimedia/adivina_la_cancion/backend/venv/bin/activate
deactivate
(venv) [~/Multimedia/adivina_la_cancion/backend] $ pip install -r requirements.txt


## Instalar sqlite browser
sudo apt install sqlitebrowser
### abrir IU de la base de datos
sqlitebrowser adivina_la_cancion.db

## Levantar el servidor backend
(venv) [~/Multimedia/adivina_la_cancion/backend] $ python3 app.py
## Levantar el servidor frontend
[~/Multimedia/adivina_la_cancion/frontend] $ ng serve --host 127.0.0.1