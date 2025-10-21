def do_something_useful():
    print("Replace this with a utility function")


#################################################################
import logging
from pathlib import Path
import sys
import time

import xdb_location.xdb.maker as mk
import xdb_location.xdb.index as idx

# Format log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s-%(name)s-%(lineno)s-%(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)


def print_help():
    print("ip2region xdb python maker")
    print("{} [command] [command options]".format(sys.argv[0]))
    print("Command: ")
    print("  gen      generate the binary db file")


def gen_db(src: str, dst: str):
    src_file, dst_file = src, dst
    index_policy = idx.Vector_Index_Policy
    # Check input parameters
    print("########")
    # print(sys.argv)
    # for i in range(2, len(sys.argv)):
    #     r = sys.argv[i]
    #     if len(r) < 5:
    #         continue
    #     if not r.startswith("--"):
    #         continue
    #     s_idx = r.index("=")
    #     if s_idx < 0:
    #         print("missing = for args pair '{}'".format(r))
    #         return
    #     if r[2:s_idx] == "src":
    #         src_file = r[s_idx + 1 :]
    #     elif r[2:s_idx] == "dst":
    #         dst_file = r[s_idx + 1 :]
    #     elif r[2:s_idx] == "index":
    #         index_policy = idx.index_policy_from_string(r[s_idx + 1 :])
    #     else:
    #         print("undefined option `{}`".format(r))
    #         return
    # if src_file == "" or dst_file == "":
    #     print("{} gen [command options]".format(sys.argv[0]))
    #     print("options:")
    #     print(" --src string    source ip text file path")
    #     print(" --dst string    destination binary xdb file path")
    #     return

    start_time = time.time()
    # Make the binary file
    maker = mk.new_maker(index_policy, src_file, dst_file)
    maker.init()
    maker.start()
    maker.end()

    logging.info(
        "Done, elapsed: {:.0f}m{:.0f}s".format(
            (time.time() - start_time) / 60, (time.time() - start_time) % 60
        )
    )


def rebuild_ip2region():
    # dbPath = Path(__file__).parent / "xdb" / "ip2region.xdb"
    # logging.info("sys.argv:"+ sys.argv)
    # if len(sys.argv) < 2:
    #     print_help()
    #     return
    

    # cmd = sys.argv[1].lower()
    # if cmd == "gen":
    #     gen_db()
    # else:
    #     print_help()
    print_help()
    # gen_db()
