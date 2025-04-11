# Space Cargo System

A comprehensive system for managing cargo placement and retrieval in space environments.

## Features

- 3D visualization of containers and items
- Optimal placement algorithms for space utilization
- Item retrieval planning
- Waste minimization strategies
- CSV import/export for data management
- Action logging and history tracking

## Architecture

The application consists of:

- **Backend**: Python with FastAPI, SQLAlchemy, and PostgreSQL
- **Frontend**: React with Three.js for 3D visualization
- **Docker**: Containerized setup for easy deployment
- **Algorithms**: All the orginal algorithms are stored in the backend < src < algorithms folder. All the algorithms are implemented in Python using jupyter notebook. the algorithms are stored seperately also and combined also
## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd space-cargo-system
   ```

2. Configure environment variables:
   ```
   # Edit .env file if needed
   ```

3. Start the application:
   ```
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Usage

### Importing Data

1. Prepare your CSV files in the format shown in the sample files
2. Access the Upload page from the navigation menu
3. Select your file and click Upload

### Managing Containers and Items

1. Use the Dashboard to view containers and their contents
2. Search for specific items or containers using the search bar
3. View detailed 3D visualizations of container contents

### Placing Items

1. Select an unplaced item
2. Choose a target container
3. The system will automatically find the optimal position

## Data Structure

Sample CSV formats are provided in the `data/` directory:
- `containers.csv`: Container specifications
- `input_items.csv`: Item details

## Development

### Project Structure

```
/space-cargo-system
├── backend/              # Python FastAPI backend
├── frontend/             # React frontend
├── data/                 # Sample data files
└── docker-compose.yml    # Docker setup
```

### Backend Development

```
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### Frontend Development

```
cd frontend
npm install
npm start
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 