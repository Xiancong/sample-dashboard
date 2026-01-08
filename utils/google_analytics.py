import os
import streamlit.components.v1 as components

# Configuration
GA_MEASUREMENT_ID = os.environ.get("GA_MEASUREMENT_ID")

def inject_google_analytics():
    """Injects the Google Analytics gtag.js script into the Streamlit app."""
    GA_JS = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_MEASUREMENT_ID}');
    </script>
    """
    
    components.html(GA_JS, height=0, width=0)
