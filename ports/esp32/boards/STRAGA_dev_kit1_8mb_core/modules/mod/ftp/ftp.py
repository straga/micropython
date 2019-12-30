# Copyright (c) 2018 Viktor Vorobjov


try:

    import uos
    import uerrno
    import uasyncio as asyncio
    from core.platform import upy_awrite as _awrite
    from core.platform import upy_aclose as _aclose

except Exception:

    import os as uos
    import errno as uerrno
    import asyncio as asyncio
    from core.platform import pc_awrite as _awrite
    from core.platform import pc_aclose as _aclose
    pass


import logging
log = logging.getLogger("FTP")
log.setLevel(logging.INFO)

class FTPServer:

    def __init__(self, addr="0.0.0.0", port=25, dport=26, cwd="/"):

        self.addr = addr
        self.port = port
        self.dport = dport
        self.max_chuck_size = 512
        self.data_start = False
        self.transfer = False
        self.transfer_path = False
        self.transfer_rpl = False
        self.con_type = False
        self._run = False
        self._run_pasv = False
        self.cwd = cwd


    def start(self):

        if not self._run:

            self._run = True
            loop = asyncio.get_event_loop()
            loop.create_task(asyncio.start_server(self.ftp_cmd_server, "0.0.0.0", self.port))
            log.info("FTP run on = {}:{}".format("0.0.0.0", self.port))

        else:
            log.info("FTP already run on = {}:{}".format(self.addr, self.port))

        return True

    async def awrite(self, writer, data, b=False):
        if not b:
            data = data.encode('utf-8')

        await _awrite(writer, data)

    async def send_list_data(self, writer):

        path = self.cwd

        try:
           uos.stat(path)
        except OSError as e:
            log.debug("PATH: {}".format(e))
            return False

        items = uos.listdir(path)

        if path == '/':
            path = ''
        for i in items:
            file_stat = uos.stat(path + "/" + i)

            file_permissions = "drwxr-xr-x" if (file_stat[0] & 0o170000 == 0o040000) else "-rw-r--r--"
            file_size = file_stat[6]
            description = "{}    1 owner group {:>10} Jan 1 2000 {}\r\n".format(
                file_permissions, file_size, i)

            try:
                await self.awrite(writer, description)
            except Exception as err:
                log.error(err)
                pass

    async def send_file_data(self, writer):

        max_chuck_size = self.max_chuck_size
        buf = bytearray(max_chuck_size)

        argument = self.transfer_path
        remaining_size = uos.stat(argument)[-4]

        try:
            with open(argument, "rb") as f:
                while remaining_size:
                    chuck_size = f.readinto(buf)
                    remaining_size -= chuck_size
                    mv = memoryview(buf)
                    # await writer.awrite(mv[:chuck_size])
                    await self.awrite(writer, mv[:chuck_size], True)
            self.transfer_rpl = "226 Transfer complete.\r\n"
        except OSError as e:
            if e.args[0] == uerrno.ENOENT:
                self.transfer_rpl = "550 No such file.\r\n"
            else:
                self.transfer_rpl = "550 Open file error.\r\n"
        finally:
            self.transfer_path = False
            del buf

        log.info("-> Transfer: {} - {}".format(argument, self.transfer_rpl))
        return True

    def check_file(self, _file):
        return "226 Transfer complete\r\n"

    async def save_file_data(self, reader):
        max_chuck_size = self.max_chuck_size
        argument = self.transfer_path

        log.debug("Argument - {}".format(argument))
        self.transfer_rpl = "550 File i/o error.\r\n"

        try:
            with open(argument, "wb") as f:
                log.debug("WB")

                while True:
                    try:
                        data = await reader.read(max_chuck_size)
                        w = f.write(data)
                        if not data or w < max_chuck_size:
                            break

                    except Exception as e:
                        log.error("exception .. {}".format(e))
                        break


            self.transfer_rpl = self.check_file(argument)

        except OSError as e:
            log.error("exception .. {}".format(e))
        finally:
            self.transfer_path = False

        log.info("<- Transfer: {} - {}".format(argument, self.transfer_rpl))



    async def ftp_data_server(self, reader, writer):

        addr = writer.get_extra_info('peername')
        log.debug("+ Data Server <- client from {}".format(addr))
        log.debug("Data Start {}".format(self.data_start))

        if not self.transfer:
            self.transfer = "Start"
        log.debug("Data Transfer {}".format(self.transfer))


        while True:
            if self.transfer:

                if self.transfer is "LIST":
                    log.debug("s1. List Dir")
                    await self.send_list_data(writer)
                    self.transfer = False

                elif self.transfer is "SEND":
                    log.debug("s1. Send File")
                    await self.send_file_data(writer)
                    self.transfer = False

                elif self.transfer is "SAVE":
                    log.debug("s1. Save File")
                    await self.save_file_data(reader)
                    self.transfer = False

                elif self.transfer is "Start":
                    log.debug("s1. State Start")
                    #Time for wait Open Socker Activite if not active = Close connection
                    await asyncio.sleep_ms(500)
                    if self.transfer is "Start":
                        self.transfer = False


            # await asyncio.sleep_ms(300)
            if not self.transfer:
                log.debug("- Data Server <- client from {}".format(addr))
                log.debug("s2. Data Server = Close")
                await _aclose(writer)
                self.data_start = False

                break



    async def send_data(self, type):

        log.debug("SEND Type: {}".format(type))
        log.debug("SEND Transfer: {}".format(self.transfer))


        if type is "passive":
            self.data_start = True
            while self.data_start:
                #wait 100ms for next check start. Lite =100, Hard = 0
                await asyncio.sleep_ms(100)

        if type is "active":
            log.info("Active: connecting to -> %s %d" % (self.data_ip, self.data_port))
            reader, writer = await asyncio.open_connection(self.data_ip, self.data_port)

            if self.transfer is "LIST":
                log.debug("s1. List Dir")
                await self.send_list_data(writer)

            elif self.transfer is "SEND":
                log.debug("s1. Send File")
                await self.send_file_data(writer)

            elif self.transfer is "SAVE":
                log.debug("s1. Save File")
                await self.save_file_data(reader)

            await _aclose(writer)


        log.debug("s3. Send Data Done")
        return True


    def get_absolute_path(self, cwd, payload):
        # Just a few special cases "..", "." and ""
        # If payload start's with /, set cwd to /
        # and consider the remainder a relative path
        if payload.startswith('/'):
            cwd = "/"
        for token in payload.split("/"):
            if token == '..':
                if cwd != '/':
                    cwd = '/'.join(cwd.split('/')[:-1])
                    if cwd == '':
                        cwd = '/'
            elif token != '.' and token != '':
                if cwd == '/':
                    cwd += token
                else:
                    cwd = cwd + '/' + token
        return cwd

    def get_path(self, argument):

        cwd = self.cwd
        path = self.get_absolute_path(cwd, argument)
        log.debug("Get path is %s" % path)
        return path


    async def ftp_cmd_server(self, reader, writer):
        addr = writer.get_extra_info('peername')
        log.info("Client from {}".format(addr))
        await self.awrite(writer, "220 Welcome to micro FTP server\r\n")

        while True:
            log.debug("Wait - CMD")
            data = False
            try:
                data = await reader.readline()
            except Exception as err:
                log.error(err)
                pass

            log.debug("Read - CMD")

            if not data:
                log.debug("no data, break")
                await _aclose(writer)
                break
            else:
                log.debug("recv = %s" % data)
                cmd = None
                try:
                    data = data.decode("utf-8")
                    split_data = data.split(' ')
                    cmd = split_data[0].strip('\r\n')
                    argument = split_data[1].strip('\r\n') if len(split_data) > 1 else None
                    log.debug("cmd is %s, argument is %s" % (cmd, argument))
                except Exception as err:
                    log.error(err)
                    pass

                if hasattr(self, cmd):
                    func = getattr(self, cmd)
                    result = await func(writer, argument)

                    if not result:
                        log.debug("result = None")
                        await _aclose(writer)
                        break
                    log.debug("result = %d" % result)

                else:
                    await self.awrite(writer, "520 not implement.\r\n")


        # await writer.aclose()
        # log.info("Client from Stop {}".format(addr))


    async def USER(self, stream, argument):
        #331 next step password
        # await stream.awrite("331 User Ok.\r\n")

        await self.awrite(stream, "230 Logged in.\r\n")
        return True

    async def PASS(self, stream, argument):
        await self.awrite(stream, "230 Passwd Ok.\r\n")
        return True

    async def SYST(self, stream, argument):
        await self.awrite(stream, "215 UNIX Type: L8\r\n")
        return True

    async def NOOP(self, stream, argument):
        await self.awrite(stream, "200 OK\r\n")
        return True

    async def FEAT(self, stream, argument):
        await self.awrite(stream, "211 no-features\r\n")
        return True


    async def CDUP(self, stream, argument):
        argument = '..' if not argument else '..'
        log.debug("CDUP argument is %s" % argument)
        try:
            self.cwd = self.get_path(argument)
            await self.awrite(stream, "250 Okey.\r\n")
        except Exception as e:
            await self.awrite(stream, "550 {}.\r\n".format(e))
        return True

    async def CWD(self, stream, argument):
        log.debug("CWD argument is %s" % argument)
        try:
            self.cwd = self.get_path(argument)
            await self.awrite(stream, "250 Okey.\r\n")
        except Exception as e:
            await self.awrite(stream, "550 {}.\r\n".format(e))
        return True

    async def PWD(self, stream, argument):
        try:
            #self.cwd = uos.getcwd()
            await self.awrite(stream, '257 "{}".\r\n'.format(self.cwd))
        except Exception as e:
            await self.awrite(stream, '550 {}.\r\n'.format(e))
        return True

    async def TYPE(self, stream, argument):
        #Always use binary mode 8-bit
        await self.awrite(stream, "200 Binary mode.\r\n")
        return True

    async def MKD(self, stream, argument):

        try:
            uos.mkdir(self.get_path(argument))
            await self.awrite(stream, "257 Okey.\r\n")
        except OSError as e:
            if e.args[0] == uerrno.EEXIST:
                await self.awrite(stream, "257 Okey.\r\n")
            else:
                await self.awrite(stream, "550 {}.\r\n".format(e))
        return True

    async def RMD(self, stream, argument):
        try:
            uos.rmdir(self.get_path(argument))
            await self.awrite(stream, "257 Okey.\r\n")
        except Exception as e:
            await self.awrite(stream, "550 {}.\r\n".format(e))
        return True

    async def SIZE(self, stream, argument):
        try:
            size = uos.stat(self.get_path(argument))[6]
            await self.awrite(stream, '213 {}\r\n'.format(size))
        except Exception as e:
            await self.awrite(stream, '550 {}.\r\n'.format(e))
        return True


    async def RETR(self, stream, argument):

        await self.awrite(stream, "150 Opening data connection\r\n")

        self.transfer = "SEND"
        self.transfer_path = self.get_path(argument)
        await self.send_data(self.con_type)

        if self.transfer_rpl:
            await self.awrite(stream, self.transfer_rpl)
            self.transfer_rpl = False
        else:
            await self.awrite(stream, "550 File Load Error.\r\n")

        return True



    async def STOR(self, stream, argument):

        await self.awrite(stream, "150 Opening data connection\r\n")


        self.transfer = "SAVE"
        self.transfer_path = self.get_path(argument)
        await self.send_data(self.con_type)

        if self.transfer_rpl:
            await self.awrite(stream, self.transfer_rpl)
            self.transfer_rpl = False
        else:
            await self.awrite(stream, "550 File Save Error.\r\n")


        return True



    async def QUIT(self, stream, argument):
        await self.awrite(stream, "221 Bye!.\r\n")
        return False



    async def DELE(self, stream, argument):
        try:
            uos.remove(self.get_path(argument))
            await self.awrite(stream, "257 Okey.\r\n")
        except Exception as e:
            await self.awrite(stream, "550 {}.\r\n".format(e))
        return True



    async def PASV(self, stream, argument):

        # Send to client server adress
        if self.addr != "0.0.0.0":

            result = '227 Entering Passive Mode ({},{},{}).\r\n'.format(
                self.addr.replace('.', ','), self.dport >> 8, self.dport % 256)

            log.debug("PASV: {}".format(result))

            await self.awrite(stream, result)

            if not self._run_pasv:

                log.info("Start Passive Data Server to {} {}".format(self.addr, self.dport))
                loop = asyncio.get_event_loop()
                loop.create_task(asyncio.start_server(self.ftp_data_server, "0.0.0.0", self.dport))
                # loop.call_soon(asyncio.start_server(self.ftp_data_server, "0.0.0.0", self.dport))
                self.con_type = "passive"
                self._run_pasv = True


            return True

        else:
            await self.awrite(stream, "221 Bye!.\r\n")
            return False




    async def PORT(self, stream, argument):
        argument = argument.split(',')
        self.data_ip = '.'.join(argument[:4])
        self.data_port = (int(argument[4])<<8)+int(argument[5])
        self.data_addr = (self.data_ip, self.data_port)
        log.info("got the port {}".format(self.data_addr))
        await self.awrite(stream, "200 OK.\r\n")
        self.con_type = "active"
        return True



    async def LIST(self, stream, argument):

        await self.awrite(stream, "150 Here comes the directory listing.\r\n")
        self.transfer = "LIST"
        await self.send_data(self.con_type)
        await self.awrite(stream, "226 Directory send okey.\r\n")
        return True

    async def MDTM(self, stream, argument):

        #Dummy for File Modification Time.
        await self.awrite(stream, "213 {}.\r\n".format(argument))
        return True




