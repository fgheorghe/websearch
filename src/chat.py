from langchain_community.utilities import SearxSearchWrapper
from langchain.llms import Ollama
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import requests
import streamlit as st


def json_to_markdown_table(json_data):
    # Create the header row
    table = "| Title | URL | Snippet |\n"
    table += "|-------|-----|---------|\n"

    # Add rows from JSON data
    for item in json_data:
        title = item.get("title", "N/A").replace("|", "\\|")
        url = item.get("link", "N/A").replace("|", "\\|")
        snippet = item.get("snippet", "N/A").replace("|", "\\|")
        table += f"| {title} | {url} | {snippet} |\n"

    return table


def create_search_internet(debug_container, searx_host):
    def search_internet(query: str):
        """Search the internet for a given query."""
        try:
            num_results = 10
            with debug_container:
                st.write("Query:", query)

            # num_results = 10
            search = SearxSearchWrapper(searx_host=searx_host)
            results = search.results(query, num_results=int(num_results))
            filtered_results = [{"link": result["link"], "title": result["title"], "snippet": result["snippet"]} for
                                result
                                in results]

            markdown_table = json_to_markdown_table(filtered_results)

            return markdown_table
        except Exception as e:
            print(f"Error searching internet: {e}")
            return []

    return search_internet


def list_models(ollama_base_url):
    response = requests.get(f"{ollama_base_url}/api/tags")
    models = response.json()['models']

    results = {}
    for model in models:
        results[model["model"]] = model["name"]
    return results


def search_chat(prompt, debug_container, selected_model, selected_tools, searx_host, ollama_base_url):
    llm = Ollama(
        model=selected_model,
        base_url=ollama_base_url,
        temperature=0.5,
        num_ctx=4096)  # , num_predict=1100)

    available_tools = [{
        "name": "search_internet_tool",
        "tool": Tool(
            name="search_internet_tool",
            description="Search the internet for a given query.",
            func=create_search_internet(debug_container, searx_host),
            return_direct=True
        )
    }]

    tools = [
        tool["tool"] for tool in available_tools if tool['name'] in selected_tools
    ]

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=100,
    )

    response = agent.run(prompt)

    return response
