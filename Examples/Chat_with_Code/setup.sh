#!/bin/bash

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv ~/.venvs/chat_with_code 

# Activate the virtual environment
echo "Activating virtual environment..."
source ~/.venvs/chat_with_code/bin/activate

# Install libraries from requirements.txt 
echo "Installing libraries from requirements.txt..."
pip install -r requirements.txt

# Handle .env file setup
if [ -f ".env.example" ]; then
    echo "Copying .env.example to .env..."
    cp .env.example .env
else
    echo "No .env.example file found. Creating a new .env file with required variables..."
    cat <<EOL > .env
# Add your GitHub Personal Access Token here
GITHUB_TOKEN=

# Add your Nebius API Key here
NEBIUS_API_KEY=
EOL
fi

# Prompt user to fill the .env file
echo "Please fill in the .env file with your GITHUB_TOKEN and NEBIUS_API_KEY."
echo "You can edit the .env file by running: nano .env (or use your preferred editor)."

# Provide instructions to run the app
echo "Setup completed successfully!"
echo "To run the Streamlit app, use the following commands:"
echo "  source ~/.venvs/chat_with_code/bin/activate"
echo "  streamlit run main.py"