import socket
import time
from threading import Timer

# Reading the configuration file (opt.conf)
filepath = r"C:\Users\archa\PycharmProjects\ClientServer\opt.conf"
with open(filepath) as fp:
    # Read the first line of the file
    line = fp.readline()
    cnt = 1  # count = cnt

    # if the read line have text then continue reading otherwise exit the while loop
    while line:
        if cnt == 1:
            KeepALive, value = line.split(":")  # spliting the line at :
            KeepALive = value.strip()  # Removing the white space from the line

        if cnt == 2:
            default_package_size, value = line.split(":")  # spliting the line at :
            default_package_size = int(value.strip())  # Removing the white space from the line

        line = fp.readline()
        cnt += 1


# End of reading flie configuration method

# client sends a hearbeat  to the server every 3rd seconds
def heart_beat():
    if KeepALive == "True":
        Timer(3.0, heart_beat).start()  # timer with 2 parameter (time in second and function name on which we are using the timer)
        mStr = "con-h 0x00"
        soc.sendto(mStr.encode(), server_address)
    else:
        return


# Create a UDP socket
# SOCK_DGRAM UDP protocol
soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Defining the IP address and the Port Number
ip_address = '127.0.0.1'
server_port = 8080
server_address = (ip_address, server_port)
print("Socket successfully created")

client_ip = '127.0.0.1'

#    Hack_ip= '127.00.2'       ip address "To Hack Myself"

# client makes a Connection request and send it to the server
request_message = 'com-0 ' + client_ip
print('C: ' + request_message)

# client encode the message before sending
request_message_encoded = request_message.encode()
soc.sendto(request_message_encoded, server_address)

# client receives the acceptance message from the server and decodes the data
data, address2 = soc.recvfrom(1024)
decoded_data = data.decode()
print('S:' + decoded_data)

# if data = 'com-0 accept ,127.0.0.1' and server is the same client accept the connection
if address2 == server_address and decoded_data == 'com-0 accept 127.0.0.1':
    connection_accept = 'com-0 accept'

    connection_message__encoded = connection_accept.encode()
    soc.sendto(connection_message__encoded, server_address)
    print('C: ' + connection_accept)
    tw_handshake_complete = True
    print('C: Three way handshake is successfully completed.')

# if Three way handshake is false client closes the socket
else:
    print('C: Closing socket')
    tw_handshake_complete = False
    soc.close()

# variables
count = 0
AutoMsg_count = 0
mStr = ' '
messageAndCount = ' '
startTime = 0
endTime = 0
TIMEOUT = 30  # if time out set to 4 second then client need to wait for 5 second and then show the timeout message and perss enter
# this is to avoid the situation where client side console wait to write a messgae instead writing a self message for the console.

while mStr != 'Exit' and mStr != 'exit':

    # send 25 package automatically in 1 second when "default_package_size"  is set
    # less <= 25
    AutoMsg_count = 0
    startTime = time.time()
    while default_package_size > AutoMsg_count and AutoMsg_count < 25 and endTime - startTime <= 1:
        AutoMsgStr = 'Automatic_sending-: ' + str(AutoMsg_count)
        soc.sendto(AutoMsgStr.encode(), server_address)
        AutoMsg_count += 1
        endTime = time.time()

    heart_beat()

    try:
        # converting  integer into string str(count)
        messageAndCount = 'C:msg-' + str(count) + '  = '
        # increasing input count. InputCount is a string value.
        t = Timer(TIMEOUT, print, ['Time Out:Press Enter to continue/exit:'])
        t.start()
        mStr = input(messageAndCount)
        count = count + 1
        t.cancel()

        if mStr == " ":
            mStr = 'con-res 0xFF'
            soc.sendto(mStr.encode(), server_address)
            mStr = 'Exit'
            soc.close()
        else:
            soc.sendto(mStr.encode(), server_address)

        data, address2 = soc.recvfrom(1024)
        # idle_check_server(data.decode())

        if data.decode() != 'con-res 0xFE':
            print('S:res-' + str(count) + ' = ' + data.decode())
            count = count + 1

        else:  # send the acknowledge message to the server to confirm that client has received the closing message
            mStr = 'con-res 0xFE'
            print('S:' + mStr)
            cStrMessage = 'con-res 0xFF'
            soc.sendto(cStrMessage.encode(), server_address)
            print('C:' + 'con-res 0xFF')
            mStr = 'Exit'
            soc.close()

    # If no client pings the server for 4 seconds, we have to assume that the client is not active
    except socket.timeout as e:
        # if array [0] is = timed out
        data, address2 = soc.recvfrom(1024)
        print('S:ServerStoppingMessage to Client:' + data.decode())
        err = e.args[0]
        if err == 'timed out' and data.decode() == 'con-res 0xFE99':
            cStrMessage = 'con-res 0xFF'
            soc.sendto(cStrMessage.encode(), server_address)
            print('C:ClientAcknowledgeMessage to Server:con-res 0xFF99')
            soc.close()

        else:
            print(e)