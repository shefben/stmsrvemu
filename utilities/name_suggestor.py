import os
import random
import struct
import globalvars
from config import read_config


config = read_config()

def load_modifiers_from_files():
	file_paths = {
		"suggestion_prepend.txt": [],
		"suggestion_append.txt": []
	}

	for file_path, modifiers_list in file_paths.items():
		try:
			with open(file_path, 'r') as file:
				modifiers_list.extend(line.strip() for line in file if line.strip())
		except IOError as e:
			pass

	if config["use_builtin_suggested_name_modifiers"].lower() == "true":
		globalvars.prepended_modifiers += [
				"mc", "cool", "star", "pro", "king", "ninja", "ace", "neo", "tech",
				"nova", "sky", "galaxy", "phantom", "Mr_", "elite", "shadow", "cyber",
				"quantum", "ethereal", "mystic", "wizard", "echo", "terra", "aqua",
				"pyro", "frost", "thunder", "drift", "flux", "banned", "dumb",
				"generic_", "gooey", "stinky", "raunchy", "putrid", "brother_",
				"nasty", "ultra", "mega", "super", "hyper", "dark", "chaos", "lucky",
				"quick", "sneaky", "crazy", "furious", "silent", "rapid", "chronic",
				"stormy", "wild", "ancient", "legendary", "ghost", "frosty", "the_phallic",
				"hard", "crunchy", "ugly", "crunchy", "re"
			]
		globalvars.appended_modifiers += [
				"rific", "dream", "_the_womanizer", "transvester",
				"_the_unlikable", "_the_terrible", "orama", "ler", "ing",
				"son",  "_jr",  "ifier", "ny", "y", "ji", "man", "zilla",
				"nator", "saures", "ton", "ious", "zen", "wick", "son",
				"leigh", "wood", "smith", "max", "dex", "ley", "nator",
				"able", "stein", "knight", "_the_cog", "s_boner", "_the_pipelayer"
			]

	globalvars.prepended_modifiers += file_paths["suggestion_prepend.txt"]
	globalvars.appended_modifiers += file_paths["suggestion_append.txt"]


def similar_username_generator(base_username, number_of_usernames):
	suggestions = set()

	# Convert append_modifiers to a list if it's a set
	append_modifiers = list(globalvars.appended_modifiers)
	prepend_modifiers = list(globalvars.prepended_modifiers)
	while len(suggestions) < number_of_usernames:
		# Random username generation logic
		rand_prependmodifier = random.choice(prepend_modifiers)
		rand_appendmodified = random.choice(append_modifiers)
		action = random.choice(['append', 'prepend', 'both', 'none'])

		if action == 'append':
			new_username = base_username + rand_appendmodified
		elif action == 'prepend':
			new_username = rand_prependmodifier + base_username
		elif action == 'both':
			new_username = rand_prependmodifier + base_username + rand_appendmodified
		else:
			new_username = base_username

		# Apply leet speak and number appending
		new_username = randomize_username(new_username)
		if new_username == base_username:
			new_username = randomize_username(random.choice(prepend_modifiers) + new_username)

		if (os.path.isfile("files/users/" + new_username + ".py")):
			new_username = randomize_username(new_username) + rand_appendmodified

		suggestions.add(new_username)

	# Convert set to the required dictionary format
	suggestedname = {}
	for i, name in enumerate(suggestions):
		key = struct.pack('<I', i)
		suggestedname[key] = name.encode('utf-8') + b'\x00'

	return suggestedname
def randomize_username(username):
	new_username_chars = list(username)
	leet_speak = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 't': '7'}
	# Leet speak replacement (up to 4 letters)
	if random.choice([True, False]):
		eligible_positions = [i for i, char in enumerate(new_username_chars) if char in leet_speak]
		leet_positions = random.sample(eligible_positions, min(2, len(eligible_positions)))
		i = 0
		for pos in leet_positions:
			if random.choice([True, False]):
				new_username_chars[pos] = leet_speak[new_username_chars[pos]]
			i += 1
			if i >= 2:
				break

	# Append a random number at the end
	if random.choice([True, False]):
		num = str(random.randint(0, 9999))
		new_username_chars.append(num)

	return ''.join(new_username_chars)