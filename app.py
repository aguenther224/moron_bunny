import os
from flask import Flask, render_template_string, request
from openai import OpenAI

# Read your OpenAI API key from the environment (set this on Render as OPENAI_API_KEY)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Moron Bunny Generator</title>
  <style>
    body { font-family: system-ui, Arial, sans-serif; max-width: 780px; margin: 40px auto; padding: 0 16px; }
    .btn { padding: 12px 18px; background:#6c47ff; color:white; border:none; border-radius:8px; cursor:pointer; font-size:16px; }
    .btn:disabled { opacity:.6; cursor:not-allowed; }
    img { max-width: 100%; border-radius: 12px; border:1px solid #ddd; }
    .row { margin: 20px 0; }
    .error { color: #c00; }

    /* Working indicator styles */
    .working { margin-left: 12px; color: #555; font-size: 14px; vertical-align: middle; }
    .spinner {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 2px solid #ccc;
      border-top-color: #6c47ff;
      border-radius: 50%;
      animation: spin .8s linear infinite;
      vertical-align: -3px;
      margin-right: 6px;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>
  <h1>Moron Bunny Generator</h1>

  <form method="post" action="/generate" class="gen-form">
    <button class="btn" type="submit">Generate moron bunny</button>
    <span class="working" hidden>
      <span class="spinner" aria-hidden="true"></span>
      Working on it...
    </span>
  </form>

  {% if error %}
    <p class="error">{{ error }}</p>
  {% endif %}

  {% if image_b64 %}
    <div class="row">
      <h2>Your new bunny</h2>
      <img alt="moron bunny" src="data:image/png;base64,{{ image_b64 }}">
    </div>
    <form method="post" action="/generate" class="gen-form">
      <button class="btn" type="submit">Generate another</button>
      <span class="working" hidden>
        <span class="spinner" aria-hidden="true"></span>
        Working on it...
      </span>
    </form>
  {% endif %}

  <script>
    // Show "Working on it..." and disable button during form submission
    window.addEventListener('DOMContentLoaded', function () {
      document.querySelectorAll('form.gen-form').forEach(function (form) {
        form.addEventListener('submit', function () {
          const btn = form.querySelector('button[type="submit"]');
          const working = form.querySelector('.working');
          if (btn) {
            btn.disabled = true;
            btn.dataset.originalText = btn.textContent;
            btn.textContent = 'Generating...';
          }
          if (working) {
            working.hidden = false;
          }
        });
      });
    });
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML)

@app.route("/generate", methods=["POST"])
def generate():
    try:
        prompt = (
            "A humorous, cute-but-dumb-looking cartoon bunny ('moron bunny'): "
            "big floppy ears, derpy crossed eyes, lopsided grin, slightly buck teeth, "
            "soft pastel colors, simple clean background, playful and silly. "
            "High-quality digital illustration, no text, PNG."
        )
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
        b64 = result.data[0].b64_json
        return render_template_string(HTML, image_b64=b64)
    except Exception as e:
        # Log to server logs and show a friendly message
        print(f"Error generating image: {e}")
        return render_template_string(HTML, error="Failed to generate image. Check server logs."), 500

if __name__ == "__main__":
    # Render sets PORT in the environment; default to 8000 locally
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
