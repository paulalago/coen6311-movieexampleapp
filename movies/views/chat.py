from pathlib import Path

import requests
from django.shortcuts import render
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from movies.Assistant import Agent
from movies.forms import ChatForm

BASE_DIR = Path(__file__).resolve().parent.parent.parent
_ = load_dotenv(BASE_DIR / '.env')

@tool
def get_movies() -> str:
    """Provide the latest up-to-date movie list."""
    response = requests.get("http://localhost:8000/movies/api/movies")
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code}"

@tool
def get_movie_details(movie_id: int) -> str:
    """Provide the latest up-to-date movie list."""
    response = requests.get("http://localhost:8000/movies/api/movies/" + str(movie_id))
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code}"

# Define the tools and create a "tools" node.
tools = [get_movies,get_movie_details]
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
agent = Agent(llm, tools)


def index(request):
    form = ChatForm()

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = ChatForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            user_input = form.cleaned_data['message']

            state = request.session['state']
            state.append(["user", user_input])
            print("STATE: ", state)
            new_state = agent.invoke({"messages": state})
            request.session['state'] = [[msg.type, msg.content] for msg in new_state['messages'] if msg.type != "tool" and len(msg.content)>0 ]

            form = ChatForm()

            context = {
                'form': form,
                'title': 'Movie Manager',
                'messages': request.session['state']
            }

            # redirect to a new URL:
            return render(request, 'index.html', context=context)
    else:

        state = agent.invoke({"messages": []})
        request.session['state'] = [(msg.type, msg.content) for msg in state['messages']]
        context = {
            'form': form,
            'title': 'Movie Manager',
            'messages': request.session['state']
        }
        return render(request, 'index.html', context=context)
