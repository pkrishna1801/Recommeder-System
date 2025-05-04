# AI-Powered Product Recommendation Engine - Frontend

This is the frontend component of the AI-Powered Product Recommendation Engine take-home assignment. It provides a React interface that allows users to browse products, set preferences, and receive personalized recommendations.

## Project Structure

```
frontend/
│
├── public/
│   └── index.html
│
├── src/
│   ├── App.js           # Main application component
│   ├── index.js         # Entry point
│   ├── components/
│   │   ├── Catalog.js   # Product catalog display (implement this)
│   │   ├── UserPreferences.js  # Preference form (implement this)
│   │   ├── Recommendations.js  # Recommendations display (implement this)
│   │   └── BrowsingHistory.js  # Browsing history component (implement this)
│   │
│   ├── services/
│   │   └── api.js       # API client for backend communication
│   │
│   └── styles/
│       └── App.css      # Styling
│
├── package.json         # NPM dependencies
└── README.md            # This file
```

## Setup Instructions

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm start
   ```

The application will open at `http://localhost:3000`.

## Implementation Tasks

As part of this assignment, you need to implement the following components:

### 1. Catalog Component (components/Catalog.js)

Create a product catalog display that:
- Shows products in a grid or list format
- Displays key product information (name, price, image, category, brand)
- Allows users to click on products to add them to browsing history
- Provides visual feedback for products that are in the browsing history

### 2. User Preferences Component (components/UserPreferences.js)

Implement a form that allows users to set their preferences:
- Price range selection (e.g., dropdown or slider)
- Category selection (checkboxes or multi-select)
- Brand selection (checkboxes or multi-select)
- Any other relevant preference options

### 3. Recommendations Component (components/Recommendations.js)

Create a recommendations display that:
- Shows recommended products with explanations
- Provides a clean, user-friendly layout
- Handles loading states during recommendation generation
- Displays empty states when no recommendations are available

### 4. Browsing History Component (components/BrowsingHistory.js)

Implement a browsing history display that:
- Shows products the user has clicked on
- Allows clearing the browsing history
- Provides a compact summary of browsed items

## API Integration

The frontend communicates with the backend through the API client in `services/api.js`. The key endpoints are:

- `GET /api/products` - Fetches the product catalog
- `POST /api/recommendations` - Gets personalized recommendations based on preferences and browsing history

## Evaluation Criteria

Your frontend implementation will be evaluated based on:

1. **Component Architecture (40%)**
   - Organization and structure of components
   - State management and data flow
   - Component reusability and modularity

2. **User Experience (40%)**
   - Intuitive interface design
   - Responsive layout
   - Loading and error states
   - Overall usability

3. **Code Quality (20%)**
   - Code readability and organization
   - CSS styling approach
   - Documentation and comments

## Tips for Success

- **Focus on functionality first**: Ensure all required features work correctly before enhancing the UI
- **Keep it responsive**: Make sure your interface works well on different screen sizes
- **Handle edge cases**: Account for empty states, loading states, and error conditions
- **Use React best practices**: Follow React patterns for state management and component composition
- **Consider performance**: Be mindful of performance, especially when handling large product catalogs
- **Clean UI**: While advanced styling is not the primary focus, a clean and intuitive interface is important

Remember that this is a full-stack assignment, so balance your time between frontend and backend implementation to create a cohesive solution.