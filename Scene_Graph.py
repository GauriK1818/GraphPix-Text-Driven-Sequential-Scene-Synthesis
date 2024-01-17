import streamlit as st
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import spacy
import networkx as nx


# Load English tokenizer, tagger, parser, NER, and word vectors
nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
    return nlp(text)

def generate_scene_graph(sentence):
    # Create a directed graph using NetworkX
    graph = nx.DiGraph()

    # Iterate through the tokens in the sentence
    for token in sentence:
        # Add nodes for each token with POS tags
        graph.add_node(token.text, pos=token.pos_)

    # Add edges based on syntactic dependencies
    for token in sentence:
        for child in token.children:
            graph.add_edge(token.text, child.text, dep=token.dep_)

    return graph

def visualize_scene_graph(graph):

    plt.figure()
    # Visualize the scene graph using NetworkX
    pos = nx.spring_layout(graph)

    # Create labels with word and POS information
    node_labels = {node: f"{node}\n{data['pos']}" for node, data in graph.nodes(data=True)}

    # Draw nodes with labels
    nx.draw(graph, pos, with_labels=True, labels=node_labels, font_weight='bold',
            node_color='skyblue', node_size=1500, font_size=7, edge_color='gray', linewidths=0.5)

    # Show the plot
    #plt.show()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')  # Explicitly set the format to PNG
    buffer.seek(0)

    return buffer
def main():
    st.title("GraphPix: Text Driven Sequential Scene Synthesis")

    # Get user input
    sentences = st.text_area("Enter sentences (3/4 lines):", "")

    scene_graphs=[]

    if st.button("Generate Scene Graphs"):
        # Preprocess the text
        doc = preprocess_text(sentences)

        # Generate and visualize scene graphs for each sentence
        for sentence in doc.sents:
            scene_graph = generate_scene_graph(sentence)
            scene_graph_buffer = visualize_scene_graph(scene_graph)

            # Display the scene graph
            st.image(scene_graph_buffer, use_column_width=True, caption=f"Scene Graph for: {sentence.text}")

        # Create a download button for each scene graph
            download_button = st.button(
                label="Download Scene Graph",
                key=f"download_button_{sentence.text}",
                on_click=save_scene_graph,
                args=(scene_graph_buffer, sentence.text),
            )

            # Append the download button to the list
            scene_graphs.append({"sentence": sentence.text, "download_button": download_button})


def save_scene_graph(scene_graph_buffer, sentence_text):
    # Save the buffer to a file temporarily
    filename = f"scene_graph_{sentence_text.replace(' ', '_')}.png"
    with open(filename, 'wb') as f:
        f.write(scene_graph_buffer.read())

    st.success(f"Scene graph for '{sentence_text}' downloaded as {filename}")

if __name__ == "__main__":
    main()
