FROM quay.io/jupyterhub/singleuser:main

USER 0

RUN apt update && apt install -y vim curl wget jq

RUN pip install --upgrade ipywidgets matplotlib numpy scipy scikit-learn

USER 1000