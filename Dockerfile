# Use Ubuntu as the base image
FROM ubuntu:22.04

# Set a working directory
WORKDIR /app

# Install Python 3 and system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgtk-3-0 \
    libwebkit2gtk-4.0-37 \
    libgirepository-1.0-1 \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libatk1.0-dev \
    libghc-pango-dev \
    libmpv1 \
    && rm -rf /var/lib/apt/lists/*

# Verify Python 3 installation
RUN python3 --version

# Copy requirements file (if you have it) for Python dependencies
COPY requirements.txt /app

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt flet_desktop

# Copy the entire project, including .env
COPY . /app

# Expose the port for Flet
EXPOSE 8015

# Run Flet on host 0.0.0.0 and port 8015 in web mode
CMD ["flet", "run", "app.py", "--host=0.0.0.0", "--port=8015", "--web"]