from langchain_community.utilities import SearxSearchWrapper
from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import requests
import streamlit as st
from rag import rag

api_token = "api-token"


def get_page_code(url, crawl_for_ai_url):
    headers = {"Authorization": f"Bearer {api_token}"}

    # Basic crawl with authentication
    response = requests.post(
        f"{crawl_for_ai_url}/crawl",
        headers=headers,
        json={
            "urls": url,
            "crawler_params": {
                # Browser Configuration
                "text_mode": True,
                # "extra_args": ["--enable-reader-mode=true"],
                # "headless": True,  # Run in headless mode
                "browser_type": "chromium",  # chromium/firefox/webkit
                # "user_agent": "custom-agent",        # Custom user agent
                # Performance & Behavior
                # "page_timeout": 30000,  # Page load timeout (ms)
                # "verbose": True,  # Enable detailed logging
                # Anti-Detection Features
                # "simulate_user": True,  # Simulate human behavior
                # "magic": True,  # Advanced anti-detection
                # "override_navigator": True,  # Override navigator properties
                # Session Management
                # "user_data_dir": "./browser-data",  # Browser profile location
                # "use_managed_browser": True,  # Use persistent browser
            },
            "priority": 10
        }
    )

    task_id = response.json()['task_id']

    while True:
        response = requests.get(
            f"{crawl_for_ai_url}/task/{task_id}",
            headers=headers,
        )

        if response.json()['status'] == 'completed':
            return response.json()['result']


def create_search_internet(searx_host, ollama_base_url, selected_model, crawl_for_ai_url):
    def search_internet(query: str):
        """Search the internet for a given query."""
        try:
            num_results = 10

            # num_results = 10
            search = SearxSearchWrapper(searx_host=searx_host)
            results = search.results(query, num_results=int(num_results))
            filtered_results = [
                {
                    "link": result["link"],
                    "title": result["title"],
                    "snippet": result["snippet"],
                    "content": get_page_code(result["link"], crawl_for_ai_url)['markdown']
                } for
                result
                in results]

            return rag(filtered_results, query, ollama_base_url, selected_model)
        except Exception as e:
            print(f"Error searching internet: {e}")
            return "No results found (error)."

    return search_internet


def list_models(ollama_base_url):
    response = requests.get(f"{ollama_base_url}/api/tags")
    models = response.json()['models']

    results = {}
    for model in models:
        results[model["model"]] = model["name"]
    return results


def search_chat(prompt, selected_model, searx_host, ollama_base_url, crawl_for_ai_url):
    prompt = f"Using the search_internet_tool, search the internet for: {prompt}"
    llm = Ollama(
        model=selected_model,
        base_url=ollama_base_url,
        temperature=0.5,
        num_ctx=4096)  # , num_predict=1100)

    tools = [Tool(
        name="search_internet_tool",
        description="Search the internet for a given query.",
        func=create_search_internet(searx_host, ollama_base_url, selected_model, crawl_for_ai_url),
        return_direct=True
    )]

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
