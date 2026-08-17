from langgraph.graph import START , END , StateGraph
from langgraph.graph.message import MessagesState
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool 
from langgraph.prebuilt import ToolNode , tools_condition
import requests
import time 
import json



# Practice URL :- https://rag-based-pdf-chatbot.netlify.app

memory = MemorySaver() # for storing the previous communication

# Initializing the LLM 
LLM = ChatOllama(
    model="qwen3:1.7b",
    temperature=0
)

# Adding some tools 
@tool # this tool will check whether the website is reachable or not 
def check_website(url : str) -> dict:
    """
    Checks whether the website url is reachable and returns basic information about the website 
    """
    try :
        # Start the timer
        start_time = time.time()
        
        # Sending a get request 
        response = requests.get(
            url , 
            timeout = 10
        )
        
        # the ending timer
        end_time = time.time()
        
        total_time = round(end_time - start_time , 2)
        
        return {
            "url" : url ,
            "reachable" : True ,
            "status_code" : response.status_code ,
            "https" : url.startswith("https://") ,
            "response_time" : total_time
        }
    except Exception as e:
        return {
            "url" : url ,
            "reachable" : False ,
            "error" : str(e)
        } 

@tool # this is the tool that will check the security headers 
def check_security_headers(url : str) -> dict:
    """
    checks important security headers 
    """
    
    response = requests.get(url)
    
    headers = response.headers
    
    
    return {
    "Content-Security-Policy":
        headers.get("Content-Security-Policy"),

    "Strict-Transport-Security":
        headers.get("Strict-Transport-Security"),

    "X-Frame-Options":
        headers.get("X-Frame-Options"),

    "X-Content-Type-Options":
        headers.get("X-Content-Type-Options"),

    "Referrer-Policy":
        headers.get("Referrer-Policy"),

    "Permissions-Policy":
        headers.get("Permissions-Policy"),
}

@tool # this tool will help in giving the recommendations 
def analyze_security(url : str) -> dict:
    """
    combining all the security related checks into a single report 
    """
    
    # calling tool 1
    website_info = check_website.invoke({"url" : url})
    
    # calling tool 2
    header_info = check_security_headers.invoke({"url" : url})
    
    report = {
        "url": website_info["url"],
        "reachable": website_info["reachable"],
        "status_code": website_info["status_code"],
        "https": website_info["https"],
        "response_time": website_info["response_time"],

        "headers": {
            "Strict-Transport-Security":
                header_info["Strict-Transport-Security"] is not None,

            "Content-Security-Policy":
                header_info["Content-Security-Policy"] is not None,

            "X-Frame-Options":
                header_info["X-Frame-Options"] is not None,

            "X-Content-Type-Options":
                header_info["X-Content-Type-Options"] is not None,

            "Referrer-Policy":
                header_info["Referrer-Policy"] is not None,

            "Permissions-Policy":
                header_info["Permissions-Policy"] is not None,
        }
    }

    return report
    
@tool # this tool will help in generating the security report of the website 
def report_generator(report : str) -> str:
    """
    Generates and prints a clean security report from the security analysis data.
    The report must be provided as a JSON string.
    """
    
    # converts json list back into dictionary
    report = json.loads(report)
    
    headers = report["headers"]

    print("\n")
    print("=" * 50)
    print("          WEBSITE SECURITY REPORT")
    print("=" * 50)

    print("\nWebsite:")
    print(report["url"])

    print("\nReachable:")
    print("✅ Yes" if report["reachable"] else "❌ No")

    print("\nStatus Code:")
    print(report["status_code"])

    print("\nHTTPS:")
    print("✅ Enabled" if report["https"] else "❌ Disabled")

    print("\nResponse Time:")
    print(f"{report['response_time']} sec")

    print("\n" + "-" * 50)
    print("Security Headers")
    print("-" * 50)

    for header, status in headers.items():

        if status:
            print(f"✅ {header}")
        else:
            print(f"❌ {header}")

    print("\n" + "-" * 50)
    print("Recommendations")
    print("-" * 50)

    if not headers["Content-Security-Policy"]:
        print("• Add Content-Security-Policy")

    if not headers["X-Frame-Options"]:
        print("• Add X-Frame-Options")

    if not headers["X-Content-Type-Options"]:
        print("• Add X-Content-Type-Options")

    if not headers["Referrer-Policy"]:
        print("• Add Referrer-Policy")

    if not headers["Permissions-Policy"]:
        print("• Add Permissions-Policy")

    print("\n" + "=" * 50)

    return "Security report generated successfully."    
    
# adding a tool that actually measures cookies 
@tool # this tool will help in measuring cookies
def check_cookies(url : str) -> dict:
    """
    Checks the website cookies and their security attributes.
    """
    
    response = requests.get(url , timeout = 10)
    
    cookies = []
    
    for cookie in response.cookies:
        cookies.append({
            "cookie-name" : cookie.name ,
            "secure" : cookie.secure ,
            "httponly" : cookie.has_nonstandard_attr("HttpOnly") ,
            "samesite" : cookie.get_nonstandard_attr("SameSite")
        })
        
    
    return {
        "url" : url ,
        "cookies" : cookie
    }
    
# This tool will detect technologies like next js , wordpress
@tool
def detect_technologies(url : str) -> dict :
    """
    Detects publicly observable technologies used by a website
    based on HTTP headers and HTML content.
    """
    
    try:
        response = requests.get(
            url = url ,
            timeout = 10
        )    
        
        html = response.text
        headers = response.headers
        
        technologies = []
        
        # Server detection 
        server = headers.get("Server")
        
        if server :
            technologies.append(
                {
                    "type" : "server" ,
                    "name" : server
                }
            )
            
        # for next js detection 
        elif "/_next/" in html:
            technologies.append(
                {
                    "type" : "Framework" ,
                    "name" : "Next Js"
                }
            )
            
        # for react detection 
        elif (
            "__NEXT_DATA__" in html
            or "react" in html.lower()
        ):
            technologies.append(
                {
                    "type" : "Framework" ,
                    "name" : "React Js"
                }
            )
            
        # For php websites 
        elif ".php" in html:
            technologies.append(
                {
                    "type" : "language" ,
                    "name" : "PHP"
                }
            )
            
        # for wordpress websites 
        elif  (
            "wp-content" in html
            or "wp-includes" in html
        ):
            technologies.append(
                {
                    "type" : "cms" ,
                    "name" : "WordPress"
                }
            )
            
        return {
            "url" : url ,
            "tech stack" : technologies
        }
            
            
    except Exception as e:

        return {
            "url": url,
            "technologies": [],
            "error": str(e)
        }        
    


# List of TOOLS and connecting the tools with the llm
tools = [
    check_website ,
    check_security_headers ,
    analyze_security ,
    report_generator ,
    check_cookies ,
    detect_technologies
]

llm_with_tools = LLM.bind_tools(tools)

tool_node = ToolNode(tools)

# Creating a Chatbot for the trial purpose 
def chatbot(state : MessagesState):
    response = llm_with_tools.invoke(state['messages'])
    
    return {
        "messages" : [response]
    }
    
graph_builder = StateGraph(MessagesState)

# Adding the chatbot Node and t the tools 
graph_builder.add_node("chatbot" , chatbot)
graph_builder.add_node("tools" , tool_node)

# Adding the Start edges 
graph_builder.add_edge(START , "chatbot")

# Adding the Conditional Edge 
graph_builder.add_conditional_edges("chatbot" , tools_condition)
graph_builder.add_edge("tools" , "chatbot")

graph = graph_builder.compile(
    checkpointer = memory
)

config = {
    "configurable" : {
        "thread_id" : "Affan"
    }
}

# Debug Mode
DEBUG = False

while True:

    input_query = input("\n👤 User : ")

    if "bye" in input_query.lower():
        break

    print("\n🤖 SecureScan AI is analyzing...\n")

    for event in graph.stream(
        {
            "messages": [("user", input_query)]
        },
        config=config
    ):

        # Print the complete LangGraph events only if debugging
        if DEBUG:
            print(event)

        # Otherwise print only meaningful output
        else:

            for node_name, value in event.items():

                # Optional: Tell the user when tools are running
                if node_name == "tools":
                    print("🔧 Running Security Tools...")

                elif node_name == "chatbot":

                    assistant_message = value["messages"][-1]

                    # Ignore the first AI message because it only contains tool calls
                    if assistant_message.content:

                        print("\n==============================")
                        print("🤖 Assistant")
                        print("==============================")
                        print(assistant_message.content)
                        print("==============================")

print("\n👋 Thank you for using SecureScan AI.")

print(" Thank you for using my llm ")
# Below part is used to generate the image of the Agents Workflow 
png_data = graph.get_graph().draw_mermaid_png()

with open("langgraph_workflow_security.png", "wb") as f:
    f.write(png_data)
