from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Document

def rag(results, prompt, ollama_base_url, selected_model):
    Settings.llm = Ollama(
        base_url=ollama_base_url,
        model=selected_model,
        request_timeout=60.0,
        temperature=0,
        num_ctx=4096
    )

    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

    documents = [
        Document(
            text=result["content"],
            metadata={
                "title": result["title"],
                "link": result["link"],
                "snippet": result["snippet"],
            }
        )
        for result in results
    ]

    print(f"Loaded {len(documents)} documents.")
    index = VectorStoreIndex.from_documents(documents, embed_model=Settings.embed_model)
    query_engine = index.as_query_engine()

    system_prompt = "You are a helpful assistant knowledgeable about the documents in this system."
    user_query = prompt
    full_prompt = f"{system_prompt}\nUser Query: Summarize information about: {user_query}"

    response = query_engine.query(
        full_prompt
    )

    sources = {}
    for node in response.source_nodes:
        sources[node.metadata["link"]] = f"Title: {node.metadata["title"]}\n\nLink: {node.metadata["link"]}"

    return f"{response}\n\n\n Sources: \n\n\n\n{"\n\n".join(sources.values())}"