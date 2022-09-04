from collections import namedtuple
from pprint import pprint

import fire
import scapy
from scapy.all import rdpcap
from scapy.layers.dns import DNSQR
from scapy.layers.http import HTTP
from scapy.layers.inet import TCP


class PcapHandler:
    """ Class for handling and extracting data from pcap file """

    def __init__(self, file_path):
        self.pcap = rdpcap(file_path)
        self.http_payload = self.generate_http_data()

    def generate_http_data(self) -> None:
        # Filter only HTTP sessions (by known port conventions)
        http_sessions = self.pcap.filter(
            lambda pkt: (TCP in pkt) and
                        ((pkt[TCP].sport == 80) or (pkt[TCP].dport == 80))
        ).sessions()

        conversations = {}
        http_payload = namedtuple("HttpSessionPayload", ["payload", "endtime"])

        # Iterate through http sessions iterable to build conversion
        for s_id, pkts in http_sessions.items():

            # Get the payload that was sent in the session (split into packets)
            payload = []
            for pkt in pkts:
                if (pkt[TCP].sport == 80 or pkt[TCP].dport == 80) and type(
                        pkt[TCP].payload) == scapy.layers.http.HTTP:
                    payload += bytes(pkt[TCP].payload).split(
                        b"\r\n")  # convert from bytes

            endtime = pkts[-1].time

            # Determine if this session is an HTTP Request or Response
            if pkts[0].dport == 80:
                # HTTP Request
                if s_id not in conversations.keys():
                    conversations[s_id] = {}
                conversations[s_id]["req"] = http_payload(payload=payload,
                                                          endtime=endtime)
            else:
                # Swap destination and source to match session id in Request
                s_id = s_id.split(" ")
                s_id[1], s_id[3] = s_id[3], s_id[1]
                s_id = " ".join(s_id)
                if s_id not in conversations.keys():
                    conversations[s_id] = {}
                conversations[s_id]["res"] = http_payload(payload=payload,
                                                          endtime=endtime)

        return conversations

    def show_report(self) -> None:
        print(
            f"Number of Packets in .pcap file: {len(self.pcap)}\n"
            f"Number of Sessions in .pcap file: {len(self.pcap.sessions())}\n"
            f"Number of DNS Queries in .pcap file: {len(self.pcap[DNSQR])}\n"
            f"HTTP payload generate from .pcap file: \n"
        )
        pprint(self.http_payload)


def main(filename: str) -> None:
    """ Main function """
    pcap = PcapHandler(filename)
    pcap.show_report()


if __name__ == '__main__':
    fire.Fire(main)
