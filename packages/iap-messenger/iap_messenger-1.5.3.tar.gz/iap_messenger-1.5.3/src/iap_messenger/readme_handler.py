import os
import nats.errors as nats_errors
import logging
import asyncio

LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=LEVEL,
    force=True,
    format="%(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

LOGGER = logging.getLogger("iap-messenger")
LOGGER.propagate = True

async def wait_readme(sub_in, send_msg):
    '''
    Handle readme requests
    '''
    subject = sub_in.subject.replace(".*.*", "")
    l_sub = len(subject) + 1
    readme = ""
    readme_path = ""
    if os.path.exists("/app/README.md"):
        readme_path = "/app/README.md"
    elif os.path.exists("/README.md"):
        readme_path = "/README.md"
    elif os.path.exists("/app/README.txt"):
        readme_path = "/app/README.txt"
    elif os.path.exists("/README.txt"):
        readme_path = "/README.txt"
    elif os.path.exists("/app/README"):
        readme_path = "/app/README"
    elif os.path.exists("/README"):
        readme_path = "/README"
    elif os.path.exists("/app/Readme.md"):
        readme_path = "/app/Readme.md"
    elif os.path.exists("/Readme.md"):
        readme_path = "/Readme.md"
    elif os.path.exists("/app/Readme.txt"):
        readme_path = "/app/Readme.txt"
    elif os.path.exists("/Readme.txt"):
        readme_path = "/Readme.txt"
    elif os.path.exists("/app/Readme"):
        readme_path = "/app/Readme"
    elif os.path.exists("/Readme"):
        readme_path = "/Readme"
    elif os.path.exists("/app/readme.md"):
        readme_path = "/app/readme.md"
    elif os.path.exists("/readme.md"):
        readme_path = "/readme.md"
    elif os.path.exists("/app/readme.txt"):
        readme_path = "/app/readme.txt"
    elif os.path.exists("/readme.txt"):
        readme_path = "/readme.txt"
    elif os.path.exists("/app/readme"):
        readme_path = "/app/readme"
    elif os.path.exists("/readme"):
        readme_path = "/readme"

    if readme_path != "":
        with open(readme_path, "r") as f:
            readme = f.read()

    while True:
        try:
            msg = await sub_in.next_msg(timeout=600)
            await msg.respond("".encode("utf-8"))
            uid = msg.subject[(l_sub):]
        except nats_errors.TimeoutError:
            continue
        except TimeoutError:
            continue
        except nats_errors.ConnectionClosedError:
            LOGGER.error(
                "Fatal error message handler: ConnectionClosedError")
            break
        except asyncio.CancelledError:
            LOGGER.error(
                "Fatal error message handler: CancelledError")
            break
        except Exception as e:  # pylint: disable=W0703
            LOGGER.error("Unknown error:", exc_info=True)
            LOGGER.debug(e)
            continue
        # Message received
        data = readme.encode("utf-8")
        await send_msg("readme-out", uid, "text", data)
