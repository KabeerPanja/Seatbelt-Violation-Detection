import gradio as gr
from src.detect import process_image, process_video
from src.db import init_db

init_db()

with gr.Blocks() as app:

    gr.Markdown("# 🚗 Seatbelt Violation System")

    with gr.Tab("Image"):
        img_in = gr.Image(type="filepath")
        img_out = gr.Image()

        btn = gr.Button("Process Image")

        btn.click(process_image, img_in, img_out)

    with gr.Tab("Video"):
        vid_in = gr.Video()
        vid_out = gr.Video()

        btn2 = gr.Button("Process Video")

        btn2.click(process_video, vid_in, vid_out)

app.launch()