from transformers import pipeline

ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english", grouped_entities=True)

text = "My name is Ndumiso Lushaba and I live in Mbabane, Eswatini."
entities = ner_pipeline(text)

for e in entities:
    print(e)
