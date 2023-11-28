from pytube import YouTube
from moviepy.editor import *
import openai
import os
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

class YoutubeSummary(APIView):
    def __init__(self):
        super().__init__()
        load_dotenv()

    def extract_youtube_video_id(self, url: str) -> str | None:
        found = re.search(r"(?:youtu\.be\/|watch\?v=)([\w-]+)", url)
        if found:
            return found.group(1)
        return None
    def get_video_transcript(self, video_id: str, language: str = "ko") -> str | None:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            text = " ".join([line["text"] for line in transcript])
            return text
        except TranscriptsDisabled:
            return None



    def generate_summary(self, text: str) -> str:
        openai.api_key = os.getenv("OPENAI_API_KEY")

        instructions = "영상의 요리방법만 요약해주세요"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"{instructions}\n\n{text[:1000]}",  # Truncate the prompt
            temperature=0.7,
            max_tokens=800,  # Adjust this value as needed
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=None
        )
        return response.choices[0].text.strip()

    def summarize_youtube_video(self, video_url: str) -> str:
        video_id = self.extract_youtube_video_id(video_url)

        if not video_id:
            return f"올바른 유튜브 url이 아닙니다. : {video_url}"

        # Try to retrieve the Korean transcript
        transcript = self.get_video_transcript(video_id, language="ko")

        if transcript is None:
            return f"한글 자막이 없는 영상입니다.: {video_url}"

        summary = self.generate_summary(transcript)
        return summary


    def post(self, request):
        video_url = request.data.get("url", "")
        if not video_url:
            return Response(
                {"message": "유튜브 url을 정확하게 입력해주세요"},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = self.summarize_youtube_video(video_url)
        # return Response({"summary": result}, status=status.HTTP_200_OK)
        if "올바른 유튜브 url이 아닙니다." in result or "한글 자막이 없는 영상입니다." in result:
            return Response({"message": result}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"summary": result}, status=status.HTTP_200_OK)

if __name__ == '__main__':
    url = "https://www.youtube.com/watch?v=D1R-jKKp3NA"
    yt_summary = YoutubeSummary()
    print(yt_summary.summarize_youtube_video(url))


# class YoutubeSummary(APIView):
#     def __init__(self):
#         super().__init__()
#         load_dotenv()

#     def extract_youtube_video_id(self, url: str) -> str | None:
#         found = re.search(r"(?:youtu\.be\/|watch\?v=)([\w-]+)", url)
#         if found:
#             return found.group(1)
#         return None

#     def get_video_transcript(self, video_id: str) -> str | None:
#         try:
#             transcript = YouTubeTranscriptApi.get_transcript(video_id)
#         except TranscriptsDisabled:
#             return None

#         text = " ".join([line["text"] for line in transcript])
#         return text

#     def generate_summary(self, text: str) -> str:
#         openai.api_key = os.getenv("OPENAI_API_KEY")

#         instructions = "Please summarize the provided text"
#         response = openai.Completion.create(
#             engine="text-davinci-002",
#             prompt=f"{instructions}\n\n{text}",
#             temperature=0.7,
#             max_tokens=1200,
#             top_p=1.0,
#             frequency_penalty=0.0,
#             presence_penalty=0.0
#         )

#         return response.choices[0].text.strip()

#     def summarize_youtube_video(self, video_url: str) -> str:
#         video_id = self.extract_youtube_video_id(video_url)

#         transcript = self.get_video_transcript(video_id)

#         if not transcript:
#             return f"No English transcript found for this video: {video_url}"

#         summary = self.generate_summary(transcript)
#         return summary

#     def post(self, request):
#         video_url = request.data.get("url", "")
#         if not video_url:
#             return Response(
#                 {"message": "Please provide a YouTube video URL"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         result = self.summarize_youtube_video(video_url)
#         return Response({"summary": result}, status=status.HTTP_200_OK)


# if __name__ == '__main__':
#     url = "https://www.youtube.com/watch?v=D1R-jKKp3NA"
#     yt_summary = YoutubeSummary()
#     print(yt_summary.summarize_youtube_video(url))