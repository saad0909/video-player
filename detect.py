from googleapiclient import discovery

def analyze_text(text):
    api_key = "AIzaSyB7mmu9GYkAJVzhmnhc7VoiCvn6-hhd3k0"
    #service = discovery.build("commentanalyzer", "v1alpha1", developerKey=api_key)
    service = discovery.build("commentanalyzer", "v1alpha1", developerKey=api_key, 
                              discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
                              static_discovery=False,)

    analyze_request = {
        "comment": {"text": text},
        "requestedAttributes": {"TOXICITY": {}},
    }

    response = service.comments().analyze(body=analyze_request).execute()

    toxicity_score = response["attributeScores"]["TOXICITY"]["summaryScore"]["value"]
    
    return toxicity_score

# Example usage:
text = "This is a sample text fuck you with potentially explicit content."
toxicity_score = analyze_text(text)
print("Toxicity Score:", toxicity_score)
