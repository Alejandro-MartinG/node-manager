import logging
import paramiko
import socket

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class SSHService:
    SFTP_COMMANDS = ["push-path", "get"]

    def __init__(self, hostname, username, password=None, key_filename=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.logger = logging.getLogger(__name__)
        self.ssh_client = None
        self.sftp_client = None

    def execute_command(self, command=None, local_path=None, remote_path=None):
        try:
            if not command:
                raise ValueError("Command is required for 'command_execution'")

            self.connect_ssh()

            self.logger.info(f"Executing command: {command}")

            if command in self.SFTP_COMMANDS:
                if not local_path or not remote_path:
                    raise ValueError("Both local_path and remote_path are required for file transfer operations")

                self.connect_sftp()
                sftp_ops = {
                    "put": self.sftp_client.put,
                    "get": self.sftp_client.get
                }
                sftp_ops[command](localpath=local_path, remotepath=remote_path)

                self.logger.info(f"File uploaded successfully from {local_path} to {remote_path}")
                return f"File uploaded successfully from {local_path} to {remote_path}"

            else:
                stdin, stdout, stderr = self.ssh_client.exec_command(command)
                exit_status = stdout.channel.recv_exit_status()
                output = stdout.read().decode('utf-8')
                error = stderr.read().decode('utf-8')
                self.logger.info(f"Command executed with exit status: {exit_status}")
                return output, error

        except Exception as e:
            error_message = f"Error in execute_command: {str(e)}"
            self.logger.error(error_message)
            return '', error_message

        finally:
            self.close()

    def connect_sftp(self):
        if not self.sftp_client:
            self.sftp_client = self.ssh_client.open_sftp()

    def connect_ssh(self):
        if not self.ssh_client:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                self.logger.info(f"Attempting to connect to {self.hostname} as {self.username}")
                if self.key_filename:
                    self.ssh_client.connect(
                        hostname=self.hostname, 
                        username=self.username, 
                        key_filename=self.key_filename
                    )
                else:
                    self.ssh_client.connect(
                        hostname=self.hostname, 
                        username=self.username, 
                        password=self.password
                    )
                self.logger.info("Successfully connected")
            except paramiko.AuthenticationException:
                self.logger.error("Authentication failed. Please check your credentials.")
                raise
            except paramiko.SSHException as ssh_exception:
                self.logger.error(f"SSH exception occurred: {str(ssh_exception)}")
                raise
            except socket.error as socket_error:
                self.logger.error(f"Socket error occurred: {str(socket_error)}")
                raise
            except Exception as e:
                self.logger.error(f"An unexpected error occurred: {str(e)}")
                raise

    def close(self):
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
            self.logger.info("SSH connection closed")
        if self.sftp_client:
            self.sftp_client.close()
            self.sftp_client = None
            self.logger.info("SFTP connection closed")
