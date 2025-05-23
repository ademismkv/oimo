# Ornament Detection API - Railway Deployment

This folder contains all the necessary files to deploy the Ornament Detection API to Railway.

## Files in this folder

- `app/`: Contains the API application code
  - `main.py`: The FastAPI application
  - `best.pt`: The trained YOLOv8 model
  - `meanings.csv`: Ornament meanings database
- `Procfile`: Tells Railway how to run the application
- `requirements.txt`: Lists all Python dependencies
- `railway.toml`: Railway configuration (optional)

## How to Deploy to Railway

1. **Sign up for Railway**:
   - Create an account at [railway.app](https://railway.app)

2. **Install the Railway CLI**:
   ```
   npm i -g @railway/cli
   ```

3. **Login to Railway**:
   ```
   railway login
   ```

4. **Deploy the API**:
   - Option 1: Deploy via Railway CLI:
     ```
     cd deployment
     railway up
     ```
   
   - Option 2: Connect to GitHub:
     - Push this project to GitHub
     - In Railway dashboard, create new project from GitHub repo
     - Select this repository and deploy

5. **Environment Variables**:
   - No special environment variables are required as the app uses the default `PORT` variable that Railway provides

6. **Verify the Deployment**:
   - Railway will provide a URL when deployment is complete
   - Visit the URL to access the web interface
   - Or test the API endpoints using curl or Postman

## API Endpoints

- `GET /`: Web interface for uploading images and detecting ornaments
- `POST /detect/`: Upload an image to detect ornaments
- `GET /meanings/{ornament_name}`: Get the meaning of a specific ornament
- `GET /status`: Check API status
- `GET /api`: Simple endpoint to verify API is running

## Notes

- The app is configured to use a production-ready Uvicorn server.
- Static files are served from the `/static` directory.
- The `PORT` environment variable is automatically set by Railway.
- OpenCV is installed as `opencv-python-headless` for server environments.

For more information on Railway deployment, see [Railway Documentation](https://docs.railway.app/). 