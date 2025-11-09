from __future__ import annotations
import json
import os
from datetime import datetime
from typing import List
from dotenv import load_dotenv
import gradio as gr
from src.agents.planner import PlannerAgent
from src.agents.context_retriever import ContextualRetrieverAgent
from src.agents.critical_analyst import CriticalAnalysisAgent
from src.agents.insight_generator import InsightGenerationAgent
from src.agents.report_builder import ReportBuilderAgent

# Load environment variables
load_dotenv()

# Initialize agents (moved back above pipeline function to resolve name errors)
retriever = ContextualRetrieverAgent()
analyst = CriticalAnalysisAgent()
insight_gen = InsightGenerationAgent()
reporter = ReportBuilderAgent()

# Pipeline state storage
pipeline_state = {
    'last_retrieved': [],
    'last_analysis': {},
    'last_insights': {},
    'last_report': None,
    'retrieval_display': '',
    'analysis_display': '',
    'insights_display': '',
    'report_display': ''
}

def run_pipeline(query: str,
                 files: List[gr.File],
                 urls: str,
                 depth: str,
                 constraints_json: str = '{}'):
    """Run full multi-stage pipeline with depth presets and user constraints."""
    user_constraints = json.loads(constraints_json) if constraints_json else {}
    depth_presets = {
        'quick':    {"depth": "quick",    "max_sources": 8,  "min_credibility": 0.6, "min_score": 0.6, "top_k": 3},
        'standard': {"depth": "standard", "max_sources": 20, "min_credibility": 0.7, "min_score": 0.6, "top_k": 5},
        'deep':     {"depth": "deep",     "max_sources": 40, "min_credibility": 0.5, "min_score": 0.5, "top_k": 10},
    }
    depth_cfg = depth_presets.get(depth, depth_presets['standard'])
    constraints = {**user_constraints, **depth_cfg}

    file_paths = [f.name for f in files] if files else []
    url_list = [u.strip() for u in urls.split(',') if u.strip()] if urls else []

    # Planning
    try:
        planner = PlannerAgent(constraints)
        plan = planner.plan(query)
        yield 'planning', 'Plan created', None
    except Exception as e:
        yield 'error', f'Planning error: {str(e)}', None
        return

    # Indexing
    try:
        indexed = retriever.index_documents(files=file_paths, urls=url_list)
        yield 'indexing', f'Indexed {indexed} documents', None
    except Exception as e:
        yield 'error', f'Indexing error: {str(e)}', None
        return

    # Retrieval
    try:
        passages = retriever.retrieve(query=query, files=file_paths, urls=url_list, constraints=constraints)
        pipeline_state['last_retrieved'] = passages
        if not passages:
            yield 'retrieval', None, '## No Results\n\nNo relevant passages were found.'
        else:
            lines = [
                f"# Retrieved Context\n",
                f"**Query:** {query}\n",
                f"**Total Passages Retrieved:** {len(passages)}\n",
                f"**Sources:** {len(set(p.get('meta', {}).get('source', 'unknown') for p in passages))}\n",
                "\n---\n"
            ]
            for i, p in enumerate(passages, 1):
                meta = p.get('meta') or {}
                src = meta.get('source') or meta.get('url') or p.get('id') or 'unknown'
                title = meta.get('title', '')
                text = (p.get('text') or '').strip()
                snippet = (text[:800] + '...') if len(text) > 800 else text
                try:
                    score = float(p.get('score', 0))
                except Exception:
                    score = 0.0
                lines.append(f"\n## Passage {i}\n")
                lines.append(f"**Source:** `{src}`  \n")
                if title:
                    lines.append(f"**Title:** {title}  \n")
                lines.append(f"**Relevance Score:** {score:.3f}  \n")
                lines.append(f"\n### Content\n\n{snippet}\n")
                lines.append("\n" + "="*80 + "\n")
            yield 'retrieval', None, '\n'.join(lines)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        yield 'error', f'Retrieval error: {str(e)}', f'## Error Details\n\n```\n{error_details}\n```'
        return

    # Analysis
    try:
        analysis = analyst.analyze_sources(passages)
        pipeline_state['last_analysis'] = analysis
        if isinstance(analysis.get('text'), str):
            analysis_text = f"# Critical Analysis\n\n{analysis.get('text')}"
        else:
            analysis_text = f"# Critical Analysis\n\n```json\n{json.dumps(analysis, indent=2)}\n```"
        yield 'analysis', None, analysis_text
    except Exception as e:
        yield 'error', f'Analysis error: {str(e)}', None
        return

    # Insights
    try:
        insights = insight_gen.generate_insights(analysis=analysis, query=query)
        pipeline_state['last_insights'] = insights
        if isinstance(insights.get('text'), str):
            insights_text = f"# Generated Insights\n\n**Query:** {query}\n\n---\n\n{insights.get('text')}"
        else:
            insights_text = f"# Generated Insights\n\n**Query:** {query}\n\n```json\n{json.dumps(insights, indent=2)}\n```"
        yield 'insights', None, insights_text
    except Exception as e:
        yield 'error', f'Insights error: {str(e)}', None
        return

    # Report
    try:
        artifact = reporter.build_report(query=query, plan=plan, analysis=analysis, insights=insights)
        md_path = artifact.get('md_path')
        if md_path and os.path.exists(md_path):
            with open(md_path, 'r', encoding='utf-8') as f:
                report_md = f.read()
        else:
            report_md = '# Report Error\n\nCould not read generated report file.'
        pipeline_state['last_report'] = artifact
        yield 'report', None, report_md
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        yield 'error', f'Report error: {str(e)}', f'# Report Error\n\n```\n{error_details}\n```'
        return
        
        pipeline_state['last_report'] = artifact
        yield 'report', None, report_md
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        yield 'error', f'Report error: {str(e)}', f'# Report Error\n\n```\n{error_details}\n```'
        return

custom_css = """
/* Center container fix */
.gradio-container { 
    max-width: 1400px !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: 12px !important;
    display: flex !important;
    justify-content: center !important;
}
.main { 
    max-width: 1400px !important;
    width: 100% !important;
    margin: 0 auto !important;
}
.contain { 
    max-width: 100% !important; 
    margin: 0 auto !important;
    padding: 12px !important;
}
/* Tabs with proper scrolling */
.tabs { 
    margin-top: 10px !important; 
    width: 100% !important;
    min-height: 400px !important;
    max-height: 500px !important;
}
.tab-nav { width: 100% !important; }
.tabitem { 
    overflow-y: auto !important;
    max-height: 450px !important;
    padding: 15px !important;
}
/* Status bar */
#status { 
    font-weight: bold !important;
    padding: 10px !important;
    margin: 8px 0 !important;
    border-radius: 6px !important;
    background: #e8f4f8 !important;
    border: 1px solid #b8dce8 !important;
}
/* Spinner styles */
.loader { border:4px solid #f3f3f3; border-top:4px solid #3498db; border-radius:50%; width:30px; height:30px; animation:spin 0.9s linear infinite; margin:4px auto; }
@keyframes spin { 0% { transform: rotate(0deg);} 100% { transform: rotate(360deg);} }
/* Input styling */
.input-row { margin-bottom: 10px !important; }
textarea { min-height: 50px !important; max-height: 100px !important; }
.code-container { max-height: 150px !important; overflow-y: auto !important; }
/* Button styling */
.button-row { 
    margin: 12px 0 !important;
    display: flex !important;
    gap: 8px !important;
}
/* Markdown content */
.prose { 
    max-width: 100% !important;
    overflow-wrap: break-word !important;
}
/* Download button styling */
.download-btn {
    margin-top: 10px !important;
}
"""

with gr.Blocks(css=custom_css, title="Multi-Agent AI Deep Researcher") as demo:
    gr.Markdown("# 🔬 Multi-Agent AI Deep Researcher\n*C2 | Hackathon Group 1*")
    
    with gr.Row():
        with gr.Column(scale=3):
            query_in = gr.Textbox(
                label='Research Query',
                placeholder='Enter your research question...',
                lines=2,
                elem_classes=['input-row']
            )
        with gr.Column(scale=1):
            depth_in = gr.Radio(
                label='Analysis Depth',
                choices=['quick', 'standard', 'deep'],
                value='standard'
            )
    
    with gr.Row():
        with gr.Column(scale=2):
            file_in = gr.File(
                label='Upload Documents',
                file_count='multiple',
                elem_classes=['input-row']
            )
        with gr.Column(scale=2):
            url_in = gr.Textbox(
                label='Add URLs',
                placeholder='Enter URLs (comma-separated)',
                lines=2,
                elem_classes=['input-row']
            )
    
    with gr.Accordion("Advanced Settings", open=False):
        constraints_in = gr.Code(
            label='Configuration (JSON)',
            language='json',
            value=json.dumps({
                "depth": "standard",
                "max_sources": 20,
                "min_credibility": 0.7,
                "min_score": 0.6,
                "top_k": 5
            }, indent=2),
            lines=6,
            elem_classes=['code-container']
        )
    
    status = gr.Textbox(label='Status', interactive=False, elem_id='status', lines=2)
    reset_btn = gr.Button('🔁 Reset Advanced Settings to Depth Preset', variant='secondary')
    spinner = gr.HTML('<div class="loader" id="spinner"></div>', visible=False)
    
    # Action buttons
    with gr.Row(elem_classes=['button-row']):
        run_btn = gr.Button('🚀 Start Research', variant='primary', scale=2)
        index_btn = gr.Button('📥 Index Files', scale=1)
        retrieve_btn = gr.Button('🔍 Retrieve', scale=1)
        analyze_btn = gr.Button('📊 Analyze', scale=1)
        insight_btn = gr.Button('💡 Insights', scale=1)
        report_btn = gr.Button('📄 Report', scale=1)
        clear_btn = gr.Button('🗑️ Clear', scale=1)
    
    # Output sections with tabs for better organization
    with gr.Tabs(elem_classes=['tabs']):
        with gr.Tab("📋 Retrieved Context"):
            retrieval_out = gr.Markdown('Retrieved passages will appear here...', elem_classes=['markdown-container'])
            retrieval_file = gr.File(label="Download Retrieval Data", visible=False)
        with gr.Tab("🔍 Analysis"):
            analysis_out = gr.Markdown('Analysis results will appear here...', elem_classes=['markdown-container'])
            analysis_file = gr.File(label="Download Analysis Data", visible=False)
        with gr.Tab("💡 Insights"):
            insights_out = gr.Markdown('Generated insights will appear here...', elem_classes=['markdown-container'])
            insights_file = gr.File(label="Download Insights Data", visible=False)
        with gr.Tab("📄 Final Report"):
            report_out = gr.Markdown('Final report will appear here...', elem_classes=['markdown-container'])
            report_file = gr.File(label="Download Report Data", visible=False)

    def _timestamp():
        return datetime.now().strftime('%H:%M:%S')

    def on_run(query, files, urls, depth, constraints):
        """Full pipeline with progress: Index -> Retrieve -> Analyze -> Insights -> Report"""
        retrieval_text = pipeline_state.get('retrieval_display', '')
        analysis_text = pipeline_state.get('analysis_display', '')
        insights_text = pipeline_state.get('insights_display', '')
        report_text = pipeline_state.get('report_display', '')

        stage_order = ['planning','indexing','retrieval','analysis','insights','report']
        total = len(stage_order)
        completed = 0

        spinner_visible = True
        for stage, detail, content in run_pipeline(query, files, urls, depth, constraints):
            if stage in stage_order:
                completed = stage_order.index(stage) + 1
            prefix = f"[{completed}/{total}]" if completed else "[0/6]"

            if stage == 'planning':
                status_msg = f"{_timestamp()} | 🔄 {prefix} Planning"
            elif stage == 'indexing':
                status_msg = f"{_timestamp()} | 🔄 {prefix} Indexing"
            elif stage == 'retrieval':
                status_msg = f"{_timestamp()} | 🔄 {prefix} Retrieving"
            elif stage == 'analysis':
                status_msg = f"{_timestamp()} | 🔄 {prefix} Analyzing"
            elif stage == 'insights':
                status_msg = f"{_timestamp()} | 🔄 {prefix} Generating Insights"
            elif stage == 'report':
                status_msg = f"{_timestamp()} | 🔄 {prefix} Building Report"
            elif stage == 'error':
                status_msg = f"{_timestamp()} | ❌ {prefix} Error: {detail}"
            else:
                status_msg = f"{_timestamp()} | 🔄 {prefix} {stage.title()}"

            # Persist content on completion of stage
            if stage == 'retrieval':
                retrieval_text = content or 'No passages retrieved'
                pipeline_state['retrieval_display'] = retrieval_text
            elif stage == 'analysis':
                analysis_text = content or 'No analysis generated'
                pipeline_state['analysis_display'] = analysis_text
            elif stage == 'insights':
                insights_text = content or 'No insights generated'
                pipeline_state['insights_display'] = insights_text
            elif stage == 'report':
                report_text = content or 'No report generated'
                pipeline_state['report_display'] = report_text

            yield status_msg, gr.update(visible=spinner_visible), retrieval_text, analysis_text, insights_text, report_text

        # Final consolidated status
        spinner_visible = False
        final_status = f"{_timestamp()} | ✅ Research Completed ({total}/{total} stages)"
        yield final_status, gr.update(visible=spinner_visible), retrieval_text, analysis_text, insights_text, report_text

    # Individual agent functions
    def clear_all():
        pipeline_state['last_retrieved'] = []
        pipeline_state['last_analysis'] = {}
        pipeline_state['last_insights'] = {}
        pipeline_state['last_report'] = None
        pipeline_state['retrieval_display'] = ''
        pipeline_state['analysis_display'] = ''
        pipeline_state['insights_display'] = ''
        pipeline_state['report_display'] = ''
        return (
            '🗑️ Cleared all data',
            'Retrieved passages will appear here...',
            'Analysis results will appear here...',
            'Generated insights will appear here...',
            'Final report will appear here...'
        )
    
    def prepare_download_file(stage: str, filename: str):
        """Save pipeline stage content to file for download"""
        content = pipeline_state.get(f'{stage}_display', '')
        if not content or 'will appear here' in content:
            return None, gr.File(visible=False)
        
        output_dir = 'outputs'
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath, gr.File(visible=True, value=filepath)
    
    def run_indexing(files, urls):
        """Index files only - preserve existing tab data"""
        try:
            file_paths = [f.name for f in files] if files else []
            url_list = [u.strip() for u in urls.split(',') if u.strip()] if urls else []
            statuses = retriever.index_documents(files=file_paths, urls=url_list)
            
            # Count successful indexing
            indexed_count = sum(1 for s in statuses if s.get('status') == 'indexed')
            chunk_count = sum(s.get('indexed_chunks', 0) for s in statuses if s.get('status') == 'indexed')
            
            return (
                f"{_timestamp()} | ✅ Indexed {indexed_count} documents ({chunk_count} chunks)",
                pipeline_state.get('retrieval_display', ''),
                pipeline_state.get('analysis_display', ''),
                pipeline_state.get('insights_display', ''),
                pipeline_state.get('report_display', '')
            )
        except Exception as e:
            return (
                f"{_timestamp()} | ❌ Indexing error: {str(e)}",
                pipeline_state.get('retrieval_display', ''),
                pipeline_state.get('analysis_display', ''),
                pipeline_state.get('insights_display', ''),
                pipeline_state.get('report_display', '')
            )
    
    def run_retrieval(query, files, urls, depth, constraints):
        """Retrieve only - preserve existing tab data"""
        try:
            user_constraints = json.loads(constraints) if constraints else {}
            depth_presets = {
                'quick':    {"depth": "quick",    "max_sources": 8,  "min_credibility": 0.6, "min_score": 0.6, "top_k": 3},
                'standard': {"depth": "standard", "max_sources": 20, "min_credibility": 0.7, "min_score": 0.6, "top_k": 5},
                'deep':     {"depth": "deep",     "max_sources": 40, "min_credibility": 0.5, "min_score": 0.5, "top_k": 12},
            }
            depth_cfg = depth_presets.get(depth, depth_presets['standard'])
            constraints_dict = {**user_constraints, **depth_cfg}
            file_paths = [f.name for f in files] if files else []
            url_list = [u.strip() for u in urls.split(',') if u.strip()] if urls else []
            
            # Retrieve passages
            passages = retriever.retrieve(query=query, files=file_paths, urls=url_list, constraints=constraints_dict)
            pipeline_state['last_retrieved'] = passages
            
            if not passages or len(passages) == 0:
                retrieval_text = '## No Results\n\nNo relevant passages were found. Please:\n- Check if files were uploaded or URLs provided\n- Try a different query\n- Adjust the minimum score threshold in Advanced Settings'
                pipeline_state['retrieval_display'] = retrieval_text
                return (
                    f"{_timestamp()} | ⚠️ No passages retrieved. Try adjusting your query or sources.",
                    retrieval_text,
                    pipeline_state.get('analysis_display', ''),
                    pipeline_state.get('insights_display', ''),
                    pipeline_state.get('report_display', '')
                )
            
            # Format retrieval results with better markdown
            lines = [
                f"# Retrieved Context\n",
                f"**Query:** {query}\n",
                f"**Total Passages Retrieved:** {len(passages)}\n",
                f"**Sources:** {len(set(p.get('meta', {}).get('source', 'unknown') for p in passages))}\n",
                "\n---\n"
            ]
            
            # Show all passages
            for i, p in enumerate(passages, 1):
                meta = p.get('meta') or {}
                src = meta.get('source') or meta.get('url') or p.get('id') or 'unknown'
                doc_type = meta.get('type', 'unknown')
                title = meta.get('title', '')
                
                text = (p.get('text') or '').strip()
                snippet = (text[:600] + '...') if len(text) > 600 else text
                
                try:
                    score = float(p.get('score', 0))
                except Exception:
                    score = 0.0
                
                lines.append(f"\n## Passage {i}\n")
                lines.append(f"**Source:** `{src}`  \n")
                if title:
                    lines.append(f"**Title:** {title}  \n")
                lines.append(f"**Type:** {doc_type}  \n")
                lines.append(f"**Relevance Score:** {score:.3f}  \n")
                lines.append(f"\n### Content\n\n{snippet}\n")
                lines.append("\n" + "="*60 + "\n")
            
            retrieval_text = '\n'.join(lines)
            pipeline_state['retrieval_display'] = retrieval_text
            
            return (
                f"{_timestamp()} | ✅ Retrieved {len(passages)} passages from {len(set(p.get('meta', {}).get('source', 'unknown') for p in passages))} sources",
                retrieval_text,
                pipeline_state.get('analysis_display', ''),
                pipeline_state.get('insights_display', ''),
                pipeline_state.get('report_display', '')
            )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_text = f'## Error Details\n\n```\n{error_details}\n```'
            pipeline_state['retrieval_display'] = error_text
            return (
                f"{_timestamp()} | ❌ Retrieval error: {str(e)}",
                error_text,
                pipeline_state.get('analysis_display', ''),
                pipeline_state.get('insights_display', ''),
                pipeline_state.get('report_display', '')
            )
    
    def run_analysis():
        """Analyze only - preserve existing tab data"""
        try:
            if not pipeline_state['last_retrieved']:
                return (
                    f"{_timestamp()} | ❌ No retrieved passages. Run retrieval first.",
                    pipeline_state.get('retrieval_display', ''),
                    '',
                    pipeline_state.get('insights_display', ''),
                    pipeline_state.get('report_display', '')
                )
            
            analysis = analyst.analyze_sources(pipeline_state['last_retrieved'])
            pipeline_state['last_analysis'] = analysis
            
            # Format analysis output
            if isinstance(analysis.get('text'), str):
                analysis_text = f"# Critical Analysis\n\n{analysis.get('text')}"
            else:
                analysis_text = f"# Critical Analysis\n\n```json\n{json.dumps(analysis, indent=2)}\n```"
            
            pipeline_state['analysis_display'] = analysis_text
            
            return (
                f"{_timestamp()} | ✅ Analysis complete",
                pipeline_state.get('retrieval_display', ''),
                analysis_text,
                pipeline_state.get('insights_display', ''),
                pipeline_state.get('report_display', '')
            )
        except Exception as e:
            return (
                f"{_timestamp()} | ❌ Analysis error: {str(e)}",
                pipeline_state.get('retrieval_display', ''),
                '',
                pipeline_state.get('insights_display', ''),
                pipeline_state.get('report_display', '')
            )
    
    def run_insights(query):
        """Generate insights only - preserve existing tab data"""
        try:
            if not pipeline_state['last_analysis']:
                return (
                    f"{_timestamp()} | ❌ No analysis data. Run analysis first.",
                    pipeline_state.get('retrieval_display', ''),
                    pipeline_state.get('analysis_display', ''),
                    '',
                    pipeline_state.get('report_display', '')
                )
            
            insights = insight_gen.generate_insights(analysis=pipeline_state['last_analysis'], query=query)
            pipeline_state['last_insights'] = insights
            
            # Format insights output
            if isinstance(insights.get('text'), str):
                insights_text = f"# Generated Insights\n\n**Query:** {query}\n\n---\n\n{insights.get('text')}"
            else:
                insights_text = f"# Generated Insights\n\n**Query:** {query}\n\n```json\n{json.dumps(insights, indent=2)}\n```"
            
            pipeline_state['insights_display'] = insights_text
            
            return (
                f"{_timestamp()} | ✅ Insights generated",
                pipeline_state.get('retrieval_display', ''),
                pipeline_state.get('analysis_display', ''),
                insights_text,
                pipeline_state.get('report_display', '')
            )
        except Exception as e:
            return (
                f"{_timestamp()} | ❌ Insights error: {str(e)}",
                pipeline_state.get('retrieval_display', ''),
                pipeline_state.get('analysis_display', ''),
                '',
                pipeline_state.get('report_display', '')
            )
    
    def run_report_building(query, constraints):
        """Build report only - preserve existing tab data"""
        try:
            if not pipeline_state['last_analysis'] or not pipeline_state['last_insights']:
                return (
                    f"{_timestamp()} | ❌ Missing analysis or insights. Run previous steps first.",
                    pipeline_state.get('retrieval_display', ''),
                    pipeline_state.get('analysis_display', ''),
                    pipeline_state.get('insights_display', ''),
                    ''
                )
            
            constraints_dict = json.loads(constraints) if constraints else {}
            planner = PlannerAgent(constraints_dict)
            plan = planner.plan(query)
            artifact = reporter.build_report(
                query=query,
                plan=plan,
                analysis=pipeline_state['last_analysis'],
                insights=pipeline_state['last_insights']
            )
            
            # Read the generated markdown file
            md_path = artifact.get('md_path')
            if md_path and os.path.exists(md_path):
                with open(md_path, 'r', encoding='utf-8') as f:
                    report_md = f.read()
            else:
                report_md = '# Report Error\n\nCould not read generated report file.'
            
            pipeline_state['last_report'] = artifact
            pipeline_state['report_display'] = report_md
            
            return (
                f"{_timestamp()} | ✅ Report complete",
                pipeline_state.get('retrieval_display', ''),
                pipeline_state.get('analysis_display', ''),
                pipeline_state.get('insights_display', ''),
                report_md
            )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_text = f'# Report Error\n\n```\n{error_details}\n```'
            pipeline_state['report_display'] = error_text
            return (
                f"{_timestamp()} | ❌ Report error: {str(e)}",
                pipeline_state.get('retrieval_display', ''),
                pipeline_state.get('analysis_display', ''),
                pipeline_state.get('insights_display', ''),
                error_text
            )

    # Wire up buttons
    # Depth preset sync: update JSON config when depth changes
    def _depth_json(selected):
        presets = {
            'quick':    {"depth": "quick",    "max_sources": 7,  "min_credibility": 0.6, "min_score": 0.6, "top_k": 3},
            'standard': {"depth": "standard", "max_sources": 15, "min_credibility": 0.7, "min_score": 0.6, "top_k": 5},
            'deep':     {"depth": "deep",     "max_sources": 30, "min_credibility": 0.5, "min_score": 0.5, "top_k": 10},
        }
        return json.dumps(presets.get(selected, presets['standard']), indent=2)

    depth_in.change(
        fn=_depth_json,
        inputs=depth_in,
        outputs=constraints_in
    )

    run_btn.click(
        fn=on_run,
        inputs=[query_in, file_in, url_in, depth_in, constraints_in],
        outputs=[status, spinner, retrieval_out, analysis_out, insights_out, report_out],
        api_name='run_pipeline'
    )
    
    clear_btn.click(
        fn=clear_all,
        inputs=[],
        outputs=[status, retrieval_out, analysis_out, insights_out, report_out]
    )
    
    index_btn.click(
        fn=run_indexing,
        inputs=[file_in, url_in],
        outputs=[status, retrieval_out, analysis_out, insights_out, report_out]
    )
    
    retrieve_btn.click(
        fn=run_retrieval,
        inputs=[query_in, file_in, url_in, depth_in, constraints_in],
        outputs=[status, retrieval_out, analysis_out, insights_out, report_out]
    )
    
    analyze_btn.click(
        fn=run_analysis,
        inputs=[],
        outputs=[status, retrieval_out, analysis_out, insights_out, report_out]
    )
    
    insight_btn.click(
        fn=run_insights,
        inputs=[query_in],
        outputs=[status, retrieval_out, analysis_out, insights_out, report_out]
    )
    
    report_btn.click(
        fn=run_report_building,
        inputs=[query_in, constraints_in],
        outputs=[status, retrieval_out, analysis_out, insights_out, report_out]
    )

    # Reset button wiring
    def _reset_constraints(depth_choice):
        return _depth_json(depth_choice)

    reset_btn.click(
        fn=_reset_constraints,
        inputs=[depth_in],
        outputs=[constraints_in]
    )
    
    # Download file configuration - update when content changes
    retrieval_out.change(
        fn=lambda x: prepare_download_file('retrieval', 'retrieval_context.md')[1],
        inputs=[retrieval_out],
        outputs=[retrieval_file]
    )
    analysis_out.change(
        fn=lambda x: prepare_download_file('analysis', 'critical_analysis.md')[1],
        inputs=[analysis_out],
        outputs=[analysis_file]
    )
    insights_out.change(
        fn=lambda x: prepare_download_file('insights', 'insights.md')[1],
        inputs=[insights_out],
        outputs=[insights_file]
    )
    report_out.change(
        fn=lambda x: prepare_download_file('report', 'final_report.md')[1],
        inputs=[report_out],
        outputs=[report_file]
    )

if __name__ == '__main__':
    for port in range(7860, 7871):
        try:
            print(f"Starting Gradio server on port {port}...")
            demo.launch(server_name='localhost', server_port=port)
            break
        except OSError as e:
            if port < 7870:
                print(f"Port {port} is in use, trying next port...")
            else:
                print(f"Could not find an available port in range 7860-7870")
                raise
