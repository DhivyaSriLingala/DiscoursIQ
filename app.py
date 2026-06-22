import os
import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

<<<<<<< HEAD
MODEL_ID = "./model"  # local model files bundled in the Space repo
=======
MODEL_ID = "dhivya2428/discoursiq-movies"
HF_TOKEN = os.environ.get("HF_TOKEN")
>>>>>>> e3cc77e453c3922dac10bd46ccde89593951d2a8

LABEL_MAP = {"analysis": 0, "hot_take": 1, "reaction": 2}
ID_TO_LABEL = {v: k for k, v in LABEL_MAP.items()}

LABEL_DESCRIPTIONS = {
    "analysis": "Structured argument backed by specific filmmaking observations or evidence.",
    "hot_take": "Bold opinion stated confidently without supporting evidence.",
    "reaction": "Immediate emotional response to a film — feeling over reasoning.",
}

LABEL_COLORS = {
    "analysis": "#2563eb",   # blue
    "hot_take": "#dc2626",   # red
    "reaction": "#16a34a",   # green
}

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID, token=HF_TOKEN)
model.eval()


def classify(text: str):
    if not text.strip():
        return {}, "", ""

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = F.softmax(logits, dim=-1).squeeze()

    scores = {ID_TO_LABEL[i]: float(probs[i]) for i in range(len(LABEL_MAP))}
    top_label = max(scores, key=scores.get)
    confidence = scores[top_label]

    verdict = f"**{top_label.upper().replace('_', ' ')}** ({confidence:.0%} confidence)"
    description = LABEL_DESCRIPTIONS[top_label]

    return scores, verdict, description


EXAMPLES = [
    "Villeneuve's use of silence in Dune Part Two is deliberate — the sandworm riding sequence has almost no score, forcing you to sit with Paul's moral collapse rather than letting Hans Zimmer paper over it.",
    "The Godfather is overrated and I'm tired of pretending otherwise. It's just a long soap opera with good cinematography.",
    "Just walked out of Oppenheimer. I genuinely cannot process what I just watched. Give me a few days.",
    "Christopher Nolan has never once written a believable female character and his films get a pass because the visuals are impressive.",
    "The color work in Moonlight is doing real narrative labor — Jenkins and Laxton shift from cool blues in childhood to warm amber in the Miami sections to chart Chiron's psychic state, not just his environment.",
    "Watched Midsommar alone at midnight and I need someone to talk to. What the HELL was that ending.",
    "The MCU's core problem is that every film is required to service the franchise rather than itself. Any character moment that could produce genuine change is undone in the next installment because the IP needs to remain stable.",
    "Parasite just wrecked me. The last twenty minutes — I couldn't breathe. Incredible.",
]

with gr.Blocks(
    title="DiscourseIQ — r/movies Comment Classifier",
    theme=gr.themes.Soft(primary_hue="blue"),
    css="""
        .verdict-box { font-size: 1.4em; padding: 12px 16px; border-radius: 8px; background: #f1f5f9; }
        .desc-box { color: #475569; font-style: italic; margin-top: 4px; }
        footer { display: none !important; }
    """,
) as demo:
    gr.Markdown(
        """
# 🎬 DiscourseIQ
### r/movies Comment Quality Classifier

Paste any r/movies post or comment. The model classifies it as **analysis**, **hot take**, or **reaction**
— and shows how confident it is in each label.

*Fine-tuned DistilBERT · Trained on 140 annotated r/movies examples*
        """
    )

    with gr.Row():
        with gr.Column(scale=3):
            text_input = gr.Textbox(
                label="Post or comment",
                placeholder="Paste an r/movies post here…",
                lines=5,
            )
            submit_btn = gr.Button("Classify", variant="primary")

        with gr.Column(scale=2):
            verdict_md = gr.Markdown(elem_classes=["verdict-box"])
            desc_md = gr.Markdown(elem_classes=["desc-box"])
            confidence_bars = gr.Label(label="Confidence per label", num_top_classes=3)

    gr.Markdown("### Try an example")
    gr.Examples(
        examples=[[e] for e in EXAMPLES],
        inputs=[text_input],
        label=None,
    )

    gr.Markdown(
        """
---
**Label definitions**

| Label | Meaning |
|---|---|
| `analysis` | Structured argument about filmmaking craft — supported by specific examples |
| `hot_take` | Bold, confident opinion stated without evidence — asserts rather than argues |
| `reaction` | Immediate emotional response after watching — feeling over reasoning |

**Note:** The baseline zero-shot LLM (Groq Llama 3.3 70B) achieved 96.8% accuracy on this task vs.
87.1% for this fine-tuned model — an honest result documented in the [project repo](https://github.com/DhivyaSriLingala/DiscoursIQ).
The gap narrows on messier real-world text where prompt-only approaches degrade faster than fine-tuned models.
        """
    )

    submit_btn.click(
        fn=classify,
        inputs=[text_input],
        outputs=[confidence_bars, verdict_md, desc_md],
    )
    text_input.submit(
        fn=classify,
        inputs=[text_input],
        outputs=[confidence_bars, verdict_md, desc_md],
    )

demo.launch()
