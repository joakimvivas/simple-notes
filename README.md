# Simple Notes

This repository contains a **Flet-based Notes Application** that stores data in *Supabase*. Below you will find instructions on how to run the project with Docker (including the `.env` file for Supabase credentials) and how to generate an Android APK.

## Running the project locally

1. Create the Python virtual environment

```sh
python3 -m venv simple-notes-env
```

```sh
source simple-notes-env/bin/activate
```

2. Install dependencies:

It is recommended, first, upgrade pip:
```sh
pip install --upgrade pip
```

Install dependencies/requirements:
```sh
pip install -r requirements.txt
```

3. Execute the following command:

```sh
python app.py
```

## Running the Application with Docker

1. **Ensure `.env` is included**:
- Check that `.env` is **not** listed in a `.dockerignore` file.  
- By default, `COPY . /app` will include `.env` in the Docker image so that Python can load your environment variables.

2. **Build the Docker image**:
```bash
docker build -t flet-notes-app .
```

3. **Run the Docker image**:
```bash
docker run -p 8015:8015 flet-notes-app
```

## Generating an Android APK

1. Install/upgrade Flet

```bash
pip install --upgrade flet
```

2. Prepare flet.json (optional)

```json
{
  "app_name": "Flet Notes App",
  "description": "A notes application built with Flet and Supabase",
  "version": "0.0.1",
  "bundle_id": "com.example.notes",
  "company_name": "Example Inc.",
  "icon_path": "notes.png"
}
```

3. Generate the APK

```bash
flet publish --platform android --target apk app.py
```