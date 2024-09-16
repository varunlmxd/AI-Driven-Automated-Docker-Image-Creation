# Automated Docker Image Creation

This project provides an automated solution for Docker image creation and containerization, along with real-time logging and monitoring capabilities.

## Requirements

Before you begin, make sure you have the following installed:
* **Node.js**: v20.17.0
* **Python**: v3.12.6
* **Docker**: Installed and running

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/varunlmxd/Automated-Docker-Image-Creation.git
cd Automated-Docker-Image-Creation
```

### 2. Backend Setup

Navigate to the backend directory and install the necessary Python dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Start the Flask API:

```bash
flask run
```

The Flask server will start at `http://localhost:5000`.

### 3. Frontend Setup

In a new terminal, navigate to the frontend directory and install the required packages:

```bash
cd frontend
npm install
```

Start the React frontend:

```bash
npm start
```

The React app will run on `http://localhost:3000`.

## API Endpoints

### `/api/v1/build_and_run`
* **Description**: This endpoint triggers the Docker image build and runs the container.
* **Method**: `POST`
* **Example**: `http://localhost:5000/api/v1/build_and_run`

### `/api/v1/logs`
* **Description**: Fetches the logs related to Docker image creation and containerization process.
* **Method**: `GET`
* **Example**: `http://localhost:5000/api/v1/logs`

## Running the Full Application

1. Start the backend by running the Flask server.
2. Start the frontend using the React development server.
3. Use the frontend interface to trigger Docker image builds and monitor the process.
