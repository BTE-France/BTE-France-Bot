from discord.ext import commands
import discord
import socket
import struct
import json
import time
import os

class MCServCommands(commands.Cog):

    def __init__(self, client, servip, servport):
        self.servip = servip
        self.servport = servport
        self.client = client
        self.status_title = "Status du serveur Minecraft BTE - France"
        self.status_online = ":white_check_mark: Serveur en ligne!"
        self.status_offline = ":x: Serveur hors ligne! :disappointed_relieved:\n"
        self.color_online = discord.Colour(0x1813e)
        self.color_offline = discord.Colour(0xB00000)
        self.thumbnail_url = "https://cdn.discordapp.com/icons/694003889506091100/a_c40ba19cfcfbb9db5f5060e85f6539cf.png?size=128"
        self.offline_embed = discord.Embed(title=self.status_title, colour=self.color_offline, description=self.status_offline)
        self.offline_embed.set_thumbnail(url=self.thumbnail_url)

    def _status2embed(self, status):
        onlineplayers = status["players"]["online"]
        maxplayers = status["players"]["max"]
        sample = [ p["name"] for p in status["players"]["sample"] ]
        embed = discord.Embed(title=self.status_title, colour=self.color_online, description=self.status_online)
        embed.set_thumbnail(url=self.thumbnail_url)
        embed.add_field(name="En ligne:", inline=False, value=f"{onlineplayers}/{maxplayers}")
        if onlineplayers == 0:
            return embed
        diff = onlineplayers - len(sample)
        sampletitle = "Joueurs:"
        if diff > 0:
            sampletxt = ", ".join(sample)
            sampletxt += f" et {diff} autre" + "." if diff == 1 else "s."
        elif onlineplayers == 1:
            sampletitle = "Joueur:"
            sampletxt = sample[0]
        else:
            sampletxt = ", ".join(sample[:-1]) + " et " + sample[-1]
        embed.add_field(name=sampletitle, inline=False, value=sampletxt)
        return embed
        

    @commands.command(brief='Lookup the minecraft server status')
    async def mcserv(self, ctx):
        ping = StatusPing(host=self.servip, port=self.servport)
        try:
            status = ping.get_status()
            embed = self._status2embed(status)
            await ctx.send(embed=embed)
        except (ConnectionError, socket.timeout) as e:
            await ctx.send(embed=self.offline_embed)

def setup(client):
    host = os.environ['BTEBOT_IP']
    if ":" in host:
        host, port = host.split(":")
        client.add_cog(MCServCommands(client, host, int(port)))
    else:
        client.add_cog(MCServCommands(client, host, 25565))


class StatusPing:
    """ Get the ping status for the Minecraft server
    Copied from:
    https://gist.github.com/ewized/97814f57ac85af7128bf"""

    def __init__(self, host='localhost', port=25565, timeout=5):
        """ Init the hostname and the port """
        self._host = host
        self._port = port
        self._timeout = timeout

    def _unpack_varint(self, sock):
        """ Unpack the varint """
        data = 0
        for i in range(5):
            ordinal = sock.recv(1)

            if len(ordinal) == 0:
                break

            byte = ord(ordinal)
            data |= (byte & 0x7F) << 7*i

            if not byte & 0x80:
                break

        return data

    def _pack_varint(self, data):
        """ Pack the var int """
        ordinal = b''

        while True:
            byte = data & 0x7F
            data >>= 7
            ordinal += struct.pack('B', byte | (0x80 if data > 0 else 0))

            if data == 0:
                break

        return ordinal

    def _pack_data(self, data):
        """ Page the data """
        if type(data) is str:
            data = data.encode('utf8')
            return self._pack_varint(len(data)) + data
        elif type(data) is int:
            return struct.pack('H', data)
        elif type(data) is float:
            return struct.pack('L', int(data))
        else:
            return data

    def _send_data(self, connection, *args):
        """ Send the data on the connection """
        data = b''

        for arg in args:
            data += self._pack_data(arg)

        connection.send(self._pack_varint(len(data)) + data)

    def _read_fully(self, connection, extra_varint=False):
        """ Read the connection and return the bytes """
        packet_length = self._unpack_varint(connection)
        packet_id = self._unpack_varint(connection)
        byte = b''

        if extra_varint:
            # Packet contained netty header offset for this
            if packet_id > packet_length:
                self._unpack_varint(connection)

            extra_length = self._unpack_varint(connection)

            while len(byte) < extra_length:
                byte += connection.recv(extra_length)

        else:
            byte = connection.recv(packet_length)

        return byte

    def get_status(self):
        """ Get the status response """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            connection.settimeout(self._timeout)
            connection.connect((self._host, self._port))

            # Send handshake + status request
            self._send_data(connection, b'\x00\x00', self._host, self._port, b'\x01')
            self._send_data(connection, b'\x00')

            # Read response, offset for string length
            data = self._read_fully(connection, extra_varint=True)

            # Send and read unix time
            self._send_data(connection, b'\x01', time.time() * 1000)
            unix = self._read_fully(connection)

        # Load json and return
        response = json.loads(data.decode('utf8'))
        response['ping'] = int(time.time() * 1000) - struct.unpack('L', unix)[0]

        return response

