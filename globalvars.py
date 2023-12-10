
import ipaddress

from config import get_config


config = get_config()


local_ver = "0.73.RC4.4"
emu_ver = "0"
update_exception1 = ""
update_exception2 = ""
clear_config = False
converting = "0"
checksum_temp_file = 0
#servernet = "0."

# NOTE: Ben's added vars
cs_region = "US"
cellid = 1

aio_server = False
db_type = ""
peer_password = ""
dir_ismaster = "false"
cs_applist = []
server_ip = ""
server_ip_b = b""
public_ip = ""
public_ip_b = b""
hide_convert_prints = False

def startcser_sessionidtracker():
    from utilities import sessionid_manager
    return sessionid_manager.SessionIDManager()

session_id_manager = startcser_sessionidtracker()  #used by cser and harvest server to prevent fake report uploads

hl1serverlist = list(range(10000))
hl1challengenum = 0
hl2serverlist = list(range(10000))
hl2challengenum = 0
rdkfserverlist = list(range(10000))
rdkfchallengenum = 0
tracker = 0
tgt_version = "2"
steam1_blob_sent = 0
record_ver = 0
steam_ver = 0
steamui_ver = 0
compiling_cdr = False
server_net = ipaddress.IPv4Network(config["server_ip"] + '/' + config["server_sm"], strict=False)

#firstblob_eval = database.ccdb.load_ccdb()



if steamui_ver < 87 :
    http_port_neuter = ""
elif config["http_port"] == "0":
    http_port_neuter = ""
else :
    http_port_neuter = ":" + config["http_port"]


if not config["http_name"] == "" :
    octal_ip = config["http_name"]
elif not config["public_ip"] == "0.0.0.0" :
    octal_ip = config["public_ip"]
else :
    octal_ip = config["http_ip"]


ip_addresses = (
    b"65.122.178.71",
    b"67.132.200.140",
    b"68.142.64.162",
    b"68.142.64.163",
    b"68.142.64.164",
    b"68.142.64.165",
    b"68.142.64.166",
    b"69.28.140.245",
    b"69.28.140.246",
    b"69.28.140.247",
    b"69.28.148.250",
    b"69.28.151.178",
    b"69.28.152.198",
    b"69.28.153.82",
    b"69.28.156.250",
    b"69.28.191.84",
    b"68.142.64.162",
    b"68.142.64.163",
    b"68.142.64.164",
    b"68.142.64.165",
    b"68.142.64.166",
    b"68.142.72.250",
    b"68.142.88.34",
    b"68.142.91.34",
    b"68.142.91.35",
    b"69.28.145.170",
    b"69.28.145.171",
    b"69.28.151.178",
    b"69.28.153.82",
    b"72.165.61.141",
    b"72.165.61.142",
    b"72.165.61.143",
    b"72.165.61.161",
    b"72.165.61.162",
    b"72.165.61.185",
    b"72.165.61.186",
    b"72.165.61.187",
    b"72.165.61.188",
    b"72.165.61.189",
    b"72.165.61.190",
    b"86.148.72.250",
    b"87.248.196.117",
    b"87.248.196.194",
    b"87.248.196.195",
    b"87.248.196.196",
    b"87.248.196.197",
    b"87.248.196.198",
    b"87.248.196.199",
    b"87.248.196.200",
    # "127.0.0.1",
    # "172.16.3.6",
    # "172.16.3.10",
    # "172.16.3.11",
    # "172.16.3.12",
    # "172.16.3.13",
    # "172.16.3.14",
    # "172.16.3.15",
    # "172.16.3.16",
    # "172.16.3.17",
    # "172.16.3.18",
    # "172.16.3.19",
    # "172.16.3.23",
    # "172.16.3.24",
    # "172.16.3.26",
    # "172.16.3.27",
    # "172.16.3.28",
    # "172.16.3.29",
    # "172.16.3.30",
    # "172.16.3.31",
    # "172.16.3.32",
    # "172.16.3.34",
    # "172.16.3.39",
    # "172.16.3.72",
    b"193.34.50.6",
    b"194.124.229.14",
    b"207.173.176.210",
    b"207.173.176.215",
    b"207.173.176.216",
    b"207.173.177.11",
    b"207.173.177.12",
    b"207.173.178.127",
    b"207.173.178.178",
    b"207.173.178.194",
    b"207.173.178.196",
    b"207.173.178.198",
    b"207.173.178.214",
    b"207.173.179.14",
    b"207.173.179.87",
    b"207.173.179.151",
    b"207.173.179.179",
    b"208.111.133.84",
    b"208.111.133.85",
    b"208.111.158.52",
    b"208.111.158.53",
    b"208.111.171.82",
    b"208.111.171.83",
    b"213.202.254.131",
    b"217.64.127.2",
    b"888.888.888.888",
    b"888.888.888.889",
    b"888.888.888.890",
    b"888.888.888.891",)

extraips = (
    b"207.173.177.12:27010",
    b"207.173.177.11:27010",
    b"207.173.177.10:27010",
    b"207.173.177.12:27011",
    b"207.173.177.11:27011",
    b"207.173.177.10:27011"
)

loopback_ips = (
    b"127.0.0.1",
    b"127.0.0.2"
)

# UNKNOWN
# 30819D300D06092A864886F70D010101050003818B00308187028181009B932AC50DEA89BD642EDE0DDDA5BCFBDAF91B359000ED74CA983F7926B8D23C78408F38F31C5026BAACF9CC6B05BC4F1A565D40CB4397F0A58F9B7C23D28EEC84C853D5D403032321776746A8E59F706EB7067882B0EB9CD92C516048EC85B600BFFE86D127CF2739F3210A2FA6EF651F874A5B3A886BC85F2BD7A6569C9F81020111

#"6DA7F10F1B16A4012FFDE4BB09B857A8E3254573CDE9C0E91B12AEF01E8B1624FB8606058946D7D45AEE3C73EE69F6BC30CE703D25ACAC7C96DC5A87EB8DE6B2820AF5BDD5835E3BBA8C6BF679595323212E82E1BCEF57EAF06338084D3E0592F7B9A6F1BBE752947F72BC80C4A50493F7ECBA39FD73CF02BBEFF407BFCD9D956E0F337D4A68D82998979BD11409BC2A908580DB2DB3FECB96D1F95DB4C28E50900B0413D02D5073E669B54A090F5B19CA6B8A918B81CEC7EEF105E181235713B8BE293E149CF6F3CBA0AAC96B6017ECC51B00C31526F357CCD3F5889FC5895C3787399AE22CCA53B3AADEBC2D1FE3A6C1D628A0CF8D68808A08BDADA904555613B00889CD4A59F1B42FC88ACEE2C350CB4EA12B8A9CD3CE16A7E4832817D2A4C7B420AFC3BC3596513B4E3690508848AF55D83693E30199E97A42467B24585DEA5C6311D94BDE922FD7795B434D6ACCB544A04E290D3D944727D35C1A9478F33E82D3C6B97EE615FAFD0A82CCCB65EABD07580630FA6C654631695B5A0F1B9AD1E86297499E1DDC992D82D782B67AA809B8102780327A7DB4EB56FBA0FB5614D65E88A88BF322CE21DB5651CBABB0A01DAC97F78E1A92EA3CF5C2EA23A4921264137F2CCE3417857FD93347BD9C46EFD89E0016912BD7ED807252EEF43C88573EE3D66F345E55B185A9372D0A84DF574895EC4D2BF4572A1D1250D6BAB76C528B17957DA67201331C3CE20D255C2A01CA704E05F65FA9DFCF498B84F3E4E0C3D42F9D6FDAC0DD5708512F609FFF6290BEA8B00B758474E03391C475E376DD3A4586939E08454D293BF3D365D8472AF36125008630BE95339D893BF061E178CC46BC0BEB6D8420BF366E612718D4C30F39B6276DBE155F744A88663E2BAE53DC83B5BF60704BEAF9002EE1AB64E5E644"

# replacestrings = (
# ("30820120300d06092a864886f70d01010105000382010d00308201080282010100d1543176ee6741270dc1a32f4b04c3a304d499ad0570777dba31483d01eb5e639a05eb284f93cf9260b1ef9e159403ae5f7d3997e789646cfc70f26815169a9b4ba4dc5700ea4480f78466eae6d2bdf5e4181da076ca2e95b32b79c016eb91b5f158e8448d2dd5a42f883976a935dcccbbc611dc2bdf0ea3b88ca72fba919501fb8c6187b4ecddbbb6623d640e819302a6be35be74460cbad9bff0ab7dff0c5b4b8f4aff8252815989ec5fffb460166c5a75b81dd99d79b05f23d97476eb3a5d44c74dcd1136e776f5d2bb52e77f530fa2a5ad75f16c1fb5d8218d71b93073bddad930b3b4217989aa58b30566f1887907ca431e02defe51d19489486caf033d020111",
 # "30820120300d06092a864886f70d01010105000382010d00308201080282010100" + config["main_key_n"][2:] + "020111",
 # "Steam2 main RSA key (1024-bit)"),
# ("\x30\x81\x9d\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x01\x05\x00\x03\x81\x8b\x00\x30\x81\x87\x02\x81\x81\x00\xda\xde\x57\xfe\x10\x99\xf9\x4b\x81\xb9\x0d\x00\x82\x50\x5b\xe3\x74\xca\x97\x28\xab\x9a\x88\x5b\x3b\x0e\x8e\x02\x5e\x43\xe5\xcc\xd8\x1b\x00\xcd\xbd\x05\xe2\x2a\xc2\x5c\x53\x18\xbf\x84\xc3\x40\x21\x42\xa5\xc3\x8a\xc3\xf4\x27\x1b\xab\xc3\xe5\xc0\x60\x18\xed\x26\x57\xf4\x68\xc5\xda\x55\xaa\x7e\x3b\x3b\x1a\xb2\x72\x06\x17\x4a\x85\x6e\xe2\xb6\x73\x91\x9d\xeb\x47\xbd\x49\x1d\x10\x21\x3e\x90\xdb\xd5\x6e\x25\x2c\xc6\xc9\xe9\x18\x8d\x0b\xc5\x71\x9b\x57\xed\x57\x02\xc6\x45\x5f\x27\x31\x6a\xa0\xaa\x03\x78\x2f\x06\xdf\x02\x01\x11",
 # "\x30\x81\x9d\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x01\x05\x00\x03\x81\x8b\x00\x30\x81\x87\x02\x81\x81\x00" + "\xbf\x97\x3e\x24\xbe\xb3\x72\xc1\x2b\xea\x44\x94\x45\x0a\xfa\xee\x29\x09\x87\xfe\xda\xe8\x58\x00\x57\xe4\xf1\x5b\x93\xb4\x61\x85\xb8\xda\xf2\xd9\x52\xe2\x4d\x6f\x9a\x23\x80\x58\x19\x57\x86\x93\xa8\x46\xe0\xb8\xfc\xc4\x3c\x23\xe1\xf2\xbf\x49\xe8\x43\xaf\xf4\xb8\xe9\xaf\x6c\x5e\x2e\x7b\x9d\xf4\x4e\x29\xe3\xc1\xc9\x3f\x16\x6e\x25\xe4\x2b\x8f\x91\x09\xbe\x8a\xd0\x34\x38\x84\x5a\x3c\x19\x25\x50\x4e\xcc\x09\x0a\xab\xd4\x9a\x0f\xc6\x78\x37\x46\xff\x4e\x9e\x09\x0a\xa9\x6f\x1c\x80\x09\xba\xf9\x16\x2b\x66\x71\x60\x59" + "\x02\x01\x11",
 # "Steam Beta main RSA key (512-bit)"),
# ("30820120300d06092a864886f70d01010105000382010d0030820108028201010094db10802a3dcf16ad6755208bfb8fa411c6c290dd86dfbb14bf4fc621ee22689e97b37bc89e82dd20a92d191f5f18362031ccffdac814e01a94a2822ff68f25a79751b0084da37869ba50a9db586595bcfd7d97a952bdaa16b2c2a0629de272faa2f4d6b06132df02e3227c75731dc051a4582c36133b56fcb7b8469fe20cfe8d7111dbd3c7f05a2a238e25362dd4aef82a931801badbe7f1709d4d4bfa97cdf933cc769634d51cfb7af134a7d443938bb82a2074411567f2eaec5bc54716b785e118c93b21d9278f1b422d54debed21645adecd91fb63c41d6fc7632c3cd91b0423f4fdb0cc7697cf666d905a17b593b2e4434b9595aedc4683d29d494aca9020111",
 # "30820120300d06092a864886f70d01010105000382010d00308201080282010100" + config["main_key_n"][2:] + "020111",
 # "Steam1 main RSA key (1024-bit)"),
# ("30819d300d06092a864886f70d010101050003818b0030818702818100d3bb0de9bbab4becf8efc894c0723c54c3d7f8ff7bcef9f4d9c810668ca1cad7a292017c537bab1a68db17f8bd9a94751c2e37f30a7fab23c6a0443edd2d6896c1f5fcc89bb4e32291a44044777eb72c5e1ff1a9c113c75b49abdfd5bdc732c7807a18c836944279d63ef9bb4a38f50805b157ad32556e07e6575a112ca346ff020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam2 unknown RSA key 1 (512-bit), not replaced yet"),
# ("30819d300d06092a864886f70d010101050003818b0030818702818100a7ed99f0b2eb868d94d67f6a9552a9bb5e909a724a086d88694dc74148833075e89afca13c4504b0cb304d7548c5cc0aa4f3d2fbbe9cdff173f22a0844e3702696a1ec7e930323185796fb55e1b6a2e08c337e84b21f0325af7537e7e6a43ff837d0694c6ce1ff86c1562096730d075a341111c4dc83570cf7c56f62cc04a9a9020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam1 unknown RSA key 1 (512-bit), not replaced yet"),
# ("30819d300d06092a864886f70d010101050003818b0030818702818100bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam1 unknown RSA key 2 (512-bit), not replaced yet"),
# ("30819d300d06092a864886f70d010101050003818b0030818702818100bc265d3402562c8afb78904e7ec84ee5b6662a09216b6b50da4205094c54f8b09d211bdeb8219ca4df67e39d2349bcbe9cb3b0d1e18b23cf33b5b51cabbeaa529a27e2b3928bdbe1c5c5a7de6bee7e87aecfa26f82286cad35df7ee53fe12adb2d1e81e98ca5faa6db509de8c4f482fa3c4fcf875ce21d443ed635bbdcb425db020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam1 unknown RSA key 3 (512-bit), not replaced yet"),
# ("30819d300d06092a864886f70d010101050003818b0030818702818100c8667b365a9801ed17ec2456a2a4b06377a943354064332c4ce558f43ad5980e16e462b9da48ba3797905d2681a6993d0a3aaaa1613bb78869894b96064edd4c54e8d1b5492937527c88ed98afeee3ee126dbcd98b9a8c8af038ecf3800ee1150c87235da973da40102d88248b61f6dcb4c40bbd48082c191eaefea0f85579dd020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam2 unknown RSA key 2 (512-bit), not replaced yet"),
# ("30819D300D06092A864886F70D010101050003818B0030818702818100DFEC1AD62C10662C17353A14B07C59117F9DD3D82B7AE3E015CD191E46E87B8774A2184631A9031479828EE945A24912A923687389CF69A1B16146BDC1BEBFD6011BD881D4DC90FBFE4F527366CB9570D7C58EBA1C7A3375A1623446BB60B78068FA13A77A8A374B9EC6F45D5F3A99F99EC43AE963A2BB881928E0E714C04289020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam2 unknown RSA key 3 (512-bit), not replaced yet"),
# ("30819D300D06092A864886F70D010101050003818B0030818702818100AED14BC0A3368BA0390B43DCED6AC8F2A3E47E098C552EE7E93CBBE55E0F1874548FF3BD56695B1309AFC8BEB3A14869E98349658DD293212FB91EFA743B552279BF8518CB6D52444E0592896AA899ED44AEE26646420CFB6E4C30C66C5C16FFBA9CB9783F174BCBC9015D3E3770EC675A3348F746CE58AAECD9FF4A786C834B020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam2 unknown RSA key 4 (512-bit), not replaced yet"),
# ("30819D300D06092A864886F70D010101050003818B0030818702818100A8FE013BB6D7214B53236FA1AB4EF10730A7C67E6A2CC25D3AB840CA594D162D74EB0E724629F9DE9BCE4B8CD0CAF4089446A511AF3ACBB84EDEC6D8850A7DAA960AEA7B51D622625C1E58D7461E09AE43A7C43469A2A5E8447618E23DB7C5A896FDE5B44BF84012A6174EC4C1600EB0C2B8404D9E764C44F4FC6F148973B413020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam2 unknown RSA key 5 (512-bit), not replaced yet"),
# ("30819D300D06092A864886F70D010101050003818B0030818702818100D0052CE98095CD3083A8E9259663CECC485D5C5200DB1E78D76A4C2CC8418CCC8746FB1BC9E86E4F7A6BC3E70FD5A95D6CD4EEA2CC805AD3CE5359E68091C4C0D5F06323916970C5BBBD05E24F7D9012EDAC4F86963C89CC921563CB5770B9C3AE084FC85616B00CC6C88A80D237F77FAB93BBE6DE9578B811C9E562ADBC0C87020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam2 unknown RSA key 6 (512-bit), not replaced yet"),
# ("30819D300D06092A864886F70D010101050003818B00308187028181009E20ECC73E7722F42AD952210A59B9668CB3C615445F87504E12FD84D723958864DFBD2D1F4B9D5C918B34E9EA9C07AF0FB9E42940F78EB757AB730F3A4722DE4E06BD15D890D87E62ACB41CB2639F75C014CD72884C4D763E2EA553759CE62CD19831E697027E3C63D1282F3FD9C06DBB034CF4A34D85F13B8EB6F7FB9D1FA1020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam2 unknown RSA key 7 (512-bit), not replaced yet"),
# ("30819D300D06092A864886F70D010101050003818B0030818702818100B1260881BDFE84463D88C6AB8DB914A2E593893C10508B8A5ABDF692E9A5419A3EDBAE86A052849983B75E3B425C18178B260003D857DF0B6505C6CF9C84F5859FCE3B63F1FB2D4818501F6C5FA4AD1430EEB081A74ABD74CD1F4AA1FCCA3B88DD0548AED34443CEB52444EAE9099AA4FE66B2E6224D02381C248025C7044079020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Real RSA key 1 (512-bit), not replaced yet"),
# ("afakehost.example.com:27030 bfakehost.example.com:27030",
 # config["server_ip"] + ":" + config["dir_server_port"] + " " + config["server_ip"] + ":" + config["dir_server_port"],
 # "DNS directory server fallback"),
# ("127.0.0.1" + ('\x00' * 3) + "207.173.176.215",
 # config["server_ip"] + '\x00' + "207.173.176.215",
 # "DNS loopback directory server"),
# ("68.142.92.67" + ('\x00' * 3),
 # "888.888.888.888",
 # "CAS IP 1"),
# ("68.142.92.66" + ('\x00' * 3),
 # "888.888.888.889",
 # "CAS IP 2"),
# ("207.173.176.132",
 # "888.888.888.890",
 # "CAS IP 3"),
# ("207.173.176.131",
 # "888.888.888.891",
 # "CAS IP 4"),
# ("207.173.176.216" + '\x00' + "207.173.179.87" + '\x00\x00' + "207.173.178.127" + '\x00' + "207.173.178.178",
 # config["server_ip"] + ":" + config["dir_server_port"] + '\x00' + config["server_ip"] + ":" + config["dir_server_port"] + '\x00' + config["server_ip"] + ":" + config["dir_server_port"],
 # "DNS extra directory servers"),
# ("http://207.173.176.210/community/",
 # "http://" + config["community_ip"] + "/community/",
 # "Community IP URL"),
# ("207.173.177.11:27010",
 # config["server_ip"] + ":27010",
 # "HL Master Server 1"),
# ("207.173.177.12:27010",
 # config["server_ip"] + ":27010",
 # "HL Master Server 2"),
# ('207.173.177.45:27030 207.173.177.45:27030',
 # config["server_ip"] + ":" + config["dir_server_port"] + " " + config["server_ip"] + ":" + config["dir_server_port"],
 # "Steam1 directory server 1"),
# ('207.173.177.45:27030 207.173.177.46:27030',
 # config["server_ip"] + ":" + config["dir_server_port"] + " " + config["server_ip"] + ":" + config["dir_server_port"],
 # "Steam1 directory server 2"),
# ("gds1.steampowered.com:27030 gds2.steampowered.com:27030",
 # config["server_ip"] + ":" + config["dir_server_port"] + " " + config["server_ip"] + ":" + config["dir_server_port"],
 # "DNS directory server fallback"),
# ("afakehost.example.com:27030 bfakehost.example.com:27030",
 # config["server_ip"] + ":" + config["dir_server_port"] + " " + config["server_ip"] + ":" + config["dir_server_port"],
 # "DNS directory server fallback"),
# ("cm0.steampowered.com",
 # config["server_ip"],
 # "DNS content server fallback"),
# ('"tracker.valvesoftware.com:1200"',
 # '"' + config["tracker_ip"] + ':1200"',
 # "Tracker DNS"),
# )

# replacestrings_name_space = (
# ('<h1><img src="http://steampowered.com/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Account Information</h1>',
 # '<h1><img src="http://' + octal_ip + http_port_neuter + '/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Account Information</h1>',
 # "New account logo 1"),
# ('<img src="http://steampowered.com/img/print.gif" height="32" width="32" alt="STEAM" align="absmiddle"> <a href="javascript:window.print();">Click here to print this page now</a>',
 # '<img src="http://' + octal_ip + http_port_neuter + '/img/print.gif" height="32" width="32" alt="STEAM" align="absmiddle"> <a href="javascript:window.print();">Click here to print this page now</a>',
 # "New account logo 2"),
# ('For more information about Steam accounts, see <a href="http://steampowered.com/?area=support">the support page</a>.<br><br>',
 # 'For more information about Steam accounts, see <a href="http://' + octal_ip + http_port_neuter + '/?area=support">the support page</a>.<br><br>',
 # "New account logo 3"),
# ("http://steampowered.com/img/steam_logo_onwhite.gif",
 # "http://" + octal_ip + http_port_neuter + "/img/steam_logo_onwhite.gif",
 # "New account logo 4"),
# ("http://steampowered.com/img/print.gif",
 # "http://" + octal_ip + http_port_neuter + "/img/print.gif",
 # "New account logo 5"),
# ('<h1><img src="http://steampowered.com/img/steam_logo_whiteongreen.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Account Information</h1>',
 # '<h1><img src="http://' + octal_ip + http_port_neuter + '/img/steam_logo_whiteongreen.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Account Information</h1>',
 # "New account logo 6"),
# ('<img src="http://steampowered.com/img/print_ongreen.gif" height="32" width="32" alt="STEAM" align="absmiddle"> <a href="javascript:window.print();">Click here to print this page now</a>',
 # '<img src="http://' + octal_ip + http_port_neuter + '/img/print_ongreen.gif" height="32" width="32" alt="STEAM" align="absmiddle"> <a href="javascript:window.print();">Click here to print this page now</a>',
 # "New account logo 7"),
# ("http://steampowered.com/img/steam_logo_whiteongreen.gif",
 # "http://" + octal_ip + http_port_neuter + "/img/steam_logo_whiteongreen.gif",
 # "New account logo 8"),
# ("http://steampowered.com/img/print_ongreen.gif",
 # "http://" + octal_ip + http_port_neuter + "/img/print_ongreen.gif",
 # "New account logo 9"),
# ('<h1><img src="http://steampowered.com/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam - Receipt for credit card purchase</h1>',
 # '<h1><img src="http://' + octal_ip + http_port_neuter + '/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam - Receipt for credit card purchase</h1>',
 # "GCF URL 1"),
# ('<h1><img src="http://steampowered.com/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam - Receipt for CD key subscription</h1>',
 # '<h1><img src="http://' + octal_ip + http_port_neuter + '/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam - Receipt for CD key subscription</h1>',
 # "GCF URL 2"),
# ('<h1><img src="http://steampowered.com/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Game Details</h1>',
 # '<h1><img src="http://' + octal_ip + http_port_neuter + '/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Game Details</h1>',
 # "GCF URL 3"),
# ('"http://www.steampowered.com/"',
 # '"http://' + octal_ip + http_port_neuter + '/"',
 # "GCF URL 4"),
# ('(http://steampowered.com/img/square.gif);',
 # '(http://' + octal_ip + http_port_neuter + '/img/square.gif);',
 # "GCF URL 5"),
# ('"http://steampowered.com/img/steam_logo_onwhite.gif"',
 # '"http://' + octal_ip + http_port_neuter + '/img/steam_logo_onwhite.gif"',
 # "GCF URL 6"),
# ('"http://steampowered.com/img/print.gif"',
 # '"http://' + octal_ip + http_port_neuter + '/img/print.gif"',
 # "GCF URL 7"),
# ('"http://www.steampowered.com/video/requirements.php?game=240&l=english&vendorid=4098&deviceid=20042"',
 # '"http://' + octal_ip + http_port_neuter + '/video/requirements.php?game=240&l=english&vendorid=4098&deviceid=20042"',
 # "GCF URL 8"),
# ('"http://www.steampowered.com/video/driverupdate.php?game=240&l=english&vendorid=4098&deviceid=20042"',
 # '"http://' + octal_ip + http_port_neuter + '/video/driverupdate.php?game=240&l=english&vendorid=4098&deviceid=20042"',
 # "GCF URL 9"),
# ('"http://steampowered.com/?area=subscriber_agreement"',
 # '"http://' + octal_ip + http_port_neuter + '/?area=subscriber_agreement"',
 # "GCF URL 10"),
# ('"http://steampowered.com/troubleshooter/live/en/s_bill_01.php"',
 # '"http://' + octal_ip + http_port_neuter + '/troubleshooter/live/en/s_bill_01.php"',
 # "GCF URL 11"),
# ('"http://steampowered.com/?area=getsteamnow"',
 # '"http://' + octal_ip + http_port_neuter + '/?area=getsteamnow"',
 # "GCF URL 12"),
# ('"http://www.steampowered.com/status/survey.html"',
 # '"http://' + octal_ip + http_port_neuter + '/status/survey.html"',
 # "GCF URL 13"),
# ('http://www.steampowered.com/platform/update_history/"',
 # "http://" + octal_ip + http_port_neuter + '/platform/update_history/"',
 # "Platform News URL"),
# ('"207.173.178.42:1200"',
 # '"' + config["tracker_ip"] + ':1200"',
 # "Tracker IP 1"),
# ('"207.173.178.43:1200"',
 # '"' + config["tracker_ip"] + ':1200"',
 # "Tracker IP 2"),
# ('"207.173.178.44:1200"',
 # '"' + config["tracker_ip"] + ':1200"',
 # "Tracker IP 3"),
# ('"207.173.178.45:1200"',
 # '"' + config["tracker_ip"] + ':1200"',
 # "Tracker IP 4"),
# ('"207.173.177.10:27010"',
 # '"' + config["server_ip"] + ':27010"',
 # "HL Master Server 3"),
# ('"half-life.west.won.net:27010"',
 # '"' + config["server_ip"] + ':27010"',
 # "HL Master Server 4"),
# ('hlmaster.valvesoftware.com:27010',
 # config["server_ip"] + ':27010',
 # "HL Master Server 5"),
# ('half-life.east.won.net:27010',
 # config["server_ip"] + ':27010',
 # "HL Master Server 6"),
# ('"http://www.steampowered.com/?area=news"',
 # '"' + "http://" + octal_ip + http_port_neuter + "/?area=news" + '"',
 # "Steam news URL 1"),
# )
#NEWS WORKS FROM URL 1
# replacestrings_name = (
# ("http://www.steampowered.com/platform/banner/random.php",
 # "http://" + octal_ip + http_port_neuter + "/platform/banner/random.php",
 # "Banner URL"),
# ("http://storefront.steampowered.com/platform/update_history/index.php",
 # "http://" + octal_ip + http_port_neuter + config["store_url_new"] + "/platform/update_history/index.php",
 # "Client news URL"),
# ("http://www.steampowered.com/?area=news",
 # "http://" + octal_ip + http_port_neuter + "/?area=news",
 # "Steam news URL 2"),
# ("http://www.steampowered.com/index.php?area=news",
 # "http://" + octal_ip + http_port_neuter + "/index.php?area=news",
 # "Steam news URL 3"),
# ("http://www.steampowered.com/platform/friends/",
 # "http://" + octal_ip + http_port_neuter + "/platform/friends/",
 # "Tracker URL"),
# ("http://www.steampowered.com/index.php?area=subscriber_agreement",
 # "http://" + octal_ip + http_port_neuter + "/index.php?area=subscriber_agreement",
 # "SSA URL"),
# ('http://storefront.steampowered.com/v/?client=1',
 # "http://" + octal_ip + http_port_neuter + config["store_url_new"] + "/v/?client=1",
 # "Storefront URL 1"),
# ("http://storefront.steampowered.com",
 # "http://" + octal_ip + http_port_neuter + config["store_url_new"],
 # "Storefront URL 2"),
# ("http://support.steampowered.com",
 # "http://" + octal_ip + http_port_neuter + config["support_url_new"],
 # "Support URL"),
# ("http://cdntest.steampowered.com/steamcommunity/beta/",
 # "http://" + config["community_ip"] + "/steamcommunity/beta/",
 # "Community beta URL"),
# ("http://localhost/community/public/",
 # "http://" + config["community_ip"] + "/community/public/",
 # "Community local URL"),
# ("http://media.steampowered.com/steamcommunity/public/",
 # "http://" + config["community_ip"] + "/steamcommunity/public/",
 # "Community media URL"),
# ("http://steamcommunity.com/",
 # "http://" + config["community_ip"] + "/",
 # "Community URL"),
# ("http://www.steampowered.com",
 # "http://" + octal_ip + http_port_neuter,
 # "Steampowered URL 1"),
# ("http://store.steampowered.com",
 # "http://" + octal_ip + http_port_neuter,
 # "Steam Store URL"),
# ("http://developer.valvesoftware.com/wiki/Main_Page",
 # "http://" + octal_ip + http_port_neuter,
 # "Dev Wiki URL"),
# ("http://www.steampowered.com/platform/banner/",
 # "http://" + octal_ip + http_port_neuter + "/platform/banner/",
 # "New banner URL 1"),
# ("http://cdn.steampowered.com/platform/banner/cs_25.html",
 # "http://" + octal_ip + http_port_neuter + "/platform/banner/cs_25.html",
 # "New banner URL 2"),
# ("http://cdn.steampowered.com/platform/banner/",
 # "http://" + octal_ip + http_port_neuter + "/platform/banner/",
 # "New banner URL 3"),
# ("StorefrontURL",
 # "StorefrontURM",
 # "Storefront redirector"),
# ("SteamNewsURL",
 # "SteamNewsURM",
 # "Steam news redirector"),
# ("media.steampowered.com" + '\x00' + '\x00',
 # "client-download.steampowered.com",
 # "Steam 2013 Package URL"),
# ("http://steampowered.com/troubleshooter/",
 # "http://" + octal_ip + http_port_neuter + "/troubleshooter/",
 # "Troubleshooter"),
# ('http://steampowered.com',
 # "http://" + octal_ip + http_port_neuter,
 # "SteamPowered URL 2"),
# )

# replacestringsext = (
# ("30820120300d06092a864886f70d01010105000382010d00308201080282010100d1543176ee6741270dc1a32f4b04c3a304d499ad0570777dba31483d01eb5e639a05eb284f93cf9260b1ef9e159403ae5f7d3997e789646cfc70f26815169a9b4ba4dc5700ea4480f78466eae6d2bdf5e4181da076ca2e95b32b79c016eb91b5f158e8448d2dd5a42f883976a935dcccbbc611dc2bdf0ea3b88ca72fba919501fb8c6187b4ecddbbb6623d640e819302a6be35be74460cbad9bff0ab7dff0c5b4b8f4aff8252815989ec5fffb460166c5a75b81dd99d79b05f23d97476eb3a5d44c74dcd1136e776f5d2bb52e77f530fa2a5ad75f16c1fb5d8218d71b93073bddad930b3b4217989aa58b30566f1887907ca431e02defe51d19489486caf033d020111",
 # "30820120300d06092a864886f70d01010105000382010d00308201080282010100" + config["main_key_n"][2:] + "020111",
 # "Steam2 main RSA key (1024-bit)"),
# ("\x30\x81\x9d\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x01\x05\x00\x03\x81\x8b\x00\x30\x81\x87\x02\x81\x81\x00\xda\xde\x57\xfe\x10\x99\xf9\x4b\x81\xb9\x0d\x00\x82\x50\x5b\xe3\x74\xca\x97\x28\xab\x9a\x88\x5b\x3b\x0e\x8e\x02\x5e\x43\xe5\xcc\xd8\x1b\x00\xcd\xbd\x05\xe2\x2a\xc2\x5c\x53\x18\xbf\x84\xc3\x40\x21\x42\xa5\xc3\x8a\xc3\xf4\x27\x1b\xab\xc3\xe5\xc0\x60\x18\xed\x26\x57\xf4\x68\xc5\xda\x55\xaa\x7e\x3b\x3b\x1a\xb2\x72\x06\x17\x4a\x85\x6e\xe2\xb6\x73\x91\x9d\xeb\x47\xbd\x49\x1d\x10\x21\x3e\x90\xdb\xd5\x6e\x25\x2c\xc6\xc9\xe9\x18\x8d\x0b\xc5\x71\x9b\x57\xed\x57\x02\xc6\x45\x5f\x27\x31\x6a\xa0\xaa\x03\x78\x2f\x06\xdf\x02\x01\x11",
 # "\x30\x81\x9d\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x01\x05\x00\x03\x81\x8b\x00\x30\x81\x87\x02\x81\x81\x00" + "\xbf\x97\x3e\x24\xbe\xb3\x72\xc1\x2b\xea\x44\x94\x45\x0a\xfa\xee\x29\x09\x87\xfe\xda\xe8\x58\x00\x57\xe4\xf1\x5b\x93\xb4\x61\x85\xb8\xda\xf2\xd9\x52\xe2\x4d\x6f\x9a\x23\x80\x58\x19\x57\x86\x93\xa8\x46\xe0\xb8\xfc\xc4\x3c\x23\xe1\xf2\xbf\x49\xe8\x43\xaf\xf4\xb8\xe9\xaf\x6c\x5e\x2e\x7b\x9d\xf4\x4e\x29\xe3\xc1\xc9\x3f\x16\x6e\x25\xe4\x2b\x8f\x91\x09\xbe\x8a\xd0\x34\x38\x84\x5a\x3c\x19\x25\x50\x4e\xcc\x09\x0a\xab\xd4\x9a\x0f\xc6\x78\x37\x46\xff\x4e\x9e\x09\x0a\xa9\x6f\x1c\x80\x09\xba\xf9\x16\x2b\x66\x71\x60\x59" + "\x02\x01\x11",
 # "Steam Beta main RSA key (512-bit)"),
# ("30820120300d06092a864886f70d01010105000382010d0030820108028201010094db10802a3dcf16ad6755208bfb8fa411c6c290dd86dfbb14bf4fc621ee22689e97b37bc89e82dd20a92d191f5f18362031ccffdac814e01a94a2822ff68f25a79751b0084da37869ba50a9db586595bcfd7d97a952bdaa16b2c2a0629de272faa2f4d6b06132df02e3227c75731dc051a4582c36133b56fcb7b8469fe20cfe8d7111dbd3c7f05a2a238e25362dd4aef82a931801badbe7f1709d4d4bfa97cdf933cc769634d51cfb7af134a7d443938bb82a2074411567f2eaec5bc54716b785e118c93b21d9278f1b422d54debed21645adecd91fb63c41d6fc7632c3cd91b0423f4fdb0cc7697cf666d905a17b593b2e4434b9595aedc4683d29d494aca9020111",
 # "30820120300d06092a864886f70d01010105000382010d00308201080282010100" + config["main_key_n"][2:] + "020111",
 # "Steam1 main RSA key (1024-bit)"),
# ("30819d300d06092a864886f70d010101050003818b0030818702818100d3bb0de9bbab4becf8efc894c0723c54c3d7f8ff7bcef9f4d9c810668ca1cad7a292017c537bab1a68db17f8bd9a94751c2e37f30a7fab23c6a0443edd2d6896c1f5fcc89bb4e32291a44044777eb72c5e1ff1a9c113c75b49abdfd5bdc732c7807a18c836944279d63ef9bb4a38f50805b157ad32556e07e6575a112ca346ff020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam2 unknown RSA key 1 (512-bit), not replaced yet"),
# ("30819d300d06092a864886f70d010101050003818b0030818702818100a7ed99f0b2eb868d94d67f6a9552a9bb5e909a724a086d88694dc74148833075e89afca13c4504b0cb304d7548c5cc0aa4f3d2fbbe9cdff173f22a0844e3702696a1ec7e930323185796fb55e1b6a2e08c337e84b21f0325af7537e7e6a43ff837d0694c6ce1ff86c1562096730d075a341111c4dc83570cf7c56f62cc04a9a9020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam1 unknown RSA key 1 (512-bit), not replaced yet"),
# ("30819d300d06092a864886f70d010101050003818b0030818702818100bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam1 unknown RSA key 2 (512-bit), not replaced yet"),
# ("30819d300d06092a864886f70d010101050003818b0030818702818100c8667b365a9801ed17ec2456a2a4b06377a943354064332c4ce558f43ad5980e16e462b9da48ba3797905d2681a6993d0a3aaaa1613bb78869894b96064edd4c54e8d1b5492937527c88ed98afeee3ee126dbcd98b9a8c8af038ecf3800ee1150c87235da973da40102d88248b61f6dcb4c40bbd48082c191eaefea0f85579dd020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam2 unknown RSA key 2 (512-bit), not replaced yet"),
# ("30819D300D06092A864886F70D010101050003818B0030818702818100DFEC1AD62C10662C17353A14B07C59117F9DD3D82B7AE3E015CD191E46E87B8774A2184631A9031479828EE945A24912A923687389CF69A1B16146BDC1BEBFD6011BD881D4DC90FBFE4F527366CB9570D7C58EBA1C7A3375A1623446BB60B78068FA13A77A8A374B9EC6F45D5F3A99F99EC43AE963A2BB881928E0E714C04289020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam2 unknown RSA key 3 (512-bit), not replaced yet"),
# ("30819D300D06092A864886F70D010101050003818B0030818702818100AED14BC0A3368BA0390B43DCED6AC8F2A3E47E098C552EE7E93CBBE55E0F1874548FF3BD56695B1309AFC8BEB3A14869E98349658DD293212FB91EFA743B552279BF8518CB6D52444E0592896AA899ED44AEE26646420CFB6E4C30C66C5C16FFBA9CB9783F174BCBC9015D3E3770EC675A3348F746CE58AAECD9FF4A786C834B020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam2 unknown RSA key 4 (512-bit), not replaced yet"),
# ("30819D300D06092A864886F70D010101050003818B0030818702818100A8FE013BB6D7214B53236FA1AB4EF10730A7C67E6A2CC25D3AB840CA594D162D74EB0E724629F9DE9BCE4B8CD0CAF4089446A511AF3ACBB84EDEC6D8850A7DAA960AEA7B51D622625C1E58D7461E09AE43A7C43469A2A5E8447618E23DB7C5A896FDE5B44BF84012A6174EC4C1600EB0C2B8404D9E764C44F4FC6F148973B413020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam2 unknown RSA key 5 (512-bit), not replaced yet"),
# ("30819D300D06092A864886F70D010101050003818B0030818702818100D0052CE98095CD3083A8E9259663CECC485D5C5200DB1E78D76A4C2CC8418CCC8746FB1BC9E86E4F7A6BC3E70FD5A95D6CD4EEA2CC805AD3CE5359E68091C4C0D5F06323916970C5BBBD05E24F7D9012EDAC4F86963C89CC921563CB5770B9C3AE084FC85616B00CC6C88A80D237F77FAB93BBE6DE9578B811C9E562ADBC0C87020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam2 unknown RSA key 6 (512-bit), not replaced yet"),
# ("30819D300D06092A864886F70D010101050003818B00308187028181009E20ECC73E7722F42AD952210A59B9668CB3C615445F87504E12FD84D723958864DFBD2D1F4B9D5C918B34E9EA9C07AF0FB9E42940F78EB757AB730F3A4722DE4E06BD15D890D87E62ACB41CB2639F75C014CD72884C4D763E2EA553759CE62CD19831E697027E3C63D1282F3FD9C06DBB034CF4A34D85F13B8EB6F7FB9D1FA1020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Steam2 unknown RSA key 7 (512-bit), not replaced yet"),
# ("30819D300D06092A864886F70D010101050003818B0030818702818100B1260881BDFE84463D88C6AB8DB914A2E593893C10508B8A5ABDF692E9A5419A3EDBAE86A052849983B75E3B425C18178B260003D857DF0B6505C6CF9C84F5859FCE3B63F1FB2D4818501F6C5FA4AD1430EEB081A74ABD74CD1F4AA1FCCA3B88DD0548AED34443CEB52444EAE9099AA4FE66B2E6224D02381C248025C7044079020111",
 # "30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2:] + "020111",
 # "Real RSA key 1 (512-bit), not replaced yet"),
# ("afakehost.example.com:27030 bfakehost.example.com:27030",
 # config["public_ip"] + ":" + config["dir_server_port"] + " " + config["server_ip"] + ":" + config["dir_server_port"],
 # "DNS directory server fallback"),
# ("127.0.0.1" + ('\x00' * 3) + "207.173.176.215",
 # config["public_ip"] + '\x00' + "207.173.176.215",
 # "DNS loopback directory server"),
# ("68.142.92.67" + ('\x00' * 3),
 # "888.888.888.888",
 # "CAS IP 1"),
# ("68.142.92.66" + ('\x00' * 3),
 # "888.888.888.889",
 # "CAS IP 2"),
# ("207.173.176.132",
 # "888.888.888.890",
 # "CAS IP 3"),
# ("207.173.176.131",
 # "888.888.888.891",
 # "CAS IP 4"),
# ("207.173.176.216" + '\x00' + "207.173.179.87" + '\x00\x00' + "207.173.178.127" + '\x00' + "207.173.178.178",
 # config["public_ip"] + ":" + config["dir_server_port"] + '\x00' + config["server_ip"] + ":" + config["dir_server_port"] + '\x00' + config["public_ip"] + ":" + config["dir_server_port"],
 # "DNS extra directory servers"),
# ("http://207.173.176.210/community/",
 # "http://" + config["community_ip"] + "/community/",
 # "Community IP URL"),
# ("207.173.177.11:27010",
 # config["public_ip"] + ":27010",
 # "HL Master Server 1"),
# ("207.173.177.12:27010",
 # config["public_ip"] + ":27010",
 # "HL Master Server 2"),
# ('207.173.177.45:27030 207.173.177.45:27030',
 # config["public_ip"] + ":" + config["dir_server_port"] + " " + config["server_ip"] + ":" + config["dir_server_port"],
 # "Steam1 directory server 1"),
# ('207.173.177.45:27030 207.173.177.46:27030',
 # config["public_ip"] + ":" + config["dir_server_port"] + " " + config["server_ip"] + ":" + config["dir_server_port"],
 # "Steam1 directory server 2"),
# ("gds1.steampowered.com:27030 gds2.steampowered.com:27030",
 # config["public_ip"] + ":" + config["dir_server_port"] + " " + config["server_ip"] + ":" + config["dir_server_port"],
 # "DNS directory server fallback"),
# ("afakehost.example.com:27030 bfakehost.example.com:27030",
 # config["public_ip"] + ":" + config["dir_server_port"] + " " + config["server_ip"] + ":" + config["dir_server_port"],
 # "DNS directory server fallback"),
# ("cm0.steampowered.com",
 # config["public_ip"],
 # "DNS content server fallback"),
# ('"tracker.valvesoftware.com:1200"',
 # '"' + config["tracker_ip"] + ':1200"',
 # "Tracker DNS"),
# )

# replacestrings_name_space_ext = (
# ('<h1><img src="http://steampowered.com/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Account Information</h1>',
 # '<h1><img src="http://' + octal_ip + http_port_neuter + '/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Account Information</h1>',
 # "New account logo 1"),
# ('<img src="http://steampowered.com/img/print.gif" height="32" width="32" alt="STEAM" align="absmiddle"> <a href="javascript:window.print();">Click here to print this page now</a>',
 # '<img src="http://' + octal_ip + http_port_neuter + '/img/print.gif" height="32" width="32" alt="STEAM" align="absmiddle"> <a href="javascript:window.print();">Click here to print this page now</a>',
 # "New account logo 2"),
# ('For more information about Steam accounts, see <a href="http://steampowered.com/?area=support">the support page</a>.<br><br>',
 # 'For more information about Steam accounts, see <a href="http://' + octal_ip + http_port_neuter + '/?area=support">the support page</a>.<br><br>',
 # "New account logo 3"),
# ("http://steampowered.com/img/steam_logo_onwhite.gif",
 # "http://" + octal_ip + http_port_neuter + "/img/steam_logo_onwhite.gif",
 # "New account logo 4"),
# ("http://steampowered.com/img/print.gif",
 # "http://" + octal_ip + http_port_neuter + "/img/print.gif",
 # "New account logo 5"),
# ('<h1><img src="http://steampowered.com/img/steam_logo_whiteongreen.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Account Information</h1>',
 # '<h1><img src="http://' + octal_ip + http_port_neuter + '/img/steam_logo_whiteongreen.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Account Information</h1>',
 # "New account logo 6"),
# ('<img src="http://steampowered.com/img/print_ongreen.gif" height="32" width="32" alt="STEAM" align="absmiddle"> <a href="javascript:window.print();">Click here to print this page now</a>',
 # '<img src="http://' + octal_ip + http_port_neuter + '/img/print_ongreen.gif" height="32" width="32" alt="STEAM" align="absmiddle"> <a href="javascript:window.print();">Click here to print this page now</a>',
 # "New account logo 7"),
# ("http://steampowered.com/img/steam_logo_whiteongreen.gif",
 # "http://" + octal_ip + http_port_neuter + "/img/steam_logo_whiteongreen.gif",
 # "New account logo 8"),
# ("http://steampowered.com/img/print_ongreen.gif",
 # "http://" + octal_ip + http_port_neuter + "/img/print_ongreen.gif",
 # "New account logo 9"),
# ('<h1><img src="http://steampowered.com/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam - Receipt for credit card purchase</h1>',
 # '<h1><img src="http://' + octal_ip + http_port_neuter + '/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam - Receipt for credit card purchase</h1>',
 # "GCF URL 1"),
# ('<h1><img src="http://steampowered.com/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam - Receipt for CD key subscription</h1>',
 # '<h1><img src="http://' + octal_ip + http_port_neuter + '/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam - Receipt for CD key subscription</h1>',
 # "GCF URL 2"),
# ('<h1><img src="http://steampowered.com/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Game Details</h1>',
 # '<h1><img src="http://' + octal_ip + http_port_neuter + '/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Game Details</h1>',
 # "GCF URL 3"),
# ('"http://www.steampowered.com/"',
 # '"http://' + octal_ip + http_port_neuter + '/"',
 # "GCF URL 4"),
# ('(http://steampowered.com/img/square.gif);',
 # '(http://' + octal_ip + http_port_neuter + '/img/square.gif);',
 # "GCF URL 5"),
# ('"http://steampowered.com/img/steam_logo_onwhite.gif"',
 # '"http://' + octal_ip + http_port_neuter + '/img/steam_logo_onwhite.gif"',
 # "GCF URL 6"),
# ('"http://steampowered.com/img/print.gif"',
 # '"http://' + octal_ip + http_port_neuter + '/img/print.gif"',
 # "GCF URL 7"),
# ('"http://www.steampowered.com/video/requirements.php?game=240&l=english&vendorid=4098&deviceid=20042"',
 # '"http://' + octal_ip + http_port_neuter + '/video/requirements.php?game=240&l=english&vendorid=4098&deviceid=20042"',
 # "GCF URL 8"),
# ('"http://www.steampowered.com/video/driverupdate.php?game=240&l=english&vendorid=4098&deviceid=20042"',
 # '"http://' + octal_ip + http_port_neuter + '/video/driverupdate.php?game=240&l=english&vendorid=4098&deviceid=20042"',
 # "GCF URL 9"),
# ('"http://steampowered.com/?area=subscriber_agreement"',
 # '"http://' + octal_ip + http_port_neuter + '/?area=subscriber_agreement"',
 # "GCF URL 10"),
# ('"http://steampowered.com/troubleshooter/live/en/s_bill_01.php"',
 # '"http://' + octal_ip + http_port_neuter + '/troubleshooter/live/en/s_bill_01.php"',
 # "GCF URL 11"),
# ('"http://steampowered.com/?area=getsteamnow"',
 # '"http://' + octal_ip + http_port_neuter + '/?area=getsteamnow"',
 # "GCF URL 12"),
# ('"http://www.steampowered.com/status/survey.html"',
 # '"http://' + octal_ip + http_port_neuter + '/status/survey.html"',
 # "GCF URL 13"),
# ('"207.173.178.42:1200"',
 # '"' + config["tracker_ip"] + ':1200"',
 # "Tracker IP 1"),
# ('"207.173.178.43:1200"',
 # '"' + config["tracker_ip"] + ':1200"',
 # "Tracker IP 2"),
# ('"207.173.178.44:1200"',
 # '"' + config["tracker_ip"] + ':1200"',
 # "Tracker IP 3"),
# ('"207.173.178.45:1200"',
 # '"' + config["tracker_ip"] + ':1200"',
 # "Tracker IP 4"),
# ('"207.173.177.10:27010"',
 # '"' + config["public_ip"] + ':27010"',
 # "HL Master Server 3"),
# ('"half-life.west.won.net:27010"',
 # '"' + config["public_ip"] + ':27010"',
 # "HL Master Server 4"),
# ('hlmaster.valvesoftware.com:27010',
 # config["public_ip"] + ':27010',
 # "HL Master Server 5"),
# ('half-life.east.won.net:27010',
 # config["public_ip"] + ':27010',
 # "HL Master Server 6"),
# ('http://www.steampowered.com/platform/update_history/"',
 # "http://" + octal_ip + http_port_neuter + '/platform/update_history/"',
 # "Platform News URL"),
# )

# replacestrings_name_ext = (
# ("http://www.steampowered.com/platform/banner/random.php",
 # "http://" + octal_ip + http_port_neuter + "/platform/banner/random.php",
 # "Banner URL"),
# ("http://storefront.steampowered.com/platform/update_history/index.php",
 # "http://" + octal_ip + http_port_neuter + config["store_url_new"] + "/platform/update_history/index.php",
 # "Client news URL"),
# ('"http://www.steampowered.com/?area=news"',
 # '"' + "http://" + octal_ip + http_port_neuter + "/?area=news" + '"',
 # "Steam news URL 1"),
# ("http://www.steampowered.com/?area=news",
 # "http://" + octal_ip + http_port_neuter + "/?area=news",
 # "Steam news URL 2"),
# ("http://www.steampowered.com/index.php?area=news",
 # "http://" + octal_ip + http_port_neuter + "/index.php?area=news",
 # "Steam news URL 3"),
# ("http://www.steampowered.com/platform/friends/",
 # "http://" + octal_ip + http_port_neuter + "/platform/friends/",
 # "Tracker URL"),
# ("http://www.steampowered.com/index.php?area=subscriber_agreement",
 # "http://" + octal_ip + http_port_neuter + "/index.php?area=subscriber_agreement",
 # "SSA URL"),
# ('http://storefront.steampowered.com/v/?client=1',
 # "http://" + octal_ip + http_port_neuter + config["store_url_new"] + "/v/?client=1",
 # "Storefront URL 1"),
# ("http://storefront.steampowered.com",
 # "http://" + octal_ip + http_port_neuter + config["store_url_new"],
 # "Storefront URL 2"),
# ("http://support.steampowered.com",
 # "http://" + octal_ip + http_port_neuter + config["support_url_new"],
 # "Support URL"),
# ("http://cdntest.steampowered.com/steamcommunity/beta/",
 # "http://" + config["community_ip"] + "/steamcommunity/beta/",
 # "Community beta URL"),
# ("http://localhost/community/public/",
 # "http://" + config["community_ip"] + "/community/public/",
 # "Community local URL"),
# ("http://media.steampowered.com/steamcommunity/public/",
 # "http://" + config["community_ip"] + "/steamcommunity/public/",
 # "Community media URL"),
# ("http://steamcommunity.com/",
 # "http://" + config["community_ip"] + "/",
 # "Community URL"),
# ("http://www.steampowered.com",
 # "http://" + octal_ip + http_port_neuter,
 # "Steampowered URL 1"),
# ("http://store.steampowered.com",
 # "http://" + octal_ip + http_port_neuter,
 # "Steam Store URL"),
# ("http://developer.valvesoftware.com/wiki/Main_Page",
 # "http://" + octal_ip + http_port_neuter,
 # "Dev Wiki URL"),
# ("http://www.steampowered.com/platform/banner/",
 # "http://" + octal_ip + http_port_neuter + "/platform/banner/",
 # "New banner URL 1"),
# ("http://cdn.steampowered.com/platform/banner/cs_25.html",
 # "http://" + octal_ip + http_port_neuter + "/platform/banner/cs_25.html",
 # "New banner URL 2"),
# ("http://cdn.steampowered.com/platform/banner/",
 # "http://" + octal_ip + http_port_neuter + "/platform/banner/",
 # "New banner URL 3"),
# ("StorefrontURL",
 # "StorefrontURM",
 # "Storefront redirector"),
# ("SteamNewsURL",
 # "SteamNewsURM",
 # "Steam news redirector"),
# ("media.steampowered.com" + '\x00' + '\x00',
 # "client-download.steampowered.com",
 # "Steam 2013 Package URL"),
# ("gds1.steampowered.com:27030 gds2.steampowered.com:27030",
 # config["public_ip"] + ":" + config["dir_server_port"] + " " + config["server_ip"] + ":" + config["dir_server_port"],
 # "DNS directory server fallback"),
# ("http://steampowered.com/troubleshooter/",
 # "http://" + octal_ip + http_port_neuter + "/troubleshooter/",
 # "Troubleshooter"),
# ('http://steampowered.com',
 # "http://" + octal_ip + http_port_neuter,
 # "SteamPowered URL 2"),
# )

#octal_ip_b = octal_ip.encode("latin-1")

replacestringsCDR = (
    (b'http://storefront.steampowered.com/marketing',
     b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/marketing",
     b"Messages URL 1"),
    (b'http://www.steampowered.com/marketing',
     b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/marketing",
     b"Messages URL 2"),
    (b'http://storefront.steampowered.com/Steam/Marketing',
     b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1')+ b"/Steam/Marketing",
     b"Messages URL 3"),
    (b'http://www.steampowered.com/Steam/Marketing/',
     b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/Steam/Marketing/",
     b"Messages URL 4"),
    (b'http://steampowered.com/Steam/Marketing/',
     b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/Steam/Marketing/",
     b"Messages URL 5"),
    (b'http://storefront.steampowered.com/Marketing/',
     b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/Steam/Marketing/",
     b"Messages URL 6"),
    (b'http://www.steampowered.com/index.php?area=news',
     b"http://" + octal_ip.encode('latin-1')+ http_port_neuter.encode('latin-1') + b"/index.php?area=news",
     b"News URL"),
    (b'http://storefront.steampowered.com/v/?client=1',
     b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/v/?client=1",
     b"Storefront URL 1"),
    (b'http://storefront.steampowered.com/v2/',
     b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/v2/",
     b"Storefront URL 1"),
    (b'http://store.steampowered.com',
     b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1'),
     b"Storefront URL 3"))
     
def replace_string_name_space(islan):
    if islan:
        if not config["http_name"] == "":
            octal_ip = config["http_name"]
        else:
            octal_ip = config["http_ip"]
        conn_ip = config["server_ip"]
        trk_ip = config["tracker_ip"]
    else:
        if not config["http_name"] == "":
            octal_ip = config["http_name"]
        else:
            octal_ip = config["public_ip"]
        conn_ip = config["public_ip"]
        trk_ip = config["public_ip"]
        
    replace_string_space = (
        (
        b'<h1><img src="http://steampowered.com/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Account Information</h1>',
        b'<h1><img src="http://' + octal_ip.encode('latin-1') + http_port_neuter.encode(
            'latin-1') + b'/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Account Information</h1>',
        b"New account logo 1"),
        (
        b'<img src="http://steampowered.com/img/print.gif" height="32" width="32" alt="STEAM" align="absmiddle"> <a href="javascript:window.print();">Click here to print this page now</a>',
        b'<img src="http://' + octal_ip.encode('latin-1') + http_port_neuter.encode(
            'latin-1') + b'/img/print.gif" height="32" width="32" alt="STEAM" align="absmiddle"> <a href="javascript:window.print();">Click here to print this page now</a>',
        b"New account logo 2"),
        (
        b'For more information about Steam accounts, see <a href="http://steampowered.com/?area=support">the support page</a>.<br><br>',
        b'For more information about Steam accounts, see <a href="http://' + octal_ip.encode(
            'latin-1') + http_port_neuter.encode('latin-1') + b'/?area=support">the support page</a>.<br><br>',
        b"New account logo 3"),
        (b"http://steampowered.com/img/steam_logo_onwhite.gif",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/img/steam_logo_onwhite.gif",
         b"New account logo 4"),
        (b"http://steampowered.com/img/print.gif",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/img/print.gif",
         b"New account logo 5"),
        (
        b'<h1><img src="http://steampowered.com/img/steam_logo_whiteongreen.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Account Information</h1>',
        b'<h1><img src="http://' + octal_ip.encode('latin-1') + http_port_neuter.encode(
            'latin-1') + b'/img/steam_logo_whiteongreen.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Account Information</h1>',
        b"New account logo 6"),
        (
        b'<img src="http://steampowered.com/img/print_ongreen.gif" height="32" width="32" alt="STEAM" align="absmiddle"> <a href="javascript:window.print();">Click here to print this page now</a>',
        b'<img src="http://' + octal_ip.encode('latin-1') + http_port_neuter.encode(
            'latin-1') + b'/img/print_ongreen.gif" height="32" width="32" alt="STEAM" align="absmiddle"> <a href="javascript:window.print();">Click here to print this page now</a>',
        b"New account logo 7"),
        (b"http://steampowered.com/img/steam_logo_whiteongreen.gif",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode(
             'latin-1') + b"/img/steam_logo_whiteongreen.gif",
         b"New account logo 8"),
        (b"http://steampowered.com/img/print_ongreen.gif",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/img/print_ongreen.gif",
         b"New account logo 9"),
        (
        b'<h1><img src="http://steampowered.com/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam - Receipt for credit card purchase</h1>',
        b'<h1><img src="http://' + octal_ip.encode('latin-1') + http_port_neuter.encode(
            'latin-1') + b'/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam - Receipt for credit card purchase</h1>',
        b"GCF URL 1"),
        (
        b'<h1><img src="http://steampowered.com/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam - Receipt for CD key subscription</h1>',
        b'<h1><img src="http://' + octal_ip.encode('latin-1') + http_port_neuter.encode(
            'latin-1') + b'/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam - Receipt for CD key subscription</h1>',
        b"GCF URL 2"),
        (
        b'<h1><img src="http://steampowered.com/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Game Details</h1>',
        b'<h1><img src="http://' + octal_ip.encode('latin-1') + http_port_neuter.encode(
            'latin-1') + b'/img/steam_logo_onwhite.gif" height="36" width="67" alt="STEAM" align="absmiddle"> Steam Game Details</h1>',
        b"GCF URL 3"),
        (b'"http://www.steampowered.com/"',
         b'"http://' + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b'/"',
         b"GCF URL 4"),
        (b'(http://steampowered.com/img/square.gif);',
         b'(http://' + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b'/img/square.gif);',
         b"GCF URL 5"),
        (b'"http://steampowered.com/img/steam_logo_onwhite.gif"',
         b'"http://' + octal_ip.encode('latin-1') + http_port_neuter.encode(
             'latin-1') + b'/img/steam_logo_onwhite.gif"',
         b"GCF URL 6"),
        (b'"http://steampowered.com/img/print.gif"',
         b'"http://' + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b'/img/print.gif"',
         b"GCF URL 7"),
        (b'"http://www.steampowered.com/video/requirements.php?game=240&l=english&vendorid=4098&deviceid=20042"',
         b'"http://' + octal_ip.encode('latin-1') + http_port_neuter.encode(
             'latin-1') + b'/video/requirements.php?game=240&l=english&vendorid=4098&deviceid=20042"',
         b"GCF URL 8"),
        (b'"http://www.steampowered.com/video/driverupdate.php?game=240&l=english&vendorid=4098&deviceid=20042"',
         b'"http://' + octal_ip.encode('latin-1') + http_port_neuter.encode(
             'latin-1') + b'/video/driverupdate.php?game=240&l=english&vendorid=4098&deviceid=20042"',
         b"GCF URL 9"),
        (b'"http://steampowered.com/?area=subscriber_agreement"',
         b'"http://' + octal_ip.encode('latin-1') + http_port_neuter.encode(
             'latin-1') + b'/?area=subscriber_agreement"',
         b"GCF URL 10"),
        (b'"http://steampowered.com/troubleshooter/live/en/s_bill_01.php"',
         b'"http://' + octal_ip.encode('latin-1') + http_port_neuter.encode(
             'latin-1') + b'/troubleshooter/live/en/s_bill_01.php"',
         b"GCF URL 11"),
        (b'"http://steampowered.com/?area=getsteamnow"',
         b'"http://' + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b'/?area=getsteamnow"',
         b"GCF URL 12"),
        (b'"http://www.steampowered.com/status/survey.html"',
         b'"http://' + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b'/status/survey.html"',
         b"GCF URL 13"),
        (b'http://www.steampowered.com/platform/update_history/"',
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b'/platform/update_history/"',
         b"Platform1 News URL"),
        (b'"207.173.178.42:1200"',
         b'"' + trk_ip.encode('latin-1') + b':1200"',
         b"Tracker IP 1"),
        (b'"207.173.178.43:1200"',
         b'"' + trk_ip.encode('latin-1') + b':1200"',
         b"Tracker IP 2"),
        (b'"207.173.178.44:1200"',
         b'"' + trk_ip.encode('latin-1') + b':1200"',
         b"Tracker IP 3"),
        (b'"207.173.178.45:1200"',
         b'"' + trk_ip.encode('latin-1') + b':1200"',
         b"Tracker IP 4"),
        (b'"207.173.177.10:27010"',
         b'"' + conn_ip.encode('latin-1') + b':27010"',
         b"HL Master Server 3"),
        (b'"half-life.west.won.net:27010"',
         b'"' + conn_ip.encode('latin-1') + b':27010"',
         b"HL Master Server 4"),
        (b'hlmaster.valvesoftware.com:27010',
         conn_ip.encode('latin-1') + b':27010',
         b"HL Master Server 5"),
        (b'half-life.east.won.net:27010',
         conn_ip.encode('latin-1') + b':27010',
         b"HL Master Server 6"),
        (b'"http://www.steampowered.com/?area=news"',
         b'"http://' + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/?area=news" + b'"',
         b"Steam news URL 1"),
    )
    #NEWS WORKS FROM URL 1
         
    return replace_string_space

def replace_string_name(islan):
    if islan:
        if not config["http_name"] == "":
            octal_ip = config["http_name"]
        else:
            octal_ip = config["http_ip"]
        conn_ip = config["server_ip"]
        trk_ip = config["tracker_ip"]
    else:
        if not config["http_name"] == "":
            octal_ip = config["http_name"]
        else:
            octal_ip = config["public_ip"]
        conn_ip = config["public_ip"]
        trk_ip = config["public_ip"]
        
    replace_string_name = (
        (b"http://www.steampowered.com/platform/banner/random.php",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/platform/banner/random.php",
         b"Banner URL"),
        (b"http://storefront.steampowered.com/platform/update_history/index.php",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + config["store_url_new"].encode(
             'latin-1') + b"/platform/update_history/index.php",
         b"Client news URL"),
        (b"http://www.steampowered.com/?area=news",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/?area=news",
         b"Steam news URL 2"),
        (b"http://www.steampowered.com/index.php?area=news",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/index.php?area=news",
         b"Steam news URL 3"),
        (b"http://www.steampowered.com/platform/friends/",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/platform/friends/",
         b"Tracker URL"),
        (b"http://www.steampowered.com/index.php?area=subscriber_agreement",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode(
             'latin-1') + b"/index.php?area=subscriber_agreement",
         b"SSA URL"),
        (b'http://storefront.steampowered.com/v/?client=1',
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + config["store_url_new"].encode(
             'latin-1') + b"/v/?client=1",
         b"Storefront URL 1"),
        (b"http://storefront.steampowered.com",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + config["store_url_new"].encode(
             'latin-1'),
         b"Storefront URL 2"),
        (b"http://support.steampowered.com",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + config[
             "support_url_new"].encode('latin-1'),
         b"Support URL"),
        (b"http://cdntest.steampowered.com/steamcommunity/beta/",
         b"http://" + config["community_ip"].encode('latin-1') + b"/steamcommunity/beta/",
         b"Community beta URL"),
        (b"http://localhost/community/public/",
         b"http://" + config["community_ip"].encode('latin-1') + b"/community/public/",
         b"Community local URL"),
        (b"http://media.steampowered.com/steamcommunity/public/",
         b"http://" + config["community_ip"].encode('latin-1') + b"/steamcommunity/public/",
         b"Community media URL"),
        (b"http://steamcommunity.com/",
         b"http://" + config["community_ip"].encode('latin-1') + b"/",
         b"Community URL"),
        (b"http://www.steampowered.com",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1'),
         b"Steampowered URL 1"),
        (b"http://store.steampowered.com",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1'),
         b"Steam Store URL"),
        (b"http://developer.valvesoftware.com/wiki/Main_Page",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1'),
         b"Dev Wiki URL"),
        (b"http://www.steampowered.com/platform/banner/",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/platform/banner/",
         b"New banner URL 1"),
        (b"http://cdn.steampowered.com/platform/banner/cs_25.html",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/platform/banner/cs_25.html",
         b"New banner URL 2"),
        (b"http://cdn.steampowered.com/platform/banner/",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/platform/banner/",
         b"New banner URL 3"),
        (b"StorefrontURL",
         b"StorefrontURM",
         b"Storefront redirector"),
        (b"SteamNewsURL",
         b"SteamNewsURM",
         b"Steam news redirector"),
        (b"media.steampowered.com" + b'\x00' + b'\x00',
         b"client-download.steampowered.com",
         b"Steam 2013 Package URL"),
        (b"http://steampowered.com/troubleshooter/",
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1') + b"/troubleshooter/",
         b"Troubleshooter"),
        (b'http://steampowered.com',
         b"http://" + octal_ip.encode('latin-1') + http_port_neuter.encode('latin-1'),
         b"SteamPowered URL 2"),
    )
         
    return replace_string_name

def replace_string(islan):
    if islan:
        if not config["http_name"] == "":
            octal_ip = config["http_name"]
        else:
            octal_ip = config["http_ip"]
        conn_ip = config["server_ip"]
        trk_ip = config["tracker_ip"]
    else:
        if not config["http_name"] == "":
            octal_ip = config["http_name"]
        else:
            octal_ip = config["public_ip"]
        conn_ip = config["public_ip"]
        trk_ip = config["public_ip"]

    replace_string = (
        (
        b"30820120300d06092a864886f70d01010105000382010d00308201080282010100d1543176ee6741270dc1a32f4b04c3a304d499ad0570777dba31483d01eb5e639a05eb284f93cf9260b1ef9e159403ae5f7d3997e789646cfc70f26815169a9b4ba4dc5700ea4480f78466eae6d2bdf5e4181da076ca2e95b32b79c016eb91b5f158e8448d2dd5a42f883976a935dcccbbc611dc2bdf0ea3b88ca72fba919501fb8c6187b4ecddbbb6623d640e819302a6be35be74460cbad9bff0ab7dff0c5b4b8f4aff8252815989ec5fffb460166c5a75b81dd99d79b05f23d97476eb3a5d44c74dcd1136e776f5d2bb52e77f530fa2a5ad75f16c1fb5d8218d71b93073bddad930b3b4217989aa58b30566f1887907ca431e02defe51d19489486caf033d020111",
        b"30820120300d06092a864886f70d01010105000382010d00308201080282010100" + config["main_key_n"][2 :].encode(
            'latin-1') + b"020111",
        b"Steam2 main RSA key (1024-bit)"),
        (
        b"\x30\x81\x9d\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x01\x05\x00\x03\x81\x8b\x00\x30\x81\x87\x02\x81\x81\x00\xda\xde\x57\xfe\x10\x99\xf9\x4b\x81\xb9\x0d\x00\x82\x50\x5b\xe3\x74\xca\x97\x28\xab\x9a\x88\x5b\x3b\x0e\x8e\x02\x5e\x43\xe5\xcc\xd8\x1b\x00\xcd\xbd\x05\xe2\x2a\xc2\x5c\x53\x18\xbf\x84\xc3\x40\x21\x42\xa5\xc3\x8a\xc3\xf4\x27\x1b\xab\xc3\xe5\xc0\x60\x18\xed\x26\x57\xf4\x68\xc5\xda\x55\xaa\x7e\x3b\x3b\x1a\xb2\x72\x06\x17\x4a\x85\x6e\xe2\xb6\x73\x91\x9d\xeb\x47\xbd\x49\x1d\x10\x21\x3e\x90\xdb\xd5\x6e\x25\x2c\xc6\xc9\xe9\x18\x8d\x0b\xc5\x71\x9b\x57\xed\x57\x02\xc6\x45\x5f\x27\x31\x6a\xa0\xaa\x03\x78\x2f\x06\xdf\x02\x01\x11",
        b"\x30\x81\x9d\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x01\x05\x00\x03\x81\x8b\x00\x30\x81\x87\x02\x81\x81\x00" + b"\xbf\x97\x3e\x24\xbe\xb3\x72\xc1\x2b\xea\x44\x94\x45\x0a\xfa\xee\x29\x09\x87\xfe\xda\xe8\x58\x00\x57\xe4\xf1\x5b\x93\xb4\x61\x85\xb8\xda\xf2\xd9\x52\xe2\x4d\x6f\x9a\x23\x80\x58\x19\x57\x86\x93\xa8\x46\xe0\xb8\xfc\xc4\x3c\x23\xe1\xf2\xbf\x49\xe8\x43\xaf\xf4\xb8\xe9\xaf\x6c\x5e\x2e\x7b\x9d\xf4\x4e\x29\xe3\xc1\xc9\x3f\x16\x6e\x25\xe4\x2b\x8f\x91\x09\xbe\x8a\xd0\x34\x38\x84\x5a\x3c\x19\x25\x50\x4e\xcc\x09\x0a\xab\xd4\x9a\x0f\xc6\x78\x37\x46\xff\x4e\x9e\x09\x0a\xa9\x6f\x1c\x80\x09\xba\xf9\x16\x2b\x66\x71\x60\x59" + b"\x02\x01\x11",
        b"Steam Beta main RSA key (512-bit)"),
        (
        b"30820120300d06092a864886f70d01010105000382010d0030820108028201010094db10802a3dcf16ad6755208bfb8fa411c6c290dd86dfbb14bf4fc621ee22689e97b37bc89e82dd20a92d191f5f18362031ccffdac814e01a94a2822ff68f25a79751b0084da37869ba50a9db586595bcfd7d97a952bdaa16b2c2a0629de272faa2f4d6b06132df02e3227c75731dc051a4582c36133b56fcb7b8469fe20cfe8d7111dbd3c7f05a2a238e25362dd4aef82a931801badbe7f1709d4d4bfa97cdf933cc769634d51cfb7af134a7d443938bb82a2074411567f2eaec5bc54716b785e118c93b21d9278f1b422d54debed21645adecd91fb63c41d6fc7632c3cd91b0423f4fdb0cc7697cf666d905a17b593b2e4434b9595aedc4683d29d494aca9020111",
        b"30820120300d06092a864886f70d01010105000382010d00308201080282010100" + config["main_key_n"][2 :].encode(
            'latin-1') + b"020111",
        b"Steam1 main RSA key (1024-bit)"),
        (
        b"30819d300d06092a864886f70d010101050003818b0030818702818100d3bb0de9bbab4becf8efc894c0723c54c3d7f8ff7bcef9f4d9c810668ca1cad7a292017c537bab1a68db17f8bd9a94751c2e37f30a7fab23c6a0443edd2d6896c1f5fcc89bb4e32291a44044777eb72c5e1ff1a9c113c75b49abdfd5bdc732c7807a18c836944279d63ef9bb4a38f50805b157ad32556e07e6575a112ca346ff020111",
        b"30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2 :].encode(
            'latin-1') + b"020111",
        b"Steam2 unknown RSA key 1 (512-bit), not replaced yet"),
        (
        b"30819d300d06092a864886f70d010101050003818b0030818702818100a7ed99f0b2eb868d94d67f6a9552a9bb5e909a724a086d88694dc74148833075e89afca13c4504b0cb304d7548c5cc0aa4f3d2fbbe9cdff173f22a0844e3702696a1ec7e930323185796fb55e1b6a2e08c337e84b21f0325af7537e7e6a43ff837d0694c6ce1ff86c1562096730d075a341111c4dc83570cf7c56f62cc04a9a9020111",
        b"30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2 :].encode(
            'latin-1') + b"020111",
        b"Steam1 unknown RSA key 1 (512-bit), not replaced yet"),
        (
        b"30819d300d06092a864886f70d010101050003818b0030818702818100bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059020111",
        b"30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2 :].encode(
            'latin-1') + b"020111",
        b"Steam1 unknown RSA key 2 (512-bit), not replaced yet"),
        (
        b"30819d300d06092a864886f70d010101050003818b0030818702818100bc265d3402562c8afb78904e7ec84ee5b6662a09216b6b50da4205094c54f8b09d211bdeb8219ca4df67e39d2349bcbe9cb3b0d1e18b23cf33b5b51cabbeaa529a27e2b3928bdbe1c5c5a7de6bee7e87aecfa26f82286cad35df7ee53fe12adb2d1e81e98ca5faa6db509de8c4f482fa3c4fcf875ce21d443ed635bbdcb425db020111",
        b"30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2 :].encode(
            'latin-1') + b"020111",
        b"Steam1 unknown RSA key 3 (512-bit), not replaced yet"),
        (
        b"30819d300d06092a864886f70d010101050003818b0030818702818100c8667b365a9801ed17ec2456a2a4b06377a943354064332c4ce558f43ad5980e16e462b9da48ba3797905d2681a6993d0a3aaaa1613bb78869894b96064edd4c54e8d1b5492937527c88ed98afeee3ee126dbcd98b9a8c8af038ecf3800ee1150c87235da973da40102d88248b61f6dcb4c40bbd48082c191eaefea0f85579dd020111",
        b"30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2 :].encode(
            'latin-1') + b"020111",
        b"Steam2 unknown RSA key 2 (512-bit), not replaced yet"),
        (
        b"30819D300D06092A864886F70D010101050003818B0030818702818100DFEC1AD62C10662C17353A14B07C59117F9DD3D82B7AE3E015CD191E46E87B8774A2184631A9031479828EE945A24912A923687389CF69A1B16146BDC1BEBFD6011BD881D4DC90FBFE4F527366CB9570D7C58EBA1C7A3375A1623446BB60B78068FA13A77A8A374B9EC6F45D5F3A99F99EC43AE963A2BB881928E0E714C04289020111",
        b"30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2 :].encode(
            'latin-1') + b"020111",
        b"Steam2 unknown RSA key 3 (512-bit), not replaced yet"),
        (
        b"30819D300D06092A864886F70D010101050003818B0030818702818100AED14BC0A3368BA0390B43DCED6AC8F2A3E47E098C552EE7E93CBBE55E0F1874548FF3BD56695B1309AFC8BEB3A14869E98349658DD293212FB91EFA743B552279BF8518CB6D52444E0592896AA899ED44AEE26646420CFB6E4C30C66C5C16FFBA9CB9783F174BCBC9015D3E3770EC675A3348F746CE58AAECD9FF4A786C834B020111",
        b"30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2 :].encode(
            'latin-1') + b"020111",
        b"Steam2 unknown RSA key 4 (512-bit), not replaced yet"),
        (
        b"30819D300D06092A864886F70D010101050003818B0030818702818100A8FE013BB6D7214B53236FA1AB4EF10730A7C67E6A2CC25D3AB840CA594D162D74EB0E724629F9DE9BCE4B8CD0CAF4089446A511AF3ACBB84EDEC6D8850A7DAA960AEA7B51D622625C1E58D7461E09AE43A7C43469A2A5E8447618E23DB7C5A896FDE5B44BF84012A6174EC4C1600EB0C2B8404D9E764C44F4FC6F148973B413020111",
        b"30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2 :].encode(
            'latin-1') + b"020111",
        b"Steam2 unknown RSA key 5 (512-bit), not replaced yet"),
        (
        b"30819D300D06092A864886F70D010101050003818B0030818702818100D0052CE98095CD3083A8E9259663CECC485D5C5200DB1E78D76A4C2CC8418CCC8746FB1BC9E86E4F7A6BC3E70FD5A95D6CD4EEA2CC805AD3CE5359E68091C4C0D5F06323916970C5BBBD05E24F7D9012EDAC4F86963C89CC921563CB5770B9C3AE084FC85616B00CC6C88A80D237F77FAB93BBE6DE9578B811C9E562ADBC0C87020111",
        b"30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2 :].encode(
            'latin-1') + b"020111",
        b"Steam2 unknown RSA key 6 (512-bit), not replaced yet"),
        (
        b"30819D300D06092A864886F70D010101050003818B00308187028181009E20ECC73E7722F42AD952210A59B9668CB3C615445F87504E12FD84D723958864DFBD2D1F4B9D5C918B34E9EA9C07AF0FB9E42940F78EB757AB730F3A4722DE4E06BD15D890D87E62ACB41CB2639F75C014CD72884C4D763E2EA553759CE62CD19831E697027E3C63D1282F3FD9C06DBB034CF4A34D85F13B8EB6F7FB9D1FA1020111",
        b"30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2 :].encode(
            'latin-1') + b"020111",
        b"Steam2 unknown RSA key 7 (512-bit), not replaced yet"),
        (
        b"30819D300D06092A864886F70D010101050003818B0030818702818100B1260881BDFE84463D88C6AB8DB914A2E593893C10508B8A5ABDF692E9A5419A3EDBAE86A052849983B75E3B425C18178B260003D857DF0B6505C6CF9C84F5859FCE3B63F1FB2D4818501F6C5FA4AD1430EEB081A74ABD74CD1F4AA1FCCA3B88DD0548AED34443CEB52444EAE9099AA4FE66B2E6224D02381C248025C7044079020111",
        b"30819d300d06092a864886f70d010101050003818b0030818702818100" + config["net_key_n"][2 :].encode(
            'latin-1') + b"020111",
        b"Real RSA key 1 (512-bit), not replaced yet"),
        (b"afakehost.example.com:27030 bfakehost.example.com:27030",
         conn_ip.encode('latin-1') + b":" + config["dir_server_port"].encode('latin-1') + b" " + conn_ip.encode(
             'latin-1') + b":" + config["dir_server_port"].encode('latin-1'),
         b"DNS directory server fallback"),
        (b"127.0.0.1" + (b'\x00' * 3) + b"207.173.176.215",
         conn_ip.encode('latin-1') + b'\x00' + b"207.173.176.215",
         b"DNS loopback directory server"),
        (b"68.142.92.67" + (b'\x00' * 3),
         b"888.888.888.888",
         b"CAS IP 1"),
        (b"68.142.92.66" + (b'\x00' * 3),
         b"888.888.888.889",
         b"CAS IP 2"),
        (b"207.173.176.132",
         b"888.888.888.890",
         b"CAS IP 3"),
        (b"207.173.176.131",
         b"888.888.888.891",
         b"CAS IP 4"),
        (
        b"207.173.176.216" + b'\x00' + b"207.173.179.87" + b'\x00\x00' + b"207.173.178.127" + b'\x00' + b"207.173.178.178",
        conn_ip.encode('latin-1') + b":" + config["dir_server_port"].encode('latin-1') + b'\x00' + conn_ip.encode(
            'latin-1') + b":" + config["dir_server_port"].encode('latin-1') + b'\x00' + conn_ip.encode(
            'latin-1') + b":" + config["dir_server_port"].encode('latin-1'),
        b"DNS extra directory servers"),
        (b"http://207.173.176.210/community/",
         b"http://" + config["community_ip"].encode('latin-1') + b"/community/",
         b"Community IP URL"),
        (b"207.173.177.11:27010",
         conn_ip.encode('latin-1') + b":27010",
         b"HL Master Server 1"),
        (b"207.173.177.12:27010",
         conn_ip.encode('latin-1') + b":27010",
         b"HL Master Server 2"),
        (b'207.173.177.45:27030 207.173.177.45:27030',
         conn_ip.encode('latin-1') + b":" + config["dir_server_port"].encode('latin-1') + b" " + conn_ip.encode(
             'latin-1') + b":" + config["dir_server_port"].encode('latin-1'),
         b"Steam1 directory server 1"),
        (b'207.173.177.45:27030 207.173.177.46:27030',
         conn_ip.encode('latin-1') + b":" + config["dir_server_port"].encode('latin-1') + b" " + conn_ip.encode(
             'latin-1') + b":" + config["dir_server_port"].encode('latin-1'),
         b"Steam1 directory server 2"),
        (b"gds1.steampowered.com:27030 gds2.steampowered.com:27030",
         conn_ip.encode('latin-1') + b":" + config["dir_server_port"].encode('latin-1') + b" " + conn_ip.encode(
             'latin-1') + b":" + config["dir_server_port"].encode('latin-1'),
         b"DNS directory server fallback"),
        (b"afakehost.example.com:27030 bfakehost.example.com:27030",
         conn_ip.encode('latin-1') + b":" + config["dir_server_port"].encode('latin-1') + b" " + conn_ip.encode(
             'latin-1') + b":" + config["dir_server_port"].encode('latin-1'),
         b"DNS directory server fallback"),
        (b"cm0.steampowered.com",
         conn_ip.encode('latin-1'),
         b"DNS content server fallback"),
        (b'"tracker.valvesoftware.com:1200"',
         b'"' + trk_ip.encode('latin-1') + b':1200"',
         b"Tracker DNS"),
    )
         
    return replace_string