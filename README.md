# NiViz Rater

Interface for rating QC outputs from NiViz. 

Database: SQLite
Web framework: bottle 
Frontend: svelte 

## Get started

Install the dependencies for svelte

```bash
cd client
npm install
```

## Run

To run the bottle application, first initialize the database, 
then run the Web Interface
```bash
python app.py initialize_db
python app.py runserver
```

To run the svelte application in development mode:

```bash
npm run dev
```

Navigate to [localhost:5000](http://localhost:5000). You should see your app running. 


See client/README.md for more info on using svelte.


