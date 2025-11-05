from dotenv import load_dotenv
import os
import logging
import gradio as gr

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    Settings,
)
from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import TreeSummarize, Refine, CompactAndRefine

import lancedb

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Configure paths and defaults
ASSIGNMENTS_DB_ROOT = os.getenv('ASSIGNMENTS_DB_ROOT', 'assignment_vectordb')
DB_TABLE = os.getenv('A3B_VECTOR_TABLE', 'documents')
DEFAULT_EMBED_MODEL = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-small-en-v1.5')


def configure_settings(chunk_size: int, chunk_overlap: int, embed_model_name: str, openrouter_model: str | None, openrouter_temp: float | None, openrouter_key: str | None):
    """Apply Settings for LlamaIndex based on UI inputs."""
    # Embeddings
    Settings.embed_model = HuggingFaceEmbedding(model_name=embed_model_name, trust_remote_code=True)
    Settings.chunk_size = int(chunk_size)
    Settings.chunk_overlap = int(chunk_overlap)

    # Configure OpenRouter if provided
    if openrouter_key and openrouter_model:
        try:
            Settings.llm = OpenRouter(api_key=openrouter_key, model=openrouter_model, temperature=openrouter_temp or 0.1)
            logging.info("✅ OpenRouter configured for LLM responses")
        except Exception as e:
            logging.warning(f"⚠️ Failed to configure OpenRouter LLM: {e}. Falling back to vector-only mode.")
            Settings.llm = None
    else:
        Settings.llm = None


def create_or_rebuild_index(data_dir: str = 'data', force_rebuild: bool = False):
    """Create or load the LanceDB-backed VectorStoreIndex."""
    logging.info("📁 Initializing vector store...")
    db = lancedb.connect(ASSIGNMENTS_DB_ROOT)

    vector_store = LanceDBVectorStore(uri=ASSIGNMENTS_DB_ROOT, table_name=DB_TABLE, create_table_if_not_exists=True)

    # If force_rebuild is requested, or table is empty, build index from data
    try:
        need_build = force_rebuild or (DB_TABLE not in db.table_names())
    except Exception:
        need_build = True

    if need_build:
        if not os.path.isdir(data_dir):
            raise FileNotFoundError(f"Data directory not found: {data_dir}")
        reader = SimpleDirectoryReader(
            input_dir=data_dir, 
            recursive=True,
            filename_as_id=True,
            required_exts=[".txt", ".md", ".csv", ".html", ".pdf", ".json"]  # Skip audio for now
        )
        documents = reader.load_data()

        index = VectorStoreIndex.from_documents(documents, vector_store=vector_store)
        logging.info(f"✅ Created new index with {len(documents)} documents")
    else:
        index = VectorStoreIndex.from_vector_store(vector_store)
        logging.info("✅ Loaded existing vector store")

    return index


def build_query_engine(index, top_k: int, use_llm: bool, synthesizer: str, similarity_cutoff: float | None):
    """Build a query engine with optional synthesizer and postprocessor."""
    node_postprocessors = []
    if similarity_cutoff is not None and similarity_cutoff > 0.0:
        node_postprocessors.append(SimilarityPostprocessor(similarity_cutoff=similarity_cutoff))

    response_synthesizer = None
    response_mode = 'no_text'  # Default to vector-only mode
    
    if use_llm and getattr(Settings, 'llm', None) is not None:
        response_mode = 'compact'  # Use LLM synthesis mode
        if synthesizer == 'TreeSummarize':
            response_synthesizer = TreeSummarize(verbose=False)
        elif synthesizer == 'Refine':
            response_synthesizer = Refine()
        elif synthesizer == 'CompactAndRefine':
            response_synthesizer = CompactAndRefine()
        else:
            response_synthesizer = TreeSummarize(verbose=False)

    qe = index.as_query_engine(
        node_postprocessors=node_postprocessors or None,
        response_synthesizer=response_synthesizer,
        response_mode=response_mode,
        similarity_top_k=int(top_k),
    )
    return qe


def launch_ui():
    # Default UI values matching README
    model_options = ['gpt-4o', 'gpt-4o-mini', 'gpt-4o-nano']
    synth_options = ['TreeSummarize', 'Refine', 'CompactAndRefine']

    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown('# A3b — Advanced Gradio RAG')

        with gr.Row():
            # Left column - Query interface
            with gr.Column(scale=3):
                question = gr.Textbox(lines=3, placeholder='Ask a question...', label='Textbox')
                run_button = gr.Button('Submit', variant='primary', size='lg')
                output = gr.Textbox(label='Answer', lines=15, max_lines=20)
                
                # Chunk settings at bottom left
                with gr.Row():
                    chunk_size = gr.Number(value=512, label='Chunk size')
                    chunk_overlap = gr.Number(value=50, label='Chunk overlap')
                
                with gr.Row():
                    rebuild_checkbox = gr.Checkbox(label='Force Rebuild (reload all documents)', value=False)
                    init_button = gr.Button('Initialize / Load DB', size='lg')
                
                status = gr.Textbox(label='Status', lines=4, interactive=False)
            
            # Right column - Configuration panel
            with gr.Column(scale=2):
                gr.Markdown('## Configuration')
                
                use_llm_checkbox = gr.Checkbox(label='Use LLM for synthesis (requires valid OpenRouter key)', value=False)
                
                model_dropdown = gr.Dropdown(label='Model', choices=model_options, value='gpt-4o')
                
                temp_slider = gr.Slider(minimum=0.0, maximum=1.0, step=0.1, value=0.1, label='Temperature')
                
                top_k = gr.Slider(minimum=1, maximum=10, step=1, value=3, label='Similarity Top-K')
                
                postprocessor = gr.CheckboxGroup(choices=['SimilarityFilter'], label='Node Postprocessors')
                
                similarity_cutoff = gr.Slider(minimum=0.0, maximum=1.0, step=0.01, value=0.3, label='Similarity Cutoff')
                
                synth_dropdown = gr.Dropdown(label='Response Synthesizer', choices=synth_options, value='TreeSummarize')

        # Internal state holders
        index_state = gr.State(None)

        def init_db(model, temp, csize, cover, rebuild=False, data_dir='data'):
            status_msgs = []
            try:
                status_msgs.append('⚙️ Configuring settings...')
                openrouter_key = os.getenv('OPENROUTER_API_KEY')
                configure_settings(int(csize), int(cover), DEFAULT_EMBED_MODEL, model, float(temp), openrouter_key)
                status_msgs.append('✅ Settings applied')
                
                status_msgs.append('📁 Loading/creating index...')
                idx = create_or_rebuild_index(data_dir=data_dir, force_rebuild=rebuild)
                status_msgs.append('✅ Index ready!')
                return idx, '\n'.join(status_msgs)
            except Exception as e:
                logging.exception('Failed to initialize DB')
                return None, f'Error initializing DB: {e}'

        def answer_question(idx, q, use_llm, topk, synth, sim_cutoff):
            if idx is None:
                return 'Index not initialized. Click Initialize / Load DB first.'
            if not q or q.strip() == '':
                return 'Please enter a question.'
            try:
                logging.info(f"Query with settings: use_llm={use_llm}, top_k={topk}, synth={synth}, sim_cutoff={sim_cutoff}")
                qe = build_query_engine(idx, top_k=topk, use_llm=use_llm, synthesizer=synth, similarity_cutoff=sim_cutoff)
                resp = qe.query(q)
                
                # If LLM synthesis is enabled and we have a response
                if use_llm and getattr(resp, 'response', None):
                    return resp.response
                
                # Vector-only mode: return all retrieved nodes
                if resp and getattr(resp, 'source_nodes', None):
                    nodes = resp.source_nodes
                    if len(nodes) == 0:
                        return "No relevant documents found (similarity cutoff may be too high)."
                    
                    # Format multiple nodes with their scores
                    result = f"Found {len(nodes)} relevant document(s):\n\n"
                    for i, node in enumerate(nodes, 1):
                        score = getattr(node, 'score', None)
                        if isinstance(score, float):
                            score_str = f"{score:.4f}"
                        else:
                            score_str = str(score) if score is not None else "N/A"
                        result += f"--- Result {i} (Similarity: {score_str}) ---\n"
                        result += f"{node.node.text}\n\n"
                    return result
                
                return str(resp)
            except Exception as e:
                logging.exception('Error answering')
                return f'Error during query: {e}'

        init_button.click(fn=init_db, inputs=[model_dropdown, temp_slider, chunk_size, chunk_overlap, rebuild_checkbox], outputs=[index_state, status])
        run_button.click(fn=answer_question, inputs=[index_state, question, use_llm_checkbox, top_k, synth_dropdown, similarity_cutoff], outputs=[output])

    demo.launch(share=False)


if __name__ == '__main__':
    launch_ui()
