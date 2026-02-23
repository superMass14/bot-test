FROM continuumio/miniconda3:latest

WORKDIR /app

COPY environment.yml ./
COPY .env ./
RUN conda env create -f environment.yml &&  conda clean -afy

COPY . .

RUN echo "conda activate dtf_bot" >> ~/.bashrc
CMD  ["/bin/bash", "-c", "source ~/.bashrc && python main.py"]
