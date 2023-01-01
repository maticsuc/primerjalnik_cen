import os, socket, logging

LOGSTASH_IP = str(os.environ["LOGSTASH_IP"])
LOGSTASH_PORT = int(os.environ["LOGSTASH_PORT"])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class LogHandler(logging.Handler):
    def emit(self, record):
        try:
            sock.sendto(bytes(self.format(record), "utf-8"), (LOGSTASH_IP, LOGSTASH_PORT))
        except:
            pass