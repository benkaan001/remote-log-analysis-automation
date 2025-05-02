# Use a Python base image with specific version tag
FROM python:3.10-slim

# Set environment variables to non-interactive (prevents prompts during build)
ENV DEBIAN_FRONTEND=noninteractive

# Install OpenSSH Server and utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    && rm -rf /var/lib/apt/lists/*

# Create a dedicated group for SFTP
RUN groupadd sftpusers

# Create the user WITHOUT creating the home directory initially
# We need to control its ownership precisely for ChrootDirectory
RUN useradd -g sftpusers -s /usr/sbin/nologin sftpuser

# --- Set password for the SFTP user ---
# WARNING: This is for development/demo purposes only!
# In production, use SSH keys or environment variables for credentials
ARG SFTP_PASSWORD=testpassword
RUN echo "sftpuser:${SFTP_PASSWORD}" | chpasswd

# --- Create Home Directory and Set Chroot Permissions ---
# Create the user's home directory
RUN mkdir -p /home/sftpuser
# IMPORTANT: Set ownership of the chroot directory itself to root
# This is a security requirement for OpenSSH's ChrootDirectory feature
RUN chown root:root /home/sftpuser
# Set permissions for the chroot directory (read/execute for others)
RUN chmod 755 /home/sftpuser
# Create the .ssh directory inside, owned by the user (for key-based authentication)
RUN mkdir -p /home/sftpuser/.ssh && \
    chown sftpuser:sftpusers /home/sftpuser/.ssh && \
    chmod 700 /home/sftpuser/.ssh

# --- Configure SSH Server ---
RUN mkdir -p /var/run/sshd
# Generate host keys
RUN ssh-keygen -A

# Configure SSH server with secure settings
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    # Comment out or remove external sftp subsystem as we'll be using internal-sftp
    sed -i 's/^Subsystem sftp/#Subsystem sftp/' /etc/ssh/sshd_config && \
    # Add the Match Group block for SFTP configuration
    echo "" >> /etc/ssh/sshd_config && \
    echo "Match Group sftpusers" >> /etc/ssh/sshd_config && \
    echo "  ChrootDirectory /home/%u" >> /etc/ssh/sshd_config && \
    echo "  ForceCommand internal-sftp" >> /etc/ssh/sshd_config && \
    echo "  AllowTcpForwarding no" >> /etc/ssh/sshd_config && \
    echo "  X11Forwarding no" >> /etc/ssh/sshd_config

# --- Create Log Directories and Copy Sample Files ---
WORKDIR /home/sftpuser

# Create the log directory structure INSIDE the user's home directory
# These directories need to be owned by the sftpuser so they can be accessed after chroot
RUN mkdir -p logs && chown -R sftpuser:sftpusers logs

# Copy the entire locally created log structure into the container image
COPY sample_logs_generated/. /home/sftpuser/logs/

# Ensure correct ownership of copied files
RUN chown -R sftpuser:sftpusers /home/sftpuser/logs

# Expose SSH port
EXPOSE 22

# Health check to ensure SSH service is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD pgrep sshd || exit 1

# Command to run the SSH server in the foreground with detailed logging
CMD ["/usr/sbin/sshd", "-D", "-e"]