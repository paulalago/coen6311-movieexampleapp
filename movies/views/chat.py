import os
from pathlib import Path
from typing import Annotated
from typing import Literal

import requests
from django.shortcuts import render
from dotenv import load_dotenv
from langchain_core.messages.ai import AIMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from movies.forms import ChatForm

BASE_DIR = Path(__file__).resolve().parent.parent.parent
_ = load_dotenv(BASE_DIR / '.env')


class AgentState(TypedDict):
    """State representing the customer's order conversation."""

    # The chat conversation. This preserves the conversation history
    # between nodes. The `add_messages` annotation indicates to LangGraph
    # that state is updated by appending returned messages, not replacing
    # them.
    messages: Annotated[list, add_messages]

    # The customer's in-progress order.
    order: list[str]

    # Flag indicating that the order is placed and completed.
    finished: bool

MOVIEBOT_SYSINT = (
    "system",  # 'system' indicates the message is a system instruction.
    "You are a MovieRecBot, an interactive movie recommender system. A human will talk to you about the "
    "available movies you have and you will answer any questions about movie items in the list (and only about "
    "movie items - no off-topic discussion, but you can chat about the movie, their director, the actors, and their history). "
    "The customer will place an order for 1 or more items from the movie list, which you will structure "
    "and send to the ordering system after confirming the order with the human. "
    "\n\n"
    "To show the MOVIE_LIST to the user, you should call the get_movies tool. The movie list is in JSON format."
    "If you need to obtain the details about a specific movie, call the get_movie_details tool with the movie ID."
    "If you know additional details about the movie, even if not listed, you can tell the user, clearly stating that the information is not in the list."
    "Once the customer has chosen a movie, thank them and say you hope they enjoy the movie. ",
)

# This is the message with which the system opens the conversation.
WELCOME_MSG = "Welcome to the MovieRecBot chat. Type `q` to quit. How may I serve you today?"

@tool
def get_movies() -> str:
    """Provide the latest up-to-date movie list."""
    response = requests.get("http://localhost:8000/movies/api/movies")
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code}"

@tool
def get_movie_details(id: int) -> str:
    """Provide the latest up-to-date movie list."""
    response = requests.get("http://localhost:8000/movies/api/movies/"+str(id))
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code}"
def maybe_route_to_tools(state:AgentState) -> Literal["tools", "chatbot", "__end__"]:
    """Routes to the tools node if the last message was a tool call."""
    msgs = state["messages"]

    # Only route based on the last message.
    msg = msgs[-1]
    print("ROUTING: ", msg)
    # When the chatbot returns tool_calls, route to the "tools" node.
    if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        print("going to tools")
        return "tools"
    else:
        print("going to END")
        return END


def chatbot(state: AgentState) -> AgentState:
    """The chatbot itself. A wrapper around the model's own chat interface."""
    print("IN CHATBOT----------------")
    print("State:", state)
    defaults = {"order": [], "finished": False}

    if state["messages"] and len(state["messages"]) > 0:
        new_output = llm_with_tools.invoke([MOVIEBOT_SYSINT] + state["messages"])
    else:
        # If there are no messages, start with the welcome message.
        new_output = AIMessage(content=WELCOME_MSG)

    return defaults | state | {"messages": [new_output]}


# Define the tools and create a "tools" node.
tools = [get_movies,get_movie_details]
tool_node = ToolNode(tools)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
llm_with_tools = llm.bind_tools(tools)

# Set up the initial graph based on our state definition.
graph_builder = StateGraph(AgentState)

# Add the chatbot function to the app graph as a node called "chatbot" and the automated tools calling
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)


# Decide if tools need to be called
graph_builder.add_conditional_edges("chatbot", maybe_route_to_tools, {"tools": "tools", END: END})

# Tools always route back to chat afterwards.
graph_builder.add_edge("tools", "chatbot")
# Define the chatbot node as the app entrypoint.
graph_builder.add_edge(START, "chatbot")
chat_graph = graph_builder.compile()

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
            new_state = chat_graph.invoke({"messages": state})
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

        state = chat_graph.invoke({"messages": []})
        request.session['state'] = [(msg.type, msg.content) for msg in state['messages']]
        context = {
            'form': form,
            'title': 'Movie Manager',
            'messages': request.session['state']
        }
        return render(request, 'index.html', context=context)
