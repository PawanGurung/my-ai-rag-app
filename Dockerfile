# 1. Use an official lightweight Python runtime as a parent image
FROM python:3.12-slim

# 2. Set the working directory inside the container structure
WORKDIR /app

# 3. Copy our dependency manifest file into the container
COPY requirements.txt .

# 4. Install the required Python libraries cleanly inside the container
# --no-cache-dir keeps the final container image size small and fast
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of our application source files into the container
COPY . .

# 6. Expose the standard port 8000 so the container can accept outside traffic
EXPOSE 8000

# 7. Define the runtime command to launch our FastAPI server when the container boots up
# We bind it to 0.0.0.0 so it can accept external connections on the web
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
