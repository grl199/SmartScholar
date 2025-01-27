# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock /app/

# Install pipenv and project dependencies
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile

# Copy the rest of the application code into the container
COPY src/ /app/src/
COPY config.yaml /app/

# Expose the port the app runs on (if applicable)
EXPOSE 8501

# Run the application
CMD ["pipenv", "run", "streamlit", "run", "src/main.py"]