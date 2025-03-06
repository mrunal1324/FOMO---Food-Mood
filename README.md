# FeelFood - Mood-Based Food Recommender

FeelFood is an AI-powered web application that analyzes your mood through text input and suggests appropriate food recommendations based on your emotional state.

https://github.com/user-attachments/assets/b14c140f-88fa-4d2c-bfd6-f45a858bdf91

## Features

- Mood analysis using both NLTK sentiment analysis and OpenAI's GPT-3.5
- Personalized food recommendations based on mood
- Interactive web-based user interface
- Support for various emotional states

## Setup

### Backend Setup

1. Clone this repository
2. Navigate to the backend folder:
   ```bash
   cd backend
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
4. Activate the virtual environment:
   - Windows (PowerShell):
     ```bash
     .\venv\Scripts\Activate.ps1
     ```
   - Windows (Command Prompt):
     ```bash
     .\venv\Scripts\activate.bat
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```
5. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Create a `.env` file in the `backend` folder and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
7. Start the backend server:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Open a new terminal and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the frontend server:
   ```bash
   npm run dev
   ```

## Usage

1. Make sure both the backend and frontend servers are running.
2. Open your browser and navigate to the provided frontend URL (usually `http://localhost:3000`).
3. Enter your current mood or feelings in the text box.
4. The system will analyze your input and provide food recommendations based on your emotional state.

## Example

```
Welcome to FeelFood - Your Mood-Based Food Recommender!
Tell me how you're feeling today...

How are you feeling? I'm feeling really tired and stressed from work

Detected Mood: Stressed

Recommended Foods:
1. Calming foods
2. Herbal teas
3. Dark chocolate
4. [AI-generated recommendations will appear here]
```

## Requirements

- Python 3.7+ (for the backend)
- Node.js & npm (for the frontend)
- Internet connection for API calls

## Virtual Environment Management (Backend)

- To activate the virtual environment:
  - Windows (PowerShell): `.env\Scripts\Activate.ps1`
  - Windows (Command Prompt): `.env\Scripts\activate.bat`
  - Unix/MacOS: `source venv/bin/activate`
- To deactivate the virtual environment:
  ```bash
  deactivate
  ```

- To update dependencies:
  ```bash
  pip install -r requirements.txt --upgrade
  ```

