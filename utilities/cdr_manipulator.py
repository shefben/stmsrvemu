import ast
import binascii
import os
import pprint
import shutil
import struct
import zlib

import globalvars
from utilities import blobs, encryption
from utils import log


def fixblobs():
	if os.path.isfile("files/cache/secondblob.bin"):
		with open("files/cache/secondblob.bin", "rb") as f:
			blob = f.read()
	elif os.path.isfile("files/2ndcdr.py") or os.path.isfile("files/secondblob.py"):
		if os.path.isfile("files/2ndcdr.orig"):
			# shutil.copy2("files/2ndcdr.py","files/2ndcdr.orig")
			os.remove("files/2ndcdr.py")
			shutil.copy2("files/2ndcdr.orig", "files/secondblob.py")
			os.remove("files/2ndcdr.orig")
		if os.path.isfile("files/2ndcdr.py"):
			shutil.copy2("files/2ndcdr.py", "files/secondblob.py")
			os.remove("files/2ndcdr.py")
		with open("files/secondblob.py", "r") as g:
			file = g.read()

		print("Fixing CDR")
		file = blobs.blob_replace(file, globalvars.replacestringsCDR)
		execdict = {}
		execdict_temp_01 = {}
		execdict_temp_02 = {}
		# execfile("files/2ndcdr.py", execdict)
		exec(file, execdict)

		for file in os.walk("files/custom"):
			for pyblobfile in file[2]:
				if (pyblobfile.endswith(".py") or pyblobfile.endswith(
						".bin")) and not pyblobfile == "2ndcdr.py" and not pyblobfile == "1stcdr.py" and not pyblobfile.startswith(
						"firstblob") and not pyblobfile.startswith("secondblob"):
					# if os.path.isfile("files/extrablob.py"):
					log.info("Found extra blob: " + pyblobfile)
					execdict_update = {}

					if pyblobfile.endswith(".bin"):
						f = open("files/custom/" + pyblobfile, "rb")
						blob = f.read()
						f.close()

						if blob[0:2] == b"\x01\x43":
							blob = zlib.decompress(blob[20:])
						blob2 = blobs.blob_unserialize(blob)
						blob3 = pprint.saferepr(blob2)
						execdict_update = "blob = " + blob3

						print("Fixing CDR 1")
						execdict_update = blobs.blob_replace(execdict_update, globalvars.replacestringsCDR)

					elif pyblobfile.endswith(".py"):
						with open("files/custom/" + pyblobfile, 'r') as m:
							userblobstr_upd = m.read()
						print("Fixing CDR 2")
						userblobstr_upd = blobs.blob_replace(userblobstr_upd, globalvars.replacestringsCDR)
						execdict_update = ast.literal_eval(userblobstr_upd[7:len(userblobstr_upd)])

					for k in execdict_update:
						for j in execdict["blob"]:
							if j == k:
								execdict["blob"][j].update(execdict_update[k])
							else:
								if k == b"\x01\x00\x00\x00":
									execdict_temp_01.update(execdict_update[k])
								elif k == b"\x02\x00\x00\x00":
									execdict_temp_02.update(execdict_update[k])

					for k, v in execdict_temp_01.items():
						execdict["blob"].pop(k, v)

					for k, v in execdict_temp_02.items():
						execdict["blob"].pop(k, v)

		blob = blobs.blob_serialize(execdict["blob"])

		if blob[0:2] == b"\x01\x43":
			blob = zlib.decompress(blob[20:])

		start_search = 0
		while True:
			found = blob.find(b"\x30\x81\x9d\x30\x0d\x06\x09\x2a", start_search)
			if found < 0:
				break

			foundstring = blob[found:found + 160]
			blob = blob.replace(foundstring, encryption.BERstring)
			start_search = found + 160

		compressed_blob = zlib.compress(blob, 9)
		blob = b"\x01\x43" + struct.pack("<QQH", len(compressed_blob) + 20, len(blob), 9) + compressed_blob

		# cache_option = self.config["use_cached_blob"]
		# if cache_option == "true":
		f = open("files/cache/secondblob.bin", "wb")
		f.write(blob)
		f.close()

	else:
		if os.path.isfile("files/secondblob.orig"):
			os.remove("files/secondblob.bin")
			shutil.copy2("files/secondblob.orig", "files/secondblob.bin")
			os.remove("files/secondblob.orig")
		with open("files/secondblob.bin", "rb") as g:
			blob = g.read()

		if blob[0:2] == b"\x01\x43":
			blob = zlib.decompress(blob[20:])
		blob2 = blobs.blob_unserialize(blob)
		blob3 = pprint.saferepr(blob2)
		file = "blob = " + blob3

		print("Fixing CDR 3")
		file = blobs.blob_replace(file, globalvars.replacestringsCDR)

		execdict = {}
		execdict_temp_01 = {}
		execdict_temp_02 = {}
		exec(file, execdict)

		for file in os.walk("files/custom"):
			for pyblobfile in file[2]:
				if (pyblobfile.endswith(".py") or pyblobfile.endswith(
						".bin")) and not pyblobfile == "2ndcdr.py" and not pyblobfile == "1stcdr.py" and not pyblobfile.startswith(
						"firstblob") and not pyblobfile.startswith("secondblob"):
					# if os.path.isfile("files/extrablob.py"):
					log.info("Found extra blob: " + pyblobfile)
					execdict_update = {}

					if pyblobfile.endswith(".bin"):
						f = open("files/custom/" + pyblobfile, "rb")
						blob = f.read()
						f.close()

						if blob[0:2] == b"\x01\x43":
							blob = zlib.decompress(blob[20:])
						blob2 = blobs.blob_unserialize(blob)
						blob3 = pprint.saferepr(blob2)
						execdict_update = "blob = " + blob3

						print("Fixing CDR 4")
						execdict_update = blobs.blob_replace(execdict_update, globalvars.replacestringsCDR)

					elif pyblobfile.endswith(".py"):
						with open("files/custom/" + pyblobfile, 'r') as m:
							userblobstr_upd = m.read()

						print("Fixing CDR 5")
						userblobstr_upd = blobs.blob_replace(userblobstr_upd, globalvars.replacestringsCDR)
						execdict_update = ast.literal_eval(userblobstr_upd[7:len(userblobstr_upd)])

					for k in execdict_update:
						for j in execdict["blob"]:
							if j == k:
								execdict["blob"][j].update(execdict_update[k])
							else:
								if k == b"\x01\x00\x00\x00":
									execdict_temp_01.update(execdict_update[k])
								elif k == b"\x02\x00\x00\x00":
									execdict_temp_02.update(execdict_update[k])

					for k, v in execdict_temp_01.items():
						execdict["blob"].pop(k, v)

					for k, v in execdict_temp_02.items():
						execdict["blob"].pop(k, v)

		blob = blobs.blob_serialize(execdict["blob"])

		# h = open("files/secondblob.bin", "wb")
		# h.write(blob)
		# h.close()

		# g = open("files/secondblob.bin", "rb")
		# blob = g.read()
		# g.close()

		if blob[0:2] == b"\x01\x43":
			blob = zlib.decompress(blob[20:])

		start_search = 0
		while True:
			found = blob.find(b"\x30\x81\x9d\x30\x0d\x06\x09\x2a", start_search)
			if found < 0:
				break

			foundstring = blob[found:found + 160]
			blob = blob.replace(foundstring, encryption.BERstring)
			start_search = found + 160

		compressed_blob = zlib.compress(blob, 9)
		blob = b"\x01\x43" + struct.pack("<QQH", len(compressed_blob) + 20, len(blob), 9) + compressed_blob

		# cache_option = self.config["use_cached_blob"]
		# if cache_option == "true":
		f = open("files/cache/secondblob.bin", "wb")
		f.write(blob)
		f.close()
	return blob


def fixblobs_configserver():
	if os.path.isfile("files/cache/secondblob.bin"):  # read cached bin
		with open("files/cache/secondblob.bin", "rb") as f:
			#print("read cached blob")
			blob = f.read()
	elif os.path.isfile("files/2ndcdr.py") or os.path.isfile("files/secondblob.py"):  # read py
		print("read py blob")
		if os.path.isfile("files/2ndcdr.orig"):
			# shutil.copy2("files/2ndcdr.py","files/2ndcdr.orig")
			os.remove("files/2ndcdr.py")
			shutil.copy2("files/2ndcdr.orig", "files/secondblob.py")
			os.remove("files/2ndcdr.orig")
		if os.path.isfile("files/2ndcdr.py"):
			shutil.copy2("files/2ndcdr.py", "files/secondblob.py")
			os.remove("files/2ndcdr.py")
		with open("files/secondblob.py", "r") as g:
			file = g.read()

		print("Fixing CDR 6")
		file = blobs.blob_replace(file, globalvars.replacestringsCDR)

		execdict = {}
		execdict_temp_01 = {}
		execdict_temp_02 = {}
		# execfile("files/2ndcdr.py", execdict)
		exec(file, execdict)

		for sub_id_main in execdict["blob"][b"\x02\x00\x00\x00"]:
			if b"\x17\x00\x00\x00" in execdict["blob"][b"\x02\x00\x00\x00"][sub_id_main]:
				sub_key = execdict["blob"][b"\x02\x00\x00\x00"][sub_id_main][b"\x17\x00\x00\x00"]
				# print(sub_key)
				if b"AllowPurchaseFromRestrictedCountries" in sub_key:
					sub_key.pop(b"AllowPurchaseFromRestrictedCountries")
					# print(sub_key)
				if b"PurchaseRestrictedCountries" in sub_key:
					sub_key.pop(b"PurchaseRestrictedCountries")
					# print(sub_key)
				if b"RestrictedCountries" in sub_key:
					sub_key.pop(b"RestrictedCountries")
					# print(sub_key)
				if b"OnlyAllowRestrictedCountries" in sub_key:
					sub_key.pop(b"OnlyAllowRestrictedCountries")
					# print(sub_key)
				if b"onlyallowrunincountries" in sub_key:
					sub_key.pop(b"onlyallowrunincountries")
					print(sub_key)
				if len(sub_key) == 0:
					execdict["blob"][b"\x02\x00\x00\x00"][sub_id_main].pop(b"\x17\x00\x00\x00")

		for file in os.walk("files/custom"):
			for pyblobfile in file[2]:
				if (pyblobfile.endswith(".py") or pyblobfile.endswith(".bin")) and not pyblobfile == "2ndcdr.py" and not pyblobfile == "1stcdr.py" and not pyblobfile.startswith("firstblob") and not pyblobfile.startswith("secondblob"):
					# if os.path.isfile("files/extrablob.py"):
					log.info("Found extra blob: " + pyblobfile)
					execdict_update = {}

					if pyblobfile.endswith(".bin"):
						f = open("files/custom/" + pyblobfile, "rb")
						blob = f.read()
						f.close()

						if blob[0:2] == b"\x01\x43":
							blob = zlib.decompress(blob[20:])
						blob2 = blobs.blob_unserialize(blob)
						blob3 = pprint.saferepr(blob2)
						execdict_update = "blob = " + blob3
						print("Fixing CDR 7")
						execdict_update = blobs.blob_replace(execdict_update, globalvars.replacestringsCDR)
					elif pyblobfile.endswith(".py"):
						with open("files/custom/" + pyblobfile, 'r') as m:
							userblobstr_upd = m.read()
							print("Fixing CDR 8")
						userblobstr_upd = blobs.blob_replace(userblobstr_upd, globalvars.replacestringsCDR)
						execdict_update = ast.literal_eval(userblobstr_upd[7:len(userblobstr_upd)])

					for k in execdict_update:
						for j in execdict["blob"]:
							if j == k:
								execdict["blob"][j].update(execdict_update[k])
							else:
								if k == b"\x01\x00\x00\x00":
									execdict_temp_01.update(execdict_update[k])
								elif k == b"\x02\x00\x00\x00":
									execdict_temp_02.update(execdict_update[k])

					for k, v in execdict_temp_01.items():
						execdict["blob"].pop(k, v)

					for k, v in execdict_temp_02.items():
						execdict["blob"].pop(k, v)

		blob = blobs.blob_serialize(execdict["blob"])

		if blob[0:2] == b"\x01\x43":
			blob = zlib.decompress(blob[20:])

		start_search = 0
		while True:
			found = blob.find(b"\x30\x81\x9d\x30\x0d\x06\x09\x2a", start_search)
			if found < 0:
				break

			foundstring = blob[found:found + 160]
			blob = blob.replace(foundstring, encryption.BERstring)
			start_search = found + 160

		compressed_blob = zlib.compress(blob, 9)
		blob = b"\x01\x43" + struct.pack("<QQH", len(compressed_blob) + 20, len(blob), 9) + compressed_blob

		# cache_option = self.config["use_cached_blob"]
		# if cache_option == "true":
		f = open("files/cache/secondblob.bin", "wb")
		f.write(blob)
		f.close()

	else:  # read bin
		log.info("Converting binary CDR to cache...")
		if os.path.isfile("files/secondblob.orig"):
			os.remove("files/secondblob.bin")
			shutil.copy2("files/secondblob.orig", "files/secondblob.bin")
			os.remove("files/secondblob.orig")
		with open("files/secondblob.bin", "rb") as g:
			blob = g.read()

		if blob[0:2] == b"\x01\x43":
			blob = zlib.decompress(blob[20:])
			log.warning("The first client waiting for this CDR might appear to have crashed")
		blob2 = blobs.blob_unserialize(blob)
		blob3 = pprint.saferepr(blob2)  # 1/5th of the time compared with using pprint.saferepr
		file = "blob = " + blob3
		print("Fixing CDR 9")
		for (search, replace, info) in globalvars.replacestringsCDR:
			# print "Fixing CDR 23"
			fulllength = len(search)
			newlength = len(replace)
			missinglength = fulllength - newlength
			if missinglength < 0:
				# print "WARNING: Replacement text " + replace + " is too long! Not replaced!"
				pass
			else:
				if isinstance(search, bytes):
					search = search.decode('latin-1')
				if isinstance(replace, bytes):
					replace = replace.decode('latin-1')
				file = file.replace(search, replace)
				# print("Replaced " + info + " " + sea

		execdict = {}
		execdict_temp_01 = {}
		execdict_temp_02 = {}
		# blob3 = pprint.saferepr(blob2)  # 1/5th of the time compared with using pprint.saferepr
		# file = "blob = " + blob3
		exec(file, execdict)
		for sub_id_main in execdict["blob"][b"\x02\x00\x00\x00"]:

			if b"\x17\x00\x00\x00" in execdict["blob"][b"\x02\x00\x00\x00"][sub_id_main]:
				sub_key = execdict["blob"][b"\x02\x00\x00\x00"][sub_id_main][b"\x17\x00\x00\x00"]
				# print(sub_key)
				if b"AllowPurchaseFromRestrictedCountries" in sub_key:
					sub_key.pop(b"AllowPurchaseFromRestrictedCountries")
					# print(sub_key)
				if b"PurchaseRestrictedCountries" in sub_key:
					sub_key.pop(b"PurchaseRestrictedCountries")
					# print(sub_key)
				if b"RestrictedCountries" in sub_key:
					sub_key.pop(b"RestrictedCountries")
					# print(sub_key)
				if b"OnlyAllowRestrictedCountries" in sub_key:
					sub_key.pop(b"OnlyAllowRestrictedCountries")
					# print(sub_key)
				if b"onlyallowrunincountries" in sub_key:
					sub_key.pop(b"onlyallowrunincountries")
					print(sub_key)
				if len(sub_key) == 0:
					execdict["blob"][b"\x02\x00\x00\x00"][sub_id_main].pop(b"\x17\x00\x00\x00")

		for sig in execdict["blob"][b"\x05\x00\x00\x00"]:  # replaces the old signature search, completes in less than 1 second now
			value = execdict["blob"][b"\x05\x00\x00\x00"][sig]
			# print(value)
			if len(value) == 160 and value.startswith(binascii.a2b_hex("30819d300d06092a")):
				execdict["blob"][b"\x05\x00\x00\x00"][sig] = encryption.BERstring
		for file in os.walk("files/custom"):
			for pyblobfile in file[2]:
				if (pyblobfile.endswith(".py") or pyblobfile.endswith(".bin")) \
						and not pyblobfile == "2ndcdr.py" \
						and not pyblobfile == "1stcdr.py" \
						and not pyblobfile.startswith("firstblob") \
						and not pyblobfile.startswith("secondblob"):

					# if os.path.isfile("files/extrablob.py"):
					log.info("Found extra blob: " + pyblobfile)
					execdict_update = {}

					if pyblobfile.endswith(".bin"):
						f = open("files/custom/" + pyblobfile, "rb")
						blob = f.read()
						f.close()

						if blob[0:2] == b"\x01\x43":
							blob = zlib.decompress(blob[20:])
						blob2 = blobs.blob_unserialize(blob)
						blob3 = pprint.saferepr(blob2)
						execdict_update = "blob = " + blob3
						print("Fixing CDR 10")
						execdict_update = blobs.blob_replace(execdict_update, globalvars.replacestringsCDR)

					elif pyblobfile.endswith(".py"):
						with open("files/custom/" + pyblobfile, 'r') as m:
							userblobstr_upd = m.read()
						print("Fixing CDR 11")
						userblobstr_upd = blobs.blob_replace(userblobstr_upd, globalvars.replacestringsCDR)

						execdict_update = ast.literal_eval(userblobstr_upd[7:len(userblobstr_upd)])

					for k in execdict_update:
						for j in execdict["blob"]:
							if j == k:
								execdict["blob"][j].update(execdict_update[k])
							else:
								if k == b"\x01\x00\x00\x00":
									execdict_temp_01.update(execdict_update[k])
								elif k == b"\x02\x00\x00\x00":
									execdict_temp_02.update(execdict_update[k])

					for k, v in execdict_temp_01.items():
						execdict["blob"].pop(k, v)

					for k, v in execdict_temp_02.items():
						execdict["blob"].pop(k, v)

		blob = blobs.blob_serialize(execdict["blob"])
		# print("serialize: " + repr(blob))
		# h = open("files/secondblob.bin", "wb")
		# h.write(blob)
		# h.close()

		# g = open("files/secondblob.bin", "rb")
		# blob = g.read()
		# g.close()

		if blob[0:2] == b"\x01\x43":
			blob = zlib.decompress(blob[20:])

		# start_search = 0
		# while True:
		#    found = blob.find("\x30\x81\x9d\x30\x0d\x06\x09\x2a", start_search)
		#    if found < 0:
		#        break

		# TINserver's Net Key
		# BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("9525173d72e87cbbcbdc86146587aebaa883ad448a6f814dd259bff97507c5e000cdc41eed27d81f476d56bd6b83a4dc186fa18002ab29717aba2441ef483af3970345618d4060392f63ae15d6838b2931c7951fc7e1a48d261301a88b0260336b8b54ab28554fb91b699cc1299ffe414bc9c1e86240aa9e16cae18b950f900f") + "\x02\x01\x11"
		# BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059") + b"\x02\x01\x11"
		#    BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex(self.config["net_key_n"][2:]) + "\x02\x01\x11"
		#    foundstring = blob[found:found + 160]
		#    blob = blob.replace(foundstring, BERstring)
		#    start_search = found + 160

		compressed_blob = zlib.compress(blob, 9)
		blob = b"\x01\x43" + struct.pack("<QQH", len(compressed_blob) + 20, len(blob), 9) + compressed_blob

		# cache_option = self.config["use_cached_blob"]
		# if cache_option == "true":
		f = open("files/cache/secondblob.bin", "wb")
		f.write(blob)
		f.close()
	return blob