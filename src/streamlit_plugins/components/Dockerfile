FROM python:3.8

RUN mkdir -p /streamlit/components
COPY requirements.txt /streamlit/requirements.txt
RUN pip install --no-cache-dir -r /streamlit/requirements.txt

ENV PYTHONPATH=/streamlit

ENTRYPOINT ["bash", "-c", "pip install --no-cache-dir -r \"/streamlit/components/$APP/example/requirements.txt\" && streamlit run \"/streamlit/components/$APP/example/app.py\""]