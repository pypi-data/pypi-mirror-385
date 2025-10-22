#!/usr/bin/env python3

import os
import logging
import argparse
import psutil
import re
import alsaaudio
import sys
from pyudev import Context, Devices

# Parse arguments
parser = argparse.ArgumentParser(
    description="Real-Time Config IRQ Udev Service. Set RT priorities of IRQs "
                "of audio devices using udev")
parser.add_argument("-c", "--configuration",
                    default="/etc/rtcirqus.d/rtcirqus.conf",
                    help="Path to configuration file [/etc/rtcirqus.d/"
                         "rtcirqus.conf]")
parser.add_argument("-p", "--priority",
                    default=90,
                    help="Maximum priority to set [90]")
parser.add_argument("-s", "--step",
                    default=5,
                    help="Steps between priorities [5]")
parser.add_argument("-a", "--action",
                    default="add",
                    help="Action to perform, add or remove")
parser.add_argument("-d", "--dev-path",
                    help="udev device path")

args = parser.parse_args()

# Set variables
udev_action = args.action
udev_dev_path = args.dev_path
conf = {}
conf["file"] = args.configuration
conf["prio_max"] = args.priority
conf["prio_step"] = args.step
conf["options"] = ["deny_list", "prio_list", "prio_max", "prio_step"]
conf["deny_list"] = []
conf["prio_list"] = []
irq_re = re.compile(r"irq\/\d+-(audiodsp|snd|[e,u,x]hci_hcd)")
snd = {}
snd["card_indexes"] = alsaaudio.card_indexes()
snd["cards"] = [
    dict([
        ("name", card[0]), ("description", card[1]), ("index", card[2])]
    ) for card in [
        alsaaudio.card_name(index) + (index,) for index in
        snd["card_indexes"]]]
udev_context = Context()
snd["usb_cards"] = []
snd["onboard_cards"] = []
procs = {proc.info["name"]: proc.info["pid"] for proc in psutil.process_iter(
    ["name", "pid"])}

# Set default logging level
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


class Rtcirqus:
    # Check if we're running as root
    def check_root(self):
        if os.getuid() != 0:
            logging.error("Not running as root. rtcirqus needs to be run as "
                          "root in order to set IRQ priorities")

            sys.exit(1)

    # Read configuration file
    def read_config(self):
        if os.path.exists(conf["file"]):
            with open(conf["file"], "r") as f:
                for line in f.readlines():
                    if not line.startswith("#"):
                        key, value = line.split("=")[0].strip(), \
                                      line.split("=")[1].strip()
                        if "_list" in key:
                            conf[key] = [
                                value.strip() for value in value.split(",")]
                        elif key in conf["options"]:
                            conf[key] = int(value.strip())
        else:
            logging.warning(
                "No configuration file found, continuing with defaults")

    # Sort audio devices if defined in configuration file
    def sort_cards(self):
        snd["cards_sorted"] = sorted(
           snd["cards"],
           key=lambda x: conf["prio_list"].index(x["name"]) if
           x["name"] in conf["prio_list"] else True)

        snd["card_indexes_sorted"] = [y["index"] for y in snd["cards_sorted"]]

        snd["dev_paths"] = [
            Devices.from_name(
                udev_context, "sound", f"card{index}").device_path for index in
            snd["card_indexes_sorted"]]

    # Check if kernel runs with threadirqs parameter and if threaded IRQs of
    # audio devices are actually available
    def check_threadirqs(self):
        for proc_name in procs:
            if irq_re.match(proc_name):
                irq_match = True

        with open("/proc/cmdline", "r") as f:
            kernel_cmdline = f.readline().strip().split()

        if "threadirqs" in kernel_cmdline and irq_match:
            logging.info("Loaded kernel is using threaded IRQs and "
                         "threaded IRQ processes detected")

        else:
            logging.info("Loaded kernel is not using threaded IRQs, no "
                         "'threadirqs' parameter found.")

    # Create lists of USB and onboard audio devices
    def detect_cards(self):
        for card in snd["cards"]:
            if "usb-" in card["description"]:
                snd["usb_cards"].append(card)
            else:
                snd["onboard_cards"].append(card)

        if len(snd["onboard_cards"]) > 0:
            logging.info(
                "Onboard cards found: "
                f"{', '.join([card['name'] for card in snd['onboard_cards']])}"
            )

        if len(snd["usb_cards"]) > 0:
            logging.info(
                "USB cards found: "
                f"{', '.join([card['name'] for card in snd['usb_cards']])}"
            )

    # Get IRQs of audio devices and pass these on to the relevant functions
    def get_irq(self):
        if udev_action == "add":
            for dev_path in snd["dev_paths"]:
                split_dev_path = re.split(
                    r"([a-z_]+/sound|sound|usb\d+)", dev_path)[0]
                card_index = int(dev_path.split("/")[-1].removeprefix("card"))
                irq_root_path = f"/sys{split_dev_path}"
                irq_path = f"{irq_root_path}irq"

                if os.path.exists(f"{irq_root_path}msi_irqs"):
                    msi_irqs = True
                else:
                    msi_irqs = False

                if "usb" in dev_path:
                    card_type = "USB"
                else:
                    card_type = "onboard"

                card_name = alsaaudio.card_name(card_index)[0]

                if card_name not in conf["deny_list"] \
                        and os.path.exists(irq_path):
                    if msi_irqs:
                        irq = sorted(
                            os.listdir(f"{irq_root_path}msi_irqs"))[0]
                    else:
                        with open(irq_path, "r") as f:
                            irq = f.readline().strip()

                    logging.info(
                        f"Setting RT priority {conf['prio_max']} for "
                        f"{card_type} card {card_name} with IRQ {irq}")

                    self.set_rt_prio(irq, conf["prio_max"])

                    conf["prio_max"] = conf["prio_max"] - conf["prio_step"]

        if udev_action == "remove":
            self.unset_rt_prio()

    # Set real-time priority of threaded IRQs of audio devices
    def set_rt_prio(self, irq, prio_rt):
        os_sched = os.SCHED_FIFO

        for proc_name in procs:
            if irq_re.match(proc_name) and irq in proc_name:
                proc_pid = procs[proc_name]
                os_sched_param = os.sched_param(int(prio_rt))
                os.sched_setscheduler(proc_pid, os_sched, os_sched_param)

    def unset_rt_prio(self):
        split_re = re.split(r"(sound|usb\d+)", udev_dev_path)[0]
        irq_root_path = f"/sys{split_re}"
        irq_path = f"{irq_root_path}irq"

        if os.path.exists(f"{irq_root_path}msi_irqs"):
            irq = sorted(
                os.listdir(f"{irq_root_path}msi_irqs"))[0]
        else:
            with open(irq_path, "r") as f:
                irq = f.readline().strip()

        self.set_rt_prio(irq, 50)

    def main(self):
        self.read_config()
        self.sort_cards()
        self.check_threadirqs()
        self.detect_cards()
        self.check_root()
        self.get_irq()


def main():
    app = Rtcirqus()
    app.main()


if __name__ == "__main__":
    main()
