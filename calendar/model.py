from typing import Annotated
from typing_extensions import TypedDict
from langchain_community.utilities import ArxivAPIWrapper,WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun,WikipediaQueryRun

###Router between search and calendar management###
# from typing import Literal
# from langchain_core.prompts import ChatPromptTemplate
# from pydantic import BaseModel, Field

# class RouteQuery(BaseModel):
#     """Route a user query to the most relevant datasource."""

#     datasource: Literal["Calendar", "web"] = Field(
#         ...,
#         description="Given a user question choose to route it to wikipedia or arxiv or a Calendar.",
#     )

# from langchain_groq import ChatGroq
# key="GRPOQ_API_KEY"
# llm=ChatGroq(groq_api_key=key,model_name="llama-3.3-70b-versatile")
# structured_llm_router = llm.with_structured_output(RouteQuery)
# system = """You are an expert at routing a user question to a Calendar or wikipedia or arxiv.
# The Calendar can be editted to add update and remove existing records can can be read to.
# return Calendar for questions on these topics. otherwise return web."""
# route_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", system),
#         ("human", "{question}"),
#     ]
# )
# question_router = route_prompt | structured_llm_router

#############################################################################################################################

## Arxiv And Wikipedia tools#####
# arxiv_wrapper=ArxivAPIWrapper(top_k_results=1,doc_content_chars_max=300)
# arxiv_tool=ArxivQueryRun(api_wrapper=arxiv_wrapper)

# api_wrapper=WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=300)
# wiki_tool=WikipediaQueryRun(api_wrapper=api_wrapper)
###############################################################
key='Groq_API_Key'

from tools.tools import get_time_tools,add_event_tool,get_event_tool

# web_tools=[arxiv_tool,wiki_tool]
Calendar_tools=[get_time_tools(),add_event_tool(),get_event_tool()]

## Langgraph Application
from langgraph.graph.message import add_messages

class State(TypedDict):
  messages:Annotated[list,add_messages]

from langgraph.graph import StateGraph,START,END


from langchain_groq import ChatGroq
llm=ChatGroq(groq_api_key=key,model_name="llama-3.3-70b-versatile")
llm_with_tools=llm.bind_tools(tools=Calendar_tools)
# llm_with_web=llm.bind_tools(tools=web_tools)

def Calendar_Bot(state:State):
  return {"messages":[llm_with_tools.invoke(state["messages"])]}

# def web_Bot(state:State):
#   return {"messages":[llm_with_web.invoke(state["messages"])]}

# def route_question(state:State):
#   source= {"messages":[question_router.invoke(state["messages"])]}
#   if source["messages"][0].datasource=="Calendar":
#     return "calendar"
#   elif source["messages"][0].datasource=="web":
#     return "web"
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.checkpoint.memory import MemorySaver
memory=MemorySaver()
graph_builder= StateGraph(State)

graph_builder.add_node("Calendar_Bot",Calendar_Bot)
# graph_builder.add_node("web_Bot",web_Bot)
calendar_tools_node = ToolNode(tools=Calendar_tools)
# web_tools_node = ToolNode(tools=web_tools)
# graph_builder.add_node("tools_w", web_tools_node)
graph_builder.add_node("tools", calendar_tools_node)
# graph_builder.add_conditional_edges(START, route_question,{
#         "calendar": "Calendar_Bot",
#         "web": "web_Bot",
#     }
#                                     )
# graph_builder.add_conditional_edges(
#     "web_Bot",
#     tools_condition,
# )
graph_builder.add_conditional_edges(
    "Calendar_Bot",
    tools_condition,
)
graph_builder.add_edge("tools", "Calendar_Bot")
graph_builder.add_edge(START,"Calendar_Bot")
# graph_builder.add_edge("tools_w", "web_Bot")
# graph_builder.add_edge(START,"web_Bot")
graph=graph_builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}
graph.stream({'messages':[{'role':"user",'content':'I need you to remeber what time it is now.'}]}
                            ,config,stream_mode='values')
while True:
  user_input=input("User: ")
  if user_input.lower() in ["quit","q"]:
    print("Good Bye")
    break
  for event in graph.stream({'messages':[{'role':"user",'content':user_input}]}
                            ,config,stream_mode='values'):
    for value in event.values():
      pass
  print("Assistant:",value[-1].content)