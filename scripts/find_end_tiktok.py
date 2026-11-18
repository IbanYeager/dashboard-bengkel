with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="pane-tiktok"')
# find closing for this tab pane container
end_pos = text.find('</main>', pos)
print("From end of pane-tiktok to </main>:")
print(text[end_pos-300:end_pos+200])
