import socket
import time

def receiveData(conn) -> bytearray:
  data = bytearray()
  while len(data) < 4:
    try:
      packet = conn.recv(4 - len(data))
    except BlockingIOError:
      time.sleep(0.01)
      continue
    if not packet:
      raise Exception("Socket closed")
    data.extend(packet)
  recv_data_size = int.from_bytes(data, byteorder='little')
  # print(f"Receiving {recv_data_size} bytes of audio...")
  data = bytearray()
  while len(data) < recv_data_size:
    try:
      packet = conn.recv(recv_data_size - len(data))
    except BlockingIOError:
      time.sleep(0.01)
      continue
    if not packet:
      raise Exception("Socket closed")
    data.extend(packet)
  # print("... received.")
  return data

def sendData(conn, data):
  send_data_size = len(data)
  # print("Sending {} bytes of audio...".format(send_data_size))
  data_len = send_data_size.to_bytes(4, "little")
  conn.sendall(data_len)
  conn.sendall(data)
