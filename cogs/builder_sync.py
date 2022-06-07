from interactions.ext.tasks import IntervalTrigger, create_task
from variables import server, builder_non_confirme, builder
import interactions
import requests
from datetime import datetime
import os

CACHED_IDS = []


class BuilderSync(interactions.Extension):
    def __init__(self, client: interactions.Client):
        self.client: interactions.Client = client
        self.synchronize_builders.start(self)

    @create_task(IntervalTrigger(5 * 60))
    async def synchronize_builders(self):
        date = datetime.now().strftime("%H:%M")
        print(f"[{date}] Synchronizing builders...")
        try:
            api_key = os.environ["BTE_API_KEY"]
        except KeyError:
            print("BTE API key not found, cannot synchronize builders!")
            return
        headers = {
            "Host": "buildtheearth.net",
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }
        try:
            response = requests.get(
                "https://buildtheearth.net/api/v1/members", headers=headers
            ).json()
        except Exception as e:
            print("Error while accessing BTE API:\n ", e)
        else:
            for user in response["members"]:
                if user["discordId"] in CACHED_IDS:  # User was already added, skipping to not hit ratelimit
                    continue

                member_dict: dict = await self.client._http.get_member(server, user["discordId"])
                if member_dict.get("message", None) is not None:  # This user is not in the Discord server
                    continue
                member = interactions.Member(**member_dict, _client=self.client._http)

                if str(builder) not in member._json["roles"]:
                    await member.add_role(role=builder, guild_id=server, reason="Automatically added as a Builder!")
                    await member.remove_role(role=builder_non_confirme, guild_id=server, reason="Automatically added as a Builder!")
                    print(f"Added {user['discordTag']} as a Builder!")

                CACHED_IDS.append(user["discordId"])


def setup(client: interactions.Client):
    BuilderSync(client)
