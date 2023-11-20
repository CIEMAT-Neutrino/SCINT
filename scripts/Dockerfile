
FROM almalinux:9
WORKDIR /home

# Install packages from AlmaLinux base and EPEL
RUN dnf -y install 'dnf-command(config-manager)'
RUN dnf config-manager --set-enabled crb && dnf -y install epel-release && dnf -y update
# Install packages needed for ROOT
RUN dnf -y install python3 python3-pip python-devel git root\* python3-root python3-jupyroot

# Install python packages 
RUN pip3 install --upgrade pip wheel iminuit urllib3 tables metakernel ipykernel jupyter-server
COPY requirements.txt ./ 
RUN pip3 install -r requirements.txt

RUN git clone --recursive "https://github.com/CIEMAT-Neutrino/SCINT.git"
RUN git clone --recursive "https://github.com/CIEMAT-Neutrino/UTILS.git"
RUN rm -rf requirements.txt && dnf clean all

# Set up environment variables
RUN echo "alias myjupyter='jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root'" >> ~/.bashrc

# Expose port for Jupyter notebook server
EXPOSE 8888
# To run jupyter when this docker container is started.
# CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''", "--no-browser", "--NotebookApp.allow_origin='*'"]

# TODO: install vscode extensions + add UTILS repo + data example

### BUILD IMAGE & RUN ###
# docker build -t scint .
# docker images
# docker run -it scint /bin/bash

### UPLOAD IMAGE ###
# docker tag myimage:latest myusername/myrepo:v1.0
# docker login
# docker push myusername/myrepo:v1.0

### DOWNLOAD IMAGE ###
# docker pull myusername/myrepo:v1.0
# docker run -p 8888:8888 -it scint /bin/bash
#or
# apptainer pull docker://myrepo:v1.0
# apptainer run --home=/whatever/path/you/want scint_v0.0.sif bash

### REMOVE IMAGE (BE CAREFUL) ###
# docker image prune -a
# docker rmi -f ID
# docker container prune

### RUN JUPYTER INSIDE CONTAINER ###
# jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --NotebookApp.token='' --NotebookApp.password='' --no-browser --NotebookApp.allow_origin='*'
# jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root and copy the token of the server to use it in the browser/local