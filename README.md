# NiViz Rater

Interface for rating QC outputs from NiViz. 

Database: SQLite
Web framework: bottle 
Frontend: svelte 

## Get started

We recommend using your favorite virtual environment while developing!

Install the dependencies for svelte

```bash
cd client
npm install
```

Install the dependencies for niviz_rater and the package itself.
```bash
pip install -r requirements.txt
pip install -e .
```

## Run

To run the bottle application, first initialize the database, 
then run the Web Interface
```bash
cd niviz_reader
python app.py initialize_db
python app.py runserver
```

To run the svelte application in development mode:

```bash
npm run dev
```

Navigate to [localhost:5000](http://localhost:5000). You should see your app running. 


See client/README.md for more info on using svelte.


