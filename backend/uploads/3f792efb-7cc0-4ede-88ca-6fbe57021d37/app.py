import psycopg2
import json
import os
import configparser
from flask import Flask, request, jsonify

# Initialise a new Flask application instance
app = Flask(__name__)

# Function to load configuration from the .ini file
def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

# Function to load JSON from a file
def get_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Function to connect to PostgreSQL
def connect_postgress(database_config):
    try:
        conn = psycopg2.connect(**database_config)
        print("Connection successful")
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise

@app.route("/")
def hello():
    return jsonify({"message": "Upsert API Working"}), 200 
# Route to insert or update a participant using query from schema file
@app.route("/postgresql-insert/upsert", methods=["POST"])
def main():
    try:
        config_file = load_config('config.ini')

        # Load PostgreSQL connection details from the config
        Database_connection = get_json(config_file.get('Database', 'postgres_config_file'))

        # Load table name and query from schema file
        schema = get_json(config_file.get('Schema', 'postgres_schema_file'))
        table = schema.get('table')
        custom_query = schema.get('query')

        if not table or not custom_query:
            return "Schema file missing table or query", 400

        # Connect to the PostgreSQL database
        conn = connect_postgress(Database_connection)

        # Get data from the request
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phno = data.get('phno')

        if not name or not email or not phno:
            return "Invalid input data", 400

        # Dynamically use the table name and query from the schema
        query = f"""
        {custom_query}
        """

        # Prepare and execute the SQL query
        cursor = conn.cursor()
        cursor.execute(query, (name, email, phno))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Participant inserted/updated successfully"}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

