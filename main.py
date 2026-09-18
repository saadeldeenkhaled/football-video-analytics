import gradio as gr
from pipeline import process_video
import os

def analyze_football_video(video_file, conf_thresh):
    if video_file is None:
        return None
        
    import config
    config.CONFIDENCE_THRESHOLD = float(conf_thresh)
    
    os.makedirs("output", exist_ok=True)
    output_path = os.path.abspath("output/output_analyzed.mp4")
    
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except Exception:
            pass

    process_video(video_file, output_path)
    return output_path

def create_ui():
    with gr.Blocks(title="AI Football Analytics", theme=gr.themes.Base()) as app:
        gr.Markdown("# ⚽ Professional Football Video Analysis System")
        gr.Markdown("Upload a tactical or broadcast football clip. The system detects players, assigns teams, and calculates real-world speed and distance using perspective mapping.")
        
        with gr.Row():
            with gr.Column():
                input_video = gr.Video(label="Input Match Video")
                conf_slider = gr.Slider(minimum=0.1, maximum=0.9, value=0.35, step=0.05, label="Detection Confidence Threshold")
                analyze_btn = gr.Button("Analyze Match", variant="primary")
            
            with gr.Column():
                output_video = gr.Video(label="Analyzed Output Video")
                
        analyze_btn.click(
            fn=analyze_football_video,
            inputs=[input_video, conf_slider],
            outputs=[output_video]
        )
        
    return app

if __name__ == "__main__":
    print("Initializing Football AI Analytics Interface...")
    app = create_ui()
    app.launch(server_name="0.0.0.0", server_port=7861, inbrowser=True)