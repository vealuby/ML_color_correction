# Base image is Python 3.11
FROM python:3.11-slim
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 net-tools -y



# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the required packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the model and application code into the container
COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]