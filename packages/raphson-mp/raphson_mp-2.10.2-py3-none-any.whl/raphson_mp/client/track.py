from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from raphson_mp.client.share import Share
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.track import AudioFormat, TrackBase
from raphson_mp.common.util import urlencode

if TYPE_CHECKING:
    from raphson_mp.client import RaphsonMusicClient


@dataclass(kw_only=True)
class DownloadedTrack:
    track: Track
    audio: bytes
    image: bytes


class NoNewsAvailableError(Exception):
    pass


class Track(TrackBase):
    async def get_audio(self, client: RaphsonMusicClient, audio_format: AudioFormat) -> bytes:
        async with client.session.get(
            "/track/" + urlencode(self.path) + "/audio?type=" + audio_format.value
        ) as response:
            return await response.content.read()

    async def get_cover_image(
        self,
        client: RaphsonMusicClient,
        img_quality: ImageQuality | None = None,
        img_format: ImageFormat | None = None,
        meme: bool | None = None,
    ) -> bytes:
        params: dict[str, str] = {}
        if img_quality:
            params["quality"] = img_quality.value
        if img_format:
            params["format"] = img_format.value
        if meme:
            params["meme"] = "1" if meme else "0"

        async with client.session.get(
            "/track/" + urlencode(self.path) + "/cover",
            params=params,
        ) as response:
            return await response.content.read()

    async def share(self, client: RaphsonMusicClient) -> Share:
        async with client.session.post("/share/create", json={"track": self.path}) as response:
            code = (await response.json())["code"]
            return Share(code, client.session)

    async def download(
        self,
        client: RaphsonMusicClient,
        audio_format: AudioFormat = AudioFormat.WEBM_OPUS_HIGH,
        img_quality: ImageQuality | None = None,
        img_format: ImageFormat | None = None,
    ) -> DownloadedTrack:
        audio, image = await asyncio.gather(
            self.get_audio(client, audio_format),
            self.get_cover_image(client, img_quality=img_quality, img_format=img_format),
        )
        return DownloadedTrack(track=self, audio=audio, image=image)
