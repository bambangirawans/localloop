# scripts/visualize_graph.py

from pyvis.network import Network
from rdflib import Graph
import os

def visualize_graph(output_path="app/static/graph.html"):
    g = Graph()
    g.parse("data/user_profile.ttl", format="ttl")

    net = Network(height="100%", width="100%", notebook=False, directed=True)

    nodes = set()
    for s, p, o in g:
        for n in [s, o]:
            if n not in nodes:
                net.add_node(str(n), label=str(n))
                nodes.add(n)
        net.add_edge(str(s), str(o), label=str(p.split('#')[-1]))

    net.set_options("""
    var options = {
      interaction: { hover: true },
      physics: { stabilization: true },
      nodes: {
        shape: 'dot',
        size: 12,
        font: { size: 14 }
      },
      edges: {
        arrows: { to: { enabled: true }},
        font: { align: 'middle' }
      }
    }
    """)

    # Add HTML/JS to support feedback panel
    html_path = output_path
    net.show(html_path)

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Inject a floating feedback panel and JS logic
    feedback_ui = """
    <div id="feedback-box" style="
      position:fixed;
      top:10px;
      right:10px;
      background:white;
      border:1px solid #ccc;
      padding:10px;
      z-index:1000;
      width:250px;
      font-family:sans-serif;
      display:none;
    ">
      <strong>Feedback for node:</strong>
      <div id="node-name" style="margin:5px 0;font-weight:bold;"></div>
      <textarea id="feedback-input" rows="4" style="width:100%;"></textarea>
      <button onclick="submitFeedback()">Send Feedback</button>
      <button onclick="hideBox()">Close</button>
    </div>

    <script>
      function showBox(nodeId) {
        document.getElementById('node-name').innerText = nodeId;
        document.getElementById('feedback-box').style.display = 'block';
      }
      function hideBox() {
        document.getElementById('feedback-box').style.display = 'none';
      }
      function submitFeedback() {
        const feedback = document.getElementById('feedback-input').value;
        const nodeId = document.getElementById('node-name').innerText;
        fetch('/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ node: nodeId, feedback: feedback })
        }).then(res => {
          alert("Feedback submitted!");
          hideBox();
        }).catch(err => alert("Error sending feedback"));
      }
      network.on("click", function(params) {
        if (params.nodes.length > 0) {
          const nodeId = params.nodes[0];
          showBox(nodeId);
        }
      });
    </script>
    """

    html = html.replace("</body>", feedback_ui + "\n</body>")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
