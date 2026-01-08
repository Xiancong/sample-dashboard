FROM python:3.10-slim

# Install system deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Run Streamlit
CMD streamlit run /app/main.py --server.port=$PORT --server.address=0.0.0.0
