from pathlib import Path

import requests
from django.http import JsonResponse
from django.shortcuts import render
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from movies.Assistant import Assistant

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
tools = [get_movies, get_movie_details]
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
agent = Assistant(llm, tools)


def index(request):
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        user_input = request.POST['message']

        state = request.session['state']
        state.append(["human", user_input])
        print("STATE: ", state)
        new_state = agent.invoke({"messages": state})
        request.session['state'] = [[msg.type, msg.content] for msg in new_state['messages'] if
                                    msg.type != "tool" and len(msg.content) > 0]

        context = {
            'title': 'Movie Manager',
            'messages': request.session['state']
        }

        # redirect to a new URL:
        return render(request, 'index.html', context=context)
    else:
        state = agent.invoke({"messages": []})
        request.session['state'] = [(msg.type, msg.content) for msg in state['messages']]
        context = {
            'title': 'Movie Manager',
            'messages': request.session['state']
        }
        return render(request, 'index.html', context=context)


def new_session(request):
    if "state" in request.session:
        request.session["state"] = []

    return JsonResponse({"status": "success"})
