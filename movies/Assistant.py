from typing import TypedDict, Annotated

from langchain_core.messages import AIMessage
from langgraph.constants import END, START
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

# This is the message with which the system opens the conversation.
WELCOME_MSG = "Welcome to the MovieRecBot chat. Type `q` to quit. How may I serve you today?"

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



class Assistant:
    def __init__(self, llm, tools: list):
        self.llm = llm
        self.graph = self._build_graph(tools)

    def invoke(self, messages):
        return self.graph.invoke(messages)


    def _build_graph(self, tools: list):
        tool_node = ToolNode(tools)
        self.llm = self.llm.bind_tools(tools)

        # Set up the initial graph based on our state definition.
        graph_builder = StateGraph(AgentState)

        # Add the chatbot function to the app graph as a node called "chatbot" and the automated tools calling
        graph_builder.add_node("chatbot", self._chatbot)
        graph_builder.add_node("tools", tool_node)

        # Decide if tools need to be called
        graph_builder.add_conditional_edges("chatbot", tools_condition, {"tools": "tools", END: END})

        # Tools always route back to chat afterward.
        graph_builder.add_edge("tools", "chatbot")
        # Define the chatbot node as the app entrypoint.
        graph_builder.add_edge(START, "chatbot")
        chat_graph = graph_builder.compile()

        return chat_graph

    def _chatbot(self, state: AgentState) -> AgentState:
        """The chatbot itself. A wrapper around the model's own chat interface."""
        print("IN CHATBOT----------------")
        print("State:", state)
        defaults = {"order": [], "finished": False}

        if state["messages"] and len(state["messages"]) > 0:
            new_output = self.llm.invoke([MOVIEBOT_SYSINT] + state["messages"])
        else:
            # If there are no messages, start with the welcome message.
            new_output = AIMessage(content=WELCOME_MSG)

        return defaults | state | {"messages": [new_output]}