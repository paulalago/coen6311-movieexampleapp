# coen6311-movieexampleapp

## Description
Example of using AI agents

## Installation

### Prerequisites
- Python version required Python 3.11+

### Steps
```sh
# Clone the repository
git clone https://github.com/paulalago/coen6311-movieexampleapp.git
cd coen6311-movieexampleapp

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup
echo "GOOGLE_API_KEY=<add_your_key>" > .env # Replace <add_your_key> with a valid key
python manage.py makemigrations
python manage.py migrate

```

## Usage
```sh
python manage.py runserver
```