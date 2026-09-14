from urllib import response
import deepl
from langdetect import detect
from google import genai
from typing import List
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MODEL = "gemini-3.1-flash-lite"

class LLMCaller:
    def __init__(self) -> None:
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.client = genai.Client(api_key=self.api_key)
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
       
        self.deepl_auth_key = os.getenv('DEEPL_API_KEY')
        if not self.deepl_auth_key:
            raise ValueError("DEEPL_API_KEY not found in environment variables")
        self.translator = deepl.Translator(self.deepl_auth_key)

    def translate_to_english(self, text):
        result = self.translator.translate_text(text, target_lang="EN-US")
        if isinstance(result, list):
            return [r.text for r in result]
        return result.text
    
    def get_emotions(self, text):
        if detect(text) != "en":
            text = self.translate_to_english(text)
        
        prompt = (
            f"I have this text: {text} (end of text). Analyze the sentiment and emotions in the text and Generate 6 unique and evocative umbrella terms that capture the nuanced feelins expressed.\n"
            "Format your response EXACTLY like this, with all on one line:\n"
            "term1 : definition1;term2 : definition2;term3 : definition3;term4 : definition4;term5 : definition5;term6 : definition6\n"
            "Rules:\n"
            "1. Each term should be a single unique word\n"
            "2. Use English and foreign terms about 50% of the time each, with non-English wordswhen they capture a complex emotion\n"
            "3. Include interesting or poetic words (like 'ephemeral' or 'ethereal') when fitting, can be from any language\n"
            "4. Definitions must be brief (5-10 words) but evocative\n"
            "6. All text should be lowercase\n"
            "7. No blank lines between terms\n"
            "8. No additional text or formatting\n"
            "9. Try to be capture what the writer is feeling as closely as possible"
        )
        
        response = self.client.models.generate_content(model = MODEL, contents=prompt)
        return response.text

llmcaller = LLMCaller()