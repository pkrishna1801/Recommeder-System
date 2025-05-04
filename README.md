# AI-Powered Product Recommendation System

A full-stack application that leverages LLMs to generate personalized product recommendations based on user preferences and browsing history.

## Project Overview

This system demonstrates how to effectively use language models (LLMs) like GPT-4 to create intelligent product recommendations. The application consists of:

- **Backend API**: Flask-based REST API that interfaces with OpenAI's GPT models
- **Frontend UI**: React-based user interface for browsing products and receiving recommendations

The system analyzes user preferences (categories, brands, price ranges) and browsing behavior to generate relevant and personalized product recommendations with explanations of why each product was recommended.

## Features

- **Product Catalog**: Browse and explore a diverse catalog of products
- **User Preferences**: Set your preferences for categories, brands, and price ranges
- **Browsing History**: View and manage your product browsing history
- **AI Recommendations**: Get personalized product recommendations with detailed explanations
- **Responsive Design**: Works on both desktop and mobile devices

## Technology Stack

### Backend
- **Framework**: Flask (Python)
- **AI Integration**: OpenAI GPT-3.5/GPT-4 via API
- **Data Storage**: JSON-based product catalog (local file)

### Frontend
- **Framework**: React
- **Styling**: CSS with responsive design
- **API Communication**: Fetch API with JSON payloads

## Installation and Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the backend directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   MODEL_NAME=gpt-4  # or gpt-3.5-turbo
   MAX_TOKENS=1000
   TEMPERATURE=0.7
   DATA_PATH=data/products.json
   ```

6. Start the Flask server:
   ```
   python app.py
   ```

The backend API will be available at http://localhost:5000

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

The application will be available at http://localhost:3000

## How It Works

### Backend Architecture

1. **Product Service**: Manages the product catalog data
2. **LLM Service**: Interfaces with OpenAI's API to generate recommendations
   - Pre-filters products based on user preferences
   - Crafts prompts based on user behavior and preferences
   - Parses LLM responses into structured recommendations

### Frontend Architecture

1. **App Component**: Main component that manages state and user interactions
2. **Catalog Component**: Displays the product catalog with browsing functionality
3. **UserPreferences Component**: Captures user preferences for categories, brands, and price
4. **BrowsingHistory Component**: Shows products the user has viewed
5. **Recommendations Component**: Displays AI-generated recommendations with explanations

### Recommendation Process

1. User browses products and sets preferences
2. Frontend sends browsing history and preferences to the backend
3. Backend pre-filters relevant products based on preferences
4. LLM service constructs a prompt with user data and available products
5. OpenAI API generates personalized recommendations with explanations
6. Backend parses the response and returns structured recommendations
7. Frontend displays the recommendations with relevance scores and reasoning

## API Documentation

### Product Endpoints

- `GET /api/products`: Retrieve all products
- `GET /api/products/<product_id>`: Get a specific product by ID
- `GET /api/products/categories`: Get all product categories
- `GET /api/products/brands`: Get all product brands

### Recommendation Endpoints

- `POST /api/recommendations`: Generate personalized recommendations
  - Request Body:
    ```json
    {
      "preferences": {
        "priceRange": "all", 
        "categories": ["Electronics", "Home"], 
        "brands": ["SoundWave", "FitTech"]
      },
      "browsing_history": ["prod001", "prod002"]
    }
    ```
  - Response:
    ```json
    {
      "success": true,
      "recommendations": [
        {
          "product": { ... },
          "explanation": "This product matches your interest in...",
          "relevance_score": 0.95
        },
        ...
      ],
      "count": 5
    }
    ```

## Prompt Engineering

The system uses carefully engineered prompts to generate high-quality recommendations:

1. **Structured Sections**:
   - User preferences
   - Browsing history with detailed product information
   - Behavioral insights extracted from browsing patterns
   - Available products with relevant details

2. **Guided Output Format**:
   - Specific JSON structure for easy parsing
   - Relevance scores for ranking
   - Personalized explanations for each recommendation

3. **Preference Inference**:
   - Extracting implicit preferences from browsing patterns
   - Identifying recurring themes in user behavior

## Customization and Extension

### Modifying the Product Catalog

Edit the `products.json` file in the `backend/data` directory to add, remove, or modify products.

### Changing the Recommendation Algorithm

Modify the `_create_recommendation_prompt` method in `llm_service.py` to adjust how recommendations are generated.

### Adding User Authentication

The current implementation does not include user management. To add this feature:

1. Add user authentication to the backend (e.g., Flask-Login)
2. Create user-specific endpoints for storing preferences and history
3. Add login/signup components to the frontend

## License

[MIT License](LICENSE)

## Acknowledgments

- This project uses OpenAI's GPT models for generating recommendations
- Product data is fictional and created for demonstration purposes