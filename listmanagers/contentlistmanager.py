import datetime
import pprint
import threading
import logging
from builtins import object

log = logging.getLogger("CSLSTHNDLR")
class ContentServerManager(object):
    contentserver_list = []
    lock = threading.Lock()

    def add_contentserver_info(self, wan_ip, lan_ip, port, region,
                               received_applist, is_permanent = 0, is_pkgcs = False):
        if not all([wan_ip, lan_ip, port, region]):
            log.error("Missing required server information.")
            return False
        current_time = datetime.datetime.now()
        if is_pkgcs is True:
            entry = (wan_ip, lan_ip, port, region, current_time, [],
                     is_permanent, is_pkgcs)
        else:
            entry = (wan_ip, lan_ip, port, region, current_time, received_applist,
                     is_permanent, is_pkgcs)
        with self.lock:
            self.contentserver_list.append(entry)
            log.info(f"{wan_ip} added to Content Directory Server List")

    def remove_old_entries(self):
        removed_entries = []
        current_time = datetime.datetime.now()
        with self.lock:
            for entry in self.contentserver_list:
                timestamp = entry[4]
                time_diff = current_time - timestamp
                if time_diff.total_seconds() > 3600 and not entry[6]:  # Check if older than 60 minutes (3600 seconds)
                    self.contentserver_list.remove(entry)
                    removed_entries.append(entry)
        if len(removed_entries) == 0:
            return 0  # No entries were removed
        else:
            return 1  # Entries were successfully removed

    def get_empty_or_no_applist_entries(self, islan):
        empty_entries = []
        with self.lock:
            for entry in self.contentserver_list:
                if not entry[5] or len(entry[5]) == 0: # TODO change to use entry[7] aka is_pkgcs
                    if not islan:
                        empty_entries.append((entry[0], entry[2]))
                    else:
                        empty_entries.append((entry[1], entry[2])) # Add LAN IP address and port to matches
        count = len(empty_entries)
        if count > 0:
            return empty_entries, count
        else:
            return None, 0  # No entries found

    def find_ip_address(self, region=None, appid=None, version=None, islan = 0):
        if not region and not appid and not version:  # Check if all arguments are empty or None
            if not islan:
                all_entries = [(entry[0], entry[2]) for entry in self.contentserver_list]
            else:
                all_entries = [(entry[1], entry[2]) for entry in self.contentserver_list] # Add LAN IP address and port to matches
            count = len(all_entries)
            if count > 0:
                return all_entries, count
            else:
                return None, 0  # No entries found
        else:
            matches = []
            with self.lock:
                for entry in self.contentserver_list:
                    if entry[5] is not None or entry[5] != "":
                        if region and entry[3] == region:
                            for app_entry in entry[5]:
                                if app_entry[0] == appid and app_entry[1] == version:
                                    if not islan :
                                        matches.append((entry[0], entry[2]))  # Add IP address and port to matches
                                    else :
                                        matches.append((entry[1], entry[2]))  # Add LAN IP address and port to matches
                        elif appid and version:
                            for app_entry in entry[5]:
                                if app_entry[0] == appid and app_entry[1] == version:
                                    if not islan:
                                        matches.append((entry[0], entry[2]))  # Add IP address and port to matches
                                    else:
                                        matches.append((entry[1], entry[2]))  # Add LAN IP address and port to matches
            count = len(matches)
            if count > 0:
                return matches, count
            else:
                return None, 0  # No matching entries found

    def remove_entry(self, wan_ip, lan_ip, port, region):
        with self.lock:
            for entry in self.contentserver_list:
                if entry[0] == wan_ip and entry[1] == lan_ip and entry[2] == port and entry[3] == region:
                    self.contentserver_list.remove(entry)
                    return True
        return False

    def print_contentserver_list(self, printapps=0):
        with self.lock:
            for entry in self.contentserver_list:
                print("WAN IP Address:", entry[0])
                print("LAN IP Address:", entry[1])
                print("Port:", entry[2])
                print("Region:", entry[3])
                if printapps == 1:
                    print("App List:")
                    for app_entry in entry[5]:
                        print("App ID:", app_entry[0])
                        print("Version:", app_entry[1])
                else:
                    appcount = 0
                    for app_entry in entry[5]:
                        appcount += 1
                    print("Number of Apps Available: " + str(appcount))
                print("--------------------")


manager = ContentServerManager()