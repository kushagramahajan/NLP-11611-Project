# Ubuntu Linux as the base image
FROM ubuntu:18.04
ARG DEBIAN_FRONTEND=noninteractive

# Set UTF-8 encoding
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install Python
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install python3-pip python3-dev

RUN apt-get update && \
    apt-get install -y openjdk-8-jdk && \
    apt-get install -y ant && \
    apt-get clean;

RUN apt install wget -y && \
    apt install gzip -y && \
    apt install git-all -y 

# Install spaCy
RUN pip3 install numpy
RUN pip3 install scipy
RUN pip3 install --upgrade pip
RUN pip3 install spacy
RUN pip3 install pyinflect
# RUN python3 -m spacy download en_core_web_lg
RUN pip3 install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.0.0/en_core_web_sm-3.0.0.tar.gz
RUN pip3 install bs4
RUN pip3 install nltk
RUN pip3 install mlconjug3
RUN pip3 install gensim
RUN git clone https://github.com/huggingface/neuralcoref.git
RUN pip3 install -r neuralcoref/requirements.txt
RUN pip3 install -e neuralcoref/

RUN python3 -m nltk.downloader punkt
RUN python3 -m nltk.downloader wordnet
RUN python3 -m spacy download en_core_web_md


#RUN wget -c "https://s3.amazonaws.com/dl4j-distribution/GoogleNews-vectors-negative300.bin.gz"
#RUN gzip -d GoogleNews-vectors-negative300.bin.gz
#RUN mv GoogleNews-vectors-negative300.bin /QA

# Add the files into container, under QA folder, modify this based on your need
RUN mkdir /QA
ADD answer /QA
ADD answerQuestions.py /QA
ADD GoogleNews-vectors-negative300.bin /QA
ADD ask /QA
ADD sentence_process.py /QA
ADD tags.py /QA
ADD question_file.py /QA
ADD stanford-parser /QA
ADD neural_cor.py /QA
RUN python3 /QA/neural_cor.py

# ADD stanford-ner-jars /QA

# WHAT ABOUT CHMOD OF ANSWER

# Change the permissions of programs
CMD ["chmod 777 /QA/*"]

# Set working dir as /QA
WORKDIR /QA
ENTRYPOINT ["/bin/bash", "-c"]
