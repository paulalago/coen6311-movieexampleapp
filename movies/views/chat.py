from pathlib import Path

from django.http import JsonResponse
from django.shortcuts import render
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from movies.Assistant import Assistant

BASE_DIR = Path(__file__).resolve().parent.parent.parent
_ = load_dotenv(BASE_DIR / '.env')

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
agent = Assistant(llm)


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
