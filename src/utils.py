import time

def response_generator(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.025)  # Simulate delay for streaming effect

def make_stream(container, text):
    accumulated_content = ""
    for chunk in response_generator(text):
        accumulated_content += chunk
        container.markdown(accumulated_content, unsafe_allow_html=True)