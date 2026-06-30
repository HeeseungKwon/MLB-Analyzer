SHELL := /bin/bash

.PHONY: setup up ingest stream init-db

setup:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

up:
	docker-compose up -d --build

init-db:
	python db/init_db.py

ingest-statcast:
	python ingest/ingest_statcast.py

run-streamlit:
	streamlit run app/streamlit_app.py
