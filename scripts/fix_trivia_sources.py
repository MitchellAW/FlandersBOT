import argparse
import asyncio
import json
from urllib.parse import urlparse

import aiohttp
import anyio
from compuglobal import Frinkiac, Morbotron

CGHMC_URLS = ["https://frinkiac.com", "https://morbotron.com"]


def get_cghmc_host(url: str | list[str] | None) -> str | None:
    if url is None or isinstance(url, list):
        return None
    return urlparse(url).hostname


def get_episode_timestamp(url: str | list[str] | None) -> tuple[str, int] | tuple[None, None]:
    if url is None or isinstance(url, list):
        return None, None

    episode, timestamp = urlparse(url).path.strip("/").split("/")[-2:]
    return episode, int(timestamp.strip(".jpg"))


async def fix_sources(session: aiohttp.ClientSession, file_name: str) -> None:
    api_lookup = {
        "frinkiac.com": Frinkiac(session=session),
        "morbotron.com": Morbotron(session=session),
    }

    async with await anyio.open_file(f"flanders/cogs/data/{file_name}") as trivia_file:
        trivia_data = await trivia_file.read()
        questions = json.loads(trivia_data)

    new_question_data = []
    for i, question in enumerate(questions):
        if i % 5 == 0:
            print(f"Progress: {i / len(questions) * 100:.2f} %")

        current_question = question.copy()
        source = question.get("source")
        host = get_cghmc_host(source)
        if host in api_lookup:
            episode, timestamp = get_episode_timestamp(source)
            api = api_lookup.get(host)

            if episode is not None and timestamp is not None and api is not None:
                frames = await api.get_frames(episode, timestamp, before=1000, after=1000)

                if len(frames) > 0:
                    closest = min(frames, key=lambda frame: frame.timestamp - timestamp)
                    new_source_url = f"https://{host}/caption/{episode}/{closest.timestamp}"
                    current_question.update({"source": new_source_url})

                else:
                    print(f"No nearby frames found for: {i}. {current_question.get('question')}\n{source}")

            else:
                print(f"Could not parse api, episode or timestamp for question {i} from {source}")

        else:
            print(f"Host {host} not in list of hosts")

        new_question_data.append(current_question)
        async with await anyio.open_file(f"flanders/cogs/data/fixed_{file_name}", "w") as output_json:
            json_dump = json.dumps(new_question_data, indent=4)
            await output_json.write(json_dump)

    print(f"Completed writing all new sources to flanders/cogs/data/{file_name}")


async def main(file_name: str) -> None:
    async with aiohttp.ClientSession() as session:
        await fix_sources(session=session, file_name=file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str)
    args = parser.parse_args()

    asyncio.run(main(args.file))
