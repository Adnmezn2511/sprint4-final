# Graphes Multiplex

## Description initiale du projet
Ce projet vise à développer une application web permettant, dans un premier temps, de charger
et visualiser plusieurs graphes. Ensuite, l'utilisateur pourra sélectionner un type de nœud ou un élément spécifique afin d'identifier
un ensemble de candidats en appliquant l'algorithme de marche aléatoire. Le graphe affiché sera alors mis à jour dynamiquement pour 
illustrer le chemin parcouru par l'algorithme. 

Les réseaux biologiques offrent un moyen de modéliser et d'analyser les interactions entre différentes entités biologiques.
Chaque type d'information peut être représenté sous forme de graphe, et un graphe multiplex intègre plusieurs couches 
d'informations où les nœuds représentent les intersections entre ces couches. L'intérêt principal d'un graphe biologique 
multiplex réside dans sa capacité à modéliser des informations complémentaires. Par exemple, une couche peut illustrer les 
relations entre gènes, protéines et maladies, tandis qu'une autre peut représenter les gènes co-exprimés en lien avec un phénotype ou une pathologie.

Un algorithme de marche aléatoire exploite ces informations multiplexes pour effectuer des prédictions, comme identifier les gènes
impliqués dans une maladie donnée. 

## Deploiement sur un serveur

- Clonez le dépôt ou récupérez et décompressez l'archive du dépôt et effectuez les opérations suivantes depuis ```graph-multiplex/```.

- Modifiez deploy.env pour choisir l'hôte et le port

- 
    ```bash
    chmod +x deploy.sh
    ./deploy.sh
    ```

## Installation locale

Clonez le dépôt ou récupérez et décompressez l'archive du dépôt, puis effectuez les opérations suivantes depuis  ```graph-multiplex/```.


Construisez l'image et lancez avec **docker compose** (plus pratique pour accéder aux fichiers de résultats):
```bash
sudo docker compose -f docker-compose.prod.yml up
```
Puis accédez au site sur [http://localhost](http://localhost)

*ou*

Construisez l'image avec un *Dockerfile* uniquement :

```bash
sudo docker build -t multiplex -f Dockerfile.prod --squash .
```
## Utilisation

Pour lancer l'application la méthode recommandée est avec Docker

#### Lancement
avec *docker compose* :
```bash
sudo docker compose -f docker-compose.prod.yml up
```
ou avec docker :
```bash
sudo docker run -p 80:8000 multiplex
```
ou avec docker avec accès aux fichiers générés :
```bash
sudo docker run -v ./backend/samples:/app/samples -p 80:8000 multiplex
```

#### Accèder au site sur [http://localhost](http://localhost)


## Environnement de developpement - Docker
Dans un terminal à la racine du projet:
```bash
sudo docker compose up --build
```
ou
```bash
docker-compose up --build
```
## Environnement de developpement - Sans Docker
### Installation
Dans un premier terminal à la racine du projet :

```bash
cd frontend
npm install
npm start
```
Dans un autre terminal à la racine du projet :

sur linux/mac
```bash
cd backend
source setup-venv.sh
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
```
sur Windows avec PowerShell
```PowerShell
cd backend
python3 -m venv venv
venv\Scripts\Activate.ps1
pip install -r ./requirements.txt
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
```
si vous ne pouvez pas activer le venv avec PowerShell,
lancez en administrateur :
```
Set-ExecutionPolicy Unrestricted -Scope Process
```
Pour annuler ce changement
```
Set-ExecutionPolicy Default -Scope Process

```
### Utilisation
Dans un premier terminal à la racine du projet :
```bash
cd frontend
npm start
```
Dans un autre terminal à la racine du projet :  
sur linux/mac
```bash
cd backend
source venv/bin/activate
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
```
sur Windows avec PowerShell
```PowerShell
cd backend
venv\Scripts\Activate.ps1
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
```
[localhost:8000/test-itRWR](localhost:8000/test-itRWR)

### build bug ? :

```bash
sudo docker builder prune
sudo docker system prune
```

### Selenium Test (Chrome)
Les fichiers test sont dans backend\app\tests et commencent par selenium_
Pour lancer les tests selenium sans Docker, Activez votre venv puis 
```bash
pip install selenium
pip install selenium webdriver-manager
pip install pytest
cd app/tests
```
```bash
python selenium_upload_zip.py -v
```
-v pour le mode verbose

