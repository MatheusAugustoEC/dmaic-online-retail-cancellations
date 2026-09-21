"""Injeta docs/entrega_dados.json dentro de docs/index.html, substituindo o
placeholder do <script type="application/json" id="dados-projeto">. Rodar
sempre depois de fase6_dados_entrega.py, sempre que os dados mudarem.
"""
import json
import re

with open("docs/entrega_dados.json", encoding="utf-8") as f:
    dados = json.load(f)

with open("docs/index.html", encoding="utf-8") as f:
    html = f.read()

payload = json.dumps(dados, ensure_ascii=False)
# escapa </script> para nao fechar a tag prematuramente dentro do JSON
payload_safe = payload.replace("</script", "<\\/script")

novo = re.sub(
    r'<script type="application/json" id="dados-projeto">.*?</script>',
    lambda m: f'<script type="application/json" id="dados-projeto">{payload_safe}</script>',
    html,
    count=1,
    flags=re.DOTALL,
)

if novo == html:
    raise SystemExit("Marcador dados-projeto nao encontrado em docs/index.html - nada foi injetado.")

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(novo)

import os
print(f"Injetado. docs/index.html agora tem {os.path.getsize('docs/index.html')/1024:.0f} KB.")
