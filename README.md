# FeelFood - Mood-Based Food Recommender

FeelFood is an AI-powered application that analyzes your mood through text input and suggests appropriate food recommendations based on your emotional state.

## Features

- Mood analysis using both NLTK sentiment analysis and OpenAI's GPT-3.5
- Personalized food recommendations based on mood
- Interactive command-line interface
- Support for various emotional states

## Setup

### Option 1: Using Setup Script (Recommended)

1. Clone this repository
2. Run the setup script:
   ```bash
   .\setup_venv.ps1
   ```


https://github.com/user-attachments/assets/47db3a49-e444-4872-b4f5-f6e45f0e93cc


### Option 2: Manual Setup

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
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
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Make sure your virtual environment is activated (you should see `(venv)` in your terminal prompt)
2. Run the script:
   ```bash
   python mood_food_recommender.py
   ```
3. Enter your current mood or feelings when prompted. The system will analyze your input and provide food recommendations based on your emotional state.
4. To exit the program, type 'quit' when prompted.

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

- Python 3.7+
- OpenAI API key
- Internet connection for API calls

## Note

This application requires an OpenAI API key to function. You can obtain one by signing up at https://platform.openai.com/

## Virtual Environment Management

- To activate the virtual environment:
  - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
  - Windows (Command Prompt): `.\venv\Scripts\activate.bat`
  - Unix/MacOS: `source venv/bin/activate`
- To deactivate the virtual environment:
  ```bash
  deactivate
  ```
- To update dependencies:
  ```bash
  pip install -r requirements.txt --upgrade
  ``` 
