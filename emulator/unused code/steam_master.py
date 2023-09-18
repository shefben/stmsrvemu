# Define constants
import threading
import ctypes
import time
import struct
import socket

MAXHOSTNAMELEN = 256
MAX_CHALLENGES = 32
SERVER_TIMEOUT = 60 * 15
MIN_SV_TIMEOUT_INTERVAL = 60
MAX_SINFO = 2048
VALUE_LENGTH = 64

# Define data structures


class challenge_t:
    def __init__(self):
        self.adr = netadr_t()
        self.challenge = 0
        self.time = 0


class modsv_t:
    def __init__(self):
        self.next = None
        self.gamedir = ""
        self.ip_players = 0
        self.ip_servers = 0
        self.ip_bots = 0
        self.ip_bots_servers = 0
        self.lan_players = 0
        self.lan_servers = 0
        self.lan_bots = 0
        self.lan_bots_servers = 0
        self.proxy_servers = 0
        self.proxy_players = 0

class netadr_t:
    def __init__(self):
        self.sin_family = 0
        self.sin_port = 0
        self.sin_addr = ''



class string_criteria_t:
    def __init__(self):
        self.checksum = 0
        self.length = 0
        self.value = ""


class sv_t:
    def __init__(self):
        self.next = None
        self.address = netadr_t()
        self.isoldserver = 0
        self.islan = 0
        self.time = 0
        self.uniqueid = 0
        self.isproxy = 0
        self.isProxyTarget = 0
        self.proxyTarget = string_criteria_t()
        self.players = 0
        self.max = 0
        self.bots = 0
        self.gamedir = string_criteria_t()
        self.map = string_criteria_t()
        self.os = ""
        self.password = 0
        self.dedicated = 0
        self.secure = 0
        self.info = ""
        self.info_length = 0

    def criteria_hash(value, length):
        val = 0xFFFFFFFF
        for i in range(length):
            val ^= ord(value[i])
            for j in range(8):
                if val & 1:
                    val = (val >> 1) ^ 0xEDB88320
                else:
                    val >>= 1
        return val ^ 0xFFFFFFFF


    def set_criteria(c, value):
        c.value = value[:VALUE_LENGTH - 1].lower()
        c.length = len(c.value)
        c.checksum = criteria_hash(c.value, c.length)


    def va(fmt, *args):
        return fmt % args


    def check_parm(psz, ppszValue=None):
        sz = bytearray(128)
        # Input command line from user
        cmdline = ' '.join(
            ['"' + arg + '"' if ' ' in arg else arg for arg in raw_input().split()])

        pret = cmdline.find(psz)

        if pret != -1 and ppszValue:
            p1 = pret
            *ppszValue, = None

            while p1 < len(cmdline) and cmdline[p1] != ' ':
                p1 += 1

            if p1 < len(cmdline):
                p2 = p1 + 1

                for i in range(128):
                    if p2 >= len(cmdline) or cmdline[p2] == ' ':
                        break
                    sz[i] = cmdline[p2]
                    p2 += 1

                *ppszValue, = sz[:i + 1]

        return cmdline[pret:] if pret != -1 else None


    def net_string_to_sockaddr(s):
        saddrs = s.split(':')
        port = int(saddrs[-1])

        if len(saddrs) > 2:
            address = ':'.join(saddrs[:-1])
        else:
            address = saddrs[0]

        try:
            ip_address = socket.inet_aton(address)
        except socket.error:
            ip_address = socket.gethostbyname(address)

        return struct.pack("!HH4s", socket.AF_INET, port, ip_address)


    def string_to_adr(s):
        b1, b2, b3, b4, p = map(int, s.split('.'))
        a = struct.pack("!BBBBH", b1, b2, b3, b4, p)
        return a


    def adr_to_string(a):
        b1, b2, b3, b4, p = struct.unpack("!BBBBH", a)
        return "%i.%i.%i.%i:%i" % (b1, b2, b3, b4, p)


    def compare_adr(a, b):
        return a == b


    def compare_base_adr(a, b):
        return a[:4] == b[:4]


    def idprintf(buf, nLen):
        return ''.join(format(c, '02x') for c in buf)



    # Example usage:
    # You can now use these data structures and functions to perform similar operations as in the C/C++ code.


    class LARGE_INTEGER(ctypes.Structure):
        _fields_ = [
            ('LowPart', ctypes.c_uint32),
            ('HighPart', ctypes.c_int32)
        ]


    def sys_float_time():
        pfreq = 0
        lowshift = 0
        curtime = 0.0
        lastcurtime = 0.0
        sametimecount = 0

        if not pfreq:
            freq = LARGE_INTEGER()
            if ctypes.windll.kernel32.QueryPerformanceFrequency(ctypes.byref(freq)):
                pfreq = float(freq.LowPart) + float(freq.HighPart << 32)
                lowshift = 0
                while pfreq >= 10e6:
                    pfreq *= 0.1
                    lowshift += 1

        if pfreq:
            performance_count = LARGE_INTEGER()
            ctypes.windll.kernel32.QueryPerformanceCounter(
                ctypes.byref(performance_count))

            temp = ((performance_count.LowPart >> lowshift) | (
                performance_count.HighPart << (32 - lowshift)))

            if first:
                oldtime = temp
                first = False
            else:
                if temp <= oldtime and (oldtime - temp) < 0x10000000:
                    oldtime = temp
                else:
                    t2 = temp - oldtime
                    time_diff = float(t2) * (1.0 / pfreq)
                    oldtime = temp
                    curtime += time_diff

                    if curtime == lastcurtime:
                        sametimecount += 1
                        if sametimecount > 100000:
                            curtime += 1.0
                            sametimecount = 0
                    else:
                        sametimecount = 0

                    lastcurtime = curtime

        return curtime


class CHLMasterDlg:
    # Constants (assuming they match the original C++ code)
    A2A_ACK = 1
    M2A_MOTD = 2
    A2A_GETCHALLENGE = 3
    S2M_HEARTBEAT2 = 7
    A2M_GETACTIVEMODS = 9

    # Global variables (assuming they match the original C++ code)
    bannedips = None  # You should initialize this properly with banned IPs
    mods = [None] * 256  # You should initialize this properly with mod data


    def __init__(self, nMasterPort, bGenerateLogs, strLocalIPAddress, pParent=None):
        self.m_bShowTraffic = True
        self.m_bAllowOldProtocols = False

        self.logfile = None

        self.m_szHLVersion = "1.0.1.0"
        self.m_szCSVersion = "1.0.0.0"
        self.m_szTFCVersion = "1.0.0.0"
        self.m_szDMCVersion = "1.0.0.0"
        self.m_szOpForVersion = "1.0.0.0"
        self.m_szRicochetVersion = "1.0.0.0"
        self.m_szDODVersion = "1.0.0.0"

        self.m_nLanServerCount = 0
        self.m_nLanUsers = 0
        self.m_nServerCount = 0
        self.m_nUsers = 0

        self.m_bShowPackets = False

        self.net_hostport = nMasterPort
        self.m_bGenerateLogs = bGenerateLogs
        self.m_strLocalIPAddress = strLocalIPAddress

        # Initialize other variables...

    def __del__(self):
        self.FreeServers()
        self.FreeGameServers()
        self.FreeMods()
        if self.net_socket:
            self.net_socket.close()
        if self.logfile:
            self.logfile.close()
            self.logfile = None
            
    def FreeServers(self):
        self.free_list(authservers)
        self.free_list(titanservers)
        self.free_list(masterservers)
        self.free_list(bannedips)

    def free_list(self, sv_list):
        sv = sv_list
        while sv:
            next_sv = sv.next
            del sv
            sv = next_sv

    def Nibble(self, c):
        if '0' <= c <= '9':
            return ord(c) - ord('0')
        elif 'A' <= c <= 'F':
            return ord(c) - ord('A') + 0x0A
        elif 'a' <= c <= 'f':
            return ord(c) - ord('a') + 0x0A
        return 0x00

    def HexConvert(self, pszInput, nInputLength, pOutput):
        p = pOutput
        for i in range(0, nInputLength, 2):
            p_in = pszInput[i:i + 2]
            val = (self.Nibble(p_in[0]) << 4) | self.Nibble(p_in[1])
            p.append(val)

    def MSG_ReadData(self, nLength, nBuffer):
        start = packet_data[msg_readcount:]
        # Read error
        if msg_readcount + nLength > packet_length:
            return False

        nBuffer.extend(start[:nLength])
        msg_readcount += nLength
        return True

    def NET_GetLocalAddress(self):
        if m_strLocalIPAddress:
            success = NET_StringToSockaddr(m_strLocalIPAddress, net_local_adr)
            if not success:
                Sys_Error("Cannot parse ip address on command line")
        else:
            buff = socket.gethostname()
            if len(buff) >= MAXHOSTNAMELEN:
                buff = buff[:MAXHOSTNAMELEN]
            h = socket.gethostbyname(buff)
            if len(h) != 4:
                Sys_Error("gethostbyname failed")
            net_local_adr.sin_addr = h

        namelen = socket.sizeof(address)
        try:
            _, address = socket.getsockname(net_socket)
        except socket.error as e:
            Sys_Error("NET_Init: getsockname:", e.strerror)

        net_local_adr.sin_port = address[1]

        UTIL_Printf("IP address %s\r\n", AdrToString(net_local_adr))


    def CheckServerTimeouts(self):
        current = Sys_FloatTime()

        # Don't do this too often.
        if (current - self.tLastTimeOut) < MIN_SV_TIMEOUT_INTERVAL:
            return

        self.tLastTimeOut = current

        for h in range(SERVER_HASH_SIZE):
            svp = self.servers[h]
            while svp:
                sv = svp.contents
                if (current - sv.time) < SERVER_TIMEOUT:
                    svp = byref(sv.next)
                    continue
                svp.contents = sv.next
                free(sv)

    def Nack(self, comment, *args):
        string = comment % args
        reply = "{}\r\n{}".format(chr(A2A_NACK), string)
        Sys_SendPacket(byref(self.packet_from), reply.encode(), len(reply) + 1)

    def RejectConnection(self, adr, pszMessage):
        reply = "{}{}{}{}{}\n{}".format(chr(255), chr(255), chr(
            255), chr(255), chr(A2C_PRINT), pszMessage)
        Sys_SendPacket(byref(adr), reply.encode(), len(pszMessage) + 7)

    def RequestRestart(self, adr):
        reply = "{}{}{}{}{}\r\n".format(chr(255), chr(
            255), chr(255), chr(255), M2S_REQUESTRESTART)
        Sys_SendPacket(byref(adr), reply.encode(), len(reply) + 1)

    def Packet_GetChallenge(self):
        oldest = 0
        oldestTime = 0x7fffffff

        msg_readcount = 1

        bucket = self.packet_from.sin_addr.S_un.S_un_b.s_b4

        # see if we already have a challenge for this ip
        for i in range(MAX_CHALLENGES):
            if CompareBaseAdr(self.packet_from, self.challenges[bucket][i].adr.contents):
                break
            if self.challenges[bucket][i].time < oldestTime:
                oldestTime = self.challenges[bucket][i].time
                oldest = i

        if i == MAX_CHALLENGES:
            # overwrite the oldest
            self.challenges[bucket][oldest].challenge = (
                rand() << 16 | rand()) & ~(1 << 31)
            self.challenges[bucket][oldest].adr = self.packet_from
            self.challenges[bucket][oldest].time = self.m_curtime
            i = oldest
        # Issue a new Challenge #
        elif (self.m_curtime - self.challenges[bucket][i].time) > HB_TIMEOUT:
            self.challenges[bucket][i].challenge = (
                rand() << 16 | rand()) & ~(1 << 31)
            self.challenges[bucket][i].adr = self.packet_from
            self.challenges[bucket][i].time = self.m_curtime

        reply = "{}{}{}{}{}\n".format(chr(255), chr(
            255), chr(255), chr(255), M2A_CHALLENGE)
        n = 6
        reply += struct.pack("<I", self.challenges[bucket][i].challenge)
        n += 4

        Sys_SendPacket(byref(self.packet_from), reply.encode(), n)

    def ListMods(self):
        p = None
        i = 1

        UTIL_Printf("MODS ---------\r\n")

        for h in range(MOD_HASH_SIZE):
            p = self.mods[h]
            while p:
                UTIL_Printf("{} {}\r\n".format(i, p.gamedir))
                UTIL_Printf("   internet  {:7} sv {:7} pl {:7} b {:7} bs\r\n".format(
                    p.ip_servers, p.ip_players, p.ip_bots, p.ip_bots_servers))
                UTIL_Printf("   lan       {:7} sv {:7} pl {:7} b {:7} bs\r\n".format(
                    p.lan_servers, p.lan_players, p.lan_bots, p.lan_bots_servers))
                UTIL_Printf("   proxy     {:7} sv {:7} pl\r\n".format(
                    p.proxy_servers, p.proxy_players))
                p = p.next
                i += 1

    def FreeMods(self):
        for h in range(MOD_HASH_SIZE):
            p = self.mods[h]
            while p:
                n = p.next
                free(p)
                p = n
            self.mods[h] = None

    def FindMod(self, pgamedir):
        if not pgamedir or not pgamedir[0]:
            return None

        h = self.HashMod(pgamedir)
        p = self.mods[h]
        while p:
            if pgamedir.lower() == p.gamedir.lower():
                return p
            p = p.next

        return None

    def HashMod(self, pgamedir):
        # compute a hash value
        c = 0
        szLowerCaseDir = pgamedir.lower()

        for p in szLowerCaseDir:
            c += (ord(p) << 1)
            c ^= ord(p)
        c %= MOD_HASH_SIZE
        return c

    def AdjustCounts(self):
        s = None
        sv = None

        # First clear current mod counts;
        self.FreeMods()

        for sh in range(SERVER_HASH_SIZE):
            # Now go through servers and find all of the mods.
            sv = self.servers[sh]
            while sv:
                s = self.FindMod(sv.gamedir.value)
                if not s:
                    # Add it
                    h = self.HashMod(sv.gamedir.value)

                    s = modsv_t()
                    s.gamedir = sv.gamedir.value

                    s.next = self.mods[h]
                    self.mods[h] = s

                if sv.islan:
                    s.lan_servers += 1
                    s.lan_players += (sv.players - sv.bots)
                    s.lan_bots += sv.bots
                    if sv.bots:
                        s.lan_bots_servers += 1
                elif sv.isproxy:
                    s.proxy_servers += 1
                    s.proxy_players += (sv.players - sv.bots)
                else:
                    s.ip_servers += 1
                    s.ip_players += (sv.players - sv.bots)
                    s.ip_bots += sv.bots
                    if sv.bots:
                        s.ip_bots_servers += 1

                sv = sv.next

    def Packet_Heartbeat(self):
        szSName = [None] * 2048

        sv = None
        num = 0
        seq = 0
        nChallengeValue = 0
        gamedir = None
        info = None
        bNewServer = False
        nprotocol = 0

        nChallengeValue = int(MSG_ReadString())
        seq = int(MSG_ReadString())
        num = int(MSG_ReadString())
        nprotocol = int(MSG_ReadString())  # Throw away
        gamedir = MSG_ReadString()
        info = MSG_ReadString()

        if not self.m_bAllowOldProtocols and nprotocol != CURRENT_PROTOCOL:
            self.RejectConnection(byref(self.packet_from),
                                "Outdated protocol.")
            return

        challenge_result = self.CheckChallenge(
            nChallengeValue, byref(self.packet_from))

        if challenge_result == 1:
            self.RejectConnection(byref(self.packet_from), "Bad challenge.")
            return
        elif challenge_result == 2:
            self.RejectConnection(byref(self.packet_from),
                                "No challenge for your address.")
            return

        # Find the server
        sv = self.FindServerByAddress(byref(self.packet_from))

        if not sv:
            h = 0
            sv = sv_t()
            sv.address = self.packet_from

            # Assign the unique id.
            sv.uniqueid = self.m_nUniqueID
            self.m_nUniqueID += 1

            h = self.HashServer(byref(self.packet_from))

            sv.next = self.servers[h]
            self.servers[h] = sv
            bNewServer = True  # Try and send it the master's public key

        sv.time = self.m_curtime

        if gamedir and len(gamedir) > 0 and len(gamedir) <= 254:
            self.SetCriteria(sv.gamedir, gamedir)
        else:
            self.SetCriteria(sv.gamedir, "")

        sv.players = num

        if len(info) + 1 < len(sv.info):
            sv.info = info
        else:
            sv.info = ""

        sv.info_length = len(sv.info) + 1

        self.Peer_Heartbeat(sv)

    def CheckChallenge(self, challenge, adr):
        bucket = adr.sin_addr.S_un.S_un_b.s_b4

        for i in range(MAX_CHALLENGES):
            if CompareBaseAdr(adr, self.challenges[bucket][i].adr.contents):
                if challenge == self.challenges[bucket][i].challenge:
                    return 0
                else:
                    return 1
                break

        if i >= MAX_CHALLENGES:
            return 2

        return 0

    def Packet_Heartbeat2(self):
        szSName = [None] * 2048

        sv = None
        num = 0
        maxplayers = 0
        bots = 0

        challenge = 0
        gamedir = [None] * 64
        map = [None] * 64
        os = [None] * 2
        dedicated = 0
        password = 0
        secure = 0
        islan = 0
        proxyaddress = [None] * 128
        isproxytarget = 0
        isproxy = 0
        version = [None] * 32

        info = [None] * MAX_SINFO

        bNewServer = False
        protocol = 0

        info = MSG_ReadString()

        if not info or not info[0]:
            self.RejectConnection(byref(self.packet_from),
                                "Outdated protocol.")
            return

        protocol = int(Info_ValueForKey(info, "protocol"))
        challenge = int(Info_ValueForKey(info, "challenge"))
        num = int(Info_ValueForKey(info, "players"))
        maxplayers = int(Info_ValueForKey(info, "max"))
        bots = int(Info_ValueForKey(info, "bots"))
        dedicated = int(Info_ValueForKey(info, "dedicated"))
        password = int(Info_ValueForKey(info, "password"))
        secure = int(Info_ValueForKey(info, "secure"))
        gamedir = Info_ValueForKey(info, "gamedir")[:63]
        map = Info_ValueForKey(info, "map")[:63]
        os = Info_ValueForKey(info, "os")[:1]
        islan = int(Info_ValueForKey(info, "lan"))
        isproxy = int(Info_ValueForKey(info, "proxy")) == 1
        isproxytarget = int(Info_ValueForKey(info, "proxytarget")) == 1
        proxyaddress = Info_ValueForKey(info, "proxyaddress")[:127]
        version = Info_ValueForKey(info, "version")[:31]

        proxyaddress = proxyaddress[:127]
        gamedir = gamedir[:63]
        map = map[:63]
        os = os[:1]
        version = version[:31]

        gamedir = gamedir.lower()
        map = map.lower()
        os = os.lower()

        # protocol != 1 for Sony stand-alone game support...1.1.1.0 engine license (EricS)
        if not self.m_bAllowOldProtocols and (protocol != CURRENT_PROTOCOL) and (protocol != 1):
            self.RejectConnection(byref(self.packet_from),
                                "Outdated protocol.")

            if not islan:
                return

        # everyone in the current release sends up a version, so we know they're outdated if we don't get one.
        if not version:
            self.RejectConnection(byref(self.packet_from),
                                "Outdated Version. Please update your server.")
            return

        # We need to check the version of the server based on the mod it's running.
        reject = 0

        # If they didn't send a version we already know they're out of date.
        if not version:
            reject = 1
        else:
            # Steam appends its own version to the Mod version...we need to remove it.
            if "/" in version:
                version = version.split("/")[0]

            # Check the version against the Mod version
            if gamedir == "valve":
                if version != self.m_szHLVersion:
                    reject = 1
            elif gamedir == "cstrike":
                if version != self.m_szCSVersion:
                    reject = 1
            elif gamedir == "tfc":
                if version != self.m_szTFCVersion:
                    reject = 1
            elif gamedir == "dmc":
                if version != self.m_szDMCVersion:
                    reject = 1
            elif gamedir == "opfor":
                if version != self.m_szOpForVersion:
                    reject = 1
            elif gamedir == "ricochet":
                if version != self.m_szRicochetVersion:
                    reject = 1
            elif gamedir == "dod":
                if version != self.m_szDODVersion:
                    reject = 1

        # are they different?
        if reject:
            self.RequestRestart(byref(self.packet_from))
            return

        challenge_result = self.CheckChallenge(
            challenge, byref(self.packet_from))

        if challenge_result == 1:
            self.RejectConnection(byref(self.packet_from), "Bad challenge.")
            return
        elif challenge_result == 2:
            self.RejectConnection(byref(self.packet_from),
                                "No challenge for your address.")
            return

        sv = self.FindServerByAddress(byref(self.packet_from))
        if not sv:
            h = self.HashServer(byref(self.packet_from))

            sv = sv_t()
            sv.address = self.packet_from

            # Assign the unique id.
            sv.uniqueid = self.m_nUniqueID
            self.m_nUniqueID += 1

            sv.next = self.servers[h]
            self.servers[h] = sv
            bNewServer = True  # Try and send it the master's public key

        sv.time = self.m_curtime

        self.SetCriteria(sv.gamedir, gamedir)
        self.SetCriteria(sv.map, map)
        sv.os = os

        sv.islan = islan
        sv.players = num
        sv.max = maxplayers
        sv.bots = bots
        sv.password = password
        sv.dedicated = dedicated
        sv.secure = secure
        sv.info = info
        sv.info_length = len(sv.info) + 1
        sv.isproxy = isproxy
        sv.isProxyTarget = isproxytarget
        if isproxytarget:
            self.SetCriteria(sv.proxyTarget, proxyaddress)

        self.Peer_Heartbeat2(sv)

    def Packet_Shutdown(self):
        sv = None
        svp = None

        h = self.HashServer(byref(self.packet_from))

        svp = byref(self.servers[h])
        while True:
            sv = svp.contents
            if not sv:
                break

            if CompareAdr(self.packet_from, sv.address.contents):
                svp.contents = sv.next
                self.Peer_Shutdown(sv)

                free(sv)
                return
            else:
                svp = byref(sv.next)

    def Packet_GetServers(self):
        sv = None
        i = 0
        h = 0
        nomore = False

        reply = [255, 255, 255, 255, M2A_SERVERS]
        i = 6

        for h in range(SERVER_HASH_SIZE):
            sv = self.servers[h]
            while sv:
                if sv.islan or sv.isproxy:
                    sv = sv.next
                    continue

                if i + 6 > sizeof(reply):
                    nomore = True
                    break

                reply.extend(sv.address.sin_addr)
                reply.extend(sv.address.sin_port.to_bytes(2, 'little'))
                i += 6
                sv = sv.next

            if nomore:
                break

        Sys_SendPacket(byref(self.packet_from), reply, i)

    def Packet_GetBatch(self):
        truenextid = 0

        msg_readcount = 1

        # Read batch Start point
        truenextid = int(MSG_ReadLong())

        self.Packet_GetBatch_Responder(truenextid, None)

    def Packet_RequestsBatch(self):
        return

    def SizeMod(self, p):
        c = 0

        if not p:
            return 0

        c += len(p.gamedir) + 2

        c += len("ip") + 2
        c += len(str(p.ip_players)) + 2

        c += len("is") + 2
        c += len(str(p.ip_servers)) + 2

        c += len("lp") + 2
        c += len(str(p.lan_players)) + 2

        c += len("ls") + 2
        c += len(str(p.lan_servers)) + 2

        c += len("pp") + 2
        c += len(str(p.proxy_players)) + 2

        c += len("ps") + 2
        c += len(str(p.proxy_servers)) + 2

        return c

    def Packet_Printf(self, curpos, fmt, *args):
        string = fmt % args
        len_string = len(string) + 1

        reply[curpos:curpos + len_string] = string.encode()
        curpos += len_string

    def Packet_GetModBatch2(self):
        pMod = None
        i = 0
        pszNextMod = None
        h = 0

        msg_readcount = 3

        # Read batch Start point
        pszNextMod = MSG_ReadString()
        if not pszNextMod or not pszNextMod[0]:  # First batch
            # Bad
            UTIL_VPrintf("Packet_GetModBatch2:  Malformed from %s\r\n",
                        AdrToString(self.packet_from))
            return

        if not stricmp(pszNextMod, "start-of-list"):
            h = 0
            pMod = self.mods[h]
        else:
            h = HashMod(pszNextMod)
            pMod = FindMod(pszNextMod)
            if pMod:
                pMod = pMod.next
            else:
                # Start sending from start of this list. Sigh since the requested mod is now missing ( last server quit during query? )
                pMod = self.mods[h]

        reply = bytearray([255, 255, 255, 255, M2A_ACTIVEMODS2])
        i += 6

        while h < MOD_HASH_SIZE:
            while pMod:
                if i + self.SizeMod(pMod) > (sizeof(reply) - 128):
                    goto finish

                # Don't report about bogus mods
                if len(pMod.gamedir) <= 0:
                    continue

                self.Packet_Printf(i, "gamedir")
                self.Packet_Printf(i, pMod.gamedir)

                self.Packet_Printf(i, "is")
                self.Packet_Printf(i, va("%i", pMod.ip_servers))

                self.Packet_Printf(i, "ib")
                self.Packet_Printf(i, va("%i", pMod.ip_bots))

                self.Packet_Printf(i, "ibs")
                self.Packet_Printf(i, va("%i", pMod.ip_bots_servers))

                self.Packet_Printf(i, "ip")
                self.Packet_Printf(i, va("%i", pMod.ip_players))

                self.Packet_Printf(i, "ls")
                self.Packet_Printf(i, va("%i", pMod.lan_servers))

                self.Packet_Printf(i, "lp")
                self.Packet_Printf(i, va("%i", pMod.lan_players))

                self.Packet_Printf(i, "lb")
                self.Packet_Printf(i, va("%i", pMod.lan_bots))

                self.Packet_Printf(i, "lbs")
                self.Packet_Printf(i, va("%i", pMod.lan_bots_servers))

                self.Packet_Printf(i, "ps")
                self.Packet_Printf(i, va("%i", pMod.proxy_servers))

                self.Packet_Printf(i, "pp")
                self.Packet_Printf(i, va("%i", pMod.proxy_players))

                self.Packet_Printf(i, "end")
                self.Packet_Printf(i, "end")

                pMod = pMod.next

            h += 1
            pMod = self.mods[h]

        finish:

            # Now write the final one we got to, if any.
        if not pMod:  # Still more in list, had to abort early
            pszEnd = "end-of-list"
            reply[i:i + len(pszEnd) + 1] = pszEnd.encode()
            i += len(pszEnd) + 1
        else:
            pszEnd = "more-in-list"
            reply[i:i + len(pszEnd) + 1] = pszEnd.encode()
            i += len(pszEnd) + 1

        Sys_SendPacket(self.packet_from, reply, i)

    def Packet_GetModBatch3(self):
        pMod = None
        i = 0
        pszNextMod = None
        h = 0

        msg_readcount = 3

        # Read batch Start point
        pszNextMod = MSG_ReadString()
        if not pszNextMod or not pszNextMod[0]:  # First batch
            # Bad
            UTIL_VPrintf("Packet_GetModBatch3:  Malformed from %s\r\n",
                        AdrToString(self.packet_from))
            return

        if not stricmp(pszNextMod, "start-of-list"):
            h = 0
            pMod = self.mods[h]
        else:
            h = HashMod(pszNextMod)
            pMod = FindMod(pszNextMod)
            if pMod:
                pMod = pMod.next
            else:
                # Start sending from start of this list. Sigh since the requested mod is now missing ( last server quit during query? )
                pMod = self.mods[h]

        reply = bytearray([255, 255, 255, 255, M2A_ACTIVEMODS3])
        i += 6

        while h < MOD_HASH_SIZE:
            while pMod:
                if i + self.SizeMod(pMod) > (sizeof(reply) - 128):
                    goto finish

                # Don't report about bogus mods
                if len(pMod.gamedir) <= 0:
                    continue

                self.Packet_Printf(i, "gamedir")
                self.Packet_Printf(i, pMod.gamedir)

                self.Packet_Printf(i, "is")
                self.Packet_Printf(i, va("%i", pMod.ip_servers))

                self.Packet_Printf(i, "ib")
                self.Packet_Printf(i, va("%i", pMod.ip_bots))

                self.Packet_Printf(i, "ibs")
                self.Packet_Printf(i, va("%i", pMod.ip_bots_servers))

                self.Packet_Printf(i, "ip")
                self.Packet_Printf(i, va("%i", pMod.ip_players))

                self.Packet_Printf(i, "ls")
                self.Packet_Printf(i, va("%i", pMod.lan_servers))

                self.Packet_Printf(i, "lp")
                self.Packet_Printf(i, va("%i", pMod.lan_players))

                self.Packet_Printf(i, "lb")
                self.Packet_Printf(i, va("%i", pMod.lan_bots))

                self.Packet_Printf(i, "lbs")
                self.Packet_Printf(i, va("%i", pMod.lan_bots_servers))

                self.Packet_Printf(i, "ps")
                self.Packet_Printf(i, va("%i", pMod.proxy_servers))

                self.Packet_Printf(i, "pp")
                self.Packet_Printf(i, va("%i", pMod.proxy_players))

                self.Packet_Printf(i, "end")
                self.Packet_Printf(i, "end")

                pMod = pMod.next

            h += 1
            pMod = self.mods[h]

        finish:

            # Now write the final one we got to, if any.
        if not pMod:  # Still more in list, had to abort early
            pszEnd = "end-of-list"
            reply[i:i + len(pszEnd) + 1] = pszEnd.encode()
            i += len(pszEnd) + 1
        else:
            pszEnd = "more-in-list"
            reply[i:i + len(pszEnd) + 1] = pszEnd.encode()
            i += len

    def Packet_Ping(self):
        reply = bytearray([255, 255, 255, 255, A2A_ACK])
        Sys_SendPacket(self.packet_from, reply, len(reply) + 1)

    def Packet_Motd(self):
        strMOTD = self.m_hEditMOTD.GetWindowText()
        reply = bytearray([255, 255, 255, 255, M2A_MOTD]) + strMOTD.encode()
        Sys_SendPacket(self.packet_from, reply, len(reply) + 1)

    def PacketFilter(self):
        banned = self.bannedips
        while banned:
            if CompareBaseAdr(banned.address, self.packet_from):
                return False
            banned = banned.next
        return True

    def PacketCommand(self):
        szChannel = ""

        if not self.PacketFilter():
            return

        if self.m_bShowPackets:
            UTIL_VPrintf("%s\r\n", self.packet_data)

        msg_readcount = 2  # skip command and \r\n

        if packet_length > 1500:
            UTIL_VPrintf("Bad packet size: %i\r\n", packet_length)
            return

        # Check for WON Monitoring tool status request.
        if packet_length == 8:
            if packet_data[0] == 3 and packet_data[1] == 1 and packet_data[2] == 5:
                self.Packet_WONMonitor()
                return

        command = packet_data[0]
        if command == S2M_HEARTBEAT2:
            self.Packet_Heartbeat2()
        elif command == S2M_SHUTDOWN:
            self.Packet_Shutdown()
        elif command == A2M_GET_SERVERS:
            self.Packet_GetServers()
        elif command == A2M_GET_SERVERS_BATCH:
            self.Packet_GetBatch()
        elif command == A2M_GET_SERVERS_BATCH2:
            self.Packet_GetBatch2()
        elif command == A2M_GETMASTERSERVERS:
            self.Packet_GetMasterServers()
        elif command == A2A_PING:
            self.Packet_Ping()
        elif command == A2M_GET_MOTD:
            self.Packet_Motd()
        elif command == A2A_GETCHALLENGE:
            self.Packet_GetChallenge()
        elif command == A2A_NACK:
            pass
        elif command == A2M_GETACTIVEMODS:
            self.Packet_GetModBatch()
        elif command == A2M_GETACTIVEMODS2:
            self.Packet_GetModBatch2()
        elif command == A2M_GETACTIVEMODS3:
            self.Packet_GetModBatch3()
        elif command == M2M_MSG:
            self.Packet_GetPeerMessage()
        else:
            """
            if not strnicmp(packet_data[0], "users", strlen("users")):
                self.Packet_RequestsBatch()
            else:
            """
            UTIL_VPrintf("Bad PacketCommand from %s\r\n",
                        AdrToString(self.packet_from))


    def handle_packet(self, data, address):
        # Set the packet data and address before processing
        self.packet_data = data
        self.packet_from = address

        # Process the packet command
        self.PacketCommand()

    def udp_server_thread(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # You should replace 'your_ip_address' and 'your_port_number' with the actual IP and port you want to bind to
        udp_socket.bind(('your_ip_address', your_port_number))

        print("UDP server listening on {}:{}".format(
            'your_ip_address', your_port_number))

        while True:
            data, address = udp_socket.recvfrom(4096)
            threading.Thread(target=self.handle_packet,
                            args=(data, address)).start()

    def start(self):
        # Start the UDP server in a separate thread
        threading.Thread(target=self.udp_server_thread).start()

    def FreeServers(self):
        self.free_list(authservers)
        self.free_list(titanservers)
        self.free_list(masterservers)
        self.free_list(bannedips)

    def free_list(self, sv_list):
        sv = sv_list
        while sv:
            next_sv = sv.next
            del sv
            sv = next_sv

    def Nibble(self, c):
        if '0' <= c <= '9':
            return ord(c) - ord('0')
        elif 'A' <= c <= 'F':
            return ord(c) - ord('A') + 0x0A
        elif 'a' <= c <= 'f':
            return ord(c) - ord('a') + 0x0A
        return 0x00

    def HexConvert(self, pszInput, nInputLength, pOutput):
        p = pOutput
        for i in range(0, nInputLength, 2):
            p_in = pszInput[i:i + 2]
            val = (self.Nibble(p_in[0]) << 4) | self.Nibble(p_in[1])
            p.append(val)

    def MSG_ReadData(self, nLength, nBuffer):
        global msg_readcount, packet_length, packet_data
        start = packet_data[msg_readcount:msg_readcount + nLength]
        # Read error
        if msg_readcount + nLength > packet_length:
            return False

        nBuffer.extend(start)
        msg_readcount += nLength
        return True

    def NET_GetLocalAddress(self):
        global m_strLocalIPAddress, net_local_adr, net_socket
        if m_strLocalIPAddress:
            success = NET_StringToSockaddr(m_strLocalIPAddress, net_local_adr)
            if not success:
                Sys_Error("Cannot parse ip address on command line")
        else:
            buff = socket.gethostname()
            if len(buff) >= MAXHOSTNAMELEN:
                buff = buff[:MAXHOSTNAMELEN]
            h = socket.gethostbyname(buff)
            if len(h) != 4:
                Sys_Error("gethostbyname failed")
            net_local_adr.sin_addr = h

        namelen = socket.sizeof(net_local_adr)
        try:
            _, address = net_socket.getsockname()
        except socket.error as e:
            Sys_Error("NET_Init: getsockname:", e.strerror)

        net_local_adr.sin_port = address[1]

        UTIL_Printf("IP address %s\r\n", AdrToString(net_local_adr))

    def UTIL_VPrintf(self, msg, *args):
        global logfile
        szText = None
        szOrig = None
        szTime = None
        szDate = None

        szOrig = msg % args
        szTime = time.strftime('%H:%M:%S')
        szDate = time.strftime('%Y-%m-%d')
        szText = f"{szDate}/{szTime}:  {szOrig}"

        # Add in the date and time
        if logfile:
            logfile.write(szText)
        self.UTIL_Printf(szText)

    def UTIL_Printf(self, msg, *args):


    def Sys_SendPacket(self, to, data, len):
        try:
            ret = net_socket.sendto(data[:len], 0, to)
            if ret == -1:
                errno_val = errno.WSAGetLastError()
                # UTIL_VPrintf(f"ERROR: Sys_SendPacket: ({errno_val}) {strerror(errno_val)}\r\n")
        except socket.error as e:
            errno_val = e.errno
            # UTIL_VPrintf(f"ERROR: Sys_SendPacket: ({errno_val}) {e.strerror}\r\n")

    def MSG_ReadString(self):
        global msg_readcount, packet_length, packet_data
        start = packet_data[msg_readcount:]
        bMore = False

        for i in range(msg_readcount, packet_length):
            if packet_data[i] in (b'\r', b'\n', b'\0'):
                msg_readcount = i + 1
                break
        else:
            bMore = True

        packet_data[msg_readcount - 1] = b'\0'
        msg_readcount += 1

        # skip any \r\n
        if bMore:
            while msg_readcount < packet_length and packet_data[msg_readcount] in (b'\r', b'\n'):
                msg_readcount += 1

        return start

    def MSG_ReadByte(self):
        global msg_readcount, packet_length, packet_data
        if msg_readcount >= packet_length:
            self.UTIL_Printf("Overflow reading byte\n")
            return -1

        c = packet_data[msg_readcount]
        msg_readcount += 1
        return c

    def MSG_ReadShort(self):
        global msg_readcount, packet_length, packet_data
        if msg_readcount + 2 > packet_length:
            self.UTIL_Printf("Overflow reading short\n")
            return -1

        c = packet_data[msg_readcount:msg_readcount + 2]
        msg_readcount += 2
        return int.from_bytes(c, 'big')

    def MSG_ReadLong(self):
        global msg_readcount, packet_length, packet_data
        if



if __name__ == "__main__":
    master_server = CHLMasterDlg()
    master_server.start()
