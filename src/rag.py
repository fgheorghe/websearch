from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Document

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

def rag(results, prompt, ollama_base_url, selected_model):
    Settings.llm = Ollama(
        base_url=ollama_base_url,
        model=selected_model,
        request_timeout=60.0,
        temperature=0,
        num_ctx=4096
    )

    # print(results)

    documents = [
        Document(
            text=f"{result["title"]}\n{result["snippet"]}\n{result["content"]}",
            metadata={
                "document-title": result["title"],
                "document-link": result["link"],
                # "document-snippet": result["snippet"],
            }
        )
        for result in results
    ]

    print(f"Loaded {len(documents)} documents.")
    index = VectorStoreIndex.from_documents(documents, embed_model=Settings.embed_model)
    query_engine = index.as_query_engine()

    system_prompt = "You are a helpful assistant knowledgeable about the documents in this system. The provided documents are web pages content. Carefully read each provided web page content."
    user_query = prompt
    full_prompt = f"{system_prompt}\nUser Query: Create questions about: {user_query}"

    questions = query_engine.query(
        full_prompt
    )

    print(questions)

    full_prompt = f"{system_prompt}\nUser Query: Answer these questions, by carefully reading each provided web page content. If a question does not have a clear answer, ignore it: {questions}"

    response = query_engine.query(
        full_prompt
    )

    summary = query_engine.query(
        f"{system_prompt}\nUser Query: Summarise the information in relation to: {prompt}"
    )

    sources = {}
    citations = []
    for node in response.source_nodes:
        if node.metadata["document-link"] not in sources:
            citations.append({"title": node.metadata["document-title"], "link": node.metadata["document-link"] })
            sources[node.metadata["document-link"]] = True

    for node in summary.source_nodes:
        if node.metadata["document-link"] not in sources:
            citations.append({"title": node.metadata["document-title"], "link": node.metadata["document-link"] })
            sources[node.metadata["document-link"]] = True

    for node in questions.source_nodes:
        if node.metadata["document-link"] not in sources:
            citations.append({"title": node.metadata["document-title"], "link": node.metadata["document-link"] })
            sources[node.metadata["document-link"]] = True


    return {
        "content": f"{summary}\n{response}",
        "citations": citations
    }