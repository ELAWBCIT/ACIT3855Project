FROM python:3

LABEL maintainer='elaw24@my.bcit.ca'

RUN mkdir /app
RUN mkdir -p /app/logs
RUN mkdir -p /app/conf
RUN mkdir -p /app/stats

# Copy the requirements.txt to leverage Docker cache via `pip install`
COPY ./requirements.txt /app/requirements.txt

# Setting the working directory
WORKDIR /app

# Installation of dependencies 
RUN pip3 install -r requirements.txt

# Copying the source code 
COPY . /app

# Change permissions and become a non-privileged user
RUN chown -R nobody:nogroup /app
USER nobody

# Service listens to por 8080 on the container. 
EXPOSE 8100

# Entrypoint means to run python. 
ENTRYPOINT [ "python3" ]

# Default = run app.py 
CMD [ "app.py" ]