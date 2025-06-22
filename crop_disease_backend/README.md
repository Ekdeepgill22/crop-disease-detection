# Crop Disease Detection Backend

A Flask-based backend API for crop disease detection using the Kindwise API.

## Features

- Disease detection using Kindwise API
- User authentication and authorization
- Diagnosis history tracking
- Advisory system for disease treatment
- Weather-based recommendations
- Image upload and processing

## Setup

### Prerequisites

- Python 3.8+
- MongoDB
- Kindwise API key

### Installation

1. Clone the repository and navigate to the backend directory:
```bash
cd crop_disease_backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following variables:
```env
# Database Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=crop_disease_db

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Kindwise API Configuration
KINDWISE_API_KEY=your-kindwise-api-key-here

# Weather API (optional)
WEATHER_API_KEY=your-weather-api-key-here
```

5. Start MongoDB service

6. Run the application:
```bash
python run.py
```

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token

### Disease Detection
- `POST /disease/predict` - Upload image and get disease prediction
- `GET /disease/history` - Get user's diagnosis history
- `GET /disease/diagnosis/{id}` - Get specific diagnosis
- `GET /disease/supported-crops` - Get list of supported crops

### Advisory
- `GET /advisory/disease/{disease_name}` - Get advisory for specific disease
- `GET /advisory/weather` - Get weather-based advice

## Environment Variables

- `MONGODB_URL`: MongoDB connection string
- `DATABASE_NAME`: Database name
- `SECRET_KEY`: JWT secret key
- `KINDWISE_API_KEY`: Your Kindwise API key
- `WEATHER_API_KEY`: OpenWeatherMap API key (optional)

## Supported Crops

The system supports various crops including:
- Tomato, Potato, Pepper, Corn
- Wheat, Rice, Cotton, Soybean
- Apple, Grape, Cucumber, Lettuce
- Carrot, Onion, Garlic
- Strawberry, Blueberry, Raspberry, Blackberry

## Architecture

- **Controllers**: Business logic and API handlers
- **Models**: Data models and validation
- **Routes**: API endpoint definitions
- **Utils**: Helper functions and utilities
- **Database**: MongoDB connection and operations
